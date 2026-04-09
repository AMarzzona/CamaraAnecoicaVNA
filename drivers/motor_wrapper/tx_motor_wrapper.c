#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "nimotion.h"
#include "tx_motor_wrapper.h"

// =============================================================================
// Configuration
// =============================================================================

#define TX_AXIS 1

#define TX_VERTICAL_DEG   0.0
#define TX_HORIZONTAL_DEG 90.0

#define DEFAULT_VELOCITY     800.0
#define DEFAULT_ACCELERATION 5000.0
#define DEFAULT_DECELERATION 15000.0

#define MOTOR_STEPS_PER_REV 6000.0

#define WAIT_TIMEOUT_MS 30000
#define WAIT_POLL_MS 20

// =============================================================================
// Internal state
// =============================================================================

static TnimcInterfaceHandle g_handle = 0;
static int g_is_open = 0;
static int g_last_error_code = 0;
static char g_last_error_message[512] = "OK";

// =============================================================================
// Helpers
// =============================================================================

static double deg_to_steps(double deg)
{
    return deg * (MOTOR_STEPS_PER_REV / 360.0);
}

static double steps_to_deg(double steps)
{
    return steps * (360.0 / MOTOR_STEPS_PER_REV);
}

static void set_error(int code, const char* msg)
{
    g_last_error_code = code;
    strncpy(g_last_error_message, msg, sizeof(g_last_error_message) - 1);
    g_last_error_message[sizeof(g_last_error_message) - 1] = '\0';
}

static int check_rc(int rc, const char* context)
{
    if (rc != 0)
    {
        char desc[256] = {0};
        nimcGetErrorDescription(rc, desc, sizeof(desc));

        char full[512];
        snprintf(full, sizeof(full), "%s failed (rc=%d): %s", context, rc, desc);

        set_error(rc, full);
        return rc;
    }

    set_error(0, "OK");
    return 0;
}

static int ensure_open(void)
{
    if (!g_is_open)
    {
        set_error(-1, "Controller is not open");
        return -1;
    }
    return 0;
}

static int write_double_trajectory(TnimcTrajectoryData attr, double value)
{
    TnimcData data;
    memset(&data, 0, sizeof(data));
    data.doubleData = value;

    return check_rc(
        nimcWriteTrajectoryData(g_handle, TX_AXIS, attr, &data),
        "nimcWriteTrajectoryData"
    );
}

static int write_long_trajectory(TnimcTrajectoryData attr, long value)
{
    TnimcData data;
    memset(&data, 0, sizeof(data));
    data.longData = value;

    return check_rc(
        nimcWriteTrajectoryData(g_handle, TX_AXIS, attr, &data),
        "nimcWriteTrajectoryData"
    );
}

static int configure_default_profile(void)
{
    int rc;

    rc = write_double_trajectory(TnimcTrajectoryDataMaxVelocity, DEFAULT_VELOCITY);
    if (rc) return rc;

    rc = write_double_trajectory(TnimcTrajectoryDataMaxAcceleration, DEFAULT_ACCELERATION);
    if (rc) return rc;

    rc = write_double_trajectory(TnimcTrajectoryDataMaxDeceleration, DEFAULT_DECELERATION);
    if (rc) return rc;

    rc = write_long_trajectory(TnimcTrajectoryDataPositionMode, TnimcAxisPositionModeAbsolute);
    if (rc) return rc;

    return 0;
}

static int move_to_angle(double angle_deg)
{
    int rc;
    double target_steps = deg_to_steps(angle_deg);

    rc = configure_default_profile();
    if (rc) return rc;

    rc = write_double_trajectory(TnimcTrajectoryDataTargetPosition, target_steps);
    if (rc) return rc;

    rc = check_rc(nimcExecute(g_handle), "nimcExecute");
    if (rc) return rc;

    return 0;
}

static int wait_move_complete_internal(unsigned int timeout_ms)
{
    DWORD start = GetTickCount();

    while (1)
    {
        TnimcData data;
        memset(&data, 0, sizeof(data));

        int rc = check_rc(
            nimcReadAxisStatus(g_handle, TX_AXIS, TnimcAxisStatusMoveComplete, &data),
            "nimcReadAxisStatus(MoveComplete)"
        );
        if (rc) return rc;

        if (data.boolData)
            return 0;

        if ((GetTickCount() - start) > timeout_ms)
        {
            set_error(-2, "Timeout waiting for motion complete");
            return -2;
        }

        Sleep(WAIT_POLL_MS);
    }
}

