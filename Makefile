CC=python3
SRC=src
INC=includes
BIN=bin
TEST=test

.DEFAULT_GOAL := ass4

ass4: $(SRC)/myParser.py $(SRC)/myLexer.py $(INC)/SymTab.py
	@mkdir -p $(BIN)
	@cp $(SRC)/myParser.py $(BIN)/parser
	@chmod +x $(BIN)/parser

ass3: $(SRC)/myParser.py $(SRC)/myLexer.py $(SRC)/htmlWriter.py $(SRC)/parserHtmlScipt.sh
	@mkdir -p $(BIN)
	@cp $(SRC)/parserHtmlScipt.sh $(BIN)/parser
	@chmod +x $(BIN)/parser

ass2: $(SRC)/myCodeGen.py
	@mkdir -p $(BIN)
	@cp $(SRC)/myCodeGen.py $(BIN)/codegen
	@chmod +x $(BIN)/codegen

ass1: $(SRC)/assignment1.py $(SRC)/myLexer.py
	@mkdir -p $(BIN)
	@cp $(SRC)/assignment1.py $(BIN)/lexer
	@chmod +x $(BIN)/lexer

clean:
	@rm -rf bin/* src/{*.pyc,__pycache__,lextab.py,parsetab.py,parser.out} includes/{*.pyc,__pycache__}
