/*
 * tx.c — Driver de controle do motor stepper da antena Tx
 *
 * Uso: tx.exe <targetPosition> <outputPath>
 *
 *   targetPosition  Posição alvo em passos (inteiro). 6000 passos = 360°.
 *   outputPath      Caminho do arquivo onde a posição final será gravada.
 *                   O driver Python (tx.py) lê esse arquivo para verificar
 *                   se o motor convergiu.
 *
 * Hardware: NI FlexMotion, board ID 3, eixo 1.
 * Antes de usar, a placa deve ser inicializada no NI MAX (Measurement &
 * Automation Explorer). Se a placa estiver em estado de reset (power-up),
 * este programa retorna -1 imediatamente.
 *
 * Perfil de movimento:
 *   Aceleração / Desaceleração : 4000 passos/s²
 *   Velocidade máxima          : 500  passos/s
 *   Modo                       : posição absoluta
 */

#define _CRT_SECURE_NO_WARNINGS

#include "flexmotn.h"
#include "NIMCExample.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        printf("Uso: tx.exe <targetPosition> <outputPath>\n");
        return -1;
    }

    /* Identificação do hardware */
    u8 boardID = 3;
    u8 axis    = 1;

    /* Perfil cinemático do movimento */
    f64 acceleration = 4000;
    f64 deceleration = 4000;
    f64 velocity     = 500;

    i32         targetPosition = atoi(argv[1]);
    const char *outputPath     = argv[2];

    u16 axisStatus;
    u16 csr = 0;
    i32 position;
    u16 commandID;
    u16 resourceID;
    i32 errorCode;

    /*
     * Lê o Control and Status Register (CSR) da placa.
     * Se o bit POWER_UP_RESET estiver ativo, a placa ainda não foi
     * inicializada no NI MAX e não pode receber comandos de movimento.
     */
    err = flex_read_csr_rtn(boardID, &csr);
    CheckError;

    if (csr & NIMC_POWER_UP_RESET)
    {
        printf("Placa em reset. Inicialize via NI MAX antes de usar.\n");
        return -1;
    }

    /* Carrega o perfil de movimento e inicia o deslocamento absoluto */
    err = flex_load_acceleration(boardID, axis, NIMC_ACCELERATION, acceleration, 0xFF);
    CheckError;

    err = flex_load_acceleration(boardID, axis, NIMC_DECELERATION, deceleration, 0xFF);
    CheckError;

    err = flex_load_velocity(boardID, axis, velocity, 0xFF);
    CheckError;

    err = flex_set_op_mode(boardID, axis, NIMC_ABSOLUTE_POSITION);
    CheckError;

    err = flex_load_target_pos(boardID, axis, targetPosition, 0xFF);
    CheckError;

    err = flex_start(boardID, axis, 0);
    CheckError;

    /*
     * Polling até o movimento completar.
     * NIMC_MOVE_COMPLETE_BIT: movimento concluído normalmente.
     * NIMC_AXIS_OFF_BIT:      eixo desabilitado (condição de erro).
     * Se um erro modal ocorrer durante o movimento, a placa é parada
     * com desaceleração controlada antes de reportar o erro.
     */
    do
    {
        err = flex_read_pos_rtn(boardID, axis, &position);
        CheckError;

        err = flex_read_axis_status_rtn(boardID, axis, &axisStatus);
        CheckError;

        err = flex_read_csr_rtn(boardID, &csr);
        CheckError;

        if (csr & NIMC_MODAL_ERROR_MSG)
        {
            flex_stop_motion(boardID, NIMC_VECTOR_SPACE1, NIMC_DECEL_STOP, 0);
            err = csr & NIMC_MODAL_ERROR_MSG;
            CheckError;
        }

    } while (!(axisStatus & (NIMC_MOVE_COMPLETE_BIT | NIMC_AXIS_OFF_BIT)));

    printf("Posição final: %d\n", position);

    /*
     * Grava a posição final no arquivo de cache.
     * O driver Python (tx.py) lê esse valor na próxima chamada para
     * verificar se o motor atingiu a posição alvo antes de tentar novamente.
     */
    FILE *f = fopen(outputPath, "w");
    if (f != NULL)
    {
        fprintf(f, "%d", position);
        fclose(f);
    }
    else
    {
        perror("Erro ao gravar arquivo de cache");
    }

    return 0;

/* --------------------------------------------------------------------------
 * Tratamento de erros NI FlexMotion (macro nimcHandleError define o label).
 * Lê e exibe todos os erros modais pendentes antes de encerrar.
 * -------------------------------------------------------------------------- */
nimcHandleError;

    if (csr & NIMC_MODAL_ERROR_MSG)
    {
        do
        {
            flex_read_error_msg_rtn(boardID, &commandID, &resourceID, &errorCode);
            nimcDisplayError(errorCode, commandID, resourceID);
            flex_read_csr_rtn(boardID, &csr);
        } while (csr & NIMC_MODAL_ERROR_MSG);
    }
    else
    {
        nimcDisplayError(err, 0, 0);
    }

    return -1;
}
