#!/bin/bash

function usage() {
	echo "$0 <commandlineinputfile>"
}

inputfile="$1"

if [ "$inputfile" == "" ]
then
	usage
	exit 1
fi

if ! [ -f "$inputfile" ]
then
	echo "file not found: $inputfile"
	usage
	exit 1
fi

cat "$inputfile" | while read line
do
	if [ "$line" == "" ]
	then
		echo ""
		continue
	fi

	cmd=( $line )

	# print input command
	if [ "${line::1}" != "#" ]
	then
		echo "$ $line"
	else
		echo "$line"
	fi
	# execute and print results
	bash -c "$line"
done

