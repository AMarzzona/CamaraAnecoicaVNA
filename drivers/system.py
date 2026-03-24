from __future__ import annotations

from pathlib import Path
from datetime import datetime
from uuid import uuid4
from time import sleep

import numpy as np

from vna import VNA
from motor import MTR
from ..config import CFG


class SYS:
    """
    Sistema integrado de medição VNA + motores.

    Este módulo coordena:
    - Configuração do VNA (frequência, potência, IF)
    - Controle angular das antenas (Tx e Rx)
    - Aquisição dos parâmetros S ao longo de uma varredura angular
    - Persistência dos dados em disco (.npz)

    Convenções assumidas:
    - self.mtr.rotate_tx(angle_deg): rotação absoluta da antena transmissora (Tx)
    - self.mtr.rotate_rx(angle_deg): rotação absoluta da antena receptora (Rx)
    - Sistema angular em graus [0, 360)

    Hipóteses importantes:
    - A geometria do sistema é fixa (somente Rx gira durante a varredura)
    - O VNA já está corretamente conectado e operacional
    - Não há verificação de erro de hardware (falhas de motor/VISA não tratadas)
    """

    def __init__(self):
        """
        Inicializa todo o sistema de medição.

        Sequência:
        1. Instancia o VNA e aplica configuração base
        2. Configura sweep de frequência
        3. Instancia o controlador de motores
        4. Prepara diretório de cache para armazenamento dos dados

        Dependências:
        - CFG deve conter todos os parâmetros necessários
        """

        # Inicialização do VNA (comunicação VISA)
        self.vna = VNA(CFG.VNA_ADDRESS)

        # Configuração operacional do VNA (potência, IF, traces)
        self.vna.setup(cal=CFG.CAL, pwr=CFG.PWR, IF=CFG.IF)

        # Configuração do sweep de frequência
        self.vna.configure_sweep(fstart=CFG.FSTART, fstop=CFG.FSTOP, points=CFG.POINTS)

        # Inicialização do sistema de motores
        self.mtr = MTR(CFG.MTR_ADDRESS)

        # Diretório local para armazenamento dos dados
        # Observação: caminho relativo ao diretório de execução
        self.cache_dir = Path("../.cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _step_angle(self) -> float:
        """
        Calcula o passo angular da varredura.

        Definição:
            step = BEAM_WIDTH / 10

        Interpretação física:
        - Amostragem angular equivalente a 10 pontos por largura de feixe
        - Garante resolução suficiente para reconstrução do diagrama de radiação

        Retorna:
            float: passo angular em graus

        Erro:
            - Lança exceção se BEAM_WIDTH <= 0
        """
        step = float(CFG.BEAM_WIDTH) / 10.0

        if step <= 0:
            raise ValueError("CFG.BEAM_WIDTH deve ser positivo.")

        return step

    def _angles(self) -> np.ndarray:
        """
        Gera vetor de ângulos para a varredura completa.

        Intervalo:
            [0, 360) com passo definido por _step_angle()

        Retorna:
            np.ndarray: vetor 1D de ângulos (graus)

        Observação:
            - 360 não é incluído (evita redundância com 0°)
            - Distribuição uniforme
        """
        step = self._step_angle()
        return np.arange(0.0, 360.0, step, dtype=float)

    def _make_run_id(self) -> str:
        """
        Gera identificador único para o experimento.

        Implementação:
            - UUID truncado (8 caracteres hexadecimais)

        Uso:
            - Evitar colisão de nomes de arquivos
            - Facilitar rastreabilidade de medições

        Retorna:
            str: identificador curto (ex: 'A1B2C3D4')
        """
        return uuid4().hex[:8].upper()

    def _make_filename(self, pol: str, run_id: str, timestamp: datetime) -> Path:
        """
        Gera nome do arquivo de saída.

        Formato:
            YYYYMMDD_HHMMSS_<ID>_<POL>.npz

        Onde:
            POL ∈ {V, H}

        Parâmetros:
            pol: polarização da Tx
            run_id: identificador do ensaio
            timestamp: instante da medição

        Retorna:
            Path completo para o arquivo

        Erro:
            - Lança exceção para polarização inválida
        """
        if pol not in {"V", "H"}:
            raise ValueError("pol deve ser 'V' ou 'H'.")

        name = f"{timestamp:%Y%m%d}_{timestamp:%H%M%S}_{run_id}_{pol}.npz"
        return self.cache_dir / name

    def _set_tx_vertical(self) -> None:
        """
        Configura a antena transmissora em polarização vertical.

        Convenção adotada:
            0° → vertical

        Dependência:
            - Implementação interna do driver MTR
        """
        self.mtr.rotate_tx(0.0)

    def _set_tx_horizontal(self) -> None:
        """
        Configura a antena transmissora em polarização horizontal.

        Convenção adotada:
            90° → horizontal
        """
        self.mtr.rotate_tx(90.0)

    def _measure_full_rotation(self, tx_pol: str) -> dict[str, np.ndarray]:
        """
        Executa varredura angular completa da antena receptora (Rx),
        mantendo a polarização da Tx fixa.

        Parâmetros:
            tx_pol: 'V' (vertical) ou 'H' (horizontal)

        Fluxo:
            1. Define polarização da Tx
            2. Itera sobre todos os ângulos
            3. Para cada ângulo:
                - posiciona Rx
                - aguarda estabilização mecânica
                - mede parâmetros S
            4. Empilha os resultados em arrays 2D

        Retorna:
            dict contendo:
                angle: (Na,)
                freq:  (Nf,)
                Sij:   (Na, Nf)

        Observações críticas:
            - Tempo de estabilização fixo (sleep)
              → pode ser insuficiente dependendo do motor
            - Não há verificação de erro de posicionamento
            - freq é assumido constante ao longo da varredura
        """
        angles = self._angles()

        # Seleção da polarização da Tx
        if tx_pol == "V":
            self._set_tx_vertical()
        elif tx_pol == "H":
            self._set_tx_horizontal()
        else:
            raise ValueError("tx_pol deve ser 'V' ou 'H'.")

        freq = None

        # Listas temporárias (posteriormente convertidas para arrays)
        s11_list = []
        s21_list = []
        s12_list = []
        s22_list = []

        for angle in angles:
            # Movimento da antena receptora (posição absoluta)
            self.mtr.rotate_rx(float(angle))

            # Tempo de acomodação mecânica
            # IMPORTANTE:
            # - valor empírico
            # - deve ser ajustado conforme inércia/carga do sistema
            sleep(0.001)

            # Aquisição dos parâmetros S
            data = self.vna.measure_all_s()

            # Captura vetor de frequência apenas na primeira iteração
            if freq is None:
                freq = np.asarray(data["freq"])

            # Armazenamento incremental
            s11_list.append(np.asarray(data["S11"]))
            s21_list.append(np.asarray(data["S21"]))
            s12_list.append(np.asarray(data["S12"]))
            s22_list.append(np.asarray(data["S22"]))

        # Conversão para arrays numpy estruturados
        result = {
            "angle": np.asarray(angles),
            "freq": np.asarray(freq),
            "S11": np.asarray(s11_list),
            "S21": np.asarray(s21_list),
            "S12": np.asarray(s12_list),
            "S22": np.asarray(s22_list),
        }

        return result

    def _save_measurement(
        self, data: dict[str, np.ndarray], pol: str, run_id: str, timestamp: datetime
    ) -> Path:
        """
        Persiste os dados da medição em arquivo .npz.

        Estrutura salva:
            - angle
            - freq
            - S11, S21, S12, S22

        Parâmetros:
            data: dicionário retornado por _measure_full_rotation
            pol: polarização da Tx
            run_id: identificador do ensaio
            timestamp: instante da medição

        Retorna:
            Path do arquivo salvo

        Observação:
            - np.savez usa compressão leve (não otimizada)
            - para grandes volumes, considerar np.savez_compressed
        """
        filepath = self._make_filename(pol=pol, run_id=run_id, timestamp=timestamp)

        np.savez(
            filepath,
            angle=data["angle"],
            freq=data["freq"],
            S11=data["S11"],
            S21=data["S21"],
            S12=data["S12"],
            S22=data["S22"],
        )

        return filepath

    def measurement(self) -> dict[str, Path]:
        """
        Executa o ciclo completo de medição do sistema.

        Sequência operacional:
            1. Define timestamp e ID do experimento
            2. Mede com Tx vertical
            3. Salva resultado (_V.npz)
            4. Mede com Tx horizontal
            5. Salva resultado (_H.npz)

        Retorna:
            dict:
                {
                    "v": Path do arquivo vertical,
                    "h": Path do arquivo horizontal
                }

        Considerações importantes:
            - Execução potencialmente longa (depende de Na × tempo de sweep)
            - Não há paralelismo
            - Falhas intermediárias não são tratadas (risco de perda parcial)
            - Timestamp é compartilhado entre V e H (mesmo experimento)
        """
        timestamp = datetime.now()
        run_id = self._make_run_id()

        # Medição com polarização vertical
        data_v = self._measure_full_rotation(tx_pol="V")
        file_v = self._save_measurement(
            data=data_v, pol="V", run_id=run_id, timestamp=timestamp
        )

        # Medição com polarização horizontal
        data_h = self._measure_full_rotation(tx_pol="H")
        file_h = self._save_measurement(
            data=data_h, pol="H", run_id=run_id, timestamp=timestamp
        )

        return {
            "v": file_v,
            "h": file_h,
        }
