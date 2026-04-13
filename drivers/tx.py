import os
import subprocess
import time

BASE_DIR = os.path.dirname(__file__)

CONTROL_DIR = os.path.join(BASE_DIR, "tx_motor_control")
EXECUTABLE = os.path.join(CONTROL_DIR, "tx.exe")

# Caminho ABSOLUTO (fundamental agora)
CACHE_FILE = os.path.abspath(
    os.path.join(BASE_DIR, "..", ".cache", "tx", "finalPosition.txt")
)

os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

# =========================
# CONSTANTES DO SISTEMA
# =========================
STEPS_PER_REV = 6000
DEG_PER_REV = 360

MAX_ATTEMPTS = 10
RETRY_DELAY = 0.2  # segundos


def deg_to_steps(deg: float) -> int:
    steps = (STEPS_PER_REV / DEG_PER_REV) * deg
    return int(round(steps))


def _read_position():
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return None


def rotate_tx(target_deg: float):
    target_steps = deg_to_steps(target_deg)

    print(f"[TX] Target (deg): {target_deg}")
    print(f"[TX] Target (steps): {target_steps}")

    attempt = 0

    while True:
        current_steps = _read_position()

        print(f"[TX] Posição atual (steps): {current_steps}")

        # =========================
        # CONVERGÊNCIA
        # =========================
        if current_steps == target_steps:
            print("[TX] Posição atingida.")
            return

        # =========================
        # PROTEÇÃO
        # =========================
        if attempt >= MAX_ATTEMPTS:
            raise RuntimeError(
                f"[TX] Falha de convergência após {MAX_ATTEMPTS} tentativas. "
                f"Atual={current_steps}, Target={target_steps}"
            )

        attempt += 1
        print(f"[TX] Tentativa #{attempt} — movendo motor...")

        # =========================
        # CHAMADA DO EXECUTÁVEL
        # =========================
        result = subprocess.run(
            [
                EXECUTABLE,
                str(target_steps),
                CACHE_FILE
            ],
            cwd=CONTROL_DIR
        )

        if result.returncode != 0:
            raise RuntimeError("[TX] Erro ao executar tx.exe")

        time.sleep(RETRY_DELAY)