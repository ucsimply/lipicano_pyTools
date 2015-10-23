'''
'''

from pywinusb import hid

def show_hids():
    # devs = hid.HidDeviceFilter(vendor_id = 0xA600).get_devices()
    devs = hid.HidDeviceFilter().get_devices()
    for dev in devs:
        dev.open()
        print("VID: 0x%04X, PID: 0x%04X, Vendor: %s, Product: %s, SerNo: %s" % 
              (dev.vendor_id, dev.product_id, 
              dev.vendor_name, dev.product_name, dev.serial_number))
        dev.close()
    
if __name__ == '__main__':
    show_hids()

