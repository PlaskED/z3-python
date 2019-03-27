from z3 import *
import math

M_PI = RealVal('3.14159265358979323846')

def sin(x):
    return IntVal('0')

def cos(x):
    return IntVal('1')

def tan(x):
    return IntVal('0')

def abs(x):
    return If(x >= 0,x,-x)

def fabs(x):
    return If(x >= 0.0,x,-x)

def exp(x):
    e = math.e * 1.0
    return pow(e,x)

def pow(x,y):
    return x**y

def sqrt(x):
    return x**1.0/2

def min(x,y):
    return If(x < y, x, y)

def max(x,y):
    return If(x >= y, x, y)
