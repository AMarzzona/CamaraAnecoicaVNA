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
    """Orquestrador do ciclo de medição: VNA + motores Tx/Rx."""

    def __init__(self):
        self.vna = VNA(CFG.VNA_ADDRESS)
        self.vna.setup(cal=CFG.CAL, pwr=CFG.PWR, IF=CFG.IF)
        self.vna.configure_sweep(fstart=CFG.FSTART, fstop=CFG.FSTOP, points=CFG.POINTS)

        self.WATCHDOG_TIMEOUT = 5.0  # s sem variação angular antes de abortar

        self.cache_dir = Path("../.cache/sys")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_run_id(self) -> str:
        return uuid4().hex[:8].upper()

    def _make_filename(self, pol: str, run_id: str, timestamp: datetime) -> Path:
        if pol not in {"V", "H"}:
            raise ValueError("pol deve ser 'V' ou 'H'.")
        name = f"{timestamp:%Y%m%d}_{timestamp:%H%M%S}_{run_id}_{pol}.npz"
        return self.cache_dir / name

    def _set_tx_vertical(self) -> None:
        rotate_tx(0.0)

    def _set_tx_horizontal(self) -> None:
        rotate_tx(90.0)

    def _measure_full_rotation(self, tx_pol: str) -> dict[str, np.ndarray]:
        """Varre 360° com a Rx enquanto a Tx permanece fixa na polarização dada."""
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
        encoder.clear()
        pwr = rm.open_resource(CFG.RX_POWERSUPPLY_ADDRESS)
        pwr.clear()

        try:
            pwr.write("VOLT 30")
            pwr.write("CURR 1")
            pwr.write("OUTP ON")

            measure = 0
            curr_angle = None
            last_change_time = time()

            while measure < 720:
                angle = self._discretize_angle(self._parse_angle(encoder.query("MEAS?")))

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

                if time() - last_change_time > self.WATCHDOG_TIMEOUT:
                    raise RuntimeError("Watchdog: ângulo estagnado — possível travamento.")

        except KeyboardInterrupt:
            print("Interrompido pelo usuário.")

        except Exception as e:
            print(f"Erro: {e}")

        else:
            print("Medição concluída.")

        finally:
            pwr.write("OUTP OFF")
            print("Fonte desligada.")

        return {
            "angle": np.asarray(angles),
            "freq": np.asarray(freq),
            "S11": np.asarray(s11_list),
            "S21": np.asarray(s21_list),
            "S12": np.asarray(s12_list),
            "S22": np.asarray(s22_list),
        }

    def _save_measurement(
        self, data: dict[str, np.ndarray], pol: str, run_id: str, timestamp: datetime
    ) -> Path:
        filepath = self._make_filename(pol=pol, run_id=run_id, timestamp=timestamp)
        np.savez(filepath, **data)
        return filepath

    def measurement(self) -> dict[str, Path]:
        """Executa medição completa (V + H) e retorna os caminhos dos arquivos salvos."""
        timestamp = datetime.now()
        run_id = self._make_run_id()

        data_v = self._measure_full_rotation(tx_pol="V")
        file_v = self._save_measurement(data_v, pol="V", run_id=run_id, timestamp=timestamp)

        data_h = self._measure_full_rotation(tx_pol="H")
        file_h = self._save_measurement(data_h, pol="H", run_id=run_id, timestamp=timestamp)

        return {"v": file_v, "h": file_h}

    def _parse_angle(self, raw: str) -> float:
        """Converte resposta bruta do encoder para graus decimais.

        Formato: um caractere líder seguido de dígitos onde
        digits[:3] = parte inteira e digits[3:] / 1000 = parte fracionária.
        """
        digits = raw.strip()[1:]
        return round(int(digits[:3]) + int(digits[3:]) / 1000, 1)

    def _discretize_angle(self, num: float) -> float:
        """Discretiza para resolução de 0.5°: ≤0.2 → 0.0, 0.3–0.6 → 0.5, ≥0.7 → 1.0."""
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
