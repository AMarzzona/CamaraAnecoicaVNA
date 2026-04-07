#include <stdio.h>
#include <string.h>
#include <math.h>
#include <windows.h>

#pragma comment(lib, "nimotion.lib")

#include <motor_wrapper.h>
#include <nimotion.h>

// =============================================================================
// Internal constants
// =============================================================================

#define MOTOR_MAX_AXES 16
#define MOTOR_ERRMSG_SIZE 512

// Fixed mechanics for your setup
#define MOTOR_STEPS_PER_REV 200.0
#define MOTOR_MICROSTEPS    1.0
#define STEPS_PER_DEGREE    ((MOTOR_STEPS_PER_REV * MOTOR_MICROSTEPS) / 360.0)
#define DEGREES_PER_STEP    (360.0 / (MOTOR_STEPS_PER_REV * MOTOR_MICROSTEPS))

// =============================================================================
// Internal state
// =============================================================================

static TnimcInterfaceHandle g_handle = 0;
static int g_is_open = 0;

static int g_last_error = 0;
static char g_last_error_msg[MOTOR_ERRMSG_SIZE] = {0};

// Per-axis motion profile (stored in degrees units externally)
static double g_velocity_deg_s[MOTOR_MAX_AXES] = {0};
static double g_acceleration_deg_s2[MOTOR_MAX_AXES] = {0};
static double g_deceleration_deg_s2[MOTOR_MAX_AXES] = {0};
static double g_accel_jerk_deg_s3[MOTOR_MAX_AXES] = {0};
static double g_decel_jerk_deg_s3[MOTOR_MAX_AXES] = {0};

// =============================================================================
// Helpers
// =============================================================================

static int axis_valid(int axis) {
    return (axis >= 1 && axis < MOTOR_MAX_AXES);
}

static void set_local_error(int code, const char* msg) {
    g_last_error = code;
    strncpy(g_last_error_msg, msg, MOTOR_ERRMSG_SIZE - 1);
    g_last_error_msg[MOTOR_ERRMSG_SIZE - 1] = '\0';
}

static int set_error_from_ni(int status, const char* context) {
    char desc[256] = {0};
    char loc[256] = {0};

    g_last_error = status;

    if (g_is_open) {
        nimcGetLastError(g_handle, &g_last_error, desc, sizeof(desc), loc, sizeof(loc));
        snprintf(g_last_error_msg, MOTOR_ERRMSG_SIZE,
                 "%s | NI error=%d | %s | %s",
                 context, g_last_error, desc, loc);
    } else {
        snprintf(g_last_error_msg, MOTOR_ERRMSG_SIZE,
                 "%s | NI status=%d",
                 context, status);
    }

    return g_last_error;
}

static int ok_or_ni(int status, const char* context) {
    if (status != 0) {
        return set_error_from_ni(status, context);
    }
    return 0;
}

static int ensure_open(void) {
    if (!g_is_open) {
        set_local_error(-1000, "Controller is not open");
        return g_last_error;
    }
    return 0;
}

static int ensure_axis_valid(int axis) {
    if (!axis_valid(axis)) {
        set_local_error(-1001, "Invalid axis");
        return g_last_error;
    }
    return 0;
}

// -----------------------------------------------------------------------------
// Physical conversion helpers
// -----------------------------------------------------------------------------

static double round_to_nearest_step(double steps) {
    return floor(steps + 0.5);
}

static double deg_to_steps_quantized(double deg) {
    return round_to_nearest_step(deg * STEPS_PER_DEGREE);
}

static double steps_to_deg(double steps) {
    return steps * DEGREES_PER_STEP;
}

static double deg_s_to_steps_s(double value) {
    return value * STEPS_PER_DEGREE;
}

static double deg_s2_to_steps_s2(double value) {
    return value * STEPS_PER_DEGREE;
}

static double deg_s3_to_steps_s3(double value) {
    return value * STEPS_PER_DEGREE;
}

static void sleep_seconds(double seconds) {
    if (seconds <= 0.0) {
        return;
    }
    DWORD ms = (DWORD)(seconds * 1000.0);
    Sleep(ms);
}

