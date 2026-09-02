# switcher.py
# Always-on-top, translucent Assistive Window Switcher desktop widget.

import sys
import os

# Safely redirect stdout/stderr if running without console (e.g., PyInstaller --noconsole)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import faulthandler
try:
    faulthandler.enable()
except Exception:
    pass

import ctypes
try:
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)
except Exception:
    pass

import subprocess

# Identify Platform
IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform.startswith("darwin")

# Safely redirect stdout/stderr to devnull if running as GUI without console
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
import base64
import math
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QSystemTrayIcon,
                             QMenu, QAction, QSlider, QWidgetAction, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt, QPoint, QPointF, QTimer, QPropertyAnimation, QVariantAnimation, QSize, QRectF, QMetaObject, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QPainter, QPen, QBrush, QColor, QPainterPath
from PyQt5.QtWinExtras import QtWin

# ---------------------------------------------------------
# OS-Specific Window Control Definitions
# ---------------------------------------------------------
if IS_WINDOWS:
    import ctypes
    import ctypes.wintypes
    import winreg
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    shell32 = ctypes.windll.shell32
    
    shell32.ExtractIconW.argtypes = [ctypes.wintypes.HINSTANCE, ctypes.c_wchar_p, ctypes.c_int]
    shell32.ExtractIconW.restype = ctypes.wintypes.HICON
    if hasattr(user32, 'DestroyIcon'):
        user32.DestroyIcon.argtypes = [ctypes.wintypes.HICON]
        user32.DestroyIcon.restype = ctypes.wintypes.BOOL

    kernel32.OpenProcess.argtypes  = [ctypes.c_ulong, ctypes.c_bool, ctypes.c_ulong]
    kernel32.OpenProcess.restype   = ctypes.wintypes.HANDLE
    kernel32.CloseHandle.argtypes  = [ctypes.wintypes.HANDLE]
    kernel32.CloseHandle.restype   = ctypes.c_bool
    
    kernel32.QueryFullProcessImageNameW.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.c_ulong,
        ctypes.c_wchar_p,
        ctypes.POINTER(ctypes.c_ulong),
    ]
    kernel32.QueryFullProcessImageNameW.restype = ctypes.c_bool

    user32.GetWindowThreadProcessId.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.c_ulong)]
    user32.GetWindowThreadProcessId.restype  = ctypes.c_ulong

    # Win32 functions with explicit argtypes and restypes for 64-bit compatibility
    IsWindowVisible = user32.IsWindowVisible
    IsWindowVisible.argtypes = [ctypes.wintypes.HWND]
    IsWindowVisible.restype = ctypes.wintypes.BOOL

    GetWindowTextW = user32.GetWindowTextW
    GetWindowTextW.argtypes = [ctypes.wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
    GetWindowTextW.restype = ctypes.c_int

    GetWindowTextLengthW = user32.GetWindowTextLengthW
    GetWindowTextLengthW.argtypes = [ctypes.wintypes.HWND]
    GetWindowTextLengthW.restype = ctypes.c_int

    GetParent = user32.GetParent
    GetParent.argtypes = [ctypes.wintypes.HWND]
    GetParent.restype = ctypes.wintypes.HWND

    # Resolve 32-bit vs 64-bit API compatibility for window styles
    if hasattr(user32, "GetWindowLongPtrW"):
        GetWindowLongW = user32.GetWindowLongPtrW
        GetWindowLongW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
        GetWindowLongW.restype = ctypes.c_ssize_t
        
        SetWindowLongW = user32.SetWindowLongPtrW
        SetWindowLongW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
        SetWindowLongW.restype = ctypes.c_ssize_t
    else:
        GetWindowLongW = user32.GetWindowLongW
        GetWindowLongW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
        GetWindowLongW.restype = ctypes.c_long
        
        SetWindowLongW = user32.SetWindowLongW
        SetWindowLongW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_long]
        SetWindowLongW.restype = ctypes.c_long

    SetForegroundWindow = user32.SetForegroundWindow
    SetForegroundWindow.argtypes = [ctypes.wintypes.HWND]
    SetForegroundWindow.restype = ctypes.wintypes.BOOL

    ShowWindow = user32.ShowWindow
    ShowWindow.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
    ShowWindow.restype = ctypes.wintypes.BOOL

    GetForegroundWindow = user32.GetForegroundWindow
    GetForegroundWindow.argtypes = []
    GetForegroundWindow.restype = ctypes.wintypes.HWND

    IsWindow = user32.IsWindow
    IsWindow.argtypes = [ctypes.wintypes.HWND]
    IsWindow.restype = ctypes.wintypes.BOOL

    IsIconic = user32.IsIconic
    IsIconic.argtypes = [ctypes.wintypes.HWND]
    IsIconic.restype = ctypes.wintypes.BOOL

    SetLayeredWindowAttributes = user32.SetLayeredWindowAttributes
    SetLayeredWindowAttributes.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.COLORREF, ctypes.c_byte, ctypes.wintypes.DWORD]
    SetLayeredWindowAttributes.restype = ctypes.wintypes.BOOL

    SetWindowPos = user32.SetWindowPos
    SetWindowPos.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    SetWindowPos.restype = ctypes.wintypes.BOOL

    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    EnumWindows.argtypes = [EnumWindowsProc, ctypes.wintypes.LPARAM]
    EnumWindows.restype = ctypes.wintypes.BOOL

    kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
    kernel32.GetModuleHandleW.restype = ctypes.wintypes.HMODULE

    user32.SendInput.argtypes = [ctypes.c_uint, ctypes.c_void_p, ctypes.c_int]
    user32.SendInput.restype = ctypes.c_uint

    # Win32 Constants
    GWL_EXSTYLE = -20
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_LAYERED = 0x00080000
    LWA_ALPHA = 0x00000002
    SW_RESTORE = 9

    # Low-level Windows Mouse Hook for global Middle Click detection
    HOOKPROC = ctypes.WINFUNCTYPE(
        ctypes.c_ssize_t,       # LRESULT (64-bit signed on 64-bit OS)
        ctypes.c_int,           # nCode
        ctypes.wintypes.WPARAM, # wParam
        ctypes.wintypes.LPARAM  # lParam
    )

    class MouseHook:
        def __init__(self, signal_emitter):
            self.signal_emitter = signal_emitter
            self.hook_id = None
            self._c_callback = HOOKPROC(self._hook_callback)

        def install(self):
            if not IS_WINDOWS:
                return
            try:
                user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, ctypes.wintypes.HINSTANCE, ctypes.wintypes.DWORD]
                user32.SetWindowsHookExW.restype = ctypes.c_void_p
                
                # WH_MOUSE_LL = 14
                self.hook_id = user32.SetWindowsHookExW(
                    14,
                    self._c_callback,
                    kernel32.GetModuleHandleW(None),
                    0
                )
                if not self.hook_id:
                    print("[Hook Error] Failed to install mouse hook.", flush=True)
                else:
                    print("[Hook] Mouse hook installed successfully.", flush=True)
            except Exception as e:
                print(f"[Hook Error] Exception during install: {e}", flush=True)

        def uninstall(self):
            if self.hook_id:
                try:
                    user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
                    user32.UnhookWindowsHookEx.restype = ctypes.c_bool
                    user32.UnhookWindowsHookEx(self.hook_id)
                except Exception:
                    pass
                self.hook_id = None
                print("[Hook] Mouse hook uninstalled.", flush=True)

        def _hook_callback(self, nCode, wParam, lParam):
            try:
                # WM_MBUTTONDOWN = 0x0207
                if nCode >= 0 and wParam == 0x0207:
                    self.signal_emitter()
            except Exception as e:
                print(f"[Hook Error] Exception in callback: {e}", flush=True)

            try:
                user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM]
                user32.CallNextHookEx.restype = ctypes.c_ssize_t
                res = user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)
                return res if res is not None else 0
            except Exception:
                return 0
