class SYS:
    """
    Orquestrador do sistema de medição VNA + posicionamento angular.

    Responsável por coordenar:
    - Configuração do VNA
    - Aquisição angular via encoder
    - Controle de polarização da Tx
    - Persistência dos dados experimentais
    """

    def __init__(self):
        """
        Inicializa os subsistemas e aplica configuração base.

        Etapas:
        - Instancia VNA via VISA
        - Aplica setup operacional (calibração, potência, IFBW)
        - Define sweep de frequência
        - Cria diretório de cache

        Premissas:
        - CFG contém parâmetros válidos
        - Recursos VISA estão acessíveis
        """
        self.vna = VNA(CFG.VNA_ADDRESS)
        self.vna.setup(cal=CFG.CAL, pwr=CFG.PWR, IF=CFG.IF)
        self.vna.configure_sweep(
            fstart=CFG.FSTART, fstop=CFG.FSTOP, points=CFG.POINTS
        )

        self.WATCHDOG_TIMEOUT = 5.0

        self.cache_dir = Path("../.cache/sys")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # =========================
    # Identificação / arquivos
    # =========================

    def _make_run_id(self) -> str:
        """
        Produz identificador curto para rastreabilidade do experimento.

        Implementação:
        - UUID truncado (8 hex chars, uppercase)

        Garantia:
        - Alta probabilidade de unicidade
        """
        return uuid4().hex[:8].upper()

    def _make_filename(self, pol: str, run_id: str, timestamp: datetime) -> Path:
        """
        Constrói caminho do arquivo de saída.

        Formato:
            YYYYMMDD_HHMMSS_<RUN>_<POL>.npz

        Validação:
        - pol ∈ {'V','H'}

        Retorno:
        - Path absoluto dentro do diretório de cache
        """
        if pol not in {"V", "H"}:
            raise ValueError("pol deve ser 'V' ou 'H'.")

        name = f"{timestamp:%Y%m%d}_{timestamp:%H%M%S}_{run_id}_{pol}.npz"
        return self.cache_dir / name

    # =========================
    # Polarização Tx
    # =========================

    def _set_tx_polarization(self, pol: str) -> None:
        """
        Posiciona a antena transmissora conforme polarização desejada.

        Convenção angular:
        - 0°  → Vertical
        - 90° → Horizontal

        Parâmetros:
        - pol: 'V' ou 'H'
        """
        if pol == "V":
            rotate_tx(0.0)
        elif pol == "H":
            rotate_tx(90.0)
        else:
            raise ValueError("Polarização inválida.")

    # =========================
    # VISA / Instrumentação
    # =========================

    def _init_instruments(self):
        """
        Inicializa recursos VISA utilizados na aquisição.

        Recursos:
        - Encoder (leitura angular)
        - Fonte de alimentação

        Retorno:
        - (encoder, pwr)
        """
        rm = pyvisa.ResourceManager()

        encoder = rm.open_resource("TCPIP0::192.168.10.10::gpib1,8::INSTR")
        encoder.clear()

        pwr = rm.open_resource("TCPIP0::192.168.10.10::gpib1,6::INSTR")
        pwr.clear()

        return encoder, pwr

    def _configure_power_supply(self, pwr) -> None:
        """
        Configura e energiza a fonte de alimentação.

        Ações:
        - Define tensão e corrente
        - Liga saída
        """
        pwr.write("VOLT 30")
        pwr.write("CURR 1")
        pwr.write("OUTP ON")

    def _shutdown_power_supply(self, pwr) -> None:
        """
        Desliga a fonte de alimentação de forma segura.
        """
        pwr.write("OUTP OFF")

    # =========================
    # Aquisição angular
    # =========================

    def _read_angle(self, encoder) -> float:
        """
        Lê e processa o ângulo atual do encoder.

        Pipeline:
        - Query VISA
        - Parsing da string
        - Discretização

        Retorno:
        - Ângulo em graus (quantizado)
        """
        raw = encoder.query("MEAS?")
        return self._discretize_angle(self._parse_angle(raw))

    def _should_sample(self, angle: float, last_angle: float | None) -> bool:
        """
        Determina se o novo ângulo representa avanço suficiente.

        Critério:
        - Diferença ≥ 0.1° (via comparação inteira escalada)

        Retorno:
        - True se deve adquirir novo ponto
        """
        if last_angle is None:
            return True

        return int(10 * angle) != int(10 * last_angle)

    def _acquire_sparameters(self):
        """
        Executa uma leitura completa dos parâmetros S no VNA.

        Retorno:
        - dict com chaves: freq, S11, S21, S12, S22
        """
        data = self.vna.measure_all_s()

        return {
            "freq": np.asarray(data["freq"]),
            "S11": np.asarray(data["S11"]),
            "S21": np.asarray(data["S21"]),
            "S12": np.asarray(data["S12"]),
            "S22": np.asarray(data["S22"]),
        }

    def _update_watchdog(self, last_change_time: float) -> float:
        """
        Atualiza timestamp de progresso angular.

        Retorno:
        - novo timestamp
        """
        return time()

    def _check_watchdog(self, last_change_time: float) -> None:
        """
        Verifica estagnação angular.

        Lança:
        - RuntimeError se tempo exceder limite
        """
        if time() - last_change_time > self.WATCHDOG_TIMEOUT:
            raise RuntimeError("Watchdog: ângulo não evolui.")

    def _measurement_loop(self, encoder) -> dict:
        """
        Loop principal de aquisição angular.

        Responsabilidades:
        - Monitorar evolução angular
        - Disparar medições no VNA
        - Acumular resultados

        Retorno:
        - dict com listas intermediárias
        """
        angles = []
        s11_list, s21_list, s12_list, s22_list = [], [], [], []

        freq = None
        last_angle = None
        last_change_time = time()

        measure = 0

        while measure < 720:
            angle = self._read_angle(encoder)

            if self._should_sample(angle, last_angle):
                angles.append(angle)
                print(angle)
                measure += 1

                last_angle = angle
                last_change_time = self._update_watchdog(last_change_time)

                #data = self._acquire_sparameters()

                #if freq is None:
                #    freq = data["freq"]

                #s11_list.append(data["S11"])
                #s21_list.append(data["S21"])
                #s12_list.append(data["S12"])
                #s22_list.append(data["S22"])

            self._check_watchdog(last_change_time)
        return
        #return {
        #    "angle": angles,
        #    "freq": freq,
        #    "S11": s11_list,
        #    "S21": s21_list,
        #    "S12": s12_list,
        #    "S22": s22_list,
        #}

    def _finalize_data(self, raw: dict) -> dict[str, np.ndarray]:
        """
        Converte listas acumuladas em arrays NumPy.

        Garante:
        - Estrutura consistente para persistência

        Retorno:
        - dict com arrays
        """
        return {
            "angle": np.asarray(raw["angle"]),
            "freq": np.asarray(raw["freq"]),
            "S11": np.asarray(raw["S11"]),
            "S21": np.asarray(raw["S21"]),
            "S12": np.asarray(raw["S12"]),
            "S22": np.asarray(raw["S22"]),
        }

    def _measure_full_rotation(self, tx_pol: str) -> dict[str, np.ndarray]:
        """
        Executa uma varredura angular completa com polarização fixa da Tx.

        Pipeline:
        - Configura polarização
        - Inicializa instrumentos
        - Executa loop de aquisição
        - Finaliza dados

        Tratamento:
        - Garante desligamento da fonte mesmo em erro

        Retorno:
        - Dados estruturados em arrays NumPy
        """
        self._set_tx_polarization(tx_pol)

        encoder, pwr = self._init_instruments()

        try:
            self._configure_power_supply(pwr)

            raw = self._measurement_loop(encoder)
        
        except KeyboardInterrupt:
            print("Interrompido pelo usuário (Ctrl+C).")

        except Exception as e:
            print(f"Erro crítico: {e}")

        else:
            print("Medida finalizada.")

        finally:
            print("Desligando fonte...")
            self._shutdown_power_supply(pwr)

        return self._finalize_data(raw)

    # =========================
    # Persistência
    # =========================

    def _save_measurement(
        self, data: dict[str, np.ndarray], pol: str, run_id: str, timestamp: datetime
    ) -> Path:
        """
        Serializa os dados experimentais em arquivo NPZ.

        Conteúdo:
        - angle, freq, S11, S21, S12, S22

        Retorno:
        - Path do arquivo gerado
        """
        filepath = self._make_filename(pol, run_id, timestamp)

        np.savez(filepath, **data)

        return filepath

    # =========================
    # API pública
    # =========================

    def measurement(self) -> dict[str, Path]:
        """
        Executa campanha completa (polarizações V e H).

        Fluxo:
        - Gera identificador e timestamp
        - Mede V
        - Mede H
        - Persiste ambos

        Retorno:
        - dict com paths dos arquivos gerados
        """
        timestamp = datetime.now()
        run_id = self._make_run_id()

        data_v = self._measure_full_rotation("V")
        file_v = self._save_measurement(data_v, "V", run_id, timestamp)

        data_h = self._measure_full_rotation("H")
        file_h = self._save_measurement(data_h, "H", run_id, timestamp)

        return {"v": file_v, "h": file_h}

    # =========================
    # Parsing / quantização
    # =========================

    def _parse_angle(self, raw: str) -> float:
        """
        Converte string do encoder em valor angular contínuo.

        Formato esperado:
        - Prefixo + dígitos (DDDmmm)

        Retorno:
        - Ângulo em graus com resolução de 0.1°
        """
        raw = raw.strip()
        digits = raw[1:]

        integer_part = int(digits[:3])
        fractional_part = int(digits[3:]) / 1000

        return round(integer_part + fractional_part, 1)

    def _discretize_angle(self, num: float) -> float:
        """
        Quantiza o ângulo em níveis discretos.

        Regra:
        - [0–0.2] → 0.0
        - [0.3–0.6] → 0.5
        - [0.7–0.9] → 1.0

        Retorno:
        - Ângulo discretizado
        """
        integer_part = int(num)
        fractional = int(10 * num) - 10 * integer_part

        if fractional <= 2:
            frac = 0.0
        elif fractional <= 6:
            frac = 0.5
        elif fractional <= 9:
            frac = 1.0
        else:
            raise ValueError("Frações inválidas do encoder.")
    
    out = integer_part + frac
    if (int(out) == 360):
        out = 0.0

    return out