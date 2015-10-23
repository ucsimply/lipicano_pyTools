'''
'''

from pyOCD.board.board import Board
from pyOCD.interface import INTERFACE, usb_backend
from pyOCD.target.cortex_m import CORE_TYPE_NAME
from pyOCD.target.target import TARGET_RUNNING, TARGET_HALTED

HID_VID = 0xA600
HID_PID = 0xE2C0

FREQ = 100000

ARMv6M = 0xC
ARMv7M = 0xF

ARCH_NAME = {
    ARMv6M : "ARMv6M",
    ARMv7M : "ARMv7M",
}

MAP_BOOL_Y_N = {
    True  : "Yes",
    False : "No",
}

REG_NAMES = [
  'r0', 'r1',  'r2',  'r3',  'r4', 'r5', 'r6', 'r7', 
  'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'xpsr',
]

TARGET_STATE = {
    TARGET_RUNNING : "Running",
    TARGET_HALTED  : "Halted",
}

PART_NAME = {
    0x00050080 : "LPC1115",
    0x00017C40 : "LPC11U37",
    0x1A020525 : "LPC1317",
    0x08020543 : "LPC1347",
    0x481D3F47 : "LPC4088",
}

GETIDS_CODE = [
    0x4685480B, 0x1F2C4D0B, 0x60202036, 0xF80BF000,
    0x60202037, 0xF0003508, 0x203AF806, 0x35086020,
    0xF801F000, 0x4620BE00, 0x4A034629, 0x00004710,
    0x10000400, 0x10000100, 0x1FFF1FF1,
]

SIMPLE_CODE = [
 0x21002005, 0x38011809, 0xBE00D1FC,
]

LOAD_ADDR   = 0x10000000
START_ADDR  = 0x10000001
RESULT_ADDR = 0x10000100
RESULT_SIZE = 9

def get_lipicano():
    lipicans = INTERFACE[usb_backend].getAllConnectedInterface(HID_VID, HID_PID)
    print("")
    for lip in lipicans:
        print("Lipicano found: %s, %s\n" % (lip.vendor_name, lip.product_name))
    return lipicans[0]
    
def print_target_info(target):
    print("Target info:")
    print("IDCODE  : 0x%08X" % (target.idcode))
    print("Arch    : %s" % (ARCH_NAME[target.arch]))
    print("Core    : %s" % (CORE_TYPE_NAME[target.core_type]))
    print("FPU     : %s" % (MAP_BOOL_Y_N[target.has_fpu]))
    print("Hw-BPt  : %s" % (len(target.breakpoints)))
    print("Hw-WPt  : %s" % (len(target.watchpoints)))
    print("State   : %s" % (TARGET_STATE[target.getState()]))
    
def print_target_ids(target):
    reg_list = []
    data_list = []
    target.halt()
    target.writeBlockMemoryAligned32(LOAD_ADDR, GETIDS_CODE)
    reg_list.append('pc')
    data_list.append(START_ADDR)
    target.writeCoreRegistersRaw(reg_list, data_list)
    target.resume()
    while(target.getState() == TARGET_RUNNING):
        pass
    result = target.readBlockMemoryAligned32(RESULT_ADDR, RESULT_SIZE)
    print("PartID  : 0x%08X" % (result[1]))
    print("BootVer : %d.%d" % ((result[3] >> 8) & 0xFF, result[3] & 0xFF))
    print("PartSN  : 0x%08X-%08X-%08X-%08X" % (result[8], result[7], result[6], result[5]))
    name = "Unknown"
    if (result[1] in PART_NAME):
        name = PART_NAME[result[1]];
    print("Name    : %s" % (name))
    
def print_regs(target):
    reg_vals = target.readCoreRegistersRaw(REG_NAMES)
    print("Regs:")
    line = ""
    cnt = 1
    for i, reg in enumerate(REG_NAMES):
        line += "%4s = 0x%08X  " % (reg, reg_vals[i])
        cnt += 1
        if (cnt == 5):
            print(line)
            line = ""
            cnt = 1
    if (len(line) > 0):
        print(line)
    return reg_vals

def step_simple_code(target):
    reg_list = []
    data_list = []
    target.halt()
    target.writeBlockMemoryAligned32(LOAD_ADDR, SIMPLE_CODE)
    reg_list.append('pc')
    data_list.append(START_ADDR)
    target.writeCoreRegistersRaw(reg_list, data_list)
    print("\nStep simple_code:")
    stepit = True
    while stepit :
        print("")
        reg_vals = print_regs(target)
        instr_code = target.read16(reg_vals[15])
        print("Next instr: %04X" % (instr_code))
        if (instr_code == 0xBE00):
            print("Breakpoint reached")
            stepit = False
        else:
            c = raw_input("Step? [y/n]")
            if c.upper() == 'N':
                print("User break")
                stepit = False
            else:
                target.step()

if __name__ == '__main__':
    lipicano = get_lipicano()
    board = Board(target = "cortex_m", flash = "cortex_m", interface = lipicano, transport = "cmsis_dap", frequency = FREQ)
    board.init()
    target = board.target
    print_target_info(target)
    print_target_ids(target)
    # print_regs(target)
    # step_simple_code(target)
    
    
    
    
    