// =============================================================================
// NI write/read helpers
// =============================================================================

static int write_trajectory_double(int axis, TnimcTrajectoryData attr, double value) {
    TnimcData data;
    memset(&data, 0, sizeof(data));
    data.doubleData = value;

    int status = nimcWriteTrajectoryData(g_handle, axis, attr, &data);
    return ok_or_ni(status, "nimcWriteTrajectoryData(double)");
}

static int write_trajectory_long(int axis, TnimcTrajectoryData attr, long value) {
    TnimcData data;
    memset(&data, 0, sizeof(data));
    data.longData = value;

    int status = nimcWriteTrajectoryData(g_handle, axis, attr, &data);
    return ok_or_ni(status, "nimcWriteTrajectoryData(long)");
}

static int read_axis_double(int axis, TnimcAxisData attr, double* out) {
    TnimcData data;
    memset(&data, 0, sizeof(data));

    int status = nimcReadAxisData(g_handle, axis, attr, &data);
    if (ok_or_ni(status, "nimcReadAxisData") != 0) {
        return g_last_error;
    }

    *out = data.doubleData;
    return 0;
}

static int read_axis_status_bool(int axis, TnimcAxisStatus attr, int* out) {
    TnimcData data;
    memset(&data, 0, sizeof(data));

    int status = nimcReadAxisStatus(g_handle, axis, attr, &data);
    if (ok_or_ni(status, "nimcReadAxisStatus") != 0) {
        return g_last_error;
    }

    *out = (data.boolData != 0) ? 1 : 0;
    return 0;
}

// =============================================================================
// Internal move execution
// =============================================================================

static int apply_profile_to_axis(int axis) {
    int rc;

    rc = write_trajectory_double(axis, TnimcTrajectoryDataMaxVelocity,
                                 deg_s_to_steps_s(g_velocity_deg_s[axis]));
    if (rc != 0) return rc;

    rc = write_trajectory_double(axis, TnimcTrajectoryDataMaxAcceleration,
                                 deg_s2_to_steps_s2(g_acceleration_deg_s2[axis]));
    if (rc != 0) return rc;

    rc = write_trajectory_double(axis, TnimcTrajectoryDataMaxDeceleration,
                                 deg_s2_to_steps_s2(g_deceleration_deg_s2[axis]));
    if (rc != 0) return rc;

    rc = write_trajectory_double(axis, TnimcTrajectoryDataMaxAccelJerk,
                                 deg_s3_to_steps_s3(g_accel_jerk_deg_s3[axis]));
    if (rc != 0) return rc;

    rc = write_trajectory_double(axis, TnimcTrajectoryDataMaxDecelJerk,
                                 deg_s3_to_steps_s3(g_decel_jerk_deg_s3[axis]));
    if (rc != 0) return rc;

    return 0;
}

static int execute_axis_move(int axis, double target_steps, int relative) {
    int rc = apply_profile_to_axis(axis);
    if (rc != 0) return rc;

    TnimcAxisStraightLineMoveData move_data;
    memset(&move_data, 0, sizeof(move_data));
    move_data.size = sizeof(move_data);
    move_data.startMode = TnimcAxisStraightLineMoveStartModeStart;
    move_data.positionMode = relative
        ? TnimcAxisStraightLineMovePositionModeRelative
        : TnimcAxisStraightLineMovePositionModeAbsolute;
    move_data.targetPosition = target_steps;

    TnimcMoveConstraints constraints;
    memset(&constraints, 0, sizeof(constraints));
    constraints.size = sizeof(constraints);
    constraints.velocity = deg_s_to_steps_s(g_velocity_deg_s[axis]);
    constraints.acceleration = deg_s2_to_steps_s2(g_acceleration_deg_s2[axis]);
    constraints.deceleration = deg_s2_to_steps_s2(g_deceleration_deg_s2[axis]);
    constraints.accelerationJerk = deg_s3_to_steps_s3(g_accel_jerk_deg_s3[axis]);
    constraints.decelerationJerk = deg_s3_to_steps_s3(g_decel_jerk_deg_s3[axis]);

    rc = nimcAxisStraightLineMove(g_handle, axis, &move_data, &constraints);
    return ok_or_ni(rc, "nimcAxisStraightLineMove");
}

