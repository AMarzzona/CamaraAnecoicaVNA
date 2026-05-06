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

    u8 boardID = 3;
    u8 axis    = 1;

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

    // Verifica se a placa saiu do estado de reset (deve ser inicializada via MAX)
    err = flex_read_csr_rtn(boardID, &csr);
    CheckError;

    if (csr & NIMC_POWER_UP_RESET)
    {
        printf("Placa em reset. Inicialize via MAX.\n");
        return -1;
    }

    // Configura e inicia movimento absoluto
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

    // Aguarda movimento completar
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

    // Persiste posição final para verificação de convergência pelo driver Python
    FILE *f = fopen(outputPath, "w");
    if (f != NULL)
    {
        fprintf(f, "%d", position);
        fclose(f);
    }
    else
    {
        perror("Erro ao escrever arquivo de cache");
    }

    return 0;

// Tratamento de erros NI FlexMotion
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
