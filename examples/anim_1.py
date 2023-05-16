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


def anim_x(a, v):
    lv.obj_set_x(label, v)


anim = None


def sw_event_cb(e, label):
    global anim
    sw = lv.event_get_target_obj(e)

    anim = lv.anim_t()
    lv.anim_init(anim)
    lv.anim_set_var(anim, label)
    lv.anim_set_time(anim, 500)

    if lv.obj_has_state(sw, lv.STATE_CHECKED):
        lv.anim_set_values(anim, lv.obj_get_x(label), 100)
        lv.anim_set_path_cb(anim, lv.anim_path_overshoot)
    else:
        lv.anim_set_values(anim, lv.obj_get_x(label), -lv.obj_get_width(label))
        lv.anim_set_path_cb(anim, lv.anim_path_ease_in)

    lv.anim_set_custom_exec_cb(anim, anim_x)
    lv.anim_start(anim)


label = lv.label_create(lv.scr_act())
lv.label_set_text(label, "Hello animations!")
lv.obj_set_pos(label, 100, 10)


sw = lv.switch_create(lv.scr_act())
lv.obj_center(sw)
lv.obj_add_state(sw, lv.STATE_CHECKED)
lv.obj_add_event(sw, lambda e: sw_event_cb(e, label), lv.EVENT_VALUE_CHANGED)


start = time.time()

while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