elif IS_MACOS:
    try:
        from AppKit import NSWorkspace, NSRunningApplication, NSApplicationActivateIgnoringOtherApps
        MACOS_NATIVE = True
    except ImportError:
        MACOS_NATIVE = False

def set_window_opacity(hwnd, alpha):
    try:
        style = GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not (style & WS_EX_LAYERED):
            SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
        SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
    except Exception as e:
        print(f"[Fade Error] Failed to set opacity: {e}")

def restore_window_style(hwnd, original_style):
    try:
        if original_style is not None:
            SetWindowLongW(hwnd, GWL_EXSTYLE, original_style)
            # Force style update
            SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027) # SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
    except Exception as e:
        print(f"[Fade Error] Failed to restore style: {e}")

def get_window_title(hwnd):
    length = GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value.strip()

def log_debug(msg):
    try:
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "switcher_debug.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass

def pause_video_player(hwnd: int):
    if not IS_WINDOWS or not hwnd:
        return
    title = get_window_title(hwnd).lower()
    log_debug(f"pause_video_player called with hwnd={hwnd}, title='{title}'")
    
    # A broad list of common media player substrings
    video_keywords = ['vlc', 'movies & tv', 'media player', 'youtube', 'potplayer', 'kmplayer', 'mpv', 'netflix', 'prime video', 'mplayer']
    if any(kw in title for kw in video_keywords):
        log_debug(f"[Media] MATCH FOUND! Pausing video player: {title}")
        print(f"[Media] Pausing video player: {title}", flush=True)
        
        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP       = 0x0002
        VK_SPACE              = 0x20

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = (("wVk",         ctypes.wintypes.WORD),
                        ("wScan",       ctypes.wintypes.WORD),
                        ("dwFlags",     ctypes.wintypes.DWORD),
                        ("time",        ctypes.wintypes.DWORD),
                        ("dwExtraInfo", ctypes.wintypes.ULONG))

        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = (("ki", KEYBDINPUT),
                            ("mi", ctypes.c_byte * 28),
                            ("hi", ctypes.c_byte * 32))
            _anonymous_ = ("_input",)
            _fields_ = (("type",   ctypes.wintypes.DWORD),
                        ("_input", _INPUT))

        inp_down = INPUT()
        inp_down.type = INPUT_KEYBOARD
        inp_down.ki = KEYBDINPUT(wVk=VK_SPACE, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)

        inp_up = INPUT()
        inp_up.type = INPUT_KEYBOARD
        inp_up.ki = KEYBDINPUT(wVk=VK_SPACE, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)

        arr = (INPUT * 2)(inp_down, inp_up)
        ctypes.windll.user32.SendInput(2, ctypes.byref(arr), ctypes.sizeof(INPUT))
        
        import time
        time.sleep(0.1)

def lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
    r = c1.red()   + (c2.red()   - c1.red())   * t
    g = c1.green() + (c2.green() - c1.green()) * t
    b = c1.blue()  + (c2.blue()  - c1.blue())  * t
    a = c1.alpha() + (c2.alpha() - c1.alpha()) * t
    return QColor(int(r), int(g), int(b), int(a))

def get_window_icon(hwnd) -> QPixmap:
    if not IS_WINDOWS or not hwnd or not IsWindow(hwnd):
        return None
    extracted_pixmap = None
    try:
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value:
            h = kernel32.OpenProcess(0x1000, False, pid.value)
            if h:
                try:
                    buf = ctypes.create_unicode_buffer(512)
                    size = ctypes.c_ulong(512)
                    kernel32.QueryFullProcessImageNameW.argtypes = [
                        ctypes.wintypes.HANDLE,
                        ctypes.c_ulong,
                        ctypes.c_wchar_p,
                        ctypes.POINTER(ctypes.c_ulong),
                    ]
                    kernel32.QueryFullProcessImageNameW.restype = ctypes.c_bool
                    if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                        path = buf.value
                        hicon = shell32.ExtractIconW(0, path, 0)
                        if hicon and getattr(hicon, 'value', 0) > 1:
                            pixmap = QtWin.fromHICON(hicon)
                            user32.DestroyIcon(hicon)
                            if not pixmap.isNull():
                                extracted_pixmap = pixmap
                finally:
                    kernel32.CloseHandle(h)
    except Exception as e:
        print(f"[Switcher] Error extracting icon: {e}", flush=True)

    if extracted_pixmap and not extracted_pixmap.isNull():
        return extracted_pixmap

    try:
        if hasattr(user32, 'SendMessageW'):
            SendMessageW = user32.SendMessageW
            SendMessageW.argtypes = [ctypes.wintypes.HWND, ctypes.c_uint, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM]
            SendMessageW.restype = ctypes.c_void_p
            for icon_type in (2, 0, 1):
                hicon = SendMessageW(hwnd, 0x007F, icon_type, 0)
                if hicon:
                    pixmap = QtWin.fromHICON(hicon)
                    if not pixmap.isNull():
                        return pixmap
    except Exception as e:
        print(f"[Switcher] Fallback WM_GETICON error: {e}", flush=True)

    try:
        if hasattr(user32, 'GetClassLongPtrW'):
            GetClassLongPtr = user32.GetClassLongPtrW
            GetClassLongPtr.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
            GetClassLongPtr.restype = ctypes.c_void_p
        else:
            GetClassLongPtr = user32.GetClassLongW
            GetClassLongPtr.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
            GetClassLongPtr.restype = ctypes.c_ulong

        for gcl in (-34, -14):
            hicon = GetClassLongPtr(hwnd, gcl)
            if hicon:
                pixmap = QtWin.fromHICON(hicon)
                if not pixmap.isNull():
                    return pixmap
    except Exception as e:
        print(f"[Switcher] Fallback GetClassLong error: {e}", flush=True)

    return None

def get_user_windows():
    windows = []
    def enum_callback(hwnd, lParam):
        if is_user_application(hwnd):
            windows.append(hwnd)
        return True
    
    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    EnumWindows(EnumWindowsProc(enum_callback), 0)
    return windows

def is_user_application(hwnd):
    if not IsWindow(hwnd):
        return False
    if not IsWindowVisible(hwnd):
        return False
    title = get_window_title(hwnd)
    if not title:
        return False
    if GetParent(hwnd):
        return False
        
    # Exclude tool windows
    ex_style = GetWindowLongW(hwnd, GWL_EXSTYLE)
    if ex_style & WS_EX_TOOLWINDOW:
        return False
        
    # Exclude specific system/background UI processes
    ignored_titles = [
        "Program Manager", "Start", "Settings", "Cortana", 
        "Windows Shell Experience Host", "Microsoft Text Input Application",
        "Assistive Window Switcher"
    ]
    if title in ignored_titles:
        return False
        
    return True

