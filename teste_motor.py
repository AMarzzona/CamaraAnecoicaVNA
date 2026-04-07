from drivers.motor import MotorController, MotorError


def main() -> None:
    axis = 1
    board_id = 1

    try:
        with MotorController() as motor:
            print("Abrindo controlador...")
            motor.open(board_id)

            print(f"Inicializando eixo {axis}...")
            motor.initialize_axis(axis)

            print(f"Energizando eixo {axis}...")
            motor.enable_axis(axis)

            print("Limpando faults...")
            motor.clear_faults()

            print("Configurando perfil de movimento...")
            motor.configure_profile(
                axis=axis,
                velocity=800,
                acceleration=5000,
                deceleration=15000,
            )

            try:
                resolution = motor.get_step_resolution_deg()
                print(f"Resolução angular do sistema: {resolution:.6f} deg")
            except NotImplementedError:
                print("Função de resolução não disponível na DLL atual.")

            try:
                requested = 37.0
                realizable = motor.quantize_angle(requested)
                print(f"Ângulo pedido: {requested:.6f} deg")
                print(f"Ângulo realizável: {realizable:.6f} deg")
            except NotImplementedError:
                print("Função de quantização não disponível na DLL atual.")

            print("Resetando posição para 0 deg...")
            motor.reset_position(axis, 0.0)

            pos0 = motor.get_position(axis)
            print(f"Posição inicial: {pos0:.6f} deg")

            target = 90.0
            print(f"Movendo para {target:.6f} deg...")
            motor.move_absolute_blocking(axis, target, timeout_s=20.0)

            pos1 = motor.get_position(axis)
            print(f"Posição após movimento: {pos1:.6f} deg")

            print("Voltando para 0 deg...")
            motor.move_absolute_blocking(axis, 0.0, timeout_s=20.0)

            pos2 = motor.get_position(axis)
            print(f"Posição final: {pos2:.6f} deg")

            print("Desenergizando eixo...")
            motor.disable_axis(axis)

            print("Teste concluído com sucesso.")

    except MotorError as e:
        print("ERRO DE MOTOR:")
        print(e)

    except Exception as e:
        print("ERRO GERAL:")
        print(e)


if __name__ == "__main__":
    main()