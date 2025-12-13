from machine import ADC, Pin  

def is_raining() -> int:
    adc = ADC(Pin(39))
    value = adc.read_u16()
    if value >= 10000:
        return 1
    else:
        return 0 