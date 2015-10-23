'''
'''

import sys

def bin2hexw(in_fname):
    with open(in_fname,"rb") as f:
        wrk = True
        print("CODE = [")
        cnt = 1
        line = ""
        while wrk :
            block = f.read(4)
            if (len(block) > 0):
                word = 0
                for bt in reversed(block):
                    word <<= 8
                    word += ord(bt)
                line += " 0x%08X," % (word)
                cnt += 1
                if (cnt == 5):
                    print(line)
                    cnt = 1
                    line = ""
            else:
                wrk = False
                if (len(line) > 0):
                    print(line)
                print("]")
            
if __name__ == '__main__':
    if (len(sys.argv) > 1):
        bin2hexw(sys.argv[1])
    else:
        bin2hexw("binary.bin")