def get_active_window_id():
    if IS_WINDOWS:
        hwnd = GetForegroundWindow()
        if hwnd and is_user_application(hwnd):
            return hwnd
    elif IS_MACOS:
        if MACOS_NATIVE:
            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            if app:
                name = app.localizedName()
                bundle = app.bundleIdentifier()
                if name == "Assistive Window Switcher" or bundle == "org.python.python":
                    return None
                return app.processIdentifier()
        else:
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            try:
                proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=0.1)
                name = proc.stdout.strip()
                if name and name not in ["Assistive Window Switcher", "Python"]:
                    return name
            except Exception:
                pass
    return None

def switch_to_window(window_id):
    if IS_WINDOWS:
        if IsIconic(window_id):
            ShowWindow(window_id, SW_RESTORE)
        SetForegroundWindow(window_id)
        return True
    elif IS_MACOS:
        if isinstance(window_id, int): # PID
            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(window_id)
            if app:
                app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
                return True
        else: # Process Name string
            script = f'tell application "System Events" to set frontmost of application process "{window_id}" to true'
            try:
                subprocess.run(['osascript', '-e', script], timeout=0.5)
                return True
            except Exception:
                pass
    return False

def is_valid_window(window_id):
    if IS_WINDOWS:
        return IsWindow(window_id)
    elif IS_MACOS:
        if isinstance(window_id, int): # PID
            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(window_id)
            return app is not None
        else: # Process name
            script = f'tell application "System Events" to exists application process "{window_id}"'
            try:
                proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=0.2)
                return proc.stdout.strip() == "true"
            except Exception:
                return False
    return False

def toggle_show_desktop():
    if not IS_WINDOWS:
        return
    
    try:
        import tempfile
        temp_dir = tempfile.gettempdir()
        vbs_path = os.path.join(temp_dir, "toggle_desktop.vbs")
        if not os.path.exists(vbs_path):
            with open(vbs_path, "w") as f:
                f.write('Dim shell\nSet shell = CreateObject("Shell.Application")\nshell.ToggleDesktop\n')
        subprocess.Popen(["wscript.exe", vbs_path], creationflags=0x08000000)
    except Exception as e:
        print(f"[Toggle Desktop Error] {e}")

def set_run_at_startup(enabled=True):
    if not IS_WINDOWS:
        return False
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "AssistiveWindowSwitcher"
    if getattr(sys, 'frozen', False):
        exe_path = f'"{os.path.abspath(sys.executable)}"'
    else:
        python_exe = os.path.abspath(sys.executable)
        script_path = os.path.abspath(sys.argv[0])
        exe_path = f'"{python_exe}" "{script_path}"'
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            print(f"[Startup] Enabled run at startup with path: {exe_path}", flush=True)
        else:
            try:
                winreg.DeleteValue(key, app_name)
                print("[Startup] Disabled run at startup.", flush=True)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Startup] Error setting registry: {e}", flush=True)
        return False

def is_run_at_startup():
    if not IS_WINDOWS:
        return False
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "AssistiveWindowSwitcher"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False

# ---------------------------------------------------------
# Assistive Touch Custom Button
# ---------------------------------------------------------
class AssistiveButton(QWidget):
    OUTER_R     = 26
    INNER_R     = 11
    WIDGET_SIZE = 56

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setFixedSize(self.WIDGET_SIZE, self.WIDGET_SIZE)
        self.setCursor(Qt.SizeAllCursor)
        self.setMouseTracking(True)

        self.is_dragging = False
        self.drag_position = QPoint()

        self._hover_zone = None
        self._press_zone = None

        self._hover_inner_val = 0.0
        self._hover_left_val  = 0.0
        self._hover_right_val = 0.0

        self._press_inner_val = 0.0
        self._press_left_val  = 0.0
        self._press_right_val = 0.0

        self._pt = 0.0
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(28)

    def _zone(self, pos):
        cx = cy = self.WIDGET_SIZE / 2
        dx, dy = pos.x() - cx, pos.y() - cy
        r = math.hypot(dx, dy)
        if r <= self.INNER_R:
            return 'inner'
        if r <= self.OUTER_R:
            return 'left' if dx < 0 else 'right'
        return None

    def _tick(self):
        self._pt = (self._pt + 0.062) % (2 * math.pi)
        
        # Targets
        ti = 1.0 if self._hover_zone == 'inner' else 0.0
        tl = 1.0 if self._hover_zone == 'left' else 0.0
        tr = 1.0 if self._hover_zone == 'right' else 0.0

        self._hover_inner_val += (ti - self._hover_inner_val) * 0.15
        self._hover_left_val  += (tl - self._hover_left_val) * 0.15
        self._hover_right_val += (tr - self._hover_right_val) * 0.15

        for zone, attr in [('inner', '_press_inner_val'), ('left', '_press_left_val'), ('right', '_press_right_val')]:
            current = getattr(self, attr)
            if self._press_zone == zone:
                setattr(self, attr, 1.0)
            else:
                new_val = current - 0.07
                if new_val < 0.0: new_val = 0.0
                setattr(self, attr, new_val)

        self.update()

    def paintEvent(self, event):
        try:
            self._paint_impl()
        except Exception as e:
            print(f"[Switcher] paintEvent error: {e}", flush=True)

    def _paint_impl(self):
        p   = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        S   = self.WIDGET_SIZE
        cx  = cy = S / 2.0
        pls = 0.5 + 0.5 * math.sin(self._pt)
        mid_r = (self.INNER_R + 2 + self.OUTER_R) / 2.0

        # Base colors (matching windowswitch)
        c_base  = QColor(30, 34, 45, 178)   # rgba(30, 34, 45, 0.70)
        c_hover = QColor(45, 52, 68, 217)   # rgba(45, 52, 68, 0.85)
        c_press = QColor(0, 120, 215, 204)  # rgba(0, 120, 215, 0.80)

        def get_zone_color(hover_val, press_val):
            c = lerp_color(c_base, c_hover, hover_val)
            c = lerp_color(c, c_press, press_val)
            return c

        p.setPen(Qt.NoPen)
        
        # Draw Left Half outer disc
        left_color = get_zone_color(self._hover_left_val, self._press_left_val)
        p.setBrush(QBrush(left_color))
        p.drawPie(QRectF(cx - self.OUTER_R, cy - self.OUTER_R, self.OUTER_R * 2, self.OUTER_R * 2), 90 * 16, 180 * 16)
        
        # Draw Right Half outer disc
        right_color = get_zone_color(self._hover_right_val, self._press_right_val)
        p.setBrush(QBrush(right_color))
        p.drawPie(QRectF(cx - self.OUTER_R, cy - self.OUTER_R, self.OUTER_R * 2, self.OUTER_R * 2), 270 * 16, 180 * 16)

        # ─ Vertical divider line in donut (shows left / right split) ─
        div = QPen(QColor(255, 255, 255, 12))
        div.setWidthF(1.0)
        div.setStyle(Qt.DashLine)
        p.setPen(div)
        ie = self.INNER_R + 2.5
        oe = self.OUTER_R - 1.0
        p.drawLine(QPointF(cx, cy - oe), QPointF(cx, cy - ie))
        p.drawLine(QPointF(cx, cy + ie), QPointF(cx, cy + oe))

        # ─ Separator ring (between inner circle and outer ring) ─
        sp = QPen(QColor(255, 255, 255, 15))
        sp.setWidthF(1.0)
        p.setPen(sp)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), self.INNER_R + 2, self.INNER_R + 2)

        # ─ Inner circle background ─
        inner_color = get_zone_color(self._hover_inner_val, self._press_inner_val)
        p.setBrush(QBrush(inner_color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), self.INNER_R, self.INNER_R)

        # ─ Inner circle content (Active window icon) ─
        if self.parent_widget.active_icon_pixmap:
            icon_sz = 18
            rx = cx - icon_sz / 2.0
            ry = cy - icon_sz / 2.0
            p.drawPixmap(QRectF(rx, ry, icon_sz, icon_sz), self.parent_widget.active_icon_pixmap, QRectF(self.parent_widget.active_icon_pixmap.rect()))

        # ─ Outer border (matching windowswitch look and lock states) ─
        is_locked = self.parent_widget.is_locked
        is_fly_mode = self.parent_widget.is_fly_mode
        overall_hover = max(self._hover_left_val, self._hover_right_val, self._hover_inner_val)
        overall_press = max(self._press_left_val, self._press_right_val, self._press_inner_val)
        
        if is_locked:
            b_base  = QColor(255, 165, 0, 153)
            b_hover = QColor(255, 165, 0, 217)
            border_color = lerp_color(b_base, b_hover, overall_hover)
        elif is_fly_mode:
            b_base  = QColor(138, 43, 226, 153)
            b_hover = QColor(138, 43, 226, 217)
            border_color = lerp_color(b_base, b_hover, overall_hover)
        else:
            b_base  = QColor(255, 255, 255, 38)
            b_hover = QColor(77, 150, 255, 128)
            b_press = QColor(0, 120, 215, 255)
            border_color = lerp_color(b_base, b_hover, overall_hover)
            border_color = lerp_color(border_color, b_press, overall_press)

        b_pen = QPen(border_color)
        b_pen.setWidthF(2.0)
        p.setPen(b_pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), self.OUTER_R, self.OUTER_R)

        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            modifiers = event.modifiers()
            if modifiers & Qt.AltModifier:
                print("[Action] Alt+Left click detected. Closing switcher.")
                QApplication.quit()
                return
            elif modifiers & Qt.ShiftModifier:
                self.parent_widget.toggle_lock()
                event.accept()
                return
            elif modifiers & Qt.ControlModifier:
                self.parent_widget.toggle_fly_mode()
                event.accept()
                return
            
            if not self.parent_widget.is_locked and not self.parent_widget.is_fly_mode:
                self.drag_position = event.globalPos() - self.parent_widget.frameGeometry().topLeft()
                self.is_dragging = False
            
            self._press_zone = self._zone(event.pos())
            self.update()
            event.accept()
        elif event.button() == Qt.MiddleButton:
            if self.parent_widget.is_fly_mode:
                self.parent_widget.quick_switch()
                event.accept()
                return
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        z = self._zone(event.pos())
        if z != self._hover_zone:
            self._hover_zone = z
            self.update()

        if event.buttons() == Qt.LeftButton and not self.parent_widget.is_locked and not self.parent_widget.is_fly_mode:
            diff = event.globalPos() - (self.parent_widget.frameGeometry().topLeft() + self.drag_position)
            if diff.manhattanLength() > 5:
                self.is_dragging = True
            self.parent_widget.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            pz = self._press_zone
            self._press_zone = None
            self.update()
            if self.is_dragging:
                self.is_dragging = False
            else:
                modifiers = event.modifiers()
                if not (modifiers & (Qt.AltModifier | Qt.ShiftModifier | Qt.ControlModifier)):
                    z = self._zone(event.pos())
                    if z == pz:
                        if z == 'inner':
                            self.parent_widget.quick_switch()
                        elif z == 'left':
                            self.parent_widget.cycle_left()
                        elif z == 'right':
                            self.parent_widget.cycle_right()
            event.accept()
        elif event.button() == Qt.MiddleButton:
            if self.parent_widget.is_fly_mode:
                event.accept()
                return
            super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self._hover_zone = None
        self.update()
        super().leaveEvent(event)

