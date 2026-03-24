from typing import NamedTuple


class Config(NamedTuple):
    """
    Estrutura imutável contendo todos os parâmetros do sistema de medição.

    Motivação:
    - Centralizar configuração experimental em um único ponto
    - Garantir consistência entre módulos (VNA, motores, aquisição)
    - Evitar efeitos colaterais (NamedTuple é imutável)

    Observação:
    - Alterações nesses parâmetros impactam diretamente:
        * Tempo total de medição
        * Resolução espectral (frequência)
        * Resolução angular
        * Nível de ruído (via IF bandwidth)
    """

    # -------------------------
    # Endereçamento de hardware
    # -------------------------

    VNA_ADDRESS: str
    """
    Endereço VISA do VNA.

    Exemplo:
        "TCPIP0::192.168.10.12::inst0::INSTR"

    Observações:
        - Deve ser compatível com pyvisa
        - Pode ser:
            * TCP/IP (LAN)
            * USB
            * GPIB
        - Erros aqui resultam em falha de conexão na inicialização
    """

    MTR_ADDRESS: str
    """
    Endereço do controlador de motores.

    Observações:
        - Depende da implementação da classe MTR
        - Pode ser:
            * Porta serial (ex: "COM3", "/dev/ttyUSB0")
            * Endereço IP (caso controle via rede)
        - Atualmente vazio → requer preenchimento para operação real
    """

    # -------------------------
    # Parâmetros do VNA
    # -------------------------

    PWR: int
    """
    Potência de saída do VNA (em dBm).

    Impacto:
        - Valores maiores → melhor relação sinal/ruído
        - Valores muito altos → risco de não linearidade/saturação

    Valor típico:
        -10 dBm (compromisso entre linearidade e SNR)
    """

    IF: int
    """
    Largura de banda do filtro IF (Hz).

    Impacto:
        - IF menor → menor ruído, maior tempo de sweep
        - IF maior → sweep mais rápido, maior ruído

    Trade-off crítico entre:
        precisão ↔ tempo de aquisição
    """

    CAL: str
    """
    Nome do arquivo de calibração no VNA.

    Observações:
        - Deve existir no sistema de arquivos interno do instrumento
        - Caminho relativo ao diretório corrente (MMEM:CDIR)

    Importante:
        - Calibração incorreta invalida completamente os resultados
    """

    FSTART: float
    """
    Frequência inicial do sweep (Hz).

    Observação:
        - Deve estar dentro da faixa operacional do VNA
    """

    FSTOP: float
    """
    Frequência final do sweep (Hz).

    Observação:
        - Define, junto com FSTART, a largura de banda analisada
    """

    POINTS: int
    """
    Número de pontos no sweep de frequência.

    Impacto:
        - Maior número → maior resolução espectral
        - Também aumenta:
            * tempo de medição
            * volume de dados (Na × Nf)

    Exemplo:
        1001 pontos → sweep relativamente denso
    """

    # -------------------------
    # Parâmetros geométricos
    # -------------------------

    BEAM_WIDTH: int
    """
    Largura de feixe da antena (graus).

    Uso no sistema:
        - Define o passo angular:
            step = BEAM_WIDTH / 10

    Interpretação:
        - Amostragem angular com ~10 pontos por feixe

    Impacto:
        - Valor menor → maior resolução angular (mais medições)
        - Valor maior → menor tempo total de aquisição

    Restrição:
        - Deve ser > 0 (validado em tempo de execução)
    """


# Instância global de configuração
CFG = Config(
    # Endereço do VNA via LAN (VISA)
    VNA_ADDRESS="TCPIP0::192.168.10.12::inst0::INSTR",
    # Endereço do controlador de motores (a definir conforme hardware)
    MTR_ADDRESS="",
    # Potência de saída (dBm)
    PWR=-10,
    # IF bandwidth (Hz)
    IF=1000,
    # Arquivo de calibração
    CAL="cal.cal",
    # Sweep de frequência
    FSTART=1,  # Hz (atenção: valor muito baixo pode ser inválido para alguns VNAs)
    FSTOP=18e9,  # 18 GHz
    POINTS=1001,  # resolução espectral
    # Parâmetro geométrico da antena
    BEAM_WIDTH=10,  # graus
)
