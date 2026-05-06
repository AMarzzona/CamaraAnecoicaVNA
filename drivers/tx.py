import os
import subprocess
import time

BASE_DIR = os.path.dirname(__file__)
CONTROL_DIR = os.path.join(BASE_DIR, "tx_motor_control")
EXECUTABLE = os.path.join(CONTROL_DIR, "tx.exe")

# tx.exe não retorna a posição via stdout de forma confiável entre chamadas,
# por isso ela é persistida em arquivo. rotate_tx() lê esse arquivo para
# verificar se o motor convergiu antes de tentar novamente.
CACHE_FILE = os.path.abspath(
    os.path.join(BASE_DIR, "..", ".cache", "tx", "finalPosition.txt")
)
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

# O motor Tx é um stepper com 6000 passos por revolução completa (360°).
STEPS_PER_REV = 6000
DEG_PER_REV   = 360

MAX_ATTEMPTS = 10   # número máximo de tentativas antes de lançar RuntimeError
RETRY_DELAY  = 0.2  # segundos de espera entre tentativas


def deg_to_steps(deg: float) -> int:
    """Converte graus para passos do motor (6000 passos = 360°)."""
    return int(round((STEPS_PER_REV / DEG_PER_REV) * deg))


def _read_position() -> int | None:
    """
    Lê a última posição registrada pelo motor a partir do arquivo de cache.

    Retorna None se o arquivo não existir (primeira execução) ou se
    ocorrer qualquer erro de leitura.
    """
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return None


def rotate_tx(target_deg: float) -> None:
    """
    Move a antena Tx para a posição alvo em graus.

    Fluxo:
        1. Converte graus para passos.
        2. Lê a posição atual do arquivo de cache.
        3. Se já está na posição alvo, retorna imediatamente.
        4. Chama tx.exe com a posição alvo e o caminho do arquivo de cache.
           O executável move o motor e grava a posição final no arquivo.
        5. Repete até convergir ou atingir MAX_ATTEMPTS.

    tx.exe é um binário Windows que usa a biblioteca NI FlexMotion para
    controlar a placa de motion control (board ID 3, eixo 1). Ele recebe
    a posição alvo em passos e o caminho do arquivo onde deve gravar
    a posição atingida ao final do movimento.

    Lança RuntimeError se o motor não convergir após MAX_ATTEMPTS tentativas.
    """
    target_steps = deg_to_steps(target_deg)
    print(f"[TX] Alvo: {target_deg}° ({target_steps} steps)")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        current_steps = _read_position()
        print(f"[TX] Posição atual: {current_steps} steps")

        if current_steps == target_steps:
            print("[TX] Posição atingida.")
            return

        print(f"[TX] Tentativa #{attempt} — movendo motor...")
        result = subprocess.run(
            [EXECUTABLE, str(target_steps), CACHE_FILE],
            cwd=CONTROL_DIR,
        )

        if result.returncode != 0:
            raise RuntimeError("[TX] Erro ao executar tx.exe")

        # Aguarda o arquivo de cache ser atualizado pelo executável
        # antes de re-verificar a posição.
        time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"[TX] Falha de convergência após {MAX_ATTEMPTS} tentativas. "
        f"Atual={_read_position()}, Alvo={target_steps}"
    )
