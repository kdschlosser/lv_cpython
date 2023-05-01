import lvgl as lv
import _lib_lvgl
import wx
import threading
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
        color_buf = bytearray(size * 3)
        alpha_buf = bytearray(size)

        for i in range(size):
            c = px_map[i]
            j = i * 3
            color_buf[j] = c.red
            color_buf[j + 1] = c.green
            color_buf[j + 2] = c.blue
            alpha_buf[i] = c.alpha

        img = wx.Image(width, height, color_buf)
        img.SetAlpha(alpha_buf)
        bmp = img.ConvertToBitmap()
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


def run():
    lv.init()
    print('LVGL initilized')

    disp = lv.disp_create(480, 320)
    lv.disp_set_flush_cb(disp, _lib_lvgl.lib.py_lv_disp_flush_cb_t)

    flush_cb_t = lv.disp_flush_cb_t(frame.flush_lvgl)
    lv.disp_set_flush_cb(disp, flush_cb_t)

    _buf1 = _lib_lvgl.ffi.new('lv_color_t[{0}]'.format(100 * 100))

    lv.disp_set_draw_buffers(
        disp,
        _buf1,
        lv.NULL,
        100 * 100,
        lv.DISP_RENDER_MODE_PARTIAL
        )

    group = lv.group_create()
    lv.group_set_default(group)

    mouse = lv.indev_create()
    lv.indev_set_type(mouse, lv.INDEV_TYPE_POINTER)

    mouse_cb_t = lv.lv_indev_read_cb_t(mouse_cb)

    mouse_userdata = _lib_lvgl.ffi.new_handle(mouse_cb)
    mouse.user_data = mouse_userdata

    lv.indev_set_read_cb(mouse, mouse_cb_t)

    keyboard = lv.indev_create()
    lv.indev_set_type(keyboard, lv.INDEV_TYPE_KEYPAD)
    keyboard_cb_t = lv.lv_indev_read_cb_t(keyboard_cb)

    lv.indev_set_read_cb(keyboard, keyboard_cb_t)

    lv.indev_set_group(keyboard, group)

    screen = lv.scr_act()

    btn = lv.btn_create(screen)

    lv.obj_set_size(btn, 150, 75)
    lv.obj_center(btn)

    label = lv.label_create(btn)
    lv.label_set_text(label, "Button")
    lv.obj_center(label)

    while True:
        wpt.sleep(0.001)
        lv.tick_inc(1)
        lv.task_handler()


t = threading.Thread(target=run)
t.daemon = True
t.start()

app.MainLoop()
