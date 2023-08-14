import sys
import os


base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

import lvgl as lv

import wx
import threading
import ctypes
import time


from ctypes.wintypes import LONG, HWND, INT, HDC, HGDIOBJ, BOOL, DWORD


UBYTE = ctypes.c_ubyte
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
ULW_ALPHA = 0x00000002
AC_SRC_OVER = 0x00000000
AC_SRC_ALPHA = 0x00000001
WS_POPUP = 0x80000000


class POINT(ctypes.Structure):
    _fields_ = [
        ('x', LONG),
        ('y', LONG)
    ]


class SIZE(ctypes.Structure):
    _fields_ = [
        ('cx', LONG),
        ('cy', LONG)
    ]


class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [
        ('BlendOp', UBYTE),
        ('BlendFlags', UBYTE),
        ('SourceConstantAlpha', UBYTE),
        ('AlphaFormat', UBYTE)
    ]


user32 = ctypes.windll.User32
gdi32 = ctypes.windll.Gdi32

# LONG GetWindowLongW(
#   HWND hWnd,
#   int  nIndex
# )

GetWindowLongW = user32.GetWindowLongW
GetWindowLongW.restype = LONG

# LONG SetWindowLongW(
#   HWND hWnd,
#   int  nIndex,
#   LONG dwNewLong
# );
SetWindowLongW = user32.SetWindowLongW
SetWindowLongW.restype = LONG

# HDC GetDC(
#   HWND hWnd
# );
GetDC = user32.GetDC
GetDC.restype = HDC

# HWND GetDesktopWindow();
GetDesktopWindow = user32.GetDesktopWindow
GetDesktopWindow.restype = HWND

# HDC CreateCompatibleDC(
#   HDC hdc
# );
CreateCompatibleDC = gdi32.CreateCompatibleDC
CreateCompatibleDC.restype = HDC

# HGDIOBJ SelectObject(
#   HDC     hdc,
#   HGDIOBJ h
# );
SelectObject = gdi32.SelectObject
SelectObject.restype = HGDIOBJ

# BOOL UpdateLayeredWindow(
#   HWND          hWnd,
#   HDC           hdcDst,
#   POINT         *pptDst,
#   SIZE          *psize,
#   HDC           hdcSrc,
#   POINT         *pptSrc,
#   COLORREF      crKey,
#   BLENDFUNCTION *pblend,
#   DWORD         dwFlags
# );
UpdateLayeredWindow = user32.UpdateLayeredWindow
UpdateLayeredWindow.restype = BOOL


DeleteDC = gdi32.DeleteDC
DeleteDC.restype = BOOL


ReleaseDC = user32.ReleaseDC
ReleaseDC.restype = BOOL


COLORREF = DWORD


def RGB(r, g, b):
    return COLORREF(r | (g << 8) | (b << 16))


