arm-none-eabi-gcc -c -mthumb -mcpu=cortex-m0 -Wall -g -O0 -D__ASSEMBLY__ %1%.s 
arm-none-eabi-objdump -d %1%.o >dump.lst
arm-none-eabi-objdump -s -j .text %1%.o >objdump_hex.txt
arm-none-eabi-objcopy -O binary %1%.o binary.bin
python ../bin2hexw.py >code_hexw.txt


