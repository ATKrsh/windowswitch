import ctypes
import time
import sys

def get_window_title(hwnd):
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value.strip()

def pause_active_video():
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    title = get_window_title(hwnd)
    print(f"Active window: {title}")
    
    WM_APPCOMMAND = 0x0319
    APPCOMMAND_MEDIA_PLAY_PAUSE = 14
    lParam = APPCOMMAND_MEDIA_PLAY_PAUSE << 16
    
    print("Sending WM_APPCOMMAND directly to the window...")
    user32.SendMessageW(hwnd, WM_APPCOMMAND, hwnd, lParam)

time.sleep(3)
pause_active_video()
