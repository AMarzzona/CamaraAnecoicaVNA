# Sistema de Medição VNA + Controle Angular

Sistema automatizado para aquisição de parâmetros S em câmara anecoica. Controla um VNA via VISA e dois motores de posicionamento angular (Tx e Rx) para realizar uma varredura de 360° nas polarizações vertical e horizontal.

---

## Execução

```bash
pip install numpy pyvisa
python main.py
```

Gera dois arquivos `.npz` em `../.cache/sys/` (um por polarização).

---

## Configuração

Todos os parâmetros estão em `config.py` na instância global `CFG`:

| Parâmetro | Descrição |
|-----------|-----------|
| `VNA_ADDRESS` | Endereço VISA do VNA (TCP/IP, USB ou GPIB) |
| `RX_ENCODER_ADDRESS` | Endereço VISA do encoder da Rx (GPIB over LAN) |
| `RX_POWERSUPPLY_ADDRESS` | Endereço VISA da fonte da Rx (GPIB over LAN) |
| `PWR` | Potência de saída do VNA (dBm) |
| `IF` | IF bandwidth (Hz) — afeta ruído e tempo de sweep |
| `CAL` | Nome do arquivo de calibração no VNA |
| `FSTART` / `FSTOP` | Faixa de frequência do sweep (Hz) |
| `POINTS` | Número de pontos do sweep |

---

## Arquitetura

```
main.py
└── drivers/system.py  (SYS)       ← orquestrador
    ├── drivers/vna.py (VNA)        ← driver SCPI via VISA
    └── drivers/tx.py  (rotate_tx)  ← chama tx.exe via subprocess
```

**`SYS`** abre conexões VISA com o encoder e a fonte da Rx, monitora o ângulo em polling, e a cada incremento de 0,5° dispara um sweep no VNA. Um watchdog aborta a medição se o ângulo ficar estagnado por mais de 5 s.

**`VNA`** envia comandos SCPI, transfere dados em binário `REAL,64` (double precision, little-endian) e reconstrói os vetores complexos S11/S21/S12/S22.

**`rotate_tx`** converte graus em steps (6000 steps/rev), chama `tx.exe` e verifica convergência lendo `../.cache/tx/finalPosition.txt`. Requer Windows e NI FlexMotion.

---

## Compilar o driver Tx (Windows)

```bat
cd drivers/tx_motor_control
build.bat
```

Requer `FlexMS32.lib` (NI FlexMotion). Gera `tx.exe` com placa ID 3, eixo 1.

---

## Formato dos dados

Cada `.npz` contém:

| Array | Shape | Tipo |
|-------|-------|------|
| `angle` | `(Na,)` | float |
| `freq` | `(Nf,)` | float |
| `S11`, `S21`, `S12`, `S22` | `(Na, Nf)` | complex |

Nome do arquivo: `YYYYMMDD_HHMMSS_<ID>_<POL>.npz`

---

## Convenções

- `rotate_tx(0°)` → polarização vertical; `rotate_tx(90°)` → horizontal
- Rx realiza a varredura; Tx permanece fixa durante cada medição
- O vetor `freq` é gerado localmente via `np.linspace` (sweep linear assumido)
- Encoder Rx: formato bruto `Xdddmmm` onde `ddd` = graus inteiros, `mmm/1000` = fração
