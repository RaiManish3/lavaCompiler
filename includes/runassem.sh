filename=$1
asm="asm/"
make &&
bin/codegen "test/$filename.ir" 2>&1 >/dev/null &&
mkdir -p $asm &&
nasm -f elf32 "${asm}$filename.s" &&
gcc -m32 "${asm}$filename.o" -o "${asm}a.out" &&
${asm}a.out &&
rm "${asm}a.out" "${asm}$filename.o"
