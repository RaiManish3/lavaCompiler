#!/bin/bash

PARSER="src/myParser.py"
HTMLW="src/htmlWriter.py"
HTMLCODE="bin/htmlCode.html"
DEBUG_LOG="bin/debugLog.txt"
ERROR_LOG="bin/errorLog.txt"

python3 $PARSER $1 2> $DEBUG_LOG > $ERROR_LOG
cat $ERROR_LOG
python3 $HTMLW $DEBUG_LOG
xdg-open $HTMLCODE