// =============================================================================
// Public API
// =============================================================================

int motor_open_controller(unsigned int board_id) {
    if (g_is_open) {
        return 0;
    }

    memset(g_last_error_msg, 0, sizeof(g_last_error_msg));
    g_last_error = 0;

    int status = nimcCreateControlInterface(&g_handle, board_id);
    if (ok_or_ni(status, "nimcCreateControlInterface") != 0) {
        return g_last_error;
    }

    g_is_open = 1;
    return 0;
}

int motor_close_controller(void) {
    if (!g_is_open) {
        return 0;
    }

    int status = nimcDestroyControlInterface(g_handle);
    if (ok_or_ni(status, "nimcDestroyControlInterface") != 0) {
        return g_last_error;
    }

    g_handle = 0;
    g_is_open = 0;
    return 0;
}

int motor_reset_controller(void) {
    if (ensure_open() != 0) return g_last_error;
    return ok_or_ni(nimcResetController(g_handle), "nimcResetController");
}

int motor_clear_faults(void) {
    if (ensure_open() != 0) return g_last_error;
    return ok_or_ni(nimcClearFaults(g_handle), "nimcClearFaults");
}

int motor_initialize_axis(int axis) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    int rc = ok_or_ni(nimcControllerInitialize(g_handle), "nimcControllerInitialize");
    if (rc != 0) return rc;

    rc = ok_or_ni(nimcAxisClearFaults(g_handle), "nimcAxisClearFaults");
    if (rc != 0) return rc;

    // Conservative defaults
    if (g_velocity_deg_s[axis] <= 0.0)      g_velocity_deg_s[axis] = 10.0;
    if (g_acceleration_deg_s2[axis] <= 0.0) g_acceleration_deg_s2[axis] = 20.0;
    if (g_deceleration_deg_s2[axis] <= 0.0) g_deceleration_deg_s2[axis] = 20.0;
    if (g_accel_jerk_deg_s3[axis] <= 0.0)   g_accel_jerk_deg_s3[axis] = 100.0;
    if (g_decel_jerk_deg_s3[axis] <= 0.0)   g_decel_jerk_deg_s3[axis] = 100.0;

    return 0;
}

int motor_enable_axis(int axis) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;
    return ok_or_ni(nimcAxisPower(g_handle, 1, 1), "nimcAxisPower(enable)");
}

int motor_disable_axis(int axis) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;
    return ok_or_ni(nimcAxisPower(g_handle, 0, 0), "nimcAxisPower(disable)");
}

int motor_reset_position(int axis, double position_deg) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    double position_steps = deg_to_steps_quantized(position_deg);
    return ok_or_ni(nimcAxisResetPosition(g_handle, position_steps), "nimcAxisResetPosition");
}

int motor_set_velocity(int axis, double velocity_deg_s) {
    if (ensure_axis_valid(axis) != 0) return g_last_error;
    if (velocity_deg_s <= 0.0) {
        set_local_error(-1004, "Velocity must be > 0");
        return g_last_error;
    }
    g_velocity_deg_s[axis] = velocity_deg_s;
    return 0;
}

int motor_set_acceleration(int axis, double acceleration_deg_s2) {
    if (ensure_axis_valid(axis) != 0) return g_last_error;
    if (acceleration_deg_s2 <= 0.0) {
        set_local_error(-1005, "Acceleration must be > 0");
        return g_last_error;
    }
    g_acceleration_deg_s2[axis] = acceleration_deg_s2;
    return 0;
}

int motor_set_deceleration(int axis, double deceleration_deg_s2) {
    if (ensure_axis_valid(axis) != 0) return g_last_error;
    if (deceleration_deg_s2 <= 0.0) {
        set_local_error(-1006, "Deceleration must be > 0");
        return g_last_error;
    }
    g_deceleration_deg_s2[axis] = deceleration_deg_s2;
    return 0;
}

