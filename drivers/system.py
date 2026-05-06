from __future__ import annotations

from pathlib import Path
from datetime import datetime
from uuid import uuid4
from time import time

import numpy as np
import pyvisa

from drivers.vna import VNA
from config import CFG
from drivers.tx import rotate_tx


class SYS:
    """
    Orquestrador do ciclo de medição: VNA + motores Tx e Rx.

    Responsabilidades:
        - Inicializar e configurar o VNA.
        - Controlar a polarização da antena Tx (vertical ou horizontal).
        - Monitorar o encoder angular da antena Rx via VISA/GPIB.
        - Acionar a fonte de alimentação do motor da Rx.
        - Coletar parâmetros S a cada incremento de 0,5° durante a varredura.
        - Salvar os dados em arquivos .npz.

    Uso:
        inst = SYS()
        files = inst.measurement()
        # files["v"] → Path do arquivo com polarização vertical
        # files["h"] → Path do arquivo com polarização horizontal
    """

    def __init__(self):
        """
        Inicializa o VNA e prepara o diretório de saída.

        A inicialização do VNA inclui preset do instrumento, configuração
        de potência/IF e definição do sweep de frequência. Qualquer falha
        de conexão VISA aqui (endereço errado, instrumento desligado) lança
        uma exceção antes de qualquer medição começar.
        """
        self.vna = VNA(CFG.VNA_ADDRESS)
        self.vna.setup(cal=CFG.CAL, pwr=CFG.PWR, IF=CFG.IF)
        self.vna.configure_sweep(fstart=CFG.FSTART, fstop=CFG.FSTOP, points=CFG.POINTS)

        # Se o encoder ficar sem variar por mais do que esse tempo, a medição
        # é abortada — indica travamento mecânico ou perda de comunicação.
        self.WATCHDOG_TIMEOUT = 5.0  # segundos

        self.cache_dir = Path("../.cache/sys")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_run_id(self) -> str:
        """Gera um ID curto (8 hex) para identificar unicamente cada ensaio."""
        return uuid4().hex[:8].upper()

    def _make_filename(self, pol: str, run_id: str, timestamp: datetime) -> Path:
        """
        Monta o caminho do arquivo de saída.

        Formato: YYYYMMDD_HHMMSS_<ID>_<POL>.npz
        Exemplo: 20240315_143022_A1B2C3D4_V.npz
        """
        if pol not in {"V", "H"}:
            raise ValueError("pol deve ser 'V' ou 'H'.")
        name = f"{timestamp:%Y%m%d}_{timestamp:%H%M%S}_{run_id}_{pol}.npz"
        return self.cache_dir / name

    def _set_tx_vertical(self) -> None:
        """Posiciona a antena Tx em polarização vertical (0°)."""
        rotate_tx(0.0)

    def _set_tx_horizontal(self) -> None:
        """Posiciona a antena Tx em polarização horizontal (90°)."""
        rotate_tx(90.0)

    def _measure_full_rotation(self, tx_pol: str) -> dict[str, np.ndarray]:
        """
        Executa uma varredura angular completa da antena Rx (720 amostras).

        A antena Rx é movida por um motor DC alimentado pela fonte de
        alimentação GPIB. O encoder angular, também controlado via GPIB,
        é consultado em polling contínuo. A cada variação de 0,5° detectada
        pelo encoder, um sweep do VNA é disparado e os parâmetros S são
        armazenados.

        O loop termina após 720 amostras (correspondendo a duas rotações
        completas de 0,5° cada = 360° × 2, para garantir cobertura total
        mesmo com variações na velocidade do motor).

        Tratamento de interrupções:
            - KeyboardInterrupt (Ctrl+C): encerra o loop e salva os dados
              coletados até o momento.
            - RuntimeError do watchdog: idem — a fonte é sempre desligada
              no bloco finally.

        Retorna:
            dict com arrays numpy:
                'angle': (Na,)        — ângulos amostrados (graus)
                'freq':  (Nf,)        — frequências (Hz)
                'S11', 'S21', 'S12', 'S22': (Na, Nf) complex
        """
        if tx_pol == "V":
            self._set_tx_vertical()
            print("Tx: polarização vertical.")
        elif tx_pol == "H":
            self._set_tx_horizontal()
            print("Tx: polarização horizontal.")
        else:
            raise ValueError("tx_pol deve ser 'V' ou 'H'.")

        freq = None
        angles = []
        s11_list, s21_list, s12_list, s22_list = [], [], [], []

        rm = pyvisa.ResourceManager()

        encoder = rm.open_resource(CFG.RX_ENCODER_ADDRESS)
        encoder.clear()  # limpa buffer GPIB para evitar leituras residuais

        pwr = rm.open_resource(CFG.RX_POWERSUPPLY_ADDRESS)
        pwr.clear()

        try:
            # Liga o motor da Rx: 30 V, 1 A
            pwr.write("VOLT 30")
            pwr.write("CURR 1")
            pwr.write("OUTP ON")

            measure = 0
            curr_angle = None
            last_change_time = time()

            while measure < 720:
                # Lê e processa o ângulo atual do encoder
                angle = self._discretize_angle(self._parse_angle(encoder.query("MEAS?")))

                # Registra medição apenas quando o ângulo muda pelo menos 0,5°.
                # A comparação em décimos (int(10 * angle)) evita erros de
                # ponto flutuante ao comparar 0.5, 1.0, 1.5...
                if curr_angle is None or int(10 * angle) != int(10 * curr_angle):
                    angles.append(angle)
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

                # Watchdog: aborta se o encoder não variar por WATCHDOG_TIMEOUT segundos
                if time() - last_change_time > self.WATCHDOG_TIMEOUT:
                    raise RuntimeError("Watchdog: ângulo estagnado — possível travamento.")

        except KeyboardInterrupt:
            print("Interrompido pelo usuário.")

        except Exception as e:
            print(f"Erro: {e}")

        else:
            print("Medição concluída.")

        finally:
            # A fonte é desligada independentemente de como o loop terminou,
            # para não deixar o motor energizado sem supervisão.
            pwr.write("OUTP OFF")
            print("Fonte desligada.")

        return {
            "angle": np.asarray(angles),
            "freq":  np.asarray(freq),
            "S11":   np.asarray(s11_list),
            "S21":   np.asarray(s21_list),
            "S12":   np.asarray(s12_list),
            "S22":   np.asarray(s22_list),
        }

    def _save_measurement(
        self, data: dict[str, np.ndarray], pol: str, run_id: str, timestamp: datetime
    ) -> Path:
        """Salva o dicionário de resultados em um arquivo .npz não comprimido."""
        filepath = self._make_filename(pol=pol, run_id=run_id, timestamp=timestamp)
        np.savez(filepath, **data)
        return filepath

    def measurement(self) -> dict[str, Path]:
        """
        Executa o ciclo completo de medição: polarização V seguida de H.

        Ambas as medições compartilham o mesmo timestamp e run_id,
        facilitando a associação dos dois arquivos gerados.

        Retorna:
            {"v": Path, "h": Path}
        """
        timestamp = datetime.now()
        run_id = self._make_run_id()

        data_v = self._measure_full_rotation(tx_pol="V")
        file_v = self._save_measurement(data_v, pol="V", run_id=run_id, timestamp=timestamp)

        data_h = self._measure_full_rotation(tx_pol="H")
        file_h = self._save_measurement(data_h, pol="H", run_id=run_id, timestamp=timestamp)

        return {"v": file_v, "h": file_h}

    def _parse_angle(self, raw: str) -> float:
        """
        Interpreta a resposta bruta do encoder e retorna graus decimais.

        Formato da resposta: um caractere líder (ignorado) seguido de
        dígitos no padrão DDDmmm, onde:
            DDD = graus inteiros (3 dígitos, com zeros à esquerda)
            mmm = milésimos de grau (3 dígitos)

        Exemplo: "X045500" → 45 + 500/1000 = 45.5°
        """
        digits = raw.strip()[1:]
        return round(int(digits[:3]) + int(digits[3:]) / 1000, 1)

    def _discretize_angle(self, num: float) -> float:
        """
        Arredonda o ângulo para a resolução de 0,5°.

        Regra aplicada à parte fracionária (em décimos):
            0–2  → 0.0  (arredonda para baixo)
            3–6  → 0.5  (arredonda para metade)
            7–9  → 1.0  (arredonda para cima)

        Ângulos que resultam em 360° são normalizados para 0°.

        Essa discretização filtra o ruído natural do encoder, que pode
        oscilar entre leituras consecutivas na mesma posição física.
        """
        integer_part = int(num)
        dec = int(10 * num) - 10 * integer_part

        if dec <= 2:
            frac = 0.0
        elif dec <= 6:
            frac = 0.5
        else:
            frac = 1.0

        out = integer_part + frac
        return 0.0 if int(out) == 360 else out
