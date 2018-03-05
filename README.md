## A CS335 Course Project
The program aims to build a compiler for a modified langauge that has the basics of Lua language ( tables have been removed ) and OOP flavours and type sytem of Java.

### Prerequisites
[ This ](requirements.txt) lists out all the tools / libraries that are required to run the program.

### Running the Tests
While in the main directory, execute the following commands:<br>

1. For the lexer:
  ``` bash 
        $: make 
        $: bin/lexer test/test[1-5].lua
  ```

2. For the codegen:
  ``` bash
        # FOR LISTING THE ASSEMBLY CODE
        $: make
        $: bin/codegen test/[filename].ir

        # EXECUTING THE ASSEMBLY CODE
        $: bash includes/runassem.sh [filename]  #filename should be without extension or directory
  ```

3. For the parser:
  ```bash
        $: make
        $: bin/parser test/[filename].lua
  ```

### Timeline

1. <b>Task One</b>, <i> 28 Jan 2018 </i><br>
  Build a lexer for the Token.

2. <b>Task Two</b>, <i> 12 Feb 2018 </i><br>
  Build a Code Generator.

3. <b>Task Three</b>, <i> 12 March 2018 </i><br>
  Build a LALR Parser with Rightmost Derivation displayed as an HTML file.

### Authors
* Dhruv Kumar
* Sonam Tenzin
* Manish Kumar
