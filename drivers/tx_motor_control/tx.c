#include "flexmotn.h"
#include "NIMCExample.h"
#include <stdio.h>

//////////////////////////////////////////////////////////////////////
// Main Function
void main(void){

	u8	boardID = 3;					// Board Identification number
	u8	axis = 1;						// Axis Number
	f64 acceleration =4000;	// Acceleration value
	f64 deceleration =4000;	// Deceleration value
	f64 velocity=500;			// Velocity value
	i32 targetPosition;		// Target Position in counts or steps
	u16 axisStatus;			// Axis Status 
	u16 csr	= 0;				// Communication Status Register
	i32 position;				// Current position of axis
	i32 scanVar;				// Scan variable to read in values not supported bu
									//		by the scanf function

	//Variables for modal error handling
	u16 commandID;				// The commandID of the function
	u16 resourceID;			// The resource ID
	i32 errorCode;				// Error code

	//Check if the board is at power up reset condition
	err = flex_read_csr_rtn(boardID, &csr);
	CheckError;

   if (csr & NIMC_POWER_UP_RESET ){
		printf("\nThe FlexMotion board is in the reset condition. Please initialize the board before ");
		printf("running this example.  The \"flex_initialize_controller\" function will initialze the ");
		printf("board with settings selected through Measurement and Automation Explorer\n");
		return;
	}
	
	//Get the Targer Position 
	printf("Enter the target position: ");
	scanf("%d", &targetPosition);

	//Flush the Stdin
	fflush(stdin);
	
	//Load acceleration to the axis selected
	err = flex_load_acceleration(boardID, axis, NIMC_ACCELERATION, acceleration, 0xFF);
	CheckError;

	//Load deceleration to the axis selected
	err = flex_load_acceleration(boardID, axis, NIMC_DECELERATION, deceleration, 0xFF);
	CheckError;

	//Load velocity to the axis selected
	err = flex_load_velocity(boardID, axis, velocity, 0xFF);
	CheckError;

	//Load the operation mode - absolute position
	err = flex_set_op_mode(boardID, axis, NIMC_ABSOLUTE_POSITION);
	CheckError;

	//Load a target position of 20000 counts or steps
	err = flex_load_target_pos(boardID, axis, targetPosition, 0xFF); 
	CheckError;

	//Start Motion on the axis selected
	err = flex_start(boardID, axis, 0);
	CheckError;

	//Wait for move to complete on the axis AND
	//also check for modal errors at the same time.
	do{
		//Read the current position of axis
		err = flex_read_pos_rtn(boardID, axis, &position);
		CheckError;

		err = flex_read_axis_status_rtn(boardID, axis, &axisStatus);
		CheckError;

		//Read the Communication Status Register - check the 
		//modal error bit
		err = flex_read_csr_rtn(boardID, &csr);
		CheckError;

		if (csr & NIMC_MODAL_ERROR_MSG)
		{
			flex_stop_motion(boardID,NIMC_VECTOR_SPACE1, NIMC_DECEL_STOP, 0);//Stop the Motion
			err = csr & NIMC_MODAL_ERROR_MSG;
			CheckError;
		}

	}while ( ! (axisStatus & (NIMC_MOVE_COMPLETE_BIT | NIMC_AXIS_OFF_BIT ))); //Test against the move complete bit
	printf("\rAxis %d position: %10d", axis, position);						  //	or the axis off bit
	printf("\n\nFinished.\n");

	return;		// Exit the Application

	
	/////////////////////////////////////////////////////////////////////////
	// Error Handling
	//
	nimcHandleError;
	
	// Check to see if there were any Modal Errors
	if (csr & NIMC_MODAL_ERROR_MSG){
		do{
			//Get the command ID, resource and the error code of the modal
			//	error from the error stack on the board
			flex_read_error_msg_rtn(boardID,&commandID,&resourceID,&errorCode);
			nimcDisplayError(errorCode,commandID,resourceID);
			
			//Read the Communication Status Register
			flex_read_csr_rtn(boardID,&csr);
	
		}while(csr & NIMC_MODAL_ERROR_MSG);
	}
	else		// Display regular error 
	{
		nimcDisplayError(err,0,0);
	}
	return;		// Exit the Application
}


