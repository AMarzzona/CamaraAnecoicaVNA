from drivers.motor import TxMotor, TxMotorError


def main():
    try:
        with TxMotor() as tx:
            print("Abrindo sistema...")
            tx.open(1)

            print("Inicializando TX...")
            tx.initialize()

            print("Definindo posição atual como 0°...")
            tx.set_zero()

            print("Indo para horizontal (90°)...")
            tx.go_horizontal()
            print(f"Posição atual: {tx.get_position():.3f} deg")

            print("Indo para vertical (0°)...")
            tx.go_vertical()
            print(f"Posição atual: {tx.get_position():.3f} deg")

            print("Desligando eixo...")
            tx.shutdown()

            print("Teste concluído.")

    except TxMotorError as e:
        print("ERRO DO MOTOR:")
        print(e)

    except Exception as e:
        print("ERRO GERAL:")
        print(e)


if __name__ == "__main__":
    main()