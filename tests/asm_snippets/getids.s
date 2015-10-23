    .text
    .syntax unified
    .thumb
    .type   iap, %function
    .type   get_chip_ids, %function

.equ IAP_ENTRY,             0x1FFF1FF1
.equ IAP_READ_PART_ID,      54
.equ IAP_READ_BOOT_VER,     55
.equ IAP_READ_UID,          58
.equ STACK_TOP,             0x10000400
.equ RESULT_BASE,           0x10000100

/*
cmd:    .word   0
RESULT_BASE_addr:
res1:   .word   0, 0
res2:   .word   0, 0
res3:   .word   0, 0, 0, 0, 0

from RESULT_BASE address read 9 words

*/

/* load to SRAM at 0x10000000 */

get_chip_ids:
    ldr     r0, =STACK_TOP
    mov     sp, r0              /* set SP */
    ldr     r5, =RESULT_BASE    /* R5 holds pointer to results */
    subs    r4, r5, #4          /* R4 holds pointer to command */
    
    /* get part ID */
    movs    r0, #IAP_READ_PART_ID
    str     r0, [r4]
    bl      iap
    
    /* get Boot code version */
    movs    r0, #IAP_READ_BOOT_VER
    str     r0, [r4]
    adds    r5, r5, #8
    bl      iap
    
    /* get part UID - chip serial number */
    movs    r0, #IAP_READ_UID
    str     r0, [r4]
    adds    r5, r5, #8
    bl      iap
    
    /* breakpoint - halt */
    bkpt    #0
    
iap:
    mov     r0, r4          /* pointer to command to R0 */
    mov     r1, r5          /* pointer to result to R1 */
    ldr     r2, =IAP_ENTRY  /* branch to IAP */
    bx      r2
    
        
