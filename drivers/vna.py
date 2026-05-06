import pyvisa
import numpy as np


class VNA:
    """Driver SCPI para VNA via VISA."""

    def __init__(self, resource: str):
        rm = pyvisa.ResourceManager()
        self.vna = rm.open_resource(resource)
        self.vna.timeout = 20000  # ms — sweeps longos podem exceder o padrão

        # Transferência binária em double precision, little-endian (compatível com numpy)
        self.vna.write("FORM:DATA REAL,64")
        self.vna.write("FORM:BORD SWAP")

        self.vna.write("SYST:PRES")  # reset para estado conhecido

    def _idn(self):
        return self.vna.query("*IDN?")

    def setup(self, cal="", pwr=-10, IF=1000) -> None:
        """Configura potência, IF bandwidth e define os quatro traces S."""
        self.vna.write(f"SOUR:POW {pwr}")
        self.vna.write(f"SENS1:BAND {IF}")

        self.vna.write("CALC1:PAR:DEF 'S11',S11")
        self.vna.write("CALC1:PAR:DEF 'S21',S21")
        self.vna.write("CALC1:PAR:DEF 'S12',S12")
        self.vna.write("CALC1:PAR:DEF 'S22',S22")

    def _load_calibration(self, filepath: str) -> None:
        self.vna.write(f"MMEM:LOAD:CORR '{filepath}'")
        self.vna.query("*OPC?")

    def configure_sweep(self, fstart, fstop, points) -> None:
        """Configura o sweep e gera o vetor de frequência local."""
        self.vna.write(f"SENS1:FREQ:STAR {fstart}")
        self.vna.write(f"SENS1:FREQ:STOP {fstop}")
        self.vna.write(f"SENS1:SWE:POIN {points}")

        # Frequência calculada localmente — assume sweep linear (não lida do instrumento)
        self.freq = np.linspace(fstart, fstop, points)

    def _trigger(self) -> None:
        """Dispara um único sweep e aguarda conclusão (bloqueante)."""
        self.vna.write("INIT:CONT OFF")
        self.vna.write("INIT:IMM")
        self.vna.query("*OPC?")

    def _get_complex_trace(self, name: str) -> np.ndarray:
        """Lê um trace S e reconstrói o vetor complexo a partir dos pares (Re, Im)."""
        self.vna.write(f"CALC1:PAR:SEL '{name}'")
        raw = self.vna.query_binary_values(
            "CALC1:DATA? SDATA", datatype="d", container=np.array
        )
        return raw[0::2] + 1j * raw[1::2]

    def measure_all_s(self) -> dict:
        """Dispara sweep e retorna S11, S21, S12, S22 e o vetor de frequência."""
        self._trigger()
        return {
            "freq": self.freq,
            "S11": self._get_complex_trace("S11"),
            "S21": self._get_complex_trace("S21"),
            "S12": self._get_complex_trace("S12"),
            "S22": self._get_complex_trace("S22"),
        }
