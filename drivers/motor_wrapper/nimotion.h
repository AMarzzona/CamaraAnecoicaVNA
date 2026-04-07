/*=============================================================================
                   National Instruments / NI-Motion                             
  ----------------------------------------------------------------------------  
      Copyright (c) National Instruments 2005.  All Rights Reserved.            
  ----------------------------------------------------------------------------  
                                                                                
   Title:       nimotion.h                                                       
   Purpose:     Include file for NI-Motion library support. (nimotion.lib)    
                                                                                
=============================================================================*/

#ifndef ___nimotion_h___
#define ___nimotion_h___

#ifdef __cplusplus
	extern "C" {
#endif
/*-----------------------------------------------------------------------------
   Error Defines
-----------------------------------------------------------------------------*/
#include <MotnErr.h>       //Error Codes
#include <stdbool.h>

/*-----------------------------------------------------------------------------
   File Management Defines
-----------------------------------------------------------------------------*/
#ifdef kNIMCCExportSymbols
   #ifdef __GNUC__
      #define __nimcExport __attribute__((section(".export"))) i32
      #define __nimcExportVoid __attribute__((section(".export"))) void
   #else
      #define __nimcExport i32 __declspec(dllexport) __stdcall 
      #define __nimcExportVoid void __declspec(dllexport) __stdcall 
   #endif
#else
   #ifdef __GNUC__
      #define __nimcExport i32
      #define __nimcExportVoid void
   #else
      #define __nimcExport i32 __stdcall 
      #define __nimcExportVoid void __stdcall 
   #endif
#endif
#ifdef __nimcFunctions__
   #define __nimcSelectiveDefines__
#endif
#ifdef __nimcStructs__
   #define __nimcSelectiveDefines__
#endif
#ifdef __nimcMotionTypes__
   #define __nimcSelectiveDefines__
#endif
#ifdef __nimcBaseTypes__
   #define __nimcSelectiveDefines__
#endif
#ifndef __nimcSelectiveDefines__
   #define __nimcFunctions__
#endif
#ifdef __nimcFunctions__
   #define __nimcStructs__
#endif
#ifdef __nimcStructs__
   #define __nimcMotionTypes__
#endif
#ifdef __nimcMotionTypes__
   #ifndef __NIMCBasicTypes_h__ //required for backward compatibility with nimcBasicTypes.h
      #define __nimcBaseTypes__
   #endif
#endif 

/*-----------------------------------------------------------------------------
   Basic Type Defines
-----------------------------------------------------------------------------*/
#ifdef __nimcBaseTypes__

typedef long i32;
typedef double f64;
typedef float f32;
typedef short i16;
typedef char i8;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned long u32;

#endif // __nimcBaseTypes__

/*-----------------------------------------------------------------------------
   Motion Specific Type Defines
-----------------------------------------------------------------------------*/
#ifdef __nimcMotionTypes__

#define TnimcFalse 0
#define TnimcTrue 1

typedef i32 TnimcInterfaceHandle;
typedef i32 TnimcDeviceHandle;
typedef i32 TnimcAxisHandle;
typedef i32 TnimcCoordinateHandle;
typedef char* TnimcString;
typedef u32 TnimcNode;
typedef u32 TnimcGetProperty;
typedef u32 TnimcSetProperty;
typedef u32 TnimcReadData;
typedef u32 TnimcWriteData;
typedef u32 TnimcReadStatus;

#include <nimcenum.h>      //NI-Motion Attribute Enumerations

#endif // __nimcMotionTypes__

/*-----------------------------------------------------------------------------
   Motion Specific Structures
-----------------------------------------------------------------------------*/
#ifdef __nimcStructs__

#include <nimcstruct.h>   //NI-Motion Structures

#endif // __nimcStructs__

/*-----------------------------------------------------------------------------
   Functions
-----------------------------------------------------------------------------*/
#ifdef __nimcFunctions__
// <BEGINFUNCTIONS>

// Write Functions
__nimcExport nimcWriteMotionIOData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcMotionIOData attribute, TnimcData* data);
__nimcExport nimcWriteDigitalIOData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, u32 line, TnimcDigitalIOData attribute, TnimcData* data);
__nimcExport nimcWriteTrajectoryData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcTrajectoryData attribute, TnimcData* data);
__nimcExport nimcWriteCaptureCompareData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, i32 index, TnimcCaptureCompareData attribute, TnimcData* data);

