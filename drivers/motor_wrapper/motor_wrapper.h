#ifndef MOTOR_WRAPPER_H
#define MOTOR_WRAPPER_H

#ifdef _WIN32
    #define MOTOR_API __declspec(dllexport)
#else
    #define MOTOR_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

// -----------------------------------------------------------------------------
// Controller lifecycle
// -----------------------------------------------------------------------------
MOTOR_API int motor_open_controller(unsigned int board_id);
MOTOR_API int motor_close_controller(void);
MOTOR_API int motor_reset_controller(void);
MOTOR_API int motor_clear_faults(void);

// -----------------------------------------------------------------------------
// Axis configuration
// -----------------------------------------------------------------------------
MOTOR_API int motor_initialize_axis(int axis);
MOTOR_API int motor_enable_axis(int axis);
MOTOR_API int motor_disable_axis(int axis);
MOTOR_API int motor_reset_position(int axis, double position_deg);

// -----------------------------------------------------------------------------
// Motion profile (degrees-based external API)
// -----------------------------------------------------------------------------
MOTOR_API int motor_set_velocity(int axis, double velocity_deg_s);
MOTOR_API int motor_set_acceleration(int axis, double acceleration_deg_s2);
MOTOR_API int motor_set_deceleration(int axis, double deceleration_deg_s2);
MOTOR_API int motor_set_jerk(int axis, double accel_jerk_deg_s3, double decel_jerk_deg_s3);

// -----------------------------------------------------------------------------
// Motion commands (degrees)
// -----------------------------------------------------------------------------
MOTOR_API int motor_move_absolute(int axis, double position_deg);
MOTOR_API int motor_move_relative(int axis, double delta_deg);
MOTOR_API int motor_stop(int axis);

// -----------------------------------------------------------------------------
// Readback
// -----------------------------------------------------------------------------
MOTOR_API int motor_get_position(int axis, double* position_deg);
MOTOR_API int motor_is_move_complete(int axis, int* done);
MOTOR_API int motor_is_axis_active(int axis, int* active);
MOTOR_API int motor_is_moving(int axis, int* moving);

// -----------------------------------------------------------------------------
// Utility
// -----------------------------------------------------------------------------
MOTOR_API int motor_wait_move_complete(int axis, double timeout_s, double poll_interval_s);
MOTOR_API int motor_quantize_angle(double requested_deg, double* realizable_deg);
MOTOR_API int motor_get_step_resolution_deg(double* resolution_deg);

// -----------------------------------------------------------------------------
// Diagnostics
// -----------------------------------------------------------------------------
MOTOR_API int motor_get_last_error_code(void);
MOTOR_API int motor_get_last_error_message(char* buffer, unsigned int size);

#ifdef __cplusplus
}
#endif

#endif // MOTOR_WRAPPER_H