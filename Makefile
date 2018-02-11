CC=python3
SRC=src
BIN=bin
TEST=test

ass2: $(SRC)/myCodeGen.py
	@mkdir -p $(BIN)
	@cp $(SRC)/myCodeGen.py $(BIN)/codegen
	@chmod +x $(BIN)/codegen

ass1: $(SRC)/assignment1.py $(SRC)/myLexer.py
	@mkdir -p $(BIN)
	@cp $(SRC)/assignment1.py $(BIN)/lexer
	@chmod +x $(BIN)/lexer

build:
	ass2

clean:
	@rm -rf bin/* src/{*.pyc,__pycache__,lextab.py} includes/{*.pyc,__pycache__}
