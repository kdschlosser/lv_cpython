try:
    import lvgl as lv
except ImportError:
    import os
    import sys

    base_path = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

    import lvgl as lv

import time

lv.init()
disp = lv.sdl_window_create(480, 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


def slider_event_cb(e):
    slider = lv.event_get_target_obj(e)

    # Refresh the text
    lv.label_set_text(label, str(lv.slider_get_value(slider)))


# Create a slider in the center of the display
slider = lv.slider_create(lv.scr_act())
lv.obj_set_width(slider, 200)
lv.obj_center(slider)
lv.obj_add_event(slider, slider_event_cb, lv.EVENT_VALUE_CHANGED)

# Create a label above the slider
label = lv.label_create(lv.scr_act())
lv.label_set_text(label, "0")
lv.obj_align_to(label, slider, lv.ALIGN_OUT_TOP_MID, 0, -15)


start = time.time()

while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
