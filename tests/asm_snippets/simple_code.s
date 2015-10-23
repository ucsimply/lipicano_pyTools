    .text
    .syntax unified
    .thumb

.equ COUNT, 5

/* load to SRAM at 0x10000000 */

simple_code:
    movs    r0, #COUNT
    movs    r1, #0
loop:
    adds    r1, r1, r0
    subs    r0, r0, #1
    bne     loop
    
    /* breakpoint - halt */
    bkpt    #0
