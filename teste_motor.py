from drivers.tx import rotate_tx
import time

def main():
    print("=== TESTE MOTOR TX ===")

    rotate_tx(0)
    time.sleep(1)

    rotate_tx(90)
    time.sleep(1)

    rotate_tx(90)  # não deve mover

    rotate_tx(0)
    time.sleep(1)

    print("=== FIM ===")


if __name__ == "__main__":
    main()