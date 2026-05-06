import os
import subprocess
import time

BASE_DIR = os.path.dirname(__file__)
CONTROL_DIR = os.path.join(BASE_DIR, "tx_motor_control")
EXECUTABLE = os.path.join(CONTROL_DIR, "tx.exe")

# Posição final persistida entre chamadas para verificação de convergência
CACHE_FILE = os.path.abspath(
    os.path.join(BASE_DIR, "..", ".cache", "tx", "finalPosition.txt")
)
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

STEPS_PER_REV = 6000
DEG_PER_REV = 360
MAX_ATTEMPTS = 10
RETRY_DELAY = 0.2  # s


def deg_to_steps(deg: float) -> int:
    return int(round((STEPS_PER_REV / DEG_PER_REV) * deg))


def _read_position() -> int | None:
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return None


def rotate_tx(target_deg: float) -> None:
    """Move a antena Tx para a posição alvo (graus), com retenativas até MAX_ATTEMPTS."""
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

        time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"[TX] Falha de convergência após {MAX_ATTEMPTS} tentativas. "
        f"Atual={_read_position()}, Alvo={target_steps}"
    )
