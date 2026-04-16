import pyvisa
import time
import numpy as np

from drivers.tx import rotate_tx

WATCHDOG_TIMEOUT = 2.0  # segundos sem mudança tolerada

def compare_angle_lists(angle_v, angle_h, tol=1e-9):
    """
    Ordena duas listas de ângulos, subtrai elemento a elemento
    e verifica se existe discrepância não nula (dentro de tolerância).

    Parâmetros:
    - angle_v, angle_h: listas de floats
    - tol: tolerância numérica para comparação (default: 1e-9)

    Saída:
    - Imprime diagnóstico
    """

    if len(angle_v) != len(angle_h):
        raise ValueError("Listas com tamanhos diferentes.")

    # Ordenação
    v_sorted = np.sort(np.asarray(angle_v))
    h_sorted = np.sort(np.asarray(angle_h))

    # Diferença elemento a elemento
    diff = v_sorted - h_sorted

    # Verificação robusta (evita erro de ponto flutuante)
    has_difference = np.any(np.abs(diff) > tol)

    print("Diferenças:", diff)
    print("Existe diferença não nula?", has_difference)


def parse_angle(raw: str) -> float:
    raw = raw.strip()
    digits = raw[1:]

    integer_part = int(digits[:3])
    fractional_part = int(digits[3:]) / 1000

    angle = integer_part + fractional_part

    return round(angle, 1)

def discretize_angle(num: float) -> float:
    integer_part = int(num)
    fractional_part = int(10*num)-10*integer_part

    def parse_fractional_part(dec: int) -> float:
        if (dec <=2): 
            return 0.0
        elif (3 <= dec <= 6):
            return 0.5
        elif  (7 <= dec):
            return 1.0
    
    out = integer_part + parse_fractional_part(fractional_part)
    if (int(out) == 360):
        out = 0.0

    return out 

rm = pyvisa.ResourceManager()

# Enconder
encoder = rm.open_resource("TCPIP0::192.168.10.10::gpib1,8::INSTR")
encoder.clear()

# Power supply
pwr = rm.open_resource("TCPIP0::192.168.10.10::gpib1,6::INSTR")
pwr.clear()

angle_v = []
angle_h = []

try:
    print("Posicionando antena transmissora na polarização vertical (V).")
    rotate_tx(0)
except Exception as e:
    print(f"Erro crítico: {e}")
finally:
    print("Antena posicionada na polarização vertical (V).")

try:
    pwr.write("VOLT 30")
    pwr.write("CURR 1")
    pwr.write("OUTP ON")


    measure = 0
    curr_angle = None
    last_change_time = time.time()

    while True:
        angle = discretize_angle(parse_angle(encoder.query("MEAS?")))

        if angle != curr_angle:
            measure += 1
            curr_angle = angle
            angle_tx.append(angle)
            last_change_time = time.time()
            print(angle)
        
        if time.time() - last_change_time > WATCHDOG_TIMEOUT:
            raise RuntimeError("Watchdog: ângulo não evolui (possível travamento do encoder ou motor).")

        if measure == 720:
            break

except KeyboardInterrupt:
    print("Interrompido pelo usuário (Ctrl+C).")

except Exception as e:
    print(f"Erro crítico: {e}")

else:
    print("Medida finalizada.")

finally:
    print("Desligando fonte...")
    pwr.write("OUTP OFF")

try:
    print("Posicionando antena transmissora na polarização horizontal (H).")
    rotate_tx(90)
except Exception as e:
    print(f"Erro crítico: {e}")
finally:
    print("Antena posicionada na polarização horizontal (H).")

try:
    pwr.write("VOLT 30")
    pwr.write("CURR 1")
    pwr.write("OUTP ON")


    measure = 0
    curr_angle = None
    last_change_time = time.time()

    while True:
        angle = discretize_angle(parse_angle(encoder.query("MEAS?")))

        if angle != curr_angle:
            measure += 1
            curr_angle = angle
            angle_rx.append(angle)
            last_change_time = time.time()
            print(angle)
        
        if time.time() - last_change_time > WATCHDOG_TIMEOUT:
            raise RuntimeError("Watchdog: ângulo não evolui (possível travamento do encoder ou motor).")

        if measure == 720:
            break

except KeyboardInterrupt:
    print("Interrompido pelo usuário (Ctrl+C).")

except Exception as e:
    print(f"Erro crítico: {e}")

else:
    print("Medida finalizada.")

finally:
    print("Desligando fonte...")
    pwr.write("OUTP OFF")


compare_angle_lists(angle_v, angle_h)
