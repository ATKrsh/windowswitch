import ctypes
from ctypes import wintypes
import time

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),)
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

def send_media_play_pause():
    INPUT_KEYBOARD = 1
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP       = 0x0002
    VK_MEDIA_PLAY_PAUSE   = 0xB3

    inp_down = INPUT()
    inp_down.type = INPUT_KEYBOARD
    inp_down.ki = KEYBDINPUT(wVk=VK_MEDIA_PLAY_PAUSE, wScan=0, dwFlags=KEYEVENTF_EXTENDEDKEY, time=0, dwExtraInfo=0)

    inp_up = INPUT()
    inp_up.type = INPUT_KEYBOARD
    inp_up.ki = KEYBDINPUT(wVk=VK_MEDIA_PLAY_PAUSE, wScan=0, dwFlags=KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)

    arr = (INPUT * 2)(inp_down, inp_up)
    ctypes.windll.user32.SendInput(2, ctypes.byref(arr), ctypes.sizeof(INPUT))

print("Switch to your video player and make sure a video is playing.")
print("Waiting 5 seconds...")
time.sleep(5)
print("Sending hardware media pause key...")
send_media_play_pause()
print("Done!")
