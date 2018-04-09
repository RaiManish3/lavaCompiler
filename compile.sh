asm="asm/"
INPUTFILENAME=`basename $1`
ASMCODE="${INPUTFILENAME%.*}"

python src/lava.py $1 &&
mkdir -p $asm &&
<<<<<<< HEAD
nasm -f elf32 -F dwarf -g "${asm}$ASMCODE.s" &&
gcc -m32 "${asm}$ASMCODE.o" -o "${asm}a.out" && #false &&
=======
nasm -f elf32 -F dwarf -l "${asm}/t.lst" -g "${asm}$ASMCODE.s" &&
gcc -m32 "${asm}$ASMCODE.o" -o "${asm}a.out" &&
>>>>>>> ed5f94420dc27caf04056505a9ac2d3746737155
${asm}a.out &&
rm "${asm}a.out" "${asm}$ASMCODE.o"
