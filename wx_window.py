import lvgl as lv
import _lib_lvgl
import wx
import threading
import math
import win_precise_time as wpt


class Frame(wx.Frame):

    def __init__(self):

        wx.Frame.__init__(self, None, -1)

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

        self.Show()

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
        indev_data.key = self.key

    def get_mouse_state(self, indev_data):
        indev_data.state = self.state
        indev_data.point.x = self.mouse_point.x
        indev_data.point.y = self.mouse_point.y

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
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1
        size = width * height


        px_data = _lib_lvgl.ffi.cast('uint8_t[{0}]'.format(size * 4), px_map)
        dbuf = _lib_lvgl.ffi.buffer(px_data)[:]

        bmp = wx.Bitmap(width, height)
        bmp.CopyFromBuffer(dbuf, wx.BitmapBufferFormat_RGBA)
        dc = wx.ClientDC(self)
        dc.DrawBitmap(bmp, area.x1, area.y1)
        dc.Destroy()
        del dc

        lv.disp_flush_ready(disp)


app = wx.App()
frame = Frame()


def keyboard_cb(_, data):
    frame.get_keyboard_state(data)


def mouse_cb(_, data):
    frame.get_mouse_state(data)


# this is a python version of lv_point_t.
# a structure will need to be made to represent this class.
# This version accepts float values which is needed for the circle math.
# there is a function that converts this point into lv_point_t
class PyPoint:

    def __init__(self, x, y):
        self.x = x
        self.y = y


# function to convery point structure that holds float values to lv_point_t
def py_point_to_lv_point(py_point):
    return lv.point_t(x=int(py_point.x), y=int(py_point.y))


# remap a value from one value range to another value range. This function accepts floats as the inputs and returns a float
def float_remap(value, old_min, old_max, new_min, new_max):
        return ((float(value - old_min) * float(new_max - new_min)) / float(old_max - old_min)) + new_min


# same thing as above except it returns an integer
def int_remap(value, old_min, old_max, new_min, new_max):
    return int(float_remap(value, old_min, old_max, new_min, new_max))


# *** circle math ***
pi2 = 2.0 * math.pi


class Ellipse:

    def __init__(
            self,
            x,
            y,
            radius_horizontal,
            radius_vertical
    ):
        self.x = x
        self.y = y
        self.radius_horizontal = radius_horizontal
        self.radius_vertical = radius_vertical


def get_ellipse_center(ellipse: Ellipse) -> PyPoint:
        return PyPoint(ellipse.x, ellipse.y)


def get_ellipse_angle_from_point(ellipse: Ellipse, point: PyPoint) -> float:
    return math.degrees(math.atan2(ellipse.y - point.y, ellipse.x - point.x)) + 180


def get_ellipse_point_from_angle(ellipse: Ellipse, degrees: float) -> PyPoint:
    rh = ellipse.radius_horizontal
    rv = ellipse.radius_vertical
    x = ellipse.x
    y = ellipse.y

    ang = math.radians(degrees)
    cos = math.cos(ang)  # axis direction at angle ang
    sin = math.sin(ang)
    aa = x * x
    bb = y * y  # intersection between ellipse and axis
    t = aa * bb / ((cos * cos * bb) + (sin * sin * aa))
    cos *= t
    sin *= t
    sin *= x / y  # convert to circle
    ea = math.atan2(sin, cos)  # compute elliptic angle
    if ea < 0.0:
        ea += pi2  # normalize to <0,pi2>

    cos = math.cos(ea)
    sin = math.sin(ea)
    ta = sin / cos  # tan(a)
    tt = ta * rh / rv  # tan(t)
    d = 1.0 / math.sqrt(1.0 + tt * tt)
    x += math.copysign(rh * d, cos)
    y += math.copysign(rv * tt * d, sin)
    return PyPoint(x, y)


def ellipse_contains_point(ellipse: Ellipse, point: PyPoint) -> bool:
        # checking the equation of
        # ellipse with the given point
        p = (
                (((point.x - ellipse.x) ** 2) / (
                        ellipse.radius_horizontal ** 2)) +
                (((point.y - ellipse.y) ** 2) / (ellipse.radius_vertical ** 2))
        )

        return p > 1


def get_distance(point1: PyPoint, point2: PyPoint) -> int:
    return math.sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)



