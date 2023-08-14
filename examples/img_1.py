import os
import sys
import time

try:
    base_path = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..')))

    import lvgl as lv

    lv.init()

except (ImportError, AttributeError):
    sys.path.pop(0)

    import lvgl as lv

    lv.init()


disp = lv.sdl_window_create(800, 600)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


# Using the Image style properties

with open('assets/logo.png', 'rb') as f:
    img_data = f.read()

img_dsc = lv.img_dsc_t()
img_dsc.data = img_data
img_dsc.data_size = len(img_data)

# Create an object with the new style
obj = lv.img_create(lv.scr_act())
lv.obj_set_size(obj, 400, 400)

lv.obj_set_style_transform_pivot_x(obj, 200, 0)
lv.obj_set_style_transform_pivot_y(obj, 200, 0)
lv.obj_set_style_transform_angle(obj, 450, 0)
lv.img_set_src(obj, img_dsc)
lv.obj_center(obj)


while True:
    time.sleep(0.001)
    lv.tick_inc(1)
    lv.task_handler()
