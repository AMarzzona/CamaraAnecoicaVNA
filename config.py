from typing import NamedTuple


class Config(NamedTuple):
    """Parâmetros centralizados do sistema de medição (imutável)."""

    # Endereços VISA
    VNA_ADDRESS: str
    RX_ENCODER_ADDRESS: str
    RX_POWERSUPPLY_ADDRESS: str

    # Parâmetros do VNA
    PWR: int    # Potência de saída (dBm)
    IF: int     # IF bandwidth (Hz) — menor valor = menos ruído, sweep mais lento
    CAL: str    # Nome do arquivo de calibração no sistema de arquivos do VNA

    # Sweep de frequência
    FSTART: float   # Hz
    FSTOP: float    # Hz
    POINTS: int


CFG = Config(
    VNA_ADDRESS="TCPIP0::192.168.10.12::inst0::INSTR",
    RX_ENCODER_ADDRESS="TCPIP0::192.168.10.10::gpib1,8::INSTR",
    RX_POWERSUPPLY_ADDRESS="TCPIP0::192.168.10.10::gpib1,6::INSTR",
    PWR=-10,
    IF=1000,
    CAL="cal.cal",
    FSTART=2e9,
    FSTOP=10e9,
    POINTS=101,
)
