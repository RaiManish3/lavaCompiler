#!/bin/bash

PARSER="src/myParser.py"
HTMLW="src/htmlWriter.py"
HTMLCODE="bin/htmlCode.html"
DEBUG_LOG="bin/debugLog.txt"

python3 $PARSER $1 2> $DEBUG_LOG >&1 &&
python3 $HTMLW $DEBUG_LOG &&
xdg-open $HTMLCODE
