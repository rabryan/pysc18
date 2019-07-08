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

def _i2c_write_addr(i2c_addr): return i2c_addr & 0xFE
def _i2c_read_addr(i2c_addr): return i2c_addr | 0x01

class SC18IM700:
    def __init__(self, port='/dev/ttyS0'):
        self._sercom = serial.Serial(port, timeout=0.5)
    
    def _tx(self, data):
        self._sercom.write(data)
    
    def _rx(self, size=1):
        return self._sercom.read(size=size)

    def i2c_write(self, i2c_addr, data_bytes):
        size = len(data_bytes)
        if size >= 256:
            raise Exception("Cannot i2c write more than 256 bytes")
        
        addr = _i2c_write_addr(i2c_addr)
        payload = I2C_START_CMD + bytes(addr, size) + data_bytes
        self._tx(payload)

    def i2c_read(self, i2c_addr, byte_cnt=1):
        addr = _i2c_read_addr(i2c_addr)
        payload = I2C_START_CMD + bytes([addr, byte_cnt])
        return self._rx(byte_cnt)
    
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

