"""
serial communication interface with SC18IM700
"""
import serial
import logging as log

I2C_START_CMD=b'S'
I2C_STOP_CMD=b'P'
REG_WRITE_CMD=b'W'
REG_READ_CMD=b'R'
GPIO_WRITE_CMD=b'O'
GPIO_READ_CMD=b'I'
FRAME_END=b'P'

""" Registers"""
REG_BRG0=0x00
REG_BRG1=0x01
REG_PortConf1=0x02
REG_PortConf2=0x03

class SC18IM700:
    def __init__(self, port='/dev/ttyS0'):
        self._sercom = serial.Serial(port, timeout=0.5)

    def i2c_write(self, i2c_addr, data_bytes):
        pass #TODO

    def i2c_read(self, i2c_addr, byte_cnt=1):
        return b'' #TODO
    
    def reg_write(self, reg_num, data_byte):
        pass #TODO
    
    def reg_read(self, reg_num):
        return b'\xFF' #TODO
    
    def gpio_write(self, data):
        #write b'O' then data (bytes) then b'P'
        pass #TODO

    def gpio_read(self):
        #write b'IP' then read 1 byte
        return b'\x00' #TODO
    
    def power_down(self):
        #write Z 0x5A 0xA5 P
        pass #TODO



if __name__ == '__main__':
    sc18 = SC18IM700(port='/dev/ttyS0')

