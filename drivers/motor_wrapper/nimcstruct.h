/*=============================================================================
                   National Instruments / NI-Motion                             
  ----------------------------------------------------------------------------  
      Copyright (c) National Instruments 2005.  All Rights Reserved.            
  ----------------------------------------------------------------------------  
                                                                                
   Title:       nimcstruct.h                                                       
   Purpose:     Include file for NI-Motion library support. (nimotion.lib)    
                                                                                
=============================================================================*/

#ifndef ___nimcstruct_h___
#define ___nimcstruct_h___

#ifdef __cplusplus
	extern "C" {
#endif

#include "nimcenum.h"

//Notes: Structure order changed in NI-Motion 8.0
#pragma pack(push, 1)
typedef struct
{
   i32 longData;
#ifndef ___nimcstruct_noDoubleData___
   f64 doubleData;
#endif
   u8 boolData;
} TnimcData;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct
{
   u32 size;
   f64 position;
   f64 velocity;
   f64 followingError;
   f64 encoderPosition;
} TnimcAllAxisData;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct
{
   u32 size;
   u8 axisActive;
   u8 moveComplete;
   u8 profileComplete;
   u8 blendComplete;
   u8 followingErrorExceeded;
   u8 velocityThresholdExceeded;
   u8 moving;
   u8 directionForward;
   u8 indexCaptureOccurred;
   u8 positionCaptureOccurred;
   u8 positionCompareOccurred;
   u8 forwardLimitActive;
   u8 reverseLimitActive;
   u8 forwardSoftwareLimitActive;
   u8 reverseSoftwareLimitActive;
   u8 homeInputActive;
   u8 reserved;                                       //In the future this could be inhibitInActive
   u8 homeFound;
   u8 indexFound;
   u8 referenceFound;
} TnimcAllAxisStatus;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct
{
   u32 size;
   f64 velocity;
   f64 acceleration;
   f64 deceleration;
   f64 accelerationJerk;
   f64 decelerationJerk;
} TnimcMoveConstraints;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct
{
   u32 size;
   TnimcAxisStraightLineMoveStartMode startMode;
   TnimcAxisStraightLineMovePositionMode positionMode;
   f64 targetPosition;
} TnimcAxisStraightLineMoveData;
#pragma pack(pop)

#ifdef __cplusplus
   }
#endif

#endif //___nimcstruct_h___