// =============================================================================
// Exported API
// =============================================================================

__declspec(dllexport) int __stdcall tx_open(unsigned int board_id)
{
    int rc;

    if (g_is_open)
        return 0;

    rc = check_rc(
        nimcCreateControlInterface(&g_handle, board_id),
        "nimcCreateControlInterface"
    );
    if (rc) return rc;

    g_is_open = 1;
    return 0;
}

__declspec(dllexport) int __stdcall tx_close(void)
{
    int rc;

    if (!g_is_open)
        return 0;

    rc = check_rc(
        nimcDestroyControlInterface(g_handle),
        "nimcDestroyControlInterface"
    );
    if (rc) return rc;

    g_handle = 0;
    g_is_open = 0;
    return 0;
}

__declspec(dllexport) int __stdcall tx_initialize(void)
{
    int rc;

    rc = ensure_open();
    if (rc) return rc;

    rc = check_rc(nimcControllerInitialize(g_handle), "nimcControllerInitialize");
    if (rc) return rc;

    rc = check_rc(nimcAxisClearFaults(g_handle), "nimcAxisClearFaults");
    if (rc) return rc;

    rc = check_rc(nimcAxisPower(g_handle, 1, 1), "nimcAxisPower(ON)");
    if (rc) return rc;

    return 0;
}

__declspec(dllexport) int __stdcall tx_shutdown(void)
{
    int rc;

    rc = ensure_open();
    if (rc) return rc;

    rc = check_rc(nimcAxisPower(g_handle, 0, 0), "nimcAxisPower(OFF)");
    if (rc) return rc;

    return 0;
}

__declspec(dllexport) int __stdcall tx_set_zero(void)
{
    int rc;

    rc = ensure_open();
    if (rc) return rc;

    rc = check_rc(nimcAxisResetPosition(g_handle, 0.0), "nimcAxisResetPosition");
    if (rc) return rc;

    return 0;
}

__declspec(dllexport) int __stdcall tx_go_vertical(void)
{
    int rc;

    rc = ensure_open();
    if (rc) return rc;

    rc = move_to_angle(TX_VERTICAL_DEG);
    if (rc) return rc;

    rc = wait_move_complete_internal(WAIT_TIMEOUT_MS);
    if (rc) return rc;

    return 0;
}

__declspec(dllexport) int __stdcall tx_go_horizontal(void)
{
    int rc;

    rc = ensure_open();
    if (rc) return rc;

    rc = move_to_angle(TX_HORIZONTAL_DEG);
    if (rc) return rc;

    rc = wait_move_complete_internal(WAIT_TIMEOUT_MS);
    if (rc) return rc;

    return 0;
}

__declspec(dllexport) int __stdcall tx_stop(void)
{
    int rc;

    rc = ensure_open();
    if (rc) return rc;

    rc = check_rc(nimcStop(g_handle), "nimcStop");
    if (rc) return rc;

    return 0;
}

__declspec(dllexport) int __stdcall tx_get_position(double* position_deg)
{
    int rc;
    TnimcData data;

    if (position_deg == NULL)
    {
        set_error(-3, "position_deg is NULL");
        return -3;
    }

    rc = ensure_open();
    if (rc) return rc;

    memset(&data, 0, sizeof(data));

    rc = check_rc(
        nimcReadAxisData(g_handle, TX_AXIS, TnimcAxisDataPosition, &data),
        "nimcReadAxisData(Position)"
    );
    if (rc) return rc;

    *position_deg = steps_to_deg(data.doubleData);
    return 0;
}

__declspec(dllexport) int __stdcall tx_get_last_error_code(void)
{
    return g_last_error_code;
}

__declspec(dllexport) int __stdcall tx_get_last_error_message(char* buffer, unsigned int size)
{
    if (buffer == NULL || size == 0)
        return -1;

    strncpy(buffer, g_last_error_message, size - 1);
    buffer[size - 1] = '\0';
    return 0;
}