// Read Functions
__nimcExport nimcReadMotionIOData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcMotionIOData attribute, TnimcData* data);
__nimcExport nimcReadAxisData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcAxisData attribute, TnimcData* data);
__nimcExport nimcReadAxisStatus(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcAxisStatus attribute, TnimcData* data);
__nimcExport nimcReadCoordinateData(TnimcDeviceHandle deviceHandle, TnimcCoordinateHandle coordinateHandle, TnimcCoordinateData attribute, TnimcData* data);
__nimcExport nimcReadCoordinateStatus(TnimcDeviceHandle deviceHandle, TnimcCoordinateHandle coordinateHandle, TnimcCoordinateStatus attribute, TnimcData* data);
__nimcExport nimcReadCoordinatePosition(TnimcDeviceHandle deviceHandle, TnimcCoordinateHandle coordinateHandle, f64* position, u32 lengthPosition, u32 *fetched);
__nimcExport nimcReadEncoderData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, i32 index, TnimcEncoderData attribute, TnimcData* data);
__nimcExport nimcReadCaptureCompareData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, i32 index, TnimcCaptureCompareData attribute, TnimcData* data);
__nimcExport nimcReadAllAxisData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcAllAxisData* data);
__nimcExport nimcReadAllAxisStatus(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcAllAxisStatus* data);
__nimcExport nimcReadDigitalIOData(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, u32 line, TnimcDigitalIOData attribute, TnimcData* data);

// Methods
__nimcExport nimcResetController(TnimcDeviceHandle deviceHandle);
__nimcExport nimcSelfTest(TnimcDeviceHandle deviceHandle);
__nimcExport nimcClearFaults(TnimcDeviceHandle deviceHandle);
__nimcExport nimcConfigureMotionIOMap(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcMotionIOMap attribute, i32 ioAxis, TnimcMotionIOMapLineType lineType, u32 line);
__nimcExport nimcAxisStraightLineMove(TnimcDeviceHandle deviceHandle, TnimcAxisHandle axisHandle, TnimcAxisStraightLineMoveData* data, TnimcMoveConstraints* moveConstraints);
__nimcExport nimcDumdum(void);

// Create, Destroy, Open & Close Interface Functions
__nimcExport nimcCreateControlInterface(TnimcInterfaceHandle* handle, TnimcNode node);
__nimcExport nimcDestroyControlInterface(TnimcInterfaceHandle handle);
__nimcExport nimcOpenResourceInterface(TnimcInterfaceHandle* handle, TnimcString resource);
__nimcExport nimcCloseResourceInterface(TnimcInterfaceHandle handle);

// Interface Read, Write, Set & Get Functions
__nimcExport nimcSetResource(TnimcInterfaceHandle handle, TnimcString resource);
__nimcExport nimcSetProperty(TnimcInterfaceHandle handle, TnimcSetProperty property, TnimcData* data);
__nimcExport nimcSetPropertyF64Array(TnimcInterfaceHandle handle, TnimcSetProperty property, f64* dataArray, u32 sizeOfDataArray);
__nimcExport nimcGetProperty(TnimcInterfaceHandle handle, TnimcGetProperty property, TnimcData* data);
__nimcExport nimcGetPropertyF64Array(TnimcInterfaceHandle handle, TnimcGetProperty property, f64* dataArray, u32 sizeOfDataArray, u32* fetched);
__nimcExport nimcWriteData(TnimcInterfaceHandle handle, TnimcWriteData property, TnimcData* data);
__nimcExport nimcWriteDataF64Array(TnimcInterfaceHandle handle, TnimcWriteData property, f64* dataArray, u32 sizeOfDataArray);
__nimcExport nimcReadData(TnimcInterfaceHandle handle, TnimcReadData property, TnimcData* data);
__nimcExport nimcReadDataF64Array(TnimcInterfaceHandle handle, TnimcReadData property, f64* dataArray, u32 sizeOfDataArray, u32* fetched);
__nimcExport nimcReadDataI32Array(TnimcInterfaceHandle handle, TnimcReadData property, i32* dataArray, u32 sizeOfDataArray, u32* fetched);
__nimcExport nimcReadStatus(TnimcInterfaceHandle handle, TnimcReadStatus property, TnimcData* data);
__nimcExport nimcGetLastError(TnimcInterfaceHandle handle, i32* errorCode, TnimcString description, u32 sizeOfDescriptionString, TnimcString location, u32 sizeOfLocationString);

// Interface Methods
__nimcExport nimcExecute(TnimcInterfaceHandle handle);
__nimcExport nimcStop(TnimcInterfaceHandle handle);
__nimcExport nimcCommit(TnimcInterfaceHandle handle);
__nimcExport nimcRefresh(TnimcInterfaceHandle handle);

// Specific Interface Methods
__nimcExport nimcControllerInitialize(TnimcInterfaceHandle handle);
__nimcExport nimcAxisClearFaults(TnimcInterfaceHandle handle);
__nimcExport nimcAxisPower(TnimcInterfaceHandle handle, bool powerEnableAxis, bool powerEnableDrive);
__nimcExport nimcAxisResetPosition(TnimcInterfaceHandle handle, f64 position);

// Non-Interface Methods
__nimcExport nimcGetErrorDescription(i32 errorCode, TnimcString description, u32 sizeOfDescriptionString);

#endif // __nimcFunctions__

#ifdef __cplusplus
   }
#endif
 
#endif // __nimotion_h__

