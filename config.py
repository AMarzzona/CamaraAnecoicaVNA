from typing import NamedTuple


class Config(NamedTuple):
    """
    Parâmetros centralizados do sistema de medição.

    Usar NamedTuple garante imutabilidade: nenhum módulo pode alterar CFG
    acidentalmente em tempo de execução. Para modificar a configuração,
    edite apenas o bloco CFG = Config(...) ao final deste arquivo.
    """

    # ------------------------------------------------------------------
    # Endereços VISA dos instrumentos
    #
    # O formato depende da interface física:
    #   TCP/IP:  "TCPIP0::<ip>::inst0::INSTR"
    #   GPIB via LAN (controlador GPIB-LAN):
    #            "TCPIP0::<ip>::gpib1,<pad>::INSTR"
    #              onde <pad> é o Primary Address do instrumento no barramento GPIB
    #
    # Para descobrir o endereço correto, use o NI MAX (Windows) ou
    # execute pyvisa-shell e liste os recursos disponíveis.
    # ------------------------------------------------------------------

    VNA_ADDRESS: str
    # Endereço VISA do VNA. Conexão via TCP/IP direta.

    RX_ENCODER_ADDRESS: str
    # Endereço VISA do encoder angular da antena Rx.
    # Conectado via controlador GPIB-LAN (endereço GPIB primário 8).

    RX_POWERSUPPLY_ADDRESS: str
    # Endereço VISA da fonte de alimentação do motor da antena Rx.
    # Conectado via controlador GPIB-LAN (endereço GPIB primário 6).

    # ------------------------------------------------------------------
    # Parâmetros do VNA
    # ------------------------------------------------------------------

    PWR: int
    # Potência de saída da porta 1 do VNA, em dBm.
    # Valores típicos: entre -20 e 0 dBm.
    # Potências muito altas podem saturar o receptor ou introduzir
    # não-linearidades. -10 dBm é um compromisso seguro para a maioria
    # dos dispositivos sob teste.

    IF: int
    # Largura de banda do filtro IF (Intermediate Frequency), em Hz.
    # Controla a relação entre ruído e velocidade de medição:
    #   - IF baixo (ex: 100 Hz)  → menos ruído, sweep muito mais lento
    #   - IF alto  (ex: 10 kHz) → sweep rápido, mas mais ruidoso
    # Para esta aplicação (câmara anecoica, muitas posições angulares),
    # IF=1000 Hz oferece boa relação sinal/ruído sem tempo excessivo.

    CAL: str
    # Nome do arquivo de calibração armazenado na memória interna do VNA.
    # A calibração compensa as perdas dos cabos e conectores, e deve ser
    # realizada antes de cada sessão de medições.
    # ATENÇÃO: uma calibração incorreta ou desatualizada invalida todos
    # os dados coletados. Verifique a data da calibração antes de medir.
    # O carregamento está desabilitado em vna.py (_load_calibration não
    # é chamado); reative se necessário.

    # ------------------------------------------------------------------
    # Sweep de frequência
    # ------------------------------------------------------------------

    FSTART: float
    # Frequência inicial do sweep, em Hz. Ex: 2e9 = 2 GHz.

    FSTOP: float
    # Frequência final do sweep, em Hz. Ex: 10e9 = 10 GHz.

    POINTS: int
    # Número de pontos frequenciais por sweep.
    # Determina a resolução espectral: Δf = (FSTOP - FSTART) / (POINTS - 1).
    # Mais pontos aumentam a resolução, mas também o tempo de cada sweep
    # e o tamanho dos arquivos gerados.


# ------------------------------------------------------------------
# Instância global — único ponto de configuração do sistema.
# Altere os valores abaixo para adaptar a outro hardware ou experimento.
# ------------------------------------------------------------------
CFG = Config(
    VNA_ADDRESS="TCPIP0::192.168.10.12::inst0::INSTR",
    RX_ENCODER_ADDRESS="TCPIP0::192.168.10.10::gpib1,8::INSTR",
    RX_POWERSUPPLY_ADDRESS="TCPIP0::192.168.10.10::gpib1,6::INSTR",
    PWR=-10,        # dBm
    IF=1000,        # Hz
    CAL="cal.cal",
    FSTART=2e9,     # 2 GHz
    FSTOP=10e9,     # 10 GHz
    POINTS=101,
)