int motor_set_jerk(int axis, double accel_jerk_deg_s3, double decel_jerk_deg_s3) {
    if (ensure_axis_valid(axis) != 0) return g_last_error;
    if (accel_jerk_deg_s3 <= 0.0 || decel_jerk_deg_s3 <= 0.0) {
        set_local_error(-1007, "Jerk values must be > 0");
        return g_last_error;
    }
    g_accel_jerk_deg_s3[axis] = accel_jerk_deg_s3;
    g_decel_jerk_deg_s3[axis] = decel_jerk_deg_s3;
    return 0;
}

int motor_move_absolute(int axis, double position_deg) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    double target_steps = deg_to_steps_quantized(position_deg);
    return execute_axis_move(axis, target_steps, 0);
}

int motor_move_relative(int axis, double delta_deg) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    double target_steps = deg_to_steps_quantized(delta_deg);
    return execute_axis_move(axis, target_steps, 1);
}

int motor_stop(int axis) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;
    return ok_or_ni(nimcStop(g_handle), "nimcStop");
}

int motor_get_position(int axis, double* position_deg) {
    if (position_deg == NULL) {
        set_local_error(-1008, "Null pointer for position");
        return g_last_error;
    }

    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    double pos_steps = 0.0;
    int rc = read_axis_double(axis, TnimcAxisDataPosition, &pos_steps);
    if (rc != 0) return rc;

    *position_deg = steps_to_deg(pos_steps);
    return 0;
}

int motor_is_move_complete(int axis, int* done) {
    if (done == NULL) {
        set_local_error(-1009, "Null pointer for done");
        return g_last_error;
    }

    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    return read_axis_status_bool(axis, TnimcAxisStatusMoveComplete, done);
}

int motor_is_axis_active(int axis, int* active) {
    if (active == NULL) {
        set_local_error(-1010, "Null pointer for active");
        return g_last_error;
    }

    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    return read_axis_status_bool(axis, TnimcAxisStatusAxisActive, active);
}

int motor_is_moving(int axis, int* moving) {
    if (moving == NULL) {
        set_local_error(-1011, "Null pointer for moving");
        return g_last_error;
    }

    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    return read_axis_status_bool(axis, TnimcAxisStatusMoving, moving);
}

int motor_wait_move_complete(int axis, double timeout_s, double poll_interval_s) {
    if (ensure_open() != 0) return g_last_error;
    if (ensure_axis_valid(axis) != 0) return g_last_error;

    if (timeout_s <= 0.0) {
        set_local_error(-1012, "Timeout must be > 0");
        return g_last_error;
    }

    if (poll_interval_s <= 0.0) {
        poll_interval_s = 0.01;
    }

    double elapsed = 0.0;
    int done = 0;

    while (elapsed < timeout_s) {
        int rc = motor_is_move_complete(axis, &done);
        if (rc != 0) {
            return rc;
        }

        if (done) {
            return 0;
        }

        sleep_seconds(poll_interval_s);
        elapsed += poll_interval_s;
    }

    set_local_error(-1013, "Timeout waiting for move complete");
    return g_last_error;
}

int motor_get_last_error_code(void) {
    return g_last_error;
}

int motor_get_last_error_message(char* buffer, unsigned int size) {
    if (buffer == NULL || size == 0) {
        return -1;
    }

    strncpy(buffer, g_last_error_msg, size - 1);
    buffer[size - 1] = '\0';
    return 0;
}

int motor_quantize_angle(double requested_deg, double* realizable_deg) {
    if (realizable_deg == NULL) {
        set_local_error(-1014, "Null pointer for realizable_deg");
        return g_last_error;
    }

    double steps = deg_to_steps_quantized(requested_deg);
    *realizable_deg = steps_to_deg(steps);
    return 0;
}

int motor_get_step_resolution_deg(double* resolution_deg) {
    if (resolution_deg == NULL) {
        set_local_error(-1015, "Null pointer for resolution_deg");
        return g_last_error;
    }

    *resolution_deg = DEGREES_PER_STEP;
    return 0;
}