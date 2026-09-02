import ctypes
import time

user32 = ctypes.windll.user32
VK_MEDIA_PLAY_PAUSE = 0xB3

print("Pausing media in 3 seconds...")
time.sleep(3)
# Try with extended key flag
user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 1, 0)
user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 1 | 2, 0)
print("Pause signal sent.")
