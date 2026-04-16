from __future__ import annotations

from pathlib import Path
from datetime import datetime
from uuid import uuid4
from time import time

import numpy as np
import pyvisa

from vna import VNA
from ..config import CFG
from tx import rotate_tx

class SYS:
    """
    Sistema integrado de medição VNA + motores.

    Este módulo coordena:
    - Configuração do VNA (frequência, potência, IF)
    - Controle angular das antenas (Tx e Rx)
    - Aquisição dos parâmetros S ao longo de uma varredura angular
    - Persistência dos dados em disco (.npz)

    Convenções assumidas:
    - self.rotate_tx(angle_deg): rotação absoluta da antena transmissora (Tx)
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

        self.WATCHDOG_TIMEOUT = 5.0  # segundos sem mudança tolerada

        # Diretório local para armazenamento dos dados
        # Observação: caminho relativo ao diretório de execução
        self.cache_dir = Path("../.cache/sys")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

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
        rotate_tx(0.0)

    def _set_tx_horizontal(self) -> None:
        """
        Configura a antena transmissora em polarização horizontal.

        Convenção adotada:
            90° → horizontal
        """
        rotate_tx(90.0)

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

        # Seleção da polarização da Tx
        if tx_pol == "V":
            self._set_tx_vertical()
            print("Antena transmissora posicionada na polarização vertical (V).")
        elif tx_pol == "H":
            self._set_tx_horizontal()
            print("Antena transmissora posicionada na polarização horizontal (H).")
        else:
            raise ValueError("tx_pol deve ser 'V' ou 'H'.")

        freq = None
        angles = []

        # Listas temporárias (posteriormente convertidas para arrays)
        s11_list = []
        s21_list = []
        s12_list = []
        s22_list = []

        rm = pyvisa.ResourceManager()

        # Enconder
        encoder = rm.open_resource("TCPIP0::192.168.10.10::gpib1,8::INSTR")
        encoder.clear()

        # Power supply
        pwr = rm.open_resource("TCPIP0::192.168.10.10::gpib1,6::INSTR")
        pwr.clear()
        try:
            pwr.write("VOLT 30")
            pwr.write("CURR 1")
            pwr.write("OUTP ON")

            measure = 0
            curr_angle = None
            last_change_time = time()

            while (measure < 720):
                angle = self._discretize_angle(self._parse_angle(encoder.query("MEAS?")))

                if curr_angle is None or int(10*angle) != int(10*curr_angle):
                    angles[measure] = angle
                    measure += 1
                    curr_angle = angle
                    last_change_time = time()
                    
                    data = self.vna.measure_all_s()

                    if freq is None:
                        freq = np.asarray(data["freq"])

                    s11_list.append(np.asarray(data["S11"]))
                    s21_list.append(np.asarray(data["S21"]))
                    s12_list.append(np.asarray(data["S12"]))
                    s22_list.append(np.asarray(data["S22"]))
                
                if time() - last_change_time > self.WATCHDOG_TIMEOUT:
                    raise RuntimeError("Watchdog: ângulo não evolui (possível travamento do encoder ou motor).")

        except KeyboardInterrupt:
            print("Interrompido pelo usuário (Ctrl+C).")

        except Exception as e:
            print(f"Erro crítico: {e}")

        else:
            print("Medida finalizada.")

        finally:
            print("Desligando fonte...")
            pwr.write("OUTP OFF")

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
    
    def _parse_angle(self, raw: str) -> float:
        raw = raw.strip()
        digits = raw[1:]

        integer_part = int(digits[:3])
        fractional_part = int(digits[3:]) / 1000

        angle = integer_part + fractional_part

        return round(angle, 1)

    def _discretize_angle(self, num: float) -> float:
        integer_part = int(num)
        fractional_part = int(10*num)-10*integer_part

        def parse_fractional_part(dec: int) -> float:
            if (dec <=2): 
                return 0.0
            elif (3 <= dec <= 6):
                return 0.5
            elif  (7 <= dec):
                return 1.0
            else:
                 raise ValueError("Parte fracionária da leitura do encoder fora do intervalo permtido.")

    out = integer_part + parse_fractional_part(fractional_part)
    if (int(out) == 360):
        out = 0.0

    return out
