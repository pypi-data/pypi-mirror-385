def add(a, b):
    '''This will return addition of two numbers'''
    return a+b

def subtract(a, b):
    return a-b

def multiply(a, b):
    return a*b

def divide(a, b):
    if b == 0:
        raise ValueError('cannot divide by 0')
    return a/b

def power(a, b):
    return a**b
