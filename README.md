# Sistema de Medição VNA + Controle Angular

## Visão Geral

Este projeto implementa um sistema automatizado para aquisição de parâmetros de espalhamento (**S-parameters**) utilizando:

* Um **VNA (Vector Network Analyzer)** controlado via VISA
* Um sistema de **motores para posicionamento angular** de antenas transmissora (Tx) e receptora (Rx)

O objetivo principal é realizar medições angulares completas (0°–360°) para duas polarizações da antena transmissora:

* **Vertical (V)**
* **Horizontal (H)**

Os dados são armazenados em arquivos `.npz` para posterior análise.

---

## Arquitetura do Sistema

O sistema é composto por três módulos principais:

### 1. `vna.py`

Responsável pela comunicação com o VNA:

* Configuração do instrumento (potência, IF, traces)
* Configuração do sweep de frequência
* Aquisição dos parâmetros:

  * S11, S21, S12, S22

### 2. `motor.py`

(Implementação externa)

Responsável pelo controle dos motores:

* `rotate_tx(angle)` → posiciona antena transmissora
* `rotate_rx(angle)` → posiciona antena receptora

### 3. `sys.py` (classe `SYS`)

Orquestra todo o experimento:

* Coordena VNA + motores
* Executa varredura angular
* Armazena resultados

### 4. `config.py`

Define todos os parâmetros experimentais centralizados em `CFG`.

---

## Fluxo de Execução

A execução completa ocorre via:

```python
sys = SYS()
result = sys.measurement()
```

### Sequência:

1. Inicialização do VNA e motores
2. Configuração do sweep de frequência
3. Medição com Tx vertical:

   * Rotação completa da Rx (0° → 360°)
   * Aquisição dos parâmetros S
   * Salvamento em arquivo `_V.npz`
4. Medição com Tx horizontal:

   * Mesmo procedimento
   * Salvamento em `_H.npz`

---

## Estrutura dos Dados

Cada arquivo `.npz` contém:

* `angle`: vetor angular `(Na,)`
* `freq`: vetor de frequência `(Nf,)`
* `S11`, `S21`, `S12`, `S22`: matrizes `(Na, Nf)` complexas

### Interpretação:

* Cada linha corresponde a um ângulo
* Cada coluna corresponde a uma frequência

---

## Configuração

Todos os parâmetros estão definidos em:

```python
CFG = Config(...)
```

### Principais parâmetros:

| Parâmetro     | Descrição                          |
| ------------- | ---------------------------------- |
| `VNA_ADDRESS` | Endereço VISA do instrumento       |
| `MTR_ADDRESS` | Endereço do controlador de motores |
| `PWR`         | Potência (dBm)                     |
| `IF`          | Largura de banda IF (Hz)           |
| `FSTART`      | Frequência inicial                 |
| `FSTOP`       | Frequência final                   |
| `POINTS`      | Número de pontos do sweep          |
| `BEAM_WIDTH`  | Largura de feixe da antena         |

---

## Dependências

* Python ≥ 3.9
* `numpy`
* `pyvisa`

Instalação:

```bash
pip install numpy pyvisa
```

---

## Convenções Importantes

### Sistema Angular

* Unidade: graus
* Intervalo: `[0, 360)`
* Rx realiza a varredura
* Tx permanece fixa por medição

### Polarização

* `0°` → Vertical
* `90°` → Horizontal

### Frequência

* Sweep linear uniforme
* Vetor `freq` é gerado localmente (não lido do VNA)

---

## Pontos Críticos

### 1. Tempo de Medição

O tempo total é proporcional a:

```
N_ângulos × tempo_sweep
```

Onde:

```
N_ângulos ≈ 360 / (BEAM_WIDTH / 10)
```

---

### 2. IF Bandwidth

* Menor IF → maior precisão, maior tempo
* Maior IF → mais rápido, mais ruído

---

### 3. Estabilização Mecânica

```python
sleep(0.001)
```

* Valor empírico
* Pode ser insuficiente dependendo do sistema físico
* Principal fonte de erro em medições reais

---

### 4. Calibração

* Arquivo definido em `CFG.CAL`
* Deve existir no VNA
* Calibração incorreta invalida os dados

---

### 5. Armazenamento

* Dados salvos em `../.cache`
* Formato: `.npz`
* Sem compressão (rápido, porém maior uso de disco)

---

## Exemplo de Uso

```python
from sys import SYS

system = SYS()
files = system.measurement()

print(files["v"])
print(files["h"])
```

---

## Possíveis Extensões

* Paralelização de aquisição
* Compressão de dados (`np.savez_compressed`)
* Validação automática de parâmetros
* Interface gráfica para controle
* Suporte a múltiplos canais do VNA
* Sincronização mais precisa motor ↔ aquisição

---

## Limitações Atuais

* Sem tratamento de exceções (VISA/motor)
* Sem verificação de posição real dos motores
* Sweep de frequência assumido como linear
* Execução totalmente sequencial

---

## Licença

Uso interno / experimental.
