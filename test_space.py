import ctypes
import time

user32 = ctypes.windll.user32
VK_SPACE = 0x20
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

print("Waiting 3 seconds...")
time.sleep(3)
hwnd = user32.GetForegroundWindow()
print(f"Sending Space to {hwnd}")
user32.PostMessageW(hwnd, WM_KEYDOWN, VK_SPACE, 0)
time.sleep(0.05)
user32.PostMessageW(hwnd, WM_KEYUP, VK_SPACE, 0)
print("Done")
