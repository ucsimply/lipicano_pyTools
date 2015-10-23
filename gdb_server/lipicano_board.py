'''
'''

from pyOCD.board.board import Board
from pyOCD.interface import INTERFACE, usb_backend
from pyOCD.transport import TRANSPORT
from pyOCD.target.cortex_m import CORE_TYPE_NAME
from pyOCD.target.target import TARGET_RUNNING, TARGET_HALTED

from target.target_lpc1115 import LPC1115
from target.target_lpc11u37 import LPC11U37

from flash.flash_lpc1115 import Flash_LPC1115
from flash.flash_lpc11u37 import Flash_LPC11U37

LIPICANO_VID = 0xA600
LIPICANO_PID = 0xE2C0

QRY_TRANSPORT = "cmsis_dap"
QRY_TARGET    = "cortex_m"
QRY_FLASH     = "cortex_m"
QRY_FREQ      = 1000000

class ModuleInfo(object):
    def __init__(self, name, target, flash):
        self.name   = name
        self.target = target
        self.flash  = flash

# Key is the MCU part ID
# this is valid only for NXP LPC microcontrollers
MODULES = {
    0x00050080 : ModuleInfo("LPC1115",  LPC1115,   Flash_LPC1115),
    0x00017C40 : ModuleInfo("LPC11U37", LPC11U37,  Flash_LPC11U37),
#    0x1A020525 : ModuleInfo("LPC1317",  LPC1317,   Flash_LPC1317),
#    0x08020543 : ModuleInfo("LPC1347",  LPC1347,   Flash_LPC1347),
#    0x481D3F47 : ModuleInfo("LPC4088",  LPC4088,   Flash_LPC4088),
}

# calls IAP commands
GETIDS_CODE = [
    0x4685480B, 0x1F2C4D0B, 0x60202036, 0xF80BF000,
    0x60202037, 0xF0003508, 0x203AF806, 0x35086020,
    0xF801F000, 0x4620BE00, 0x4A034629, 0x00004710,
    0x10000400, 0x10000100, 0x1FFF1FF1,
]

LOAD_ADDR   = 0x10000000
START_ADDR  = 0x10000001
RESULT_ADDR = 0x10000100
RESULT_SIZE = 9

ARMv6M = 0xC
ARMv7M = 0xF

ARCH_NAME = {
    ARMv6M : "ARMv6M",
    ARMv7M : "ARMv7M",
}

TARGET_STATE = {
    TARGET_RUNNING : "Running",
    TARGET_HALTED  : "Halted",
}

MAP_BOOL_Y_N = {
    True  : "Yes",
    False : "No",
}

def print_target_info(target):
    print("\nLipicano target info:")
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
    return result[1]

def get_lipicano_board():
    lipicans = INTERFACE[usb_backend].getAllConnectedInterface(LIPICANO_VID, LIPICANO_PID)
    if ((lipicans == None) or (len(lipicans) == 0)) :
        print("No Lipicano found, sorry ...")
        return None
    lipicano = lipicans[0]
    print("\nLipicano found: %s, %s, VID/PID: %04X/%04X\n" % (
                    lipicano.vendor_name, 
                    lipicano.product_name,
                    LIPICANO_VID,
                    LIPICANO_PID))
    board = Board(target = QRY_TARGET, 
                  flash = QRY_FLASH, 
                  interface = lipicano, 
                  transport = QRY_TRANSPORT, 
                  frequency = QRY_FREQ)
    board.init()
    target = board.target
    print_target_info(target)
    part_id = print_target_ids(target)
    if (part_id not in MODULES):
        print("Unsupported module found, sorry ...")
        return None
    module = MODULES[part_id]
    print("\nLipicano module found: %s\n" % (module.name))
    return LipicanoBoard(lipicano, module)

class LipicanoBoard(Board):
    def __init__(self, interface, module):
        self.interface = interface
        self.transport = TRANSPORT[QRY_TRANSPORT](self.interface)
        self.target = module.target(self.transport)
        self.flash = module.flash(self.target)
        self.target.setFlash(self.flash)
        self.debug_clock_frequency = QRY_FREQ
        self.module_name = module.name
        self.closed = False
        return

if __name__ == '__main__':
    board = get_lipicano_board()
    if (board != None):
        board.init()
        target = board.target
        print_target_info(target)
    else:
        print("Lipicano or supported module not found.")
        
