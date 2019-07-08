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
        log.debug("Wrote {}".format(data))
    
    def _rx(self, size=1):
        resp = self._sercom.read(size=size)
        log.debug("Read {}".format(data))
        return resp

    def i2c_write(self, i2c_addr, data_bytes):
        size = len(data_bytes)
        if size >= 256:
            raise Exception("Cannot i2c write more than 256 bytes")
        
        addr = _i2c_write_addr(i2c_addr)
        payload = I2C_START_CMD + bytes([addr, size]) + data_bytes + I2C_STOP_CMD
        self._tx(payload)

    def i2c_read(self, i2c_addr, byte_cnt=1):
        addr = _i2c_read_addr(i2c_addr)
        payload = I2C_START_CMD + bytes([addr, byte_cnt]) + I2C_STOP_CMD
        return self._rx(byte_cnt)
    
    def regs_write(self, reg_nums, data_bytes):
        payload = REG_WRITE_CMD + bytes(reg_nums) + data_bytes + FRAME_END
        self._tx(payload)
    
    def regs_read(self, reg_nums):
        cnt = len(reg_nums)
        payload = REG_READ_CMD + bytes([reg_nums]) + FRAME_END
        self._tx(payload)
        return self._rx(cnt)

    def reg_write(self, reg_num, data_byte):
        payload = REG_WRITE_CMD + bytes([reg_num]) + data_byte + FRAME_END
        self._tx(payload)
    
    def reg_read(self, reg_num):
        payload = REG_READ_CMD + bytes([reg_num]) + FRAME_END
        self._tx(payload)
        return self._rx(1)
    
    def gpio_write(self, data):
        #write b'O' then data (bytes) then b'P'
        pass #TODO

    def gpio_read(self):
        payload = GPIO_READ_CMD + FRAME_END
        self._tx(payload)
        return self._rx(1)
    
    def power_down(self):
        #write Z 0x5A 0xA5 P
        pass #TODO
    
    def print_registers():
        REG_CNT=11
        regs = [0x00 + i for i in range(REG_CNT)]
        data = self.regs_read(regs)

        for i, d in enumerate(data):
            print("0x{:02X}  0x{:02X}".format(i, d))


if __name__ == '__main__':
    log.basicConfig(level = log.DEBUG)
    sc18 = SC18IM700(port='/dev/ttyS0')
    GPIO_EXP1_ADDDR = 0x20
    GPIO_EXP2_ADDDR = 0x24
    
   
    sc18.i2c_write(GPIO_EXP2_ADDDR, bytes([0x06, 0x00])) #configure P7-P0 as outputs

    sc18.i2c_write(GPIO_EXP2_ADDDR, bytes([0x10, 0xF0])) 
    sc18.i2c_write(GPIO_EXP2_ADDDR, bytes([0x11, 0x0F])) 
    sc18.i2c_write(GPIO_EXP2_ADDDR, bytes([0x12, 0x00])) 
