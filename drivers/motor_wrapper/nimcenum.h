/*=============================================================================
                   National Instruments / NI-Motion                             
  ----------------------------------------------------------------------------  
      Copyright (c) National Instruments 2005.  All Rights Reserved.            
  ----------------------------------------------------------------------------  
                                                                                
   Title:       nimcenum.h                                                       
   Purpose:     Include file for NI-Motion library support. (nimotion.lib)    
                                                                                
=============================================================================*/

#ifndef ___nimcenum_h___
#define ___nimcenum_h___

#ifdef __cplusplus
   extern "C" {
#endif

//nimcReadMotionIOData, nimcWriteMotionIOData
//Notes: This enum changed in NI-Motion 7.3
typedef enum 
{
   TnimcMotionIODataForwardLimitActiveState = 0,      //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcMotionIODataReverseLimitActiveState,          //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcMotionIODataHomeInputActiveState,             //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcMotionIODataInhibitOutActiveState,            //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcMotionIODataInhibitInActiveState,             //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcMotionIODataInPositionActiveState,            //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcMotionIODataInhibitOutTotemPole,              //R/W  - boolData    - TnimcTrue (totem pole), TnimcFalse (open collector)
   TnimcMotionIODataForwardLimitEnable,               //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataReverseLimitEnable,               //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataHomeInputEnable,                  //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataInhibitOutEnable,                 //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataInhibitInEnable,                  //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataForwardSoftwareLimitEnable,       //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataReverseSoftwareLimitEnable,       //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataForwardSoftwareLimitPosition,     //R/W  - doubleData  - in user units of position
   TnimcMotionIODataReverseSoftwareLimitPosition,     //R/W  - doubleData  - in user units of position
   TnimcMotionIODataForwardLimitSwitchFilterTime,     //R/W  - doubleData  - in seconds
   TnimcMotionIODataReverseLimitSwitchFilterTime,     //R/W  - doubleData  - in seconds
   TnimcMotionIODataHomeInputFilterTime,              //R/W  - doubleData  - in seconds
   TnimcMotionIODataForwardLimitStopType,             //R/W  - longData    - TnimcMotionIODataStopType
   TnimcMotionIODataReverseLimitStopType,             //R/W  - longData    - TnimcMotionIODataStopType
   TnimcMotionIODataHomeInputStopType,                //R/W  - longData    - TnimcMotionIODataStopType
   TnimcMotionIODataForwardSoftwareLimitStopType,     //R/W  - longData    - TnimcMotionIODataStopType
   TnimcMotionIODataReverseSoftwareLimitStopType,     //R/W  - longData    - TnimcMotionIODataStopType
   TnimcMotionIODataForwardLimitActive,               //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataReverseLimitActive,               //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataHomeInputActive,                  //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataInhibitOutActive,                 //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)  
   TnimcMotionIODataInhibitInActive,                  //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataForwardSoftwareLimitActive,       //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataReverseSoftwareLimitActive,       //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataInPositionActive,                 //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataForwardLimitSwitchFilterEnable,   //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataReverseLimitSwitchFilterEnable,   //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataHomeInputFilterEnable,            //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataPulseAlarmClear,                  //W    - boolData    - TnimcTrue (pulse), TnimcFalse (do not pulse)
   TnimcMotionIODataAlarmClearPulseWidth,             //R/W  - doubleData  - in seconds
   TnimcMotionIODataDriveReadyActiveState,            //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcMotionIODataDriveReadyEnable,                 //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcMotionIODataDriveReadyActive,                 //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcMotionIODataLast,
} TnimcMotionIOData;

//nimcReadMotionIOData, nimcWriteMotionIOData
typedef enum
{
   TnimcMotionIODataStopTypeDecelerate = 0,           //Decelerate the axis to a stop.
   TnimcMotionIODataStopTypeImmediate,                //Immediately stop the axis.
   TnimcMotionIODataStopTypeDeactivateAxis,           //Deactivate the axis.  Stop energizing the axis.
   TnimcMotionIODataStopTypeLast,
} TnimcMotionIODataStopType;

//nimcReadAxisData
typedef enum
{
   TnimcAxisDataPosition = 0,                         //R    - doubleData  - in user units of position
   TnimcAxisDataVelocity,                             //R    - doubleData  - in user units of position / second
   TnimcAxisDataFollowingError,                       //R    - doubleData  - in user units of position
   TnimcAxisDataLast,
} TnimcAxisData;

//nimcReadAxisStatus
//Notes: This enum changed in NI-Motion 7.3
typedef enum
{
   TnimcAxisStatusAxisActive = 0,                     //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcAxisStatusMoveComplete,                       //R    - boolData    - TnimcTrue (complete), TnimcFalse (not complete)
   TnimcAxisStatusProfileComplete,                    //R    - boolData    - TnimcTrue (complete), TnimcFalse (not complete)
   TnimcAxisStatusBlendComplete,                      //R    - boolData    - TnimcTrue (complete), TnimcFalse (not complete)
   TnimcAxisStatusProfileMode,                        //R    - longData    - TnimcProfileMode
   TnimcAxisStatusFollowingErrorExceeded,             //R    - boolData    - TnimcTrue (exceeded), TnimcFalse (not exceeded)
   TnimcAxisStatusVelocityThresholdExceeded,          //R    - boolData    - TnimcTrue (exceeded), TnimcFalse (not exceeded)
   TnimcAxisStatusMoving,                             //R    - boolData    - TnimcTrue (moving), TnimcFalse (not moving)
   TnimcAxisStatusDirectionForward,                   //R    - boolData    - TnimcTrue (forward), TnimcFalse (reverse)
   TnimcAxisStatusLast,
} TnimcAxisStatus;

//nimcReadAxisStatus, nimcReadCoordinateStatus
typedef enum 
{
   TnimcAxisStatusProfileModeAccelInc = 0,            //Acceleration Increasing (from S-Curve)
   TnimcAxisStatusProfileModeAccelConst,              //Acceleration Constant
   TnimcAxisStatusProfileModeAccelDec,                //Acceleraiton Decreasing (from S-Curve)
   TnimcAxisStatusProfileModeCruise,                  //Cruising Velocity
   TnimcAxisStatusProfileModeDecelInc,                //Deceleration Increasing (from S-Curve)
   TnimcAxisStatusProfileModeDecelConst,              //Deceleration Constant
   TnimcAxisStatusProfileModeDecelDec,                //Deceleration Decreasing (from S-Curve)
   TnimcAxisStatusProfileModeStop,                    //Stopped
   TnimcAxisStatusProfileModeLast,
} TnimcProfileMode;

//nimcReadCoordianteData
typedef enum
{
   TnimcCoordinateDataVelocity = 0,                   //R    - doubleData  - in user units of position / second
   TnimcCoordinateDataFollowingError,                 //R    - doubleData  - in user units of position
   TnimcCoordinateDataLast,
} TnimcCoordinateData;

//nimcReadCoordinateStatus
//Notes: This enum changed in NI-Motion 7.3
typedef enum
{
   TnimcCoordinateStatusMoveComplete = 0,             //R    - boolData    - TnimcTrue (complete), TnimcFalse (not complete)
   TnimcCoordinateStatusProfileComplete,              //R    - boolData    - TnimcTrue (complete), TnimcFalse (not complete)
   TnimcCoordinateStatusBlendComplete,                //R    - boolData    - TnimcTrue (complete), TnimcFalse (not complete)
   TnimcCoordinateStatusProfileMode,                  //R    - longData    - TnimcProfileMode
   TnimcCoordinateStatusFollowingErrorExceeded,       //R    - boolData    - TnimcTrue (exceeded), TnimcFalse (not exceeded)
   TnimcCoordinateStatusLast,
} TnimcCoordinateStatus;

//nimcReadEncoderData, nimcWriteEncoderData
//Notes: This enum changed in NI-Motion 7.3
typedef enum
{
   TnimcEncoderDataFilterFrequency = 0,               //R/W  - doubleData  - in Hertz
   TnimcEncoderDataScale,                             //R/W  - doubleData  - in user units / encoder count
   TnimcEncoderDataIndexCriteriaPhaseAActive,         //R/W  - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcEncoderDataIndexCriteriaPhaseBActive,         //R/W  - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcEncoderDataPhaseAActiveState,                 //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcEncoderDataPhaseBActiveState,                 //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcEncoderDataIndexActiveState,                  //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcEncoderDataPosition,                          //R    - doubleData  - in user units of position
   TnimcEncoderDataVelocity,                          //R    - doubleData  - in user units of position / second
   TnimcEncoderDataIndexPosition,                     //R    - doubleData  - in user units of position
   TnimcEncoderDataIndexCaptureOccurred,              //R    - boolData    - TnimcTrue (occurred), TnimcFalse (not occurred)
   TnimcEncoderDataLast,
} TnimcEncoderData;

//nimcReadCaptureCompareData, nimcWriteCaptureCompareData
//Notes: This enum changed in NI-Motion 7.3
typedef enum
{
   TnimcCaptureCompareDataCompareAction = 0,          //R/W  - longData    - TnimcCompareAction
   TnimcCaptureCompareDataComparePositionMode,        //R/W  - longData    - TnimcComparePositionMode
   TnimcCaptureCompareDataComparePulseWidth,          //R/W  - doubleData  - in seconds
   TnimcCaptureCompareDataCompareActiveState,         //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcCaptureCompareDataCompareEnable,              //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcCaptureCompareDataCompareTotemPole,           //R/W  - boolData    - TnimcTrue (totem pole), TnimcFalse (open collector)
   TnimcCaptureCompareDataComparePosition,            //R/W  - doubleData  - in user units of position
   TnimcCaptureCompareDataComparePositionWindow,      //R/W  - doubleData  - in user units of position
   TnimcCaptureCompareDataCompareRepeatPeriod,        //R/W  - doubleData  - in user units of position
   TnimcCaptureCompareDataCaptureEnable,              //R/W  - boolData    - TnimcTrue (enabled), TnimcFalse (disabled)
   TnimcCaptureCompareDataCaptureCondition,           //R/W  - longData    - TnimcCaptureCondition
   TnimcCaptureCompareDataCapturedPosition,           //R    - doubleData  - in user units of position
   TnimcCaptureCompareDataCaptureOccurred,            //R    - boolData    - TnimcTrue (occurred), TnimcFalse (not occurred)
   TnimcCaptureCompareDataCompareOccurred,            //R    - boolData    - TnimcTrue (occurred), TnimcFalse (not occurred)
   TnimcCaptureCompareDataLast,
} TnimcCaptureCompareData;

//nimcReadCaptureCompareData, nimcWriteCaptureCompareData
typedef enum
{
   TnimcCompareActionNone = 0,                        //No action is taken when Compare Position = Current Position
   TnimcCompareActionSet,                             //Compare Output is Set to Active when Compare Position = Current Position
   TnimcCompareActionReset,                           //Compare Output is Reset to Inactive when Compare Position = Current Position
   TnimcCompareActionToggle,                          //Compare Output is Toggled to Active/Inactive when Compare Position = Current Position
   TnimcCompareActionPulse,                           //Compare Output is Pulsed Active for Pulse Time when Compare Position = Current Position
   TnimcCompareActionLast,
} TnimcCompareAction;

//nimcReadCaptureCompareData, nimcWriteCaptureCompareData
typedef enum
{
   TnimcComparePositionModeAbsolute = 0,              //The breakpoint position is interpreted with reference to the zero position (origin)
   TnimcComparePositionModeRelative,                  //The breakpoint position is interpreted with reference to the encoder position when the breakpoint is enabled
   TnimcComparePositionModePeriodic,                  //Breakpoint[n] = Breakpoint position + (n x Breakpoint period).  Auto Reenable.
   TnimcComparePositionModePeriodicModulus,           //Breakpoint[n] = Breakpoint position + (n x Breakpoint modulus).  Manual Reenable.
   TnimcComparePositionModeLast
} TnimcComparePositionMode;

//nimcReadCaptureCompareData, nimcWriteCaptureCompareData
typedef enum
{
   TnimcCaptureConditionActiveHigh = 0,             //Capture the Current Position when the Capture Input is High.  Level Sensitive.
   TnimcCaptureConditionActiveLow,                  //Capture the Current Position when the Capture Input is Low.  Level Sensitive.
   TnimcCaptureConditionFallingEdge,                //Capture the Current Position when a falling edge is detected on the Capture Input.  Edge Sensitive.
   TnimcCaptureConditionRisingEdge,                 //Capture the Current Position when a rising edge is detected on the Capture Input.  Edge Sensitive.
   TnimcCaptureConditionLast,
} TnimcCaptureCondition;

//nimcReadCaptureCompareData, nimcWriteCaptureCompareData
typedef enum
{
   TnimcDigitalIODataOutputActiveState = 0,           //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcDigitalIODataInputActiveState,                //R/W  - boolData    - TnimcTrue (active low / active open), TnimcFalse (active high / active closed)
   TnimcDigitalIODataOutputActive,                    //R/W  - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcDigitalIODataInputActive,                     //R    - boolData    - TnimcTrue (active), TnimcFalse (inactive)
   TnimcDigitalIODataConfigureAsInput,                //R/W  - boolData    - TnimcTrue (input), TnimcFalse (output)
   TnimcDigitalIODataLast,
} TnimcDigitalIOData;

//nimcConfigureMotionIOMap
typedef enum
{
   TnimcMotionIOMapDefaultInput = 0,                  //Maps as the default input line
   TnimcMotionIOMapDefaultOutput,                     //Maps as the default output line
   TnimcMotionIOMapShutdown,                          //Maps as the shutdown line
   TnimcMotionIOMapInhibitOut,                        //Maps as an inhibit-out line
   TnimcMotionIOMapAlarmClear,                        //Maps as an alarm clear line
   TnimcMotionIOMapInhibitIn,                         //Maps as an inhibit-in line
   TnimcMotionIOMapDriveReady,                        //Maps as a drive ready line
   TnimcMotionIOMapInPosition,                        //Maps as an in-position line
   TnimcMotionIOMapLast,
} TnimcMotionIOMap;

//nimcConfigureMotionIOMap
typedef enum
{
   TnimcMotionIOMapLineTypeDigitalIO = 0,             //Maps the Motion IO from a Digital IO line
   TnimcMotionIOMapLineTypeRTSI,                      //Maps the Motion IO from a RTSI line
   TnimcMotionIOMapLineTypeLast,
} TnimcMotionIOMapLineType;

//nimcReadTrajectoryData, nimcWriteTrajectoryData
//Notes: This enum changed in NI-Motion 7.3
typedef enum
{
   TnimcTrajectoryDataFollowingErrorLimit = 0,        //R/W  - doubleData  - in user units of position
   TnimcTrajectoryDataVelocityThreshold,              //R/W  - doubleData  - in user units of position / second
   TnimcTrajectoryDataReadVelocityFilterTime,         //R/W  - doubleData  - in seconds
   TnimcTrajectoryDataReadVelocityFilterPosition,     //R/W  - doubleData  - in user units of position
   TnimcTrajectoryDataMoveCompleteWhenDeactivated,    //R/W  - boolData    - TnimcTrue (OR when !TnimcAxisStatusAxisActive), TnimcFalse (AxisActive has no effect)
   TnimcTrajectoryDataMoveCompleteAfterDelay,         //R/W  - boolData    - TnimcTrue (AND after TnimcTrajectoryDataMoveCompleteTimeDelay), TnimcFalse (TimeDelay has no effect)
   TnimcTrajectoryDataMoveCompleteWhenNotMoving,      //R/W  - boolData    - TnimcTrue (AND when !TnimcAxisStatusMoving), TnimcFalse (Moving has no effect)
   TnimcTrajectoryDataMoveCompleteMinimumActiveTime,//R/W  - doubleData  - in seconds
   TnimcTrajectoryDataMoveCompleteTimeDelay,          //R/W  - doubleData  - in seconds
   TnimcTrajectoryDataMoveCompleteWhenInRange,        //R/W  - boolData    - TnimcTrue (AND within TnimcTrajectoryDataMoveCompleteRangeDistance), TnimcFalse (RangeDistance has no effect)
   TnimcTrajectoryDataMoveCompleteRangeDistance,      //R/W  - doubleData  - in user units of position
   TnimcTrajectoryDataMoveCompleteWhenInPositionActive,//R/W - boolData    - TnimcTrue (AND when TnimcMotionIODataInPositionActive), TnimcFalse (InPosition has no effect)
   TnimcTrajectoryDataTargetPosition,                 //R/W  - doubleData  - in user units of position
   TnimcTrajectoryDataPositionMode,                   //R/W  - longData    - TnimcAxisPositionMode
   TnimcTrajectoryDataMaxVelocity,                    //R/W  - doubleData  - in user units of position / second
   TnimcTrajectoryDataMaxAcceleration,                //R/W  - doubleData  - in user units of position / second^2
   TnimcTrajectoryDataMaxDeceleration,                //R/W  - doubleData  - in user units of position / second^2
   TnimcTrajectoryDataMaxAccelJerk,                   //R/W  - doubleData  - in user units of position / second^3
   TnimcTrajectoryDataMaxDecelJerk,                   //R/W  - doubleData  - in user units of position / second^3
   TnimcTrajectoryDataInitialVelocity,                //R/W  - doubleData  - in user units of position / second
   TnimcTrajectoryDataFinalVelocity,                  //R/W  - doubleData  - in user units of position / second
   TnimcTrajectoryDataVelocityOverridePercent,        //R/W  - doubleData  - as a percentage of max velocity [0, 100]
   TnimcTrajectoryDataBlendMode,                      //R/W  - longData    - TnimcAxisBlendMode
   TnimcTrajectoryDataBlendDelay,                     //R/W  - doubleData  - in seconds
   TnimcTrajectoryDataReferencePosition,              //R/W  - doubleData  - in user units of position
   TnimcTrajectoryDataLast,
} TnimcTrajectoryData;

//nimcReadCoordinateTrajectoryData, nimcWriteCoordinateTrajectoryData
//Notes: This enum is not currently used.
typedef enum
{
   TnimcCoordinateTrajectoryDataMoveType = 0,
   TnimcCoordinateTrajectoryDataPositionMode,
   TnimcCoordinateTrajectoryDataArcRadius,
   TnimcCoordinateTrajectoryDataArcStartAngle,
   TnimcCoordinateTrajectoryDataArcTravelAngle,
   TnimcCoordinateTrajectoryDataHelixLinearTravel,
   TnimcCoordinateTrajectoryDataArcRoll,
   TnimcCoordinateTrajectoryDataArcPitch,
   TnimcCoordinateTrajectoryDataArcYaw,
   TnimcCoordinateTrajectoryDataMaxVelocity,
   TnimcCoordinateTrajectoryDataMaxAcceleration,
   TnimcCoordinateTrajectoryDataMaxDeceleration,
   TnimcCoordinateTrajectoryDataMaxAccelJerk,
   TnimcCoordinateTrajectoryDataMaxDecelJerk,
   TnimcCoordinateTrajectoryDataInitialVelocity,
   TnimcCoordinateTrajectoryDataFinalVelocity,
   TnimcCoordinateTrajectoryDataVelOverridePercent,
   TnimcCoordinateTrajectoryDataBlendMode,            
   TnimcCoordinateTrajectoryDataBlendDelay,           
   TnimcCoordinateTrajectoryDataLast,
} TnimcCoordinateTrajectoryData;

//nimcAxisStart
typedef enum
{
   TnimcAxisStartModeStart = 0,                       //Starts the move with the configured parameters
   TnimcAxisStartModeBlend,                           //Blends the move with the configured parameters based on TnimcTrajectoryDataBlendMode
   TnimcAxisStartModeLast,
} TnimcAxisStartMode;

//nimcWriteTrajectoryData
typedef enum
{
   TnimcAxisPositionModeAbsolute = 0,                 //The target position is interpreted with reference to the zero position (origin)
   TnimcAxisPositionModeRelative,                     //Generally, the target position is interpreted with reference to the current position when the target is loaded
   TnimcAxisPositionModeVelocity,                     //The axis moves at the maximum velocity until otherwise commanded
   TnimcAxisPositionModeRelativeToReference,          //The target position is interpreted with reference to the last found index reference position or captured position
   TnimcAxisPositionModeLast,
} TnimcAxisPositionMode;

//nimcWriteTrajectoryData
typedef enum
{
   TnimcAxisBlendModeBeforeDecelerating,
   TnimcAxisBlendModeAtProfileComplete,
   TnimcAxisBlendModeAfterDelay,
   TnimcAxisBlendModeLast,
} TnimcAxisBlendMode;

//nimcAxisStraightLineMove
typedef enum
{
   TnimcAxisStraightLineMovePositionModeAbsolute = 0, //The target position is interpreted with reference to the zero position (origin)
   TnimcAxisStraightLineMovePositionModeRelative,     //Generally, the target position is interpreted with reference to the current position when the target is loaded
   TnimcAxisStraightLineMovePositionModeVelocity,     //The axis moves at the maximum velocity until otherwise commanded
   TnimcAxisStraightLineMovePositionModeLast,
} TnimcAxisStraightLineMovePositionMode;

//nimcAxisStraightLineMove
typedef enum
{
   TnimcAxisStraightLineMoveStartModeDoNotStart = 0,  //The axis loads the move data but does not start the motion
   TnimcAxisStraightLineMoveStartModeStart,           //The axis loads the move data and starts the motion
   TnimcAxisStraightLineMoveStartModeLast,
} TnimcAxisStraightLineMoveStartMode;

#ifdef __cplusplus
   }
#endif

#endif //___nimcenum_h___
