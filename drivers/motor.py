from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Optional


# =============================================================================
# Exceptions
# =============================================================================

class MotorError(RuntimeError):
    """Erro levantado pela DLL de controle do motor."""
    pass


# =============================================================================
# DLL Loader
# =============================================================================

def _default_dll_path() -> Path:
    """
    Estrutura esperada:

    Meu projeto/
        drivers/
            motor.py
            motor_wrapper/
                motor_wrapper.dll
    """
    here = Path(__file__).resolve().parent

    candidates = [
        here / "motor_wrapper" / "motor_wrapper.dll",
        here / "motor_wrapper.dll",
        here.parent / "motor_wrapper.dll",
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Não foi possível localizar motor_wrapper.dll. "
        "Esperado em: drivers/motor_wrapper/motor_wrapper.dll"
    )


# =============================================================================
# Main class
# =============================================================================

class MotorController:
    """
    Interface Python para a DLL C de controle do NI Motion.

    Todas as posições públicas são tratadas em graus.
    """

    def __init__(self, dll_path: Optional[str | os.PathLike[str]] = None):
        if dll_path is None:
            dll_path = _default_dll_path()

        self.dll_path = Path(dll_path).resolve()

        if not self.dll_path.exists():
            raise FileNotFoundError(f"DLL não encontrada: {self.dll_path}")

        dll_dir = self.dll_path.parent
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(dll_dir))

        self._dll = ctypes.WinDLL(str(self.dll_path))
        self._configure_signatures()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _configure_signatures(self) -> None:
        dll = self._dll

        # Controller lifecycle
        dll.motor_open_controller.argtypes = [ctypes.c_uint]
        dll.motor_open_controller.restype = ctypes.c_int

        dll.motor_close_controller.argtypes = []
        dll.motor_close_controller.restype = ctypes.c_int

        dll.motor_reset_controller.argtypes = []
        dll.motor_reset_controller.restype = ctypes.c_int

        dll.motor_clear_faults.argtypes = []
        dll.motor_clear_faults.restype = ctypes.c_int

        # Axis configuration
        dll.motor_initialize_axis.argtypes = [ctypes.c_int]
        dll.motor_initialize_axis.restype = ctypes.c_int

        dll.motor_enable_axis.argtypes = [ctypes.c_int]
        dll.motor_enable_axis.restype = ctypes.c_int

        dll.motor_disable_axis.argtypes = [ctypes.c_int]
        dll.motor_disable_axis.restype = ctypes.c_int

        dll.motor_reset_position.argtypes = [ctypes.c_int, ctypes.c_double]
        dll.motor_reset_position.restype = ctypes.c_int

        # Motion profile
        dll.motor_set_velocity.argtypes = [ctypes.c_int, ctypes.c_double]
        dll.motor_set_velocity.restype = ctypes.c_int

        dll.motor_set_acceleration.argtypes = [ctypes.c_int, ctypes.c_double]
        dll.motor_set_acceleration.restype = ctypes.c_int

        dll.motor_set_deceleration.argtypes = [ctypes.c_int, ctypes.c_double]
        dll.motor_set_deceleration.restype = ctypes.c_int

        # Motion commands
        dll.motor_move_absolute.argtypes = [ctypes.c_int, ctypes.c_double]
        dll.motor_move_absolute.restype = ctypes.c_int

        dll.motor_move_relative.argtypes = [ctypes.c_int, ctypes.c_double]
        dll.motor_move_relative.restype = ctypes.c_int

        dll.motor_stop.argtypes = [ctypes.c_int]
        dll.motor_stop.restype = ctypes.c_int

        # Readback
        dll.motor_get_position.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
        dll.motor_get_position.restype = ctypes.c_int

        dll.motor_is_move_complete.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        dll.motor_is_move_complete.restype = ctypes.c_int

        dll.motor_is_axis_active.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        dll.motor_is_axis_active.restype = ctypes.c_int

        dll.motor_is_moving.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        dll.motor_is_moving.restype = ctypes.c_int

        # Utility
        dll.motor_wait_move_complete.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double]
        dll.motor_wait_move_complete.restype = ctypes.c_int

        # Diagnostics
        dll.motor_get_last_error_code.argtypes = []
        dll.motor_get_last_error_code.restype = ctypes.c_int

        dll.motor_get_last_error_message.argtypes = [ctypes.c_char_p, ctypes.c_uint]
        dll.motor_get_last_error_message.restype = ctypes.c_int

        # Optional helper functions
        if hasattr(dll, "motor_quantize_angle"):
            dll.motor_quantize_angle.argtypes = [ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
            dll.motor_quantize_angle.restype = ctypes.c_int

        if hasattr(dll, "motor_get_step_resolution_deg"):
            dll.motor_get_step_resolution_deg.argtypes = [ctypes.POINTER(ctypes.c_double)]
            dll.motor_get_step_resolution_deg.restype = ctypes.c_int

    def _get_last_error_message(self) -> str:
        buffer = ctypes.create_string_buffer(512)
        try:
            self._dll.motor_get_last_error_message(buffer, 512)
            return buffer.value.decode("utf-8", errors="replace")
        except Exception:
            return "Erro desconhecido ao consultar mensagem da DLL"

    def _check(self, rc: int, context: str) -> None:
        if rc != 0:
            msg = self._get_last_error_message()
            raise MotorError(f"{context} falhou (code={rc}): {msg}")

    # -------------------------------------------------------------------------
    # Controller lifecycle
    # -------------------------------------------------------------------------

    def open(self, board_id: int = 1) -> None:
        self._check(self._dll.motor_open_controller(board_id), "motor_open_controller")

    def close(self) -> None:
        self._check(self._dll.motor_close_controller(), "motor_close_controller")

    def reset_controller(self) -> None:
        self._check(self._dll.motor_reset_controller(), "motor_reset_controller")

    def clear_faults(self) -> None:
        self._check(self._dll.motor_clear_faults(), "motor_clear_faults")

    # -------------------------------------------------------------------------
    # Axis configuration
    # -------------------------------------------------------------------------

    def initialize_axis(self, axis: int) -> None:
        self._check(self._dll.motor_initialize_axis(axis), "motor_initialize_axis")

    def enable_axis(self, axis: int) -> None:
        self._check(self._dll.motor_enable_axis(axis), "motor_enable_axis")

    def disable_axis(self, axis: int) -> None:
        self._check(self._dll.motor_disable_axis(axis), "motor_disable_axis")

    def reset_position(self, axis: int, position: float = 0.0) -> None:
        self._check(
            self._dll.motor_reset_position(axis, float(position)),
            "motor_reset_position",
        )

    # -------------------------------------------------------------------------
    # Motion profile
    # -------------------------------------------------------------------------

    def set_velocity(self, axis: int, velocity: float) -> None:
        self._check(
            self._dll.motor_set_velocity(axis, float(velocity)),
            "motor_set_velocity",
        )

    def set_acceleration(self, axis: int, acceleration: float) -> None:
        self._check(
            self._dll.motor_set_acceleration(axis, float(acceleration)),
            "motor_set_acceleration",
        )

    def set_deceleration(self, axis: int, deceleration: float) -> None:
        self._check(
            self._dll.motor_set_deceleration(axis, float(deceleration)),
            "motor_set_deceleration",
        )

    def configure_profile(
        self,
        axis: int,
        velocity: float,
        acceleration: float,
        deceleration: Optional[float] = None,
    ) -> None:
        if deceleration is None:
            deceleration = acceleration

        self.set_velocity(axis, velocity)
        self.set_acceleration(axis, acceleration)
        self.set_deceleration(axis, deceleration)

    # -------------------------------------------------------------------------
    # Motion commands
    # -------------------------------------------------------------------------

    def move_absolute(self, axis: int, position: float) -> None:
        self._check(
            self._dll.motor_move_absolute(axis, float(position)),
            "motor_move_absolute",
        )

    def move_relative(self, axis: int, delta: float) -> None:
        self._check(
            self._dll.motor_move_relative(axis, float(delta)),
            "motor_move_relative",
        )

    def stop(self, axis: int) -> None:
        self._check(self._dll.motor_stop(axis), "motor_stop")

    # -------------------------------------------------------------------------
    # Readback
    # -------------------------------------------------------------------------

    def get_position(self, axis: int) -> float:
        value = ctypes.c_double()
        self._check(self._dll.motor_get_position(axis, ctypes.byref(value)), "motor_get_position")
        return float(value.value)

    def is_move_complete(self, axis: int) -> bool:
        value = ctypes.c_int()
        self._check(
            self._dll.motor_is_move_complete(axis, ctypes.byref(value)),
            "motor_is_move_complete",
        )
        return bool(value.value)

    def is_axis_active(self, axis: int) -> bool:
        value = ctypes.c_int()
        self._check(
            self._dll.motor_is_axis_active(axis, ctypes.byref(value)),
            "motor_is_axis_active",
        )
        return bool(value.value)

    def is_moving(self, axis: int) -> bool:
        value = ctypes.c_int()
        self._check(
            self._dll.motor_is_moving(axis, ctypes.byref(value)),
            "motor_is_moving",
        )
        return bool(value.value)

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def wait_move_complete(
        self,
        axis: int,
        timeout_s: float = 30.0,
        poll_interval_s: float = 0.01,
    ) -> None:
        self._check(
            self._dll.motor_wait_move_complete(axis, float(timeout_s), float(poll_interval_s)),
            "motor_wait_move_complete",
        )

    # -------------------------------------------------------------------------
    # Resolution / quantization helpers
    # -------------------------------------------------------------------------

    def quantize_angle(self, requested: float) -> float:
        if not hasattr(self._dll, "motor_quantize_angle"):
            raise NotImplementedError("A DLL atual não expõe motor_quantize_angle")

        value = ctypes.c_double()
        self._check(
            self._dll.motor_quantize_angle(float(requested), ctypes.byref(value)),
            "motor_quantize_angle",
        )
        return float(value.value)

    def get_step_resolution_deg(self) -> float:
        if not hasattr(self._dll, "motor_get_step_resolution_deg"):
            raise NotImplementedError("A DLL atual não expõe motor_get_step_resolution_deg")

        value = ctypes.c_double()
        self._check(
            self._dll.motor_get_step_resolution_deg(ctypes.byref(value)),
            "motor_get_step_resolution_deg",
        )
        return float(value.value)

    # -------------------------------------------------------------------------
    # Convenience high-level routines
    # -------------------------------------------------------------------------

    def move_absolute_blocking(
        self,
        axis: int,
        position: float,
        timeout_s: float = 30.0,
        poll_interval_s: float = 0.01,
    ) -> None:
        self.move_absolute(axis, position)
        self.wait_move_complete(axis, timeout_s=timeout_s, poll_interval_s=poll_interval_s)

    def move_relative_blocking(
        self,
        axis: int,
        delta: float,
        timeout_s: float = 30.0,
        poll_interval_s: float = 0.01,
    ) -> None:
        self.move_relative(axis, delta)
        self.wait_move_complete(axis, timeout_s=timeout_s, poll_interval_s=poll_interval_s)

    # -------------------------------------------------------------------------
    # Context manager support
    # -------------------------------------------------------------------------

    def __enter__(self) -> "MotorController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self.close()
        except Exception:
            pass