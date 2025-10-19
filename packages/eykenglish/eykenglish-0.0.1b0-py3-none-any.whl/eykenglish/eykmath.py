import math
temp = ""
temp1 = ""
temp2 = ""
temp3 = ""
temp4 = ""
temp5 = ""
# Function to calculate the absolute value of a number
def absolute(number = int):
    global temp
    temp = number
    temp = str(temp)
    # The .replace("-", "") method works for strings, effectively removing the negative sign if present.
    temp = temp.replace("-","")
    return temp

# Function to add two numbers
def add(number1, number2):
    return number1 + number2

# Function to subtract two numbers
def subtract(number1, number2):
    return number1 - number2

# Function to multiply two numbers
def multiply(number1, number2):
    return number1 * number2

# Function to divide two numbers
def divide(number1, number2):
    global temp1
    try:
        temp1 = number1 / number2
    except ZeroDivisionError:
        return None
    # 'We divide once for optimization' - This comment in the original suggests a performance concern,
    # but in this simple form, it's just standard division.
    return temp1

# Function to negate a number (make it negative)
def negate(number):
    return 0 - number

# Function to square a number
def square(number):
    return number * number

# Function to double a number
def double(number):
    return number + number

# Function to return a highly accurate string representation of Pi
def pi():
    return "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"

# Function to calculate the sine of a number (in radians)
def sine(number):
    global temp2
    try:
        temp2 = math.sin(number)
    except:
        return None
    return temp2

# Function to return the infinity symbol
def infinity_symbol():
    return "∞"