# Sistema de Medição VNA + Controle Angular

Sistema automatizado para aquisição de parâmetros S (S11, S21, S12, S22) em câmara anecoica. Controla um VNA via VISA/SCPI e dois sistemas de posicionamento angular — antena transmissora (Tx) e receptora (Rx) — para realizar uma varredura de 360° nas polarizações vertical e horizontal.

---

## Pré-requisitos

- Python ≥ 3.10
- `numpy` e `pyvisa` instalados:
  ```bash
  pip install numpy pyvisa
  ```
- NI-VISA instalado no sistema (fornece o backend VISA para o pyvisa)
- Todos os instrumentos ligados e acessíveis na rede antes de executar
- Motor Tx: apenas Windows, com NI FlexMotion instalado e placa inicializada no NI MAX (ver [Compilando o driver Tx](#compilando-o-driver-tx))

---

## Execução

```bash
python main.py
```

O script instancia o sistema, executa a varredura completa (V + H) e salva dois arquivos `.npz` em `../.cache/sys/`. O terminal exibe o progresso da medição em tempo real.

Para interromper antes do fim, pressione **Ctrl+C**: a fonte do motor Rx é desligada automaticamente e os dados coletados até aquele momento são salvos.

---

## Configuração

Todos os parâmetros estão em **`config.py`**, na instância global `CFG`. Edite apenas esse arquivo para adaptar o sistema a um novo hardware ou experimento.

| Parâmetro | Descrição | Efeito de aumentar |
|-----------|-----------|-------------------|
| `VNA_ADDRESS` | Endereço VISA do VNA | — |
| `RX_ENCODER_ADDRESS` | Endereço VISA do encoder da Rx | — |
| `RX_POWERSUPPLY_ADDRESS` | Endereço VISA da fonte da Rx | — |
| `PWR` | Potência de saída (dBm) | Melhor SNR, risco de saturação |
| `IF` | IF bandwidth (Hz) | Sweep mais rápido, mais ruído |
| `CAL` | Arquivo de calibração no VNA | — |
| `FSTART` / `FSTOP` | Faixa de frequência (Hz) | Maior cobertura espectral |
| `POINTS` | Pontos por sweep | Maior resolução, arquivos maiores |

**Formato dos endereços VISA:**
- TCP/IP direto: `"TCPIP0::<ip>::inst0::INSTR"`
- GPIB via controlador LAN: `"TCPIP0::<ip>::gpib1,<pad>::INSTR"` onde `<pad>` é o endereço primário do instrumento no barramento GPIB

Para descobrir os endereços disponíveis, execute `pyvisa-shell` e use o comando `list`.

---

## Arquitetura

```
main.py
└── drivers/system.py  (SYS)        ← orquestrador principal
    ├── drivers/vna.py  (VNA)        ← driver SCPI via VISA
    └── drivers/tx.py   (rotate_tx)  ← motor Tx via subprocess → tx.exe
config.py  (CFG)                     ← único ponto de configuração
```

### VNA (`drivers/vna.py`)

Comunica com o VNA via SCPI sobre VISA. Na inicialização, faz preset do instrumento e configura a transferência binária em `REAL,64` (double precision, little-endian), que é muito mais eficiente do que ASCII para vetores grandes. O vetor de frequência é calculado localmente via `np.linspace` — não é lido do instrumento.

### Motor Tx (`drivers/tx.py` + `drivers/tx_motor_control/tx.c`)

O motor Tx é controlado por uma placa NI FlexMotion. Como essa placa só tem driver para Windows, o controle é implementado em C (`tx.c`) e compilado como `tx.exe`. O Python chama o executável via `subprocess`, passando a posição alvo em passos e o caminho de um arquivo de cache. O executável realiza o movimento e grava a posição final no arquivo; o Python lê esse arquivo para verificar convergência e repetir se necessário.

Conversão: **6000 passos = 360°** (stepper).

### Motor e Encoder Rx (`drivers/system.py`)

O motor da Rx é alimentado por uma fonte DC controlada via GPIB (30 V, 1 A), que é ligada no início e desligada ao final de cada varredura. A posição angular é lida em polling contínuo a partir de um encoder GPIB. A cada variação de **0,5°** detectada, o VNA é acionado e os parâmetros S são coletados.

Um **watchdog** monitora se o encoder evolui: se o ângulo ficar estagnado por mais de 5 segundos, a medição é abortada com `RuntimeError` (indica travamento mecânico ou perda de comunicação).

### Encoder — formato da leitura

Resposta do encoder ao comando `MEAS?`:

```
Xdddmmm
```
- `X`   — caractere líder (ignorado)
- `ddd` — graus inteiros (3 dígitos, com zeros à esquerda)
- `mmm` — milésimos de grau

Exemplo: `"X045500"` → 45,5°

O ângulo é então discretizado para resolução de 0,5°:

| Parte fracionária (décimos) | Resultado |
|---|---|
| 0–2 | 0,0° |
| 3–6 | 0,5° |
| 7–9 | 1,0° |

---

## Dados gerados

Cada execução gera dois arquivos `.npz` em `../.cache/sys/`:

```
YYYYMMDD_HHMMSS_<ID>_V.npz   ← polarização vertical
YYYYMMDD_HHMMSS_<ID>_H.npz   ← polarização horizontal
```

Conteúdo de cada arquivo:

| Array | Shape | Tipo | Descrição |
|-------|-------|------|-----------|
| `angle` | `(Na,)` | float64 | Ângulos amostrados (graus) |
| `freq` | `(Nf,)` | float64 | Frequências do sweep (Hz) |
| `S11` | `(Na, Nf)` | complex128 | Parâmetro S11 em cada ângulo e frequência |
| `S21` | `(Na, Nf)` | complex128 | Parâmetro S21 |
| `S12` | `(Na, Nf)` | complex128 | Parâmetro S12 |
| `S22` | `(Na, Nf)` | complex128 | Parâmetro S22 |

Para carregar os dados em Python:

```python
import numpy as np

d = np.load("../.cache/sys/20240315_143022_A1B2C3D4_V.npz")
print(d["angle"])   # ângulos
print(d["S21"])     # matriz complexa (Na, Nf)
```

---

## Compilando o driver Tx (Windows)

Requer NI FlexMotion instalado (fornece `FlexMS32.lib` e os headers).

```bat
cd drivers/tx_motor_control
build.bat
```

Isso gera `tx.exe` no mesmo diretório. Parâmetros fixos no código: board ID 3, eixo 1, aceleração/desaceleração 4000 passos/s², velocidade 500 passos/s. Para alterar, edite `tx.c` e recompile.

**A placa NI FlexMotion deve estar inicializada no NI MAX antes de qualquer execução.** Se não estiver, `tx.exe` retorna erro imediatamente.

---

## Calibração do VNA

A calibração compensa as perdas de cabos e conectores. Deve ser realizada no próprio instrumento antes de cada sessão e salva com o nome definido em `CFG.CAL`. O carregamento automático está disponível em `vna._load_calibration()`, mas está desabilitado por padrão — ative chamando esse método em `vna.setup()` se o VNA não retiver a calibração entre sessões.

---

## Limitações conhecidas

- **Sem detecção de erro de posicionamento da Rx**: se o motor não atingir a posição esperada, o sistema continua medindo sem aviso.
- **Sweep assumido linear**: o vetor `freq` é gerado com `np.linspace`. Se o VNA estiver em modo logarítmico, os valores de frequência estarão incorretos.
- **Driver Tx exclusivo para Windows**: em outros sistemas operacionais, `rotate_tx()` falhará ao tentar executar `tx.exe`.
- **Execução sequencial**: as duas polarizações são medidas uma após a outra; não há paralelismo.
