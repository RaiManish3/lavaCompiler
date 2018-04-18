asm="asm/"
INPUTFILENAME=`basename $1`
ASMCODE="${INPUTFILENAME%.*}"

python3 src/lava.py $@ && false &&
mkdir -p $asm &&
nasm -f elf32 -F dwarf -l "${asm}/t.lst" -g "${asm}$ASMCODE.s" &&
gcc -m32 "${asm}$ASMCODE.o" -o "${asm}a.out" &&
${asm}a.out &&
rm "${asm}a.out" "${asm}$ASMCODE.o"
