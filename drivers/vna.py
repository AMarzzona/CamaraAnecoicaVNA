import pyvisa
import numpy as np


class VNA:
    """
    Driver simplificado para controle de um VNA via VISA (SCPI).

    Esta classe encapsula:
    - Configuração básica do instrumento
    - Configuração de sweep de frequência
    - Aquisição dos parâmetros S (S11, S21, S12, S22)

    Interface pública:
        - setup(...)
        - configure_sweep(...)
        - measure_all_s()

    Todos os demais métodos são internos e não devem ser utilizados diretamente.
    """

    def __init__(self, resource):
        """
        Inicializa a conexão com o instrumento via VISA.

        Parâmetros:
            resource (str): string VISA (ex: 'TCPIP0::192.168.0.10::inst0::INSTR')

        Efeitos colaterais:
            - Abre sessão VISA
            - Configura timeout
            - Define formato de dados binários (double, little-endian)
            - Executa preset do instrumento (estado conhecido)
        """

        rm = pyvisa.ResourceManager()
        self.vna = rm.open_resource(resource)

        # Timeout alto para evitar falhas em sweeps longos
        self.vna.timeout = 20000

        # Configuração para transferência binária eficiente:
        # REAL,64 → double precision (float64)
        # SWAP     → little-endian (compatível com numpy)
        self.vna.write("FORM:DATA REAL,64")
        self.vna.write("FORM:BORD SWAP")

        # Reset para estado padrão do instrumento
        # IMPORTANTE: isso apaga configurações anteriores
        self.vna.write("SYST:PRES")

    def _idn(self):
        """
        Consulta identificação do instrumento.

        Uso típico: debug ou verificação de conexão.
        """
        return self.vna.query("*IDN?")

    def setup(self, cal="", pwr=-10, IF=1000) -> None:
        """
        Configuração inicial do VNA.

        Parâmetros:
            cal (str): nome/arquivo de calibração (opcional)
            pwr (float): potência de saída (dBm)
            IF (float): largura de banda do filtro IF (Hz)

        Observações:
            - Define potência e IF bandwidth
            - Cria medições dos 4 parâmetros S
            - Não executa sweep
        """

        # Diretório atual de trabalho do VNA (para arquivos internos)
        CDIR = self.vna.query("MMEM:CDIR?")

        # Carregamento de calibração (desativado)
        # Se ativado, garantir que o caminho está correto no VNA
        # self._load_calibration(CDIR + cal)

        # Configuração de potência e largura de banda IF
        self.vna.write(f"SOUR:POW {pwr}")
        self.vna.write(f"SENS1:BAND {IF}")

        # Definição dos parâmetros S como traces ativos
        # IMPORTANTE:
        # - O nome ('S11', etc.) será usado para seleção posterior
        # - Se já existirem, o comportamento depende do firmware do VNA
        self.vna.write("CALC1:PAR:DEF 'S11',S11")
        self.vna.write("CALC1:PAR:DEF 'S21',S21")
        self.vna.write("CALC1:PAR:DEF 'S12',S12")
        self.vna.write("CALC1:PAR:DEF 'S22',S22")

    def _load_calibration(self, filepath: str) -> None:
        """
        Carrega arquivo de calibração no VNA.

        Parâmetros:
            filepath (str): caminho absoluto no sistema de arquivos do VNA

        Observação:
            - Bloqueia execução até conclusão (*OPC?)
        """
        self.vna.write(f"MMEM:LOAD:CORR '{filepath}'")
        self.vna.query("*OPC?")

    def configure_sweep(self, fstart, fstop, points) -> None:
        """
        Configura sweep de frequência.

        Parâmetros:
            fstart (float): frequência inicial (Hz)
            fstop (float): frequência final (Hz)
            points (int): número de pontos

        Efeitos:
            - Configura o sweep no VNA
            - Gera vetor de frequência local (self.freq)

        Atenção:
            - self.freq NÃO é lido do instrumento
            - Assume sweep linear uniforme
        """

        self.vna.write(f"SENS1:FREQ:STAR {fstart}")
        self.vna.write(f"SENS1:FREQ:STOP {fstop}")
        self.vna.write(f"SENS1:SWE:POIN {points}")

        # Vetor de frequência local (modelo ideal do sweep)
        # Se o VNA estiver em modo não linear, isso deve ser alterado
        self.freq = np.linspace(fstart, fstop, points)

    def _trigger(self) -> None:
        """
        Dispara uma medição única.

        Sequência:
            1. Desabilita modo contínuo
            2. Inicia sweep
            3. Aguarda conclusão (*OPC?)

        Observação:
            - Método bloqueante
            - Essencial para garantir consistência dos dados
        """

        self.vna.write("INIT:CONT OFF")
        self.vna.write("INIT:IMM")

        # Aguarda operação completar
        self.vna.query("*OPC?")

    def _get_complex_trace(self, name):
        """
        Obtém dados complexos de um parâmetro S.

        Parâmetros:
            name (str): nome do trace (ex: 'S11')

        Retorna:
            np.ndarray (complex): vetor complexo (Re + jIm)

        Processo:
            - Seleciona o trace
            - Lê dados binários intercalados (Re, Im)
            - Reconstrói vetor complexo

        Formato esperado:
            [Re0, Im0, Re1, Im1, ..., ReN, ImN]
        """

        # Seleciona parâmetro ativo
        self.vna.write(f"CALC1:PAR:SEL '{name}'")

        # Leitura binária direta (rápida e eficiente)
        raw = self.vna.query_binary_values(
            "CALC1:DATA? SDATA", datatype="d", container=np.array
        )

        # Reconstrução do vetor complexo
        complex_trace = raw[0::2] + 1j * raw[1::2]

        return complex_trace

    def measure_all_s(self):
        """
        Executa sweep e retorna todos os parâmetros S.

        Retorna:
            dict contendo:
                - 'freq': vetor de frequência
                - 'S11', 'S21', 'S12', 'S22': vetores complexos

        Fluxo:
            1. Dispara sweep (_trigger)
            2. Lê cada parâmetro individualmente
            3. Retorna dados organizados

        Observações importantes:
            - Ordem de leitura não afeta resultados
            - Assume que traces já foram definidos em setup()
            - self.freq deve ter sido previamente configurado
        """

        self._trigger()

        freq = self.freq

        S11 = self._get_complex_trace("S11")
        S21 = self._get_complex_trace("S21")
        S12 = self._get_complex_trace("S12")
        S22 = self._get_complex_trace("S22")

        return {"freq": freq, "S11": S11, "S21": S21, "S12": S12, "S22": S22}
