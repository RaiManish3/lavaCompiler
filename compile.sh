asm="asm/"
INPUTFILENAME=`basename $1`
ASMCODE="${INPUTFILENAME%.*}"

python src/lava.py $1 &&
mkdir -p $asm &&
nasm -f elf32 "${asm}$ASMCODE.s" &&
gcc -m32 "${asm}$ASMCODE.o" -o "${asm}a.out" &&
${asm}a.out &&
rm "${asm}a.out" "${asm}$ASMCODE.o"