# ---------------------------------------------------------
# Assistive Touch Floating Circle Widget
# ---------------------------------------------------------
class AssistiveSwitcherWidget(QWidget):
    # Thread-safe signal: emitted from the Win32 hook thread, handled on Qt main thread
    middle_click_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        # Setup frameless transparent stays-on-top window.
        # WindowDoesNotAcceptFocus is critical: it prevents this widget from stealing focus 
        # when clicked, preserving the active window history!
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | 
                            Qt.Tool | Qt.SubWindow | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(56, 56)
        # Embedded Base64 Minimal Icon
        icon_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAPEElEQVR4nO1bC3BUZZb+///efncn6bw6AZLCDM4QgpKHIa0DSyiXwDiTwmGGaIEgE3cy4lAu7hRVzq6SB4igEFgGwYDyEliWHlhBrdnoLnY0ccnKI2IkMuFtAoQYkn4/7uPfOre7Z2Lo9CPdRmZ2vqpbSd97/8c5//nPOf855yL0N/z/Bh7tASmlw46JMaborw00BMHfZtvvFDTIxGfMqGaPHTum7ujo0FFKEyil+iFXUnNHh66xsVFTVVUli6TPeADHszOY5CAxxg3HjqmqysuVCCEGIUQQQixCSGa327UnTpzSKRQKEV4UBB4bDBne3NwJ/fATIeRBCMEzwWw2e2fOnOny3x86RsxgURwBE5s/fz6zfv36hOzsbLmfcP2mLTvGffRR86Qb12/ca7XZsjmOS/F6uTSEMe9bBEoYwtiVSsUNlVJ1K92Q+scH8qd0VC5aeKW0tPRrSqkGIcQ/u3mzHWPsCQwH/Ih5zihOAMI3bNiQmJWVBYRr1q3bOPHYe+/P6untNXIeb5Ygijr/eAIhGFYTiB8MIlIqQxQkhRKMiVMuY2/o9YlnSkqmfvDa5ldOI4QGEEJcTU2Ntba21huPeeN4dHLy5MnEoqIiWCXlsn983vihuWmB1e4oooKgI4R4EMYejCSiYdFwiLEpQgHxpoRSKhdFqkQYe9UqxfnJeZMOHTHtfR8Y0d3d7Rk3bkc/QrViLNsCoxhQXV3N1tTUpMFWWrlybaHp6NFf2aw2I6wmIcTpI5rCzMgIJwcMEaEPgVIVEqlMqVJ8WVxcuPPf9u5oBGkwmUx9FRUVrpEyAUfbIDAQaPTy8nI9QkhnnFb2THf3jccopUqGITbpvRESHWKiIkiHQEU1EimTlJTQtH5t3do5c/7+WlvbFUdBwT0DI+w3erz99tu6uXPnJu3bd/B7q9fWv2i3O4yEYSyw4hRRUHzfGv7ECFFIZFn2+o9mz6rbtuXVlo6ODvukSZP6RtBfdCvf2nouZerUXHXNqlem7Nqz73eCIOoZwlgponG1KOEgMZuKClGk8qKC++uO/seBQ1999RXNzs7ujmY7kIgHxJh++OGHWiC+7qX19+/as38LFamOIYxttIkHgKRhjL2EIc5TbWdXls9bOD8rK4ucPn06DeYaqeNEIh0Q9nxpaWkyrPybu956jYqiFmPi+rZFPhRAz0hOBCHOM6c/q547b+HPCwoKVO3t7clxlYAZM6pZUHh7D5juAbG/G4gPAMwEMIFhiOPU6c9qFy55enZeXp5q7969YJbDAkc0CLVnIqRJ+EHe1G0Op7Pwu9jzkShHSqmMEOyoq3vxF4sXzL9QU1PTU1tby4dpFxonTpxIKCkpSTROK1vR1dVdyTDs7buN+MGKURAFnVajPvVl+//+GiHUhzHu9TlfwbcECefelpSUaFfWvVTY3X39McLcfSs/GLAlQTrtdkfJj8orHkUIyQ8dOqQajviwEnD16lV9dna2Pm/Kg1ssFttDDCNp/FHZ9wRjsDxIEKUDY8QAfUApZQlDrG/tbHhi+nTjZYzxrWHHQSFWPzs7WwG+vcVqMzIMsY8m8V4vhxwOB2IZJnqliImX5/jMF+pWgxSwDQ0N6oglgPqdiMuXLyeNHz8+OW/Kg5stFts0HwPi694GA0Mwstmd6EFjMUlI0OGjR9/j09JSwbCDlotSCpiBt3a+vnj6dOMlny64E+SOxj77icePHy9ft25jrtXmKAJnYzSI948PARKarE/C+/c0KJctq5L13e6nQDxDSLRSMOaV+s1/B3ytrq6GY/odIMFuNjQ0qEB0jr33n7OoKOj+fJQdHuCRwARjvQghkthzPCfRsnb1Svn2rfUKzutFbrc7ii1BMSKI7+y8MAcObJWVlZJfMNRDZIOJf1VVlRJ5kb6nt89ICHGDsxVuOF4Qkcvl9HklaOSQMQRZbXbkcfsCP6ALHn/sZ7KJEyeSJ3/xtOdaV5eYmJCAw20HkFiCicvhdE/ctGVbzvJlS6XT4lAPkR38Y9BDZtP2beM8Hm8W+NsgUqH2rMPhpA8UFzCrqv9Z5nS6pVUcKTBBiOd4lJKsl8ZkWQZxHE/zp+Qxxz84qvz1syu8zZ+0CiAJ4ZgAkiuKQuJHH30yafmypWfAo21q+qZjxA5tBC9BW2hERVEHx9xQ2h/2LMfzyJCWjosK8+PqI4iiCH6+xFC3201TUpLJ2pdrZOVzHxdv9w9QGctGpBivXe26HyFkeuqphxRNTd8MxbFDX16woAiUhaz7+o3vR+IpgnaGifT03qKnTrfx8ZSAvLxcIgigfjBSKpW45ZNW/pdLl3sH+i1ULpdFQLxPD9js9hyEkHbRojL74sXffIMd2uSHP8yB2cvsNkeWLxQd+lgpiBQpVSp89uw5seyRn3vioQP6B6z0J4/MZg8f2qNgfEoP79y9n1vx22qvQiZHCoU8UgcJE4Q5j5czfPrpGV1xcUEP3BwcL2ADbwZu5uXlEYjbQ+jaH72NCCxDUIJOi2IFwxAkCCKSy6TcCOZ4nj7/21rP6zt2culpadJiROUdYixSkWqaWppTi4sLLg5VhGywOUDSwh+35yI9MYrQJRWH9ewidmIwknSKSq1Cfbf7xYWLfulpbjkhZBgMWBB43zjRHZUFQRB0ly5eTgtGCxusoZSxgaSFKIJDjmL1570ch/yiHBYibCmFEndeuCjOfuRn7guXLosGQzpIwojngTASZTJ50A7YkM1iADg1IKouh5OOGZNB+voHINsRth1IilKpQBcuXIE9iZKTkmIj3g9KxaCDk2A3IVcXifMzHMBGezwcsgxY6fpXVyn+oXIxawGzFakUUIoUChmSy1nES1YgZkCgICg9JMg9OnbsOA/DMPZoYoYByGUsslitVKtTo4P731Q8+cTjkg/OsCxi5SySsUxEFyhDuO58xkZ8JggQjxHxpKTqgR467BbAfs34xRdf8Hl5eQNKheKGx+29h2GkZGRE20HyB3p6afHUIuaNbZvkOTnjYcmp0+lElq97qWTjvTHtZURFitRqFVar1RF4gr5TIcMSy6yZD18PMCCoGQygu7sbTCGvVCh6LcgWMathf9+82UMXLqxgN29cq1AqFNjt8VD4O7N0Gnn5ldVyjVqNxSgDHIMBbVVqNTI3tQjHjzeJGo1K8kPCgGFZtn/y5MnOYA/ZoTcOHz7sLSsr8xoy0s/33PraH0ujEQUwXl1XJ3/m6adA5CnP80C85M5OLS5iphYXxctNxjKW8bz77h8EnU6DBTGkjqCQONFo1Ff0eq3FbDZzYf2A7du3cw0NDWJB/pSOzz/vcEaqDDHB6Gz7OdHpdIpqtRoyu9Ig4BY7nS7kdDlFAnsgBvC8gPTJSbi39zYiJBKF6ottZGZmfA4Hy61bzXek1PHgH4G9QSlN6ey8kj3nxz/dzfF8JsaYC3UiDEhBX99tCv77rje2KHInfp9xud1UpVTi7W/s8a5as55LS0nGMWl1mATBCPp1udySjxGSfJ8EyBYvevxXL9X9S3OwqBD7jQZ+0TCbzR6ozEjUJ5651fN1DsMQD+QeQg0GCik9PQ1funRZfKR8vnvj+jXyR+f+WPJn7XYH6u3tk+w6z8XAABAgkSLC+E6IEShAhUIpv1T9worO4UpsSLDGZrMZFIb3wZKpH0BxQrgDUQDgsGi1WuzleFRZ9aynZtU6KaqhUislEwYmEmz7iC8W/soiPG2CvqWKcWMzj8vl8tv19SZXsIAIHtoswCGLxZKSkJCQfu+kB970uD0/wBi7Io0LQpAEcLOnl4ITlJqSjDdu3sYl6xMxRI5GCyACLz7/3JNVVZVnhwuNk6E3Ahyqr2+EQoeB+yblmmAfhUouDAWYJrgyM9LxgYO/F97cvY9PSNSNGvFSJEgQtWlpqe9XVVWeb2lpcQ3/bghQSlMRQukTcot2ez3e70UjBUPPBKMNkOTf/NMzS5YvW9rmX/3oU2M1NTVWkAKoyRFFUILR1+CMNvH+1deNycw4snzZ0o6WlhbQZyNLjQG6urpSxo4dmzA5/6FNAwPWmUyYGOFdkCGGKFLv4X9/a3Fh4X1dGGMpCjQiCQDs2AGlaIjb+Oqal1kZex3KUnx1OncnwErOLnv4pcLC+27u3r0bQuFSqGa493Ekne7atUu5ZMmSlKXLVsx4590/bIVMkWRnv4Nq8+GAEeZ5nk+fMCGnvum/39na1tZmLygoCFs5hsO9EDCLZ86cScrPz0+cO2/hvFOnP6u+m5gg1QUIfHJGhuHAyRPH1926dctuMBhuRtY2Cpw7dy4lNzdXBQVJUJMDZSkSj0YpbzjcygsCn5JhMBw42Xp8DULIjTG+ibEUsQ8LEs1gUIcHpWjvHNn/+6LCKbWCIELpuyyS3GG8AXoILhB7aeV9xFOTySSZvAhjsCjqlYM6vM7OTvfRI/sPzyid9huoyYGyFFiJGFMCUdYIUgWUz06YcM9GEHtYeZPJ9FVFRUVUi4FHOgkoRYNqrN37Dt67NlAtSogd0tJSofO3oBsClahg52Uytmt22cOrX39tg9nhcAharfbmyPocAQKKcW9jo2ZRWVkSpJ/n/GT+T788/8dKqMwghDj8jBhxofTQ0tgA4Zgh9jEZhiPbfle/C0xdc/PnjunT7++Pof+RIcAEf8U4FE3LP/74xLgX6tY8evXKtXlQnAB5OUhRDymVB6YEHffPWwgqxKX3iUCpEolUzjDYmpaa+v4TiyoOgocHp1WTyWSJpVIcEDcx9VePQ26MNZubszf869bpnZ0XZztczlwqUN/HEgRxkKuDdBVkbAa3lySFSh4mA2Es37kMuxRK+ZVxY8ccX1Ax/7+qqhafB8JbW1tdRqPRGo9PaHA8iB88CT8jNP5gi3bLlh05xz/+OPfala4pNrstBxKVVBQ0AjAF/8mjlELXDIutEMDUatSXMzIz2osK8r+AYAac5yEi1tra6jYajXBKjZuyxfHqaFB/0uSqqw/Jn3uuTJOYmAiMkDLOwJD/OXkyobX505TOSxdTWZaVpIDneSYlKdU+a1bp9YKCyU6tVmuBlfZHcUSTyeQEUUd/KaBD6nDgM7jGxjYNfBpHKU32X6kQe/T/DfwvfULX3t6uHa6o6S8KNHTJ+uBn+Lv6eBKjUcRgYoIprsDzv8pPaP8GdHfi/wA281geAi7zYgAAAABJRU5ErkJggg==")
        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)
        self.app_icon = QIcon(pixmap)
        self.setWindowIcon(self.app_icon)
        
        self.setWindowTitle("Assistive Window Switcher")
        
        # Opacity & size config (persisted in memory; easy to extend to file)
        self.opacity_pct = 50   # 0-100; idle opacity %
        self.size_pct    = 50   # 0-100; 50% -> 56px default

        # Set opacity (50% opacity in idle state)
        self.setWindowOpacity(self.opacity_pct / 100.0)
        
        # Inner layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.active_icon_pixmap = None
        self.is_cycling = False
        self.cycle_list = []
        self.cycle_index = 0
        self.last_cycle_time = 0.0

        # Main round button
        self.button = AssistiveButton(self)
        self.button.setFixedSize(56, 56)
        self.button.setCursor(Qt.SizeAllCursor)
        
        # Initial lock state
        self.is_locked = False
        self.is_fly_mode = False
        self.update_button_style()
        
        layout.addWidget(self.button)
        
        # System Tray Icon Setup
        self.setup_tray_icon()
        
        # Drag tracking variables
        self.drag_position = QPoint()
        self.is_dragging = False
        
        # Active Window History Tracking
        self.current_hwnd = None
        self.last_hwnd = None
        
        # Poll active window using a high-frequency timer (150 ms)
        self.history_timer = QTimer(self)
        self.history_timer.timeout.connect(self.poll_active_window)
        self.history_timer.start(150)
        
        # Snappy fade animation setup (120 ms duration)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(120)

        # Window-to-window transition variables
        self.anim_hwnd_out = None
        self.anim_hwnd_in = None
        self.anim_style_out = None
        self.anim_style_in = None
        self.window_fade_anim = None

        # Fly Mode state
        self.saved_position = None
        self.fly_timer = QTimer(self)
        self.fly_timer.timeout.connect(self.update_fly_position)
        
        # Mouse Hook for global middle click (Windows-only)
        self.mouse_hook = None
        if IS_WINDOWS:
            self.mouse_hook = MouseHook(self.middle_click_signal.emit)
            self.middle_click_signal.connect(self.on_global_middle_click)
            self.mouse_hook.install()

    # Polling function to record active window sequence
    def poll_active_window(self):
        # Reset cycling state if inactive for 2 seconds
        if self.is_cycling and (time.time() - self.last_cycle_time > 2.0):
            self.is_cycling = False
            self.cycle_list = []

        active_id = get_active_window_id()
        if not active_id:
            if self.active_icon_pixmap is not None:
                self.active_icon_pixmap = None
                self.button.update()
            return
            
        # Ignore our own widget window
        if IS_WINDOWS and active_id == int(self.winId()):
            return
            
        if active_id != self.current_hwnd:
            # Update history pair
            self.last_hwnd = self.current_hwnd
            self.current_hwnd = active_id
            
            self.active_icon_pixmap = get_window_icon(active_id)
            self.button.update()
            
            # Debug output to verify tracking
            if IS_WINDOWS:
                current_title = get_window_title(self.current_hwnd)
                last_title = get_window_title(self.last_hwnd) if self.last_hwnd else "None"
            else:
                current_title = str(self.current_hwnd)
                last_title = str(self.last_hwnd) if self.last_hwnd else "None"
            print(f"[History] Current: '{current_title}' | Last: '{last_title}'")

    # Performs the quick switch to the last active window
    def quick_switch(self):
        if self.is_dragging:
            return
            
        user_wins = get_user_windows()
        if len(user_wins) <= 1:
            if len(user_wins) == 1:
                target = user_wins[0]
                if IsIconic(target):
                    print(f"[Switch] Only 1 window open and it is minimized. Restoring: '{get_window_title(target)}'")
                    switch_to_window(target)
                else:
                    print(f"[Switch] Only 1 window open and it is visible. Toggling to desktop.")
                    toggle_show_desktop()
            else:
                print("[Switch] No user windows open. Toggling desktop.")
                toggle_show_desktop()
            return

        if self.last_hwnd and is_valid_window(self.last_hwnd):
            hwnd_out = self.current_hwnd
            hwnd_in = self.last_hwnd
            
            # If target window is same as current, do nothing
            if hwnd_out == hwnd_in:
                return
                
            # pause_video_player(hwnd_out) # Removed to prevent accidental pausing of media
                
            if IS_WINDOWS:
                target_title = get_window_title(hwnd_in)
                print(f"[Switch] Smoothly fading focus to: '{target_title}'")
                # Start the smooth fade transition (Windows-only)
                self.start_window_fade(hwnd_out, hwnd_in)
            else:
                print(f"[Switch] Toggling focus to: '{hwnd_in}'")
                switch_to_window(hwnd_in)
        else:
            print("[Switch] No valid last active window recorded yet.")

    def cycle_left(self):
        self._do_cycle(-1)

    def cycle_right(self):
        self._do_cycle(1)

    def _do_cycle(self, direction):
        now = time.time()
        if not self.is_cycling or not self.cycle_list or (now - self.last_cycle_time > 2.0):
            self.is_cycling = True
            self.cycle_list = get_user_windows()
            fg = get_active_window_id()
            if fg in self.cycle_list:
                self.cycle_index = self.cycle_list.index(fg)
            else:
                self.cycle_index = 0

        if not self.cycle_list:
            self.is_cycling = False
            return

        self.cycle_index = (self.cycle_index + direction) % len(self.cycle_list)
        target = self.cycle_list[self.cycle_index]
        if is_valid_window(target):
            print(f"[Cycle] Switching to window: {get_window_title(target)}")
            hwnd_out = get_active_window_id()
            if hwnd_out and hwnd_out != target:
                pause_video_player(hwnd_out)
                self.start_window_fade(hwnd_out, target)
            else:
                switch_to_window(target)
        self.last_cycle_time = now

    # Starts smooth window-to-window opacity fade transition
    def start_window_fade(self, hwnd_out, hwnd_in):
        # Stop any existing transition to prevent collisions
        if self.window_fade_anim and self.window_fade_anim.state() == QVariantAnimation.Running:
            self.window_fade_anim.stop()
            self.on_fade_finished()
            
        self.anim_hwnd_out = hwnd_out
        self.anim_hwnd_in = hwnd_in
        
        # Save original style of incoming window to restore it later
        self.anim_style_out = None
        self.anim_style_in = GetWindowLongW(hwnd_in, GWL_EXSTYLE) if hwnd_in and IsWindow(hwnd_in) else None
        
        # Restore target window if minimized, and set to 0 opacity
        if self.anim_hwnd_in and IsWindow(self.anim_hwnd_in):
            if IsIconic(self.anim_hwnd_in):
                ShowWindow(self.anim_hwnd_in, SW_RESTORE)
            set_window_opacity(self.anim_hwnd_in, 0)
            SetForegroundWindow(self.anim_hwnd_in)
            
        # Start QVariantAnimation to fade opacities over 120ms (snappy)
        self.window_fade_anim = QVariantAnimation(self)
        self.window_fade_anim.setDuration(120)
        self.window_fade_anim.setStartValue(0.0)
        self.window_fade_anim.setEndValue(1.0)
        self.window_fade_anim.valueChanged.connect(self.on_fade_step)
        self.window_fade_anim.finished.connect(self.on_fade_finished)
        self.window_fade_anim.start()

    # Step callback of the transition animation
    def on_fade_step(self, value):
        # Incoming window fades from 0 (0% opaque) to 255 (100% opaque).
        # Outgoing window remains fully opaque in the background to prevent desktop visibility.
        if self.anim_hwnd_in and IsWindow(self.anim_hwnd_in):
            alpha_in = int(value * 255)
            set_window_opacity(self.anim_hwnd_in, alpha_in)

    # Clean up and restore original styles once transition is done
    def on_fade_finished(self):
        if self.anim_hwnd_in and IsWindow(self.anim_hwnd_in):
            restore_window_style(self.anim_hwnd_in, self.anim_style_in)
            
        self.anim_hwnd_out = None
        self.anim_hwnd_in = None
        self.anim_style_out = None
        self.anim_style_in = None

    # Drag implementation fallback
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            modifiers = event.modifiers()
            if modifiers & Qt.AltModifier:
                print("[Action] Alt+Left click detected. Closing switcher.")
                QApplication.quit()
                return
            elif modifiers & Qt.ShiftModifier:
                self.toggle_lock()
                event.accept()
                return
            elif modifiers & Qt.ControlModifier:
                self.toggle_fly_mode()
                event.accept()
                return
            
            if not self.is_locked and not self.is_fly_mode:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.is_dragging = False
            event.accept()
        elif event.button() == Qt.MiddleButton:
            if self.is_fly_mode:
                self.quick_switch()
                event.accept()
                return
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.is_locked and not self.is_fly_mode:
            diff = event.globalPos() - (self.frameGeometry().topLeft() + self.drag_position)
            if diff.manhattanLength() > 5:
                self.is_dragging = True
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
            else:
                modifiers = event.modifiers()
                if not (modifiers & (Qt.AltModifier | Qt.ShiftModifier | Qt.ControlModifier)):
                    self.quick_switch()
            event.accept()
        elif event.button() == Qt.MiddleButton:
            if self.is_fly_mode:
                event.accept()
                return
            super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    # Helper to smoothly transition window opacity
    def fade_to(self, target_opacity):
        self.fade_animation.stop()
        self.fade_animation.setStartValue(self.windowOpacity())
        self.fade_animation.setEndValue(target_opacity)
        self.fade_animation.start()

    # Snappy hover fade effect (idle_opacity -> hover_opacity)
    def enterEvent(self, event):
        idle = self.opacity_pct / 100.0
        hover = min(1.0, idle + 0.40)   # +40% on hover, capped at 100%
        self.fade_to(hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.fade_to(self.opacity_pct / 100.0)
        super().leaveEvent(event)

    # System Tray & Lock helper methods
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.setToolTip("Assistive Window Switcher")

        SLIDER_SS = """
            QSlider::groove:horizontal {
                height: 4px; background: #374151; border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #00d2ff; border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff; width: 12px; height: 12px;
                margin: -4px 0; border-radius: 6px;
            }
        """

        # Context Menu (styled identically to captureME)
        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet("""
            QMenu {
                background-color: #1e222b;
                color: #e1e4ea;
                border: 1px solid #3a4253;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #2c3444;
                color: #00d2ff;
            }
            QMenu::separator {
                height: 1px;
                background: #3a4253;
                margin: 4px 6px;
            }
        """)

        # Actions (matching captureME tray layout)
        self.action_ontop = QAction("Always on Top", self, checkable=True)
        self.action_ontop.setChecked(True)
        self.action_ontop.triggered.connect(self.toggle_always_on_top)
        self.tray_menu.addAction(self.action_ontop)

        self.action_lock = QAction("Lock Position", self, checkable=True)
        self.action_lock.setChecked(self.is_locked)
        self.action_lock.triggered.connect(lambda: self.toggle_lock())
        self.tray_menu.addAction(self.action_lock)

        self.action_fly = QAction("Fly Mode (Follow Cursor)", self, checkable=True)
        self.action_fly.setChecked(self.is_fly_mode)
        self.action_fly.triggered.connect(lambda: self.toggle_fly_mode())
        self.tray_menu.addAction(self.action_fly)

        startup_label = "Start with Windows" if IS_WINDOWS else "Start at Login"
        self.startup_action = QAction(startup_label, self, checkable=True)
        self.startup_action.setChecked(is_run_at_startup())
        self.startup_action.triggered.connect(self.toggle_startup)
        self.tray_menu.addAction(self.startup_action)

        self.tray_menu.addSeparator()

        # --- App Opacity Slider ---
        self.op_container = QWidget()
        op_layout = QHBoxLayout(self.op_container)
        op_layout.setContentsMargins(12, 4, 12, 4)
        op_title = QLabel("App Opacity:")
        op_title.setStyleSheet("color: #d1d5db; font-size: 11px; font-weight: bold;")
        self.op_val_label = QLabel(f"{self.opacity_pct}%")
        self.op_val_label.setStyleSheet("color: #00d2ff; font-size: 11px; font-weight: bold;")
        self.op_slider = QSlider(Qt.Horizontal)
        self.op_slider.setRange(0, 100)
        self.op_slider.setValue(self.opacity_pct)
        self.op_slider.setFixedWidth(100)
        self.op_slider.setStyleSheet(SLIDER_SS)
        self.op_slider.valueChanged.connect(self.on_opacity_slider_changed)
        op_layout.addWidget(op_title)
        op_layout.addWidget(self.op_slider)
        op_layout.addWidget(self.op_val_label)
        op_action = QWidgetAction(self)
        op_action.setDefaultWidget(self.op_container)
        self.tray_menu.addAction(op_action)

        # --- Size Slider ---
        self.sz_container = QWidget()
        sz_layout = QHBoxLayout(self.sz_container)
        sz_layout.setContentsMargins(12, 4, 12, 4)
        sz_title = QLabel("Size:")
        sz_title.setStyleSheet("color: #d1d5db; font-size: 11px; font-weight: bold;")
        self.sz_val_label = QLabel(f"{self.size_pct}%")
        self.sz_val_label.setStyleSheet("color: #00d2ff; font-size: 11px; font-weight: bold;")
        self.sz_slider = QSlider(Qt.Horizontal)
        self.sz_slider.setRange(0, 100)
        self.sz_slider.setValue(self.size_pct)
        self.sz_slider.setFixedWidth(100)
        self.sz_slider.setStyleSheet(SLIDER_SS)
        self.sz_slider.valueChanged.connect(self.on_size_slider_changed)
        sz_layout.addWidget(sz_title)
        sz_layout.addWidget(self.sz_slider)
        sz_layout.addWidget(self.sz_val_label)
        sz_action = QWidgetAction(self)
        sz_action.setDefaultWidget(self.sz_container)
        self.tray_menu.addAction(sz_action)

        self.tray_menu.addSeparator()

        # Action to close
        close_action = QAction("Close Switcher", self)
        close_action.triggered.connect(QApplication.quit)
        self.tray_menu.addAction(close_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def toggle_always_on_top(self, checked):
        flags = Qt.FramelessWindowHint | Qt.Tool | Qt.SubWindow | Qt.WindowDoesNotAcceptFocus
        if checked:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def on_opacity_slider_changed(self, value):
        self.opacity_pct = value
        if hasattr(self, "op_val_label"):
            self.op_val_label.setText(f"{value}%")
        self.setWindowOpacity(value / 100.0)

    def on_size_slider_changed(self, value):
        self.size_pct = value
        if hasattr(self, "sz_val_label"):
            self.sz_val_label.setText(f"{value}%")
        # 0% -> 32px, 100% -> 88px
        new_size = int(32 + (56 * (value / 100.0)))
        self.button.OUTER_R = max(10, int(new_size * 0.464))
        self.button.INNER_R = max(4,  int(new_size * 0.196))
        self.button.WIDGET_SIZE = new_size
        self.button.setFixedSize(new_size, new_size)
        self.setFixedSize(new_size, new_size)
        self.button.update()

    def toggle_startup(self, checked):
        success = set_run_at_startup(checked)
        if not success:
            self.startup_action.setChecked(not checked)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.AltModifier:
                print("[Action] Alt+Left click on tray icon. Closing switcher.")
                QApplication.quit()
            elif modifiers & Qt.ShiftModifier:
                self.toggle_lock()
            else:
                if self.isVisible():
                    self.hide()
                    print("[Tray] Hidden switcher widget.")
                else:
                    self.show()
                    self.raise_()
                    self.activateWindow()
                    print("[Tray] Shown and activated switcher widget.")

    def toggle_lock(self):
        if self.is_fly_mode:
            self.is_fly_mode = False
            self.fly_timer.stop()
            if self.saved_position:
                self.move(self.saved_position)

        self.is_locked = not self.is_locked
        self.update_button_style()
        if self.is_locked:
            print("[Lock] Position locked.")
            self.button.setToolTip("Assistive Window Switcher (LOCKED)\n- Shift + Left Click: Unlock position")
            self.button.setCursor(Qt.ArrowCursor)
            self.tray_icon.showMessage("Switcher Locked", "Widget position is locked.", QSystemTrayIcon.Information, 2000)
        else:
            print("[Lock] Position unlocked.")
            self.button.setToolTip("Assistive Window Switcher\n- Left Click: Switch Window\n- Drag: Move Widget\n- Alt + Left Click: Close\n- Shift + Left Click: Lock position")
            self.button.setCursor(Qt.SizeAllCursor)
            self.tray_icon.showMessage("Switcher Unlocked", "Widget position is unlocked.", QSystemTrayIcon.Information, 2000)

    def update_button_style(self):
        if self.is_locked:
            self.button.setToolTip("Assistive Window Switcher (LOCKED)\n- Shift + Left Click: Unlock position")
            self.button.setCursor(Qt.ArrowCursor)
        elif self.is_fly_mode:
            self.button.setToolTip("Assistive Window Switcher (FLY MODE)\n- Middle Click (anywhere): Switch Window\n- Ctrl + Left Click: Exit Fly Mode")
            self.button.setCursor(Qt.SizeAllCursor)
        else:
            self.button.setToolTip("Assistive Window Switcher\n- Left Click: Switch Window\n- Drag: Move Widget\n- Alt + Left Click: Close\n- Shift + Left Click: Lock position")
            self.button.setCursor(Qt.SizeAllCursor)
        self.button.update()

    def toggle_fly_mode(self):
        if self.is_locked:
            self.tray_icon.showMessage("Cannot Enable Fly Mode", "Unlock position first.", QSystemTrayIcon.Warning, 2000)
            return

        self.is_fly_mode = not self.is_fly_mode
        self.update_button_style()

        if self.is_fly_mode:
            print("[Fly Mode] Enabled.")
            self.saved_position = self.pos()
            self.button.setToolTip("Assistive Window Switcher (FLY MODE)\n- Middle Click (anywhere): Switch Window\n- Ctrl + Left Click: Exit Fly Mode")
            self.button.setCursor(Qt.SizeAllCursor)
            self.fly_timer.start(16)  # ~60 FPS
            self.tray_icon.showMessage("Fly Mode Enabled", "Widget follows cursor. Middle click anywhere to switch windows.", QSystemTrayIcon.Information, 2000)
        else:
            print("[Fly Mode] Disabled.")
            self.fly_timer.stop()
            if self.saved_position:
                self.move(self.saved_position)
            self.button.setToolTip("Assistive Window Switcher\n- Left Click: Switch Window\n- Drag: Move Widget\n- Alt + Left Click: Close\n- Shift + Left Click: Lock position")
            self.tray_icon.showMessage("Fly Mode Disabled", "Widget returned to normal dock position.", QSystemTrayIcon.Information, 2000)

    def update_fly_position(self):
        pos = QCursor.pos()
        target_x = pos.x() + 20
        target_y = pos.y() + 20
        
        # Keep widget within screen boundary
        screen = QApplication.primaryScreen().geometry()
        if target_x + self.width() > screen.right():
            target_x = pos.x() - self.width() - 20
        if target_y + self.height() > screen.bottom():
            target_y = pos.y() - self.height() - 20
            
        self.move(target_x, target_y)

    def on_global_middle_click(self):
        if self.is_fly_mode and self.isVisible():
            print("[Action] Global Middle click detected in Fly Mode. Switching window.")
            self.quick_switch()
            return True  # Swallow click
        return False  # Pass through

    def closeEvent(self, event):
        if self.mouse_hook:
            self.mouse_hook.uninstall()
        super().closeEvent(event)

    def __del__(self):
        if hasattr(self, "mouse_hook") and self.mouse_hook:
            try:
                self.mouse_hook.uninstall()
            except Exception:
                pass

# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------
if __name__ == "__main__":
    log_path = os.path.join(os.path.expanduser("~"), "switcher_error.log")
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        switcher = AssistiveSwitcherWidget()
        
        # Place widget in bottom-right corner of screen initially
        screen_rect = QApplication.primaryScreen().geometry()
        init_x = screen_rect.width() - 80
        init_y = screen_rect.height() - 180
        switcher.move(init_x, init_y)
        
        switcher.show()
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        with open(log_path, "w") as f:
            f.write(traceback.format_exc())
        raise e
