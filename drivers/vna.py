import pyvisa
import numpy as np


class VNA:
    """
    Driver SCPI para controle de VNA via VISA.

    Encapsula toda a comunicação com o instrumento: configuração inicial,
    definição do sweep de frequência e aquisição dos quatro parâmetros S
    (S11, S21, S12, S22) em formato complexo.

    Uso típico:
        vna = VNA("TCPIP0::192.168.10.12::inst0::INSTR")
        vna.setup(cal="cal.cal", pwr=-10, IF=1000)
        vna.configure_sweep(fstart=2e9, fstop=10e9, points=101)
        data = vna.measure_all_s()
    """

    def __init__(self, resource: str):
        """
        Abre sessão VISA com o instrumento e aplica configurações de comunicação.

        O preset (SYST:PRES) é executado para garantir um estado inicial
        conhecido, apagando qualquer configuração residual de sessões anteriores.
        """
        rm = pyvisa.ResourceManager()
        self.vna = rm.open_resource(resource)

        # Timeout alto porque sweeps com IF baixo ou muitos pontos podem
        # levar vários segundos para completar.
        self.vna.timeout = 20000  # ms

        # Configura transferência binária: REAL,64 = float64 (double precision).
        # SWAP inverte a ordem dos bytes para little-endian, que é o que o
        # numpy espera em arquiteturas x86/x64.
        self.vna.write("FORM:DATA REAL,64")
        self.vna.write("FORM:BORD SWAP")

        # Reset para estado padrão — apaga traces, calibrações em memória
        # e configurações de sweep anteriores.
        self.vna.write("SYST:PRES")

    def _idn(self) -> str:
        """Retorna a string de identificação do instrumento. Útil para debug."""
        return self.vna.query("*IDN?")

    def setup(self, cal: str = "", pwr: int = -10, IF: int = 1000) -> None:
        """
        Configura potência, IF bandwidth e cria os quatro traces S.

        Os traces são nomeados 'S11', 'S21', 'S12', 'S22' no canal 1 (CALC1).
        Esses nomes são usados depois em _get_complex_trace() para selecionar
        qual parâmetro ler.

        O carregamento de calibração está comentado em _load_calibration().
        Descomente a chamada abaixo se o VNA não retiver a calibração entre
        sessões.
        """
        # self._load_calibration(cal)  # descomente se necessário

        self.vna.write(f"SOUR:POW {pwr}")
        self.vna.write(f"SENS1:BAND {IF}")

        # Cria uma medição para cada parâmetro S no canal 1.
        # Se já existirem traces com esses nomes, o VNA pode sobrescrevê-los
        # ou emitir um erro dependendo do firmware — o preset em __init__
        # evita esse problema.
        self.vna.write("CALC1:PAR:DEF 'S11',S11")
        self.vna.write("CALC1:PAR:DEF 'S21',S21")
        self.vna.write("CALC1:PAR:DEF 'S12',S12")
        self.vna.write("CALC1:PAR:DEF 'S22',S22")

    def _load_calibration(self, filepath: str) -> None:
        """
        Carrega um arquivo de calibração da memória interna do VNA.

        O *OPC? bloqueia até a operação completar, garantindo que a
        calibração esteja ativa antes de qualquer medição.
        """
        self.vna.write(f"MMEM:LOAD:CORR '{filepath}'")
        self.vna.query("*OPC?")

    def configure_sweep(self, fstart: float, fstop: float, points: int) -> None:
        """
        Define o sweep de frequência no instrumento e gera o vetor local.

        O vetor self.freq é calculado localmente via np.linspace porque ler
        o eixo de frequência do VNA a cada sweep seria lento e desnecessário
        (o instrumento não altera os limites entre sweeps).

        ATENÇÃO: assume sweep linear uniforme. Se o VNA estiver configurado
        em modo logarítmico, self.freq estará errado — ajuste para np.logspace.
        """
        self.vna.write(f"SENS1:FREQ:STAR {fstart}")
        self.vna.write(f"SENS1:FREQ:STOP {fstop}")
        self.vna.write(f"SENS1:SWE:POIN {points}")

        self.freq = np.linspace(fstart, fstop, points)

    def _trigger(self) -> None:
        """
        Dispara um único sweep e aguarda sua conclusão.

        INIT:CONT OFF desativa o modo de sweep contínuo, garantindo que
        INIT:IMM execute exatamente um sweep. O *OPC? bloqueia até que o
        sweep termine — sem ele, a leitura dos dados poderia acontecer
        antes do instrumento completar a medição.
        """
        self.vna.write("INIT:CONT OFF")
        self.vna.write("INIT:IMM")
        self.vna.query("*OPC?")

    def _get_complex_trace(self, name: str) -> np.ndarray:
        """
        Lê os dados de um trace S e reconstrói o vetor complexo.

        O VNA retorna os dados intercalados como [Re0, Im0, Re1, Im1, ...].
        O fatiamento [0::2] e [1::2] separa as partes real e imaginária,
        que são combinadas em um array complexo.

        A leitura binária (query_binary_values) é muito mais rápida do que
        ASCII para vetores grandes — especialmente relevante com POINTS alto.
        """
        self.vna.write(f"CALC1:PAR:SEL '{name}'")
        raw = self.vna.query_binary_values(
            "CALC1:DATA? SDATA", datatype="d", container=np.array
        )
        return raw[0::2] + 1j * raw[1::2]

    def measure_all_s(self) -> dict:
        """
        Executa um sweep e retorna todos os parâmetros S em formato complexo.

        Retorna um dicionário com as chaves:
            'freq': np.ndarray (Nf,)           — frequências em Hz
            'S11', 'S21', 'S12', 'S22': np.ndarray (Nf,) complex

        Um único sweep é disparado antes de ler os quatro parâmetros,
        garantindo que todos correspondam ao mesmo instante de medição.
        """
        self._trigger()
        return {
            "freq": self.freq,
            "S11": self._get_complex_trace("S11"),
            "S21": self._get_complex_trace("S21"),
            "S12": self._get_complex_trace("S12"),
            "S22": self._get_complex_trace("S22"),
        }
