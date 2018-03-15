#!/bin/bash

PARSER="src/myParser.py"
HTMLW="src/htmlWriter.py"
DEBUG_LOG="bin/debugLog.txt"
INPUTFILENAME=`basename $1`
HTMLCODE="${INPUTFILENAME%.*}.html"

python3 $PARSER $1 2> $DEBUG_LOG >&1 &&
python3 $HTMLW $DEBUG_LOG $HTMLCODE &&
xdg-open "bin/$HTMLCODE"
