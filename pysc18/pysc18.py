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

def _i2c_write_addr(i2c_addr): return (i2c_addr << 1) & 0xFE
def _i2c_read_addr(i2c_addr): return (i2c_addr << 1) | 0x01

class SC18IM700:
    def __init__(self, port='/dev/ttyS0'):
        self._sercom = serial.Serial(port, timeout=0.5)

    def _tx(self, data):
        self._sercom.write(data)
        log.debug("Wrote {}".format(data))

    def _rx(self, size=1):
        resp = self._sercom.read(size=size)
        log.debug("Read {}".format(resp))
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
        self._tx(payload)
        return self._rx(byte_cnt)

    def i2c_read_write(self, i2c_addr, write_bytes, read_byte_cnt=1):
        addr_w = _i2c_read_addr(i2c_addr)
        addr_r = _i2c_read_addr(i2c_addr)
        payload = I2C_START_CMD + bytes([addr_w]) + write_bytes + bytes([addr_r, read_byte_cnt]) + I2C_STOP_CMD
        self._tx(payload)
        return self._rx(read_byte_cnt)

    def regs_write(self, reg_nums, data_bytes):
        payload = REG_WRITE_CMD + bytes(reg_nums) + data_bytes + FRAME_END
        self._tx(payload)

    def regs_read(self, reg_nums):
        cnt = len(reg_nums)
        payload = REG_READ_CMD + bytes(reg_nums) + FRAME_END
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

    def print_registers(self):
        REG_CNT=11
        regs = [0x00 + i for i in range(REG_CNT)]
        data = self.regs_read(regs)

        for i, d in enumerate(data):
            print("0x{:02X}  0x{:02X}".format(i, d))

class SC18_I2C:
    """ provides a simple read/write interface for a i2c address proxied
        via the SC18IM700 module
    """
    def __init__(self, sc18, i2c_addr):
        self.sc18 = sc18
        self.i2c_addr = i2c_addr

    def write(self, data):
        self.sc18.i2c_write(self.i2c_addr, data)

    def read(self, byte_cnt):
        self.sc18.i2c_read(self.i2c_addr, byte_cnt)

if __name__ == '__main__':
    log.basicConfig(level = log.INFO)
    sc18 = SC18IM700(port='/dev/ttyS0')
    GPIO_EXP1_ADDR = 0x20 #7-bit
    GPIO_EXP2_ADDR = 0x24 #7-bit
    INA260_ADDR = 0x40 #7-bit


    def set_master_intensity(val):
        if val > 15:
            val = 15
        val = int(val)
        val = val << 4
        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x0E, val]))
        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x0E, val]))

    def setup_gpio_exps():
        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x0F, 0x00])) #disable global intensity to enable PWM
        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x0F, 0x00])) #disable global intensity to enable PWM

        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x06, 0x00])) #configure P7-P0 as outputs
        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x07, 0x00])) #configure P15-P8 as outputs
        #sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x0E, 0x00])) #master intensity to 0x0 for static output
        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x02, 0xFF])) #phase 0 output for P7-P0
        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x03, 0xFF])) #phase 0 output for P15-P8
        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x0A, 0x00])) #phase  1 output for P7-P0
        sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x0B, 0x00])) #phase 1 output for P15-P8

        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x06, 0x00])) #configure P7-P0 as outputs
        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x07, 0x00])) #configure P15-P8 as outputs
        #sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x0E, 0x00])) #master intensity to 0x0 for static output
        #sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x02, 0x00])) #static output for P7-P0
        #sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x03, 0x00])) #static output for P15-P8
        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x02, 0xFF])) #phase 0 output for P7-P0
        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x03, 0xFF])) #phase 0 output for P15-P8
        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x0A, 0x00])) #phase  1 output for P7-P0
        sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x0B, 0x00])) #phase 1 output for P15-P8


        output = 0x11
        for reg in range(0x10, 0x18):
            reg = int(reg)
            sc18.i2c_write(GPIO_EXP1_ADDR, bytes([reg, output])) #static output for P7-P0
            sc18.i2c_write(GPIO_EXP2_ADDR, bytes([reg, output])) #static output for P15-P8

        set_master_intensity(0)
    import time
    import random
    def run_led_test_loop():
        setup_gpio_exps()

        set_master_intensity(0)
        time.sleep(1)

        set_master_intensity(5)
        time.sleep(0.5)
        set_master_intensity(10)
        time.sleep(0.5)
        set_master_intensity(5)


        try:
            time.sleep(2)

            output = 0x22
            while True:
                for reg in range(0x10, 0x18):
                    reg = int(reg)
                    sc18.i2c_write(GPIO_EXP1_ADDR, bytes([reg, output])) #static output for P7-P0
                    sc18.i2c_write(GPIO_EXP2_ADDR, bytes([reg, output])) #static output for P15-P8
                if False:
                    sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x02, output])) #static output for P7-P0
                    sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x03, output])) #static output for P15-P8
                    sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x02, output])) #static output for P7-P0
                    sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x03, output])) #static output for P15-P8
                time.sleep(0.2)
                output+=1

                if output > 255:
                    output = 0
        except KeyboardInterrupt:
                sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x02, 0xff])) #static output for P7-P0
                sc18.i2c_write(GPIO_EXP1_ADDR, bytes([0x03, 0xff])) #static output for P15-P8
                sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x02, 0xff])) #static output for P7-P0
                sc18.i2c_write(GPIO_EXP2_ADDR, bytes([0x03, 0xff])) #static output for P15-P8
                set_master_intensity(0)



    b1 = sc18.i2c_read(INA260_ADDR, 1)
    print(b1)

    import struct

    def ina_set_reg_addr(addr):
        sc18.i2c_write(INA260_ADDR, bytes([addr]))

    def ina_read_reg(reg_addr):
        ina_set_reg_addr(reg_addr)
        #return sc18.i2c_read_write(INA260_ADDR, bytes([reg_addr]), 2)
        return sc18.i2c_read(INA260_ADDR, 2)

    def ina_write_reg(reg_addr, value):
        data = struct.pack(">h", value)
        #ina_set_reg_addr(reg_addr)
        #return sc18.i2c_read_write(INA260_ADDR, bytes([reg_addr]), 2)
        sc18.i2c_write(INA260_ADDR, bytes([reg_addr]) + data)


    INA260_CONFIG_REG_ADDR = 0x00
    INA260_CURRENT_REG_ADDR = 0x01
    INA260_VBUS_REG_ADDR = 0x02

    DEFAULT_CONFIG=0b0110011100111111

    mfg_id = ina_read_reg(0xFE)
    print("INA MFG ID = {}".format(mfg_id))
    die_id = ina_read_reg(0xFF)
    print("INA DIE ID = {}".format(die_id))

    ina_write_reg(INA260_CURRENT_REG_ADDR, DEFAULT_CONFIG)

    def read_current():
        resp = ina_read_reg(INA260_CURRENT_REG_ADDR)
        log.debug(resp)
        curr_val = struct.unpack(">h", resp)[0]
        log.debug(curr_val)
        curr_mA = 1.25*curr_val
        return curr_mA

    def read_vbus():
        resp = ina_read_reg(INA260_VBUS_REG_ADDR)
        log.debug(resp)
        val = struct.unpack(">h", resp)[0]
        voltage_mV = 1.25*val
        return voltage_mV

    print("Current = ?????? mA  VBUS= ??????", end='')

    while True:
        curr = read_current()
        vbus = read_vbus()
        print("\rCurrent  = {:>6} mA  VBUS= {:>6} mV".format(curr, vbus), end='')
        time.sleep(0.2)
