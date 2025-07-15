import math

def frac(x):
    while x < 0:
        x = x + 1.0
    while x > 1.0:
        x = x - 1.0	
    return x

def xsin(x, power):
    x = frac(x)
    return math.pow(math.sin(math.pi*x), power*2) 

def func(x, x_frac, power, arg, **kw):
    d = arg/100
    value = 0
    value = value + xsin(x_frac + d, power = power)
    value = value + xsin(x_frac - d, power = power)
    return value 