def incrChannel(chnl):
    if chnl < 4:            # if chnl is less than 4, increase as usual
        return chnl + 1
    else:                   # if chnl is 4, loop back to 0
        return 0

def decrChannel(chnl):
    if chnl > 0:            # if chnl is more than 0, decrease as usual
        return chnl - 1
    else:                   # if chnl is 0, loop back to 4
        return 4

# val = 1 to increase, val = 0 to decrease
def changeChannel(val, currChnl):
    newChnl = currChnl
    if val == 1:
        newChnl = incrChannel(currChnl)
    else:
        newChnl = decrChannel(currChnl)
    return newChnl
