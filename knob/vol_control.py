# Install command for alsaaudio:
# sudo -H pip3 install pyalsaaudio

import alsaaudio

def getVolumeChange(vol):
    if vol == 0:
        return 25
    elif vol >= 94:
        return 1
    elif vol >= 90:
        return 2
    elif vol >= 80:
        return 3
    elif vol >= 70:
        return 4
    elif vol >= 55:
        return 5
    else:
        return 7

def incrVol(mixer):
    vol = mixer.getvolume()[0]
    if vol >= 97:
        return vol
    if vol + getVolumeChange(vol) > 97:
        return 97
    return vol + getVolumeChange(vol)
        
def decrVol(mixer):
    vol = mixer.getvolume()[0]
    if vol == 0: # muted
        return 0
    if vol <= 25: # can't go below 25 cos it will be too soft
        return vol
    if vol - getVolumeChange(vol) < 25:
        return 0
    return vol - getVolumeChange(vol)

# val = 1 to increase, val = 0 to decrease
def changeVol(val):
    mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
    vol = mixer.getvolume()[0]
    if val == 1:
        vol = incrVol(mixer)
    else:
        vol = decrVol(mixer)
    mixer.setvolume(vol)
    print("volume set to", mixer.getvolume()[0])
    # str = formatString(vol) TODO