class Frame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(
            self,
            None,
            -1,
            style=(
                wx.FRAME_SHAPED |
                wx.NO_BORDER |
                wx.FRAME_NO_TASKBAR |
                wx.STAY_ON_TOP
            )
        )
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetClientSize((480, 320))

        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

        self.key = 0
        self.mouse_point = lv.point_t()
        self.mouse_point.x = 0
        self.mouse_point.y = 0
        self.state = lv.INDEV_STATE_RELEASED
        self.key_state = lv.INDEV_STATE_RELEASED
        self.count = 0
        self.start = time.time()
        self.Show()

    def OnPaint(self, evt):
        pass

    def draw_alpha(self, bmp):
        hndl = self.GetHandle()
        style = GetWindowLongW(HWND(hndl), INT(GWL_EXSTYLE))
        SetWindowLongW(HWND(hndl), INT(GWL_EXSTYLE), LONG(style | WS_EX_LAYERED))

        hdcDst = GetDC(None)
        hdcSrc = CreateCompatibleDC(HDC(hdcDst))

        pptDst = POINT(*self.GetPosition())
        psize = SIZE(*self.GetClientSize())
        pptSrc = POINT(0, 0)
        crKey = RGB(0, 0, 0)

        pblend = BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)
        hbmpOld = SelectObject(HDC(hdcSrc), HGDIOBJ(bmp.GetHandle()))
        UpdateLayeredWindow(
            HWND(hndl),
            HDC(hdcDst),
            ctypes.byref(pptDst),
            ctypes.byref(psize),
            HDC(hdcSrc),
            ctypes.byref(pptSrc),
            crKey,
            ctypes.byref(pblend),
            DWORD(ULW_ALPHA)
        )
        SelectObject(HDC(hdcSrc), HWND(hbmpOld))
        DeleteDC(HDC(hdcSrc))
        ReleaseDC(None, HDC(hdcDst))

        bmp.Destroy()
        del bmp

    def on_key_down(self, evt):
        key = evt.GetUnicodeKey()
        if key == wx.WXK_NONE:
            key = evt.GetKeyCode()
            mapping = {
                wx.WXK_ESCAPE: wx.WXK_ESCAPE,
                wx.WXK_DELETE: wx.WXK_DELETE,
                wx.WXK_NUMPAD_DELETE: wx.WXK_DELETE,
                wx.WXK_BACK: wx.WXK_BACK,
                wx.WXK_NUMPAD_DOWN: 18,
                wx.WXK_DOWN: 18,
                wx.WXK_NUMPAD_LEFT: 20,
                wx.WXK_LEFT: 20,
                wx.WXK_NUMPAD_RIGHT: 19,
                wx.WXK_RIGHT: 19,
                wx.WXK_NUMPAD_UP: 17,
                wx.WXK_UP: 17,
                wx.WXK_NUMPAD_ENTER: 10,
                wx.WXK_RETURN: 10,
                wx.WXK_NUMPAD_HOME: 2,
                wx.WXK_HOME: 2,
                wx.WXK_NUMPAD_END: 3,
                wx.WXK_END: 3,
                wx.WXK_MEDIA_NEXT_TRACK: 9,
                wx.WXK_TAB: 9,
                wx.WXK_NUMPAD_TAB: 9,
                wx.WXK_PAGEUP: 9,
                wx.WXK_MEDIA_PREV_TRACK: 11,
                wx.WXK_PAGEDOWN: 11,
                wx.WXK_NUMPAD0: ord('0'),
                wx.WXK_NUMPAD1: ord('1'),
                wx.WXK_NUMPAD2: ord('2'),
                wx.WXK_NUMPAD3: ord('3'),
                wx.WXK_NUMPAD4: ord('4'),
                wx.WXK_NUMPAD5: ord('5'),
                wx.WXK_NUMPAD6: ord('6'),
                wx.WXK_NUMPAD7: ord('7'),
                wx.WXK_NUMPAD8: ord('8'),
                wx.WXK_NUMPAD9: ord('9'),
                wx.WXK_NUMPAD_ADD: ord('+'),
                wx.WXK_NUMPAD_DECIMAL: ord('.'),
                wx.WXK_NUMPAD_DIVIDE: ord('/'),
                wx.WXK_NUMPAD_EQUAL: ord('='),
                wx.WXK_NUMPAD_MULTIPLY: ord('*'),
                wx.WXK_NUMPAD_SEPARATOR: ord('|'),
                wx.WXK_NUMPAD_SPACE: ord(' '),
                wx.WXK_NUMPAD_SUBTRACT: ord('-'),
            }

            self.key = mapping.get(key, 0)

        else:
            self.key = int(key)

        if self.key != 0:
            self.key_state = lv.INDEV_STATE_PRESSED
        else:
            self.key_state = lv.INDEV_STATE_RELEASED

        evt.Skip()

    def on_key_up(self, evt):
        self.key = 0
        self.key_state = lv.INDEV_STATE_RELEASED
        evt.Skip()

    def get_keyboard_state(self, indev_data):
        indev_data.contents.key = self.key

    def get_mouse_state(self, indev_data):
        indev_data.state = self.state
        indev_data.contents.point.x = self.mouse_point.x
        indev_data.contents.point.y = self.mouse_point.y

    def on_mouse_leave(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
            self.state = lv.INDEV_STATE_RELEASED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

        evt.Skip()

    def on_mouse_move(self, evt):
        if self.HasCapture():
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

    def on_left_up(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
            self.state = lv.INDEV_STATE_RELEASED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

        evt.Skip()

    def on_left_down(self, evt):
        if not self.HasCapture():
            self.CaptureMouse()
            self.state = lv.INDEV_STATE_PRESSED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

        evt.Skip()

    def flush_lvgl(self, disp, area, px_map):
        print('mouse cb')

        import ctypes
        width = area.contents.x2 - area.contents.x1 + 1
        height = area.contents.y2 - area.contents.y1 + 1
        size = width * height * lv.color_t.__SIZE__

        array = ctypes.cast(px_map, ctypes.POINTER((ctypes.c_ubyte * size))).contents
        array = bytes(array)
        bmp = wx.Bitmap.FromBufferRGBA(width, height, array)
        # wx.Bitmap(width, height)
        # bmp.CopyFromBuffer(array, wx.BitmapBufferFormat_RGBA)
        self.draw_alpha(bmp)

        lv.disp_flush_ready(disp)

        self.count += 1

        if not self.count % 300:
            stop = time.time()
            diff = (stop * 1000) - (self.start * 1000)
            print(1 / (diff / 300 / 1000))
            self.count = 0
            self.start = time.time()


app = wx.App()
frame = Frame()


def keyboard_cb(_, data):
    frame.get_keyboard_state(data)


upper right parcel
bottom left = 39.53382474892872, -105.3435258056878
top left = 39.5367372373607, -105.34203003819114
top right = 39.53668860973968, -105.33516342992291
bottom right = 39.53018430548781, -105.33540103617521
bottom right (bottom left) = 39.53005748158588, -105.33955912359458
bottom right (top left) = 39.53380261120658, -105.33877798271865


main parcel

8480
bottom right = 39.52274736578246, -105.34300684236187
top left = 39.53711983758532, -105.35140904936372
bottom left = 39.52247771473773, -105.35079501656158
0.01464212284759, 0.00061403280214

L corner = 39.5335264900994, -105.34730736296096
top right = 39.5370647139351, -105.34695906521614
L outside = 39.53382474892872, -105.3435258056878

height, width




6214, 7101


9040 = 666

8960=888

8080=101010


8760=131313
8640=161616
8480=202020

9240
219, 6941
341, 7074

9200
89, 4352
301, 4552
365, 4700
379, 4827
311, 4929
117, 5013
198, 6551
351, 6761
552, 6916
666, 7064



9160
74, 4125
363, 4339
583, 4820
488, 5081
141, 5298
153, 5821
212, 6077
481, 5623
599, 6580
904, 7044


9120



def mouse_cb(_, data):
    frame.get_mouse_state(data)


def run():
    lv.init()

    disp = lv.disp_create(800, 600)

    lv.disp_set_flush_cb(disp, frame.flush_lvgl)
    lv.disp_set_color_format(disp, lv.COLOR_FORMAT_XRGB8888)
    _buf1 = (lv.color_t * (801 * 601))()
    # _buf2 = (lv.color_t * (800 * 600))()
    lv.disp_set_draw_buffers(disp, _buf1,  None, 801 * 601, lv.DISP_RENDER_MODE_FULL)

    group = lv.group_create()
    lv.group_set_default(group)

    mouse = lv.indev_create()
    lv.indev_set_type(mouse, lv.INDEV_TYPE_POINTER)
    lv.indev_set_read_cb(mouse, mouse_cb)
    lv.timer_set_period(mouse.read_timer, 1)

    keyboard = lv.indev_create()
    lv.indev_set_type(keyboard, lv.INDEV_TYPE_KEYPAD)
    lv.indev_set_read_cb(keyboard, keyboard_cb)
    lv.timer_set_period(keyboard.read_timer, 1)

    lv.indev_set_group(keyboard, group)

    screen = lv.scr_act()
    lv.obj_set_style_bg_color(screen, lv.color_hex(0x000000), 0)

    def value_changed_event_cb(e, label):

        txt = "{:d}%".format(lv.arc_get_value(arc))
        lv.label_set_text(label, txt)

        # Rotate the label to the current position of the arc
        lv.arc_rotate_obj_to_angle(arc, label, 50)

    label = lv.label_create(screen)
    lv.obj_set_style_text_color(label, lv.color_hex(0x00FF00), 0)

    # lv.obj_set_style_text_font(label, lv.font_montserrat_24, 0)

    # Create an Arc
    arc = lv.arc_create(screen)
    lv.obj_set_style_arc_color(arc, lv.color_hex(0xFF0000), lv.PART_INDICATOR)
    lv.obj_set_size(arc, 200, 200)
    lv.obj_set_style_arc_width(arc, 30, 0)
    lv.obj_set_style_arc_width(arc, 30, lv.PART_INDICATOR)
    lv.arc_set_rotation(arc, 135)
    lv.arc_set_bg_angles(arc, 0, 270)
    lv.arc_set_value(arc, 0)
    lv.obj_center(arc)
    lv.obj_add_event(
        arc,
        lambda e: value_changed_event_cb(e, label),
        lv.EVENT_VALUE_CHANGED,
        None
    )

    # Manually update the label for the first time
    lv.obj_send_event(arc, lv.EVENT_VALUE_CHANGED, None)

    val = 0
    inc = 1

    import time

    while True:
        time.sleep(0.0001)
        val += inc

        if val in (0, 100):
            inc = -inc

        lv.arc_set_value(arc, val)
        lv.obj_send_event(arc, lv.EVENT_VALUE_CHANGED, None)

        lv.tick_inc(1)
        lv.task_handler()


t = threading.Thread(target=run)
t.daemon = True
t.start()

app.MainLoop()
