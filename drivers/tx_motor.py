from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Optional


class TxMotorError(RuntimeError):
    pass


def _default_dll_path() -> Path:
    here = Path(__file__).resolve().parent

    candidates = [
        here / "motor_wrapper" / "tx_motor_wrapper.dll",
        here / "tx_motor_wrapper.dll",
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Não foi possível localizar tx_motor_wrapper.dll"
    )


class TxMotor:
    def __init__(self, dll_path: Optional[str | os.PathLike[str]] = None):
        if dll_path is None:
            dll_path = _default_dll_path()

        self.dll_path = Path(dll_path).resolve()

        if not self.dll_path.exists():
            raise FileNotFoundError(f"DLL não encontrada: {self.dll_path}")

        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(self.dll_path.parent))

        self._dll = ctypes.WinDLL(str(self.dll_path))
        self._configure()

    def _configure(self) -> None:
        dll = self._dll

        dll.tx_open.argtypes = [ctypes.c_uint]
        dll.tx_open.restype = ctypes.c_int

        dll.tx_close.argtypes = []
        dll.tx_close.restype = ctypes.c_int

        dll.tx_initialize.argtypes = []
        dll.tx_initialize.restype = ctypes.c_int

        dll.tx_shutdown.argtypes = []
        dll.tx_shutdown.restype = ctypes.c_int

        dll.tx_set_zero.argtypes = []
        dll.tx_set_zero.restype = ctypes.c_int

        dll.tx_go_vertical.argtypes = []
        dll.tx_go_vertical.restype = ctypes.c_int

        dll.tx_go_horizontal.argtypes = []
        dll.tx_go_horizontal.restype = ctypes.c_int

        dll.tx_stop.argtypes = []
        dll.tx_stop.restype = ctypes.c_int

        dll.tx_get_position.argtypes = [ctypes.POINTER(ctypes.c_double)]
        dll.tx_get_position.restype = ctypes.c_int

        dll.tx_get_last_error_code.argtypes = []
        dll.tx_get_last_error_code.restype = ctypes.c_int

        dll.tx_get_last_error_message.argtypes = [ctypes.c_char_p, ctypes.c_uint]
        dll.tx_get_last_error_message.restype = ctypes.c_int

    def _last_error_message(self) -> str:
        buffer = ctypes.create_string_buffer(512)
        self._dll.tx_get_last_error_message(buffer, 512)
        return buffer.value.decode("utf-8", errors="replace")

    def _check(self, rc: int, context: str) -> None:
        if rc != 0:
            raise TxMotorError(f"{context} falhou: {self._last_error_message()}")

    def open(self, board_id: int = 1) -> None:
        self._check(self._dll.tx_open(board_id), "tx_open")

    def close(self) -> None:
        self._check(self._dll.tx_close(), "tx_close")

    def initialize(self) -> None:
        self._check(self._dll.tx_initialize(), "tx_initialize")

    def shutdown(self) -> None:
        self._check(self._dll.tx_shutdown(), "tx_shutdown")

    def set_zero(self) -> None:
        self._check(self._dll.tx_set_zero(), "tx_set_zero")

    def go_vertical(self) -> None:
        self._check(self._dll.tx_go_vertical(), "tx_go_vertical")

    def go_horizontal(self) -> None:
        self._check(self._dll.tx_go_horizontal(), "tx_go_horizontal")

    def stop(self) -> None:
        self._check(self._dll.tx_stop(), "tx_stop")

    def get_position(self) -> float:
        value = ctypes.c_double()
        self._check(self._dll.tx_get_position(ctypes.byref(value)), "tx_get_position")
        return float(value.value)

    def __enter__(self) -> "TxMotor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self.close()
        except Exception:
            pass