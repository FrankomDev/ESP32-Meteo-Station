# this is my primitive driver but works XD
# if you are interested in doing something similiar look at docs below and i marked some important chapters in my code
# https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf

from machine import I2C, Pin

class BME280:
    def __init__(self):
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.address = 0x76
        self._calib_params()

    def _to_signed(self, b: bytes) -> int:
        n = int.from_bytes(b, "little")
        bits = 8*len(b)
        if n >= 1 << (bits - 1):
            n -= 1 << bits
        return n

    def _calib_params(self):
        #docs 4.2.2
        calib_t = self.i2c.readfrom_mem(self.address, 0x88, 6)
        self.T1 = int.from_bytes(calib_t[0:2], "little") #unsigned
        self.T2 = self._to_signed(calib_t[2:4])
        self.T3 = self._to_signed(calib_t[4:6])

        calib_p = self.i2c.readfrom_mem(self.address, 0x8E, 18)
        self.P1 = int.from_bytes(calib_p[0:2], "little") #unsigned
        self.P2 = self._to_signed(calib_p[2:4])
        self.P3 = self._to_signed(calib_p[4:6])
        self.P4 = self._to_signed(calib_p[6:8])
        self.P5 = self._to_signed(calib_p[8:10])
        self.P6 = self._to_signed(calib_p[10:12])
        self.P7 = self._to_signed(calib_p[12:14])
        self.P8 = self._to_signed(calib_p[14:16])
        self.P9 = self._to_signed(calib_p[16:18])

        calib_h1 = self.i2c.readfrom_mem(self.address, 0xA1, 1)
        calib_h2 = self.i2c.readfrom_mem(self.address, 0xE1, 7)
        self.H1 = int.from_bytes(calib_h1[0:1], "little")
        self.H2 = self._to_signed(calib_h2[0:2])
        self.H3 = int.from_bytes(calib_h2[2:3], "little")
        raw_h4 = (calib_h2[3]<<4) | (calib_h2[4] & 0x0F)
        self.H4 = self._to_signed(raw_h4.to_bytes(2, "little"))
        raw_h5 = int.from_bytes(calib_h2[4:6], "little")>>4
        self.H5 = self._to_signed(raw_h5.to_bytes(2, "little"))
        self.H6 = self._to_signed(calib_h2[6:7])

        # write config
        #docs 5.4.3 - 5.4.6
        self.i2c.writeto_mem(self.address, 0xF2, bytes([0x01]))
        self.i2c.writeto_mem(self.address, 0xF4, bytes([0x27]))
        self.i2c.writeto_mem(self.address, 0xF5, bytes([0xA0]))

    def _humidity(self, t_fine : int, raw_humidity : int) -> int:
        var_h = (t_fine - 76800.0)
        var_h = (raw_humidity - (self.H4 *64.0 + self.H5/16384 * var_h)) * (self.H2/65536.0 * (1.0 + self.H6/67108864.0 * var_h * (1.0 + self.H3/67108864.0 * var_h)))
        var_h = var_h * (1.0 - self.H1 * var_h/524288.0)
        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0
        return var_h

    def _pressure(self, t_fine : int, raw_pressure : int) -> int:
        var1 = (t_fine/2.0) - 64000.0
        var2 = var1*var1 * self.P6/32768.0
        var2 = var2 + var1 * self.P5 * 2.0
        var2 = (var2/4.0) + (self.P4 * 65536.0)
        var1 = (self.P3 * var1 * var1/524288.0 + self.P2 * var1) / 524288.0
        var1 = (1.0 + var1/32768.0) * self.P1
        if var1==0.0:
            return 0
        p = 1048576.0 - raw_pressure
        p = (p - (var2/4096.0)) * 6250.0 / var1
        var1 = self.P9 * p * p/2147483648.0
        var2 = p * self.P8/32768.0
        p = p + (var1 + var2 + self.P7) / 16.0
        return p/100.0

    def _temperature(self, raw_temperature : int) -> list:
        var1 = (raw_temperature/16384.0 - self.T1/1024.0) * self.T2
        var2 = ((raw_temperature/131072.0 - self.T1/8192.0)** 2) * self.T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0
        return [temperature, t_fine]

    def get_data(self) -> list:
        #docs 5.4.7 - 5.4.9
        raw_pressure_bytes = self.i2c.readfrom_mem(self.address, 0xF7, 3)
        raw_temperature_bytes = self.i2c.readfrom_mem(self.address, 0xFA, 3)
        raw_humidity_bytes = self.i2c.readfrom_mem(self.address, 0xFD, 2)
        raw_temperature = int.from_bytes(raw_temperature_bytes, "big") >> 4
        raw_pressure = int.from_bytes(raw_pressure_bytes, "big") >> 4
        raw_humidity = int.from_bytes(raw_humidity_bytes, "big")

        #docs 8.1
        t = self._temperature(raw_temperature)
        t_fine : int = t[1]
        temperature = t[0]
        pressure = self._pressure(t_fine, raw_pressure)
        humidity = self._humidity(t_fine, raw_humidity)

        return [temperature, pressure, humidity]