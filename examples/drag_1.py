import os
import sys

base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..')))

import lvgl as lv

import time

lv.init()
disp = lv.sdl_window_create(420, 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


def drag_event_handler(e):
    indev = lv.indev_get_act()

    vect = lv.point_t()
    lv.indev_get_vect(indev, vect)
    x = lv.obj_get_x(obj) + vect.x
    y = lv.obj_get_y(obj) + vect.y
    lv.obj_set_pos(obj, x, y)


#
# Make an object dragable.
#
screen = lv.scr_act()
obj = lv.obj_create(screen)

lv.obj_set_size(obj, 150, 100)
lv.obj_add_event(obj, drag_event_handler, lv.EVENT_PRESSING, None)

label = lv.label_create(obj)
lv.label_set_text(label, "Drag me")
lv.obj_center(label)
start = time.time()

while True:
    time.sleep(0.001)
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    start = stop
    lv.tick_inc(diff)
    lv.task_handler()