class ellipse_dsc_t:

    def __init__(self, color: "lv_color_t", width: "lv_coord_t", start_angle: "uint16_t", end_angle: "uint16_t", img_src: "void*:, opa: uint8_t, blend_mode: "lv_blend_mode_t",  rounded: "int8_t"):   
    
"""
typedef struct {
    lv_color_t color;
    lv_coord_t width;
    uint16_t start_angle;
    uint16_t end_angle;
    const void * img_src;
    lv_opa_t opa;
    lv_blend_mode_t blend_mode  : 2;
    uint8_t rounded : 1;
} lv_draw_arc_dsc_t;"""

def render_ellipse(ctx, ellipse: Ellipse, color: "lv_color_t", width: "uint16_t"):
    point = get_ellipse_center(ellipse)
    radius = min(ellipse.radius_vertical, ellipse.radius_horizontal)

    ellipse_dsc = lv.draw_arc_dsc_t()
    lv.draw_arc_dsc_init(ellipse_dsc)

    ellipse_dsc.start_angle = 0
    ellipse_dsc.end_angle = 3590

    ellipse_dsc.color.red = color.red
    ellipse_dsc.green.red = color.green
    ellipse_dsc.color.blue = color.blue
    ellipse_dsc.opa = color.alpha
    ellipse_dsc.width = width


# draw_line_dsc_t create_separator(lv_color_t color, lv_opa_t opa, lv_coord_t width);
def create_separator(color, opa, width):
    separator_dsc = lv.draw_line_dsc_t()
    lv.draw_line_dsc_init(separator_dsc)

    separator_dsc.color = color
    separator_dsc.width = width
    separator_dsc.opa = opa
    separator_dsc.round_start = False
    separator_dsc.round_end = False

    return separator_dsc


separator1_dsc = create_separator(lv.color_hex(0xFF0000), 125, 3)
separator2_dsc = create_separator(lv.color_hex(0x00FF00), 125, 3)
separator3_dsc = create_separator(lv.color_hex(0x0000FF), 125, 3)


class meter_phase:

    def __init__(self, amps_value=0, volts_value=0):
        self.amps_value = amps_value
        self.volts_value = volts_value


class meter_gauge:

    def __init__(self, ):




    293









def gui(screen):










def run():
    lv.init()
    print('LVGL initilized')

    disp = lv.disp_create(480, 320)
    lv.disp_set_flush_cb(disp, _lib_lvgl.lib.py_lv_disp_flush_cb_t)

    flush_cb_t = lv.disp_flush_cb_t(frame.flush_lvgl)
    lv.disp_set_flush_cb(disp, flush_cb_t)

    _buf1 = _lib_lvgl.ffi.new('lv_color_t[{0}]'.format(100 * 100))

    lv.disp_set_draw_buffers(disp, _buf1,  lv.NULL, 100 * 100, lv.DISP_RENDER_MODE_PARTIAL)

    group = lv.group_create()
    lv.group_set_default(group)

    mouse = lv.indev_create()
    lv.indev_set_type(mouse, lv.INDEV_TYPE_POINTER)
    mouse_cb_t = lv.indev_read_cb_t(mouse_cb)
    lv.indev_set_read_cb(mouse, mouse_cb_t)
    lv.timer_set_period(mouse.read_timer, 1)

    keyboard = lv.indev_create()
    lv.indev_set_type(keyboard, lv.INDEV_TYPE_KEYPAD)
    keyboard_cb_t = lv.indev_read_cb_t(keyboard_cb)
    lv.indev_set_read_cb(keyboard, keyboard_cb_t)
    lv.timer_set_period(keyboard.read_timer, 1)

    lv.indev_set_group(keyboard, group)

    screen = lv.scr_act()

    btn = lv.btn_create(screen)

    lv.obj_set_size(btn, 150, 100)
    lv.obj_center(btn)

    import time

    start = time.time()

    while True:
        stop = time.time()
        diff = int((stop * 1000) - (start * 1000))
        if diff >= 5:
            start = stop
            lv.refr_now(disp)
            lv.tick_inc(diff)
            lv.task_handler()
        else:
            wpt.sleep(0.005 - (diff / 1000))


t = threading.Thread(target=run)
t.daemon = True
t.start()

app.MainLoop()
