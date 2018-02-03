import re

def isnumber(num):
    return re.match('-?\d+', num) != None
