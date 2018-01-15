#!/bin/bash

#provide the following parameters

#[ number_of_expected_arguments actual_number_of_arguments (list_of_arguments program_description)]

EXPECTED_NUMBER_OF_ARGUMENTS=$1
ACTUAL_NUMBER_OF_ARGUMENTS=$2
ARGUMENT_LIST="No argument list is given"
PROGRAM_DESCRIPTION="No program description is given"

#check that number of arguments is a valid number
if [ "$EXPECTED_NUMBER_OF_ARGUMENTS" -le 0 ]; then
	echo "Program needs to provide the expected number of arguments, which should be bigger than 0"
	exit 1
fi

#if a list of arguments is given, replace the variable
if [ ! -z "$3" ]; then
	ARGUMENT_LIST=$3
fi

#if program description is given, replace the variable
if [ ! -z "$4" ]; then
        PROGRAM_DESCRIPTION=$4
fi

#Check if number of arguments match expectation.
#if not, print help information
if [ $ACTUAL_NUMBER_OF_ARGUMENTS -ne $EXPECTED_NUMBER_OF_ARGUMENTS ]
then
        echo $PROGRAM_DESCRIPTION
        echo "The program is expecting ${EXPECTED_NUMBER_OF_ARGUMENTS} argument(s):"
        echo -e "\t${ARGUMENT_LIST}"
        exit 1
fi
