def formatString(string):
    newStr = string
    while len(newStr) < 16:
        newStr += " "
    return newStr