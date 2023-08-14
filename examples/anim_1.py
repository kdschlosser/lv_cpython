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


disp = lv.sdl_window_create(lv.coord_t(480), 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


def anim_x(a, v):
    lv.obj_set_x(label, v)


def sw_event_cb(e):
    sw = lv.event_get_target_obj(e)

    a = lv.anim_t()
    lv.anim_init(a)
    lv.anim_set_var(a, label)
    lv.anim_set_time(a, 500)

    if lv.obj_has_state(sw, lv.STATE_CHECKED):
        lv.anim_set_values(a, lv.obj_get_x(label), 100)
        lv.anim_set_path_cb(a, lv.anim_path_overshoot)
    else:
        print('WIDTH:', -lv.obj_get_width(label))
        lv.anim_set_values(a, lv.obj_get_x(label), - lv.obj_get_width(label))
        lv.anim_set_path_cb(a, lv.anim_path_ease_in)

    lv.anim_set_custom_exec_cb(a, anim_x)
    lv.anim_start(a)


label = lv.label_create(lv.scr_act())

lv.label_set_text(label, "Hello animations!")
lv.obj_set_pos(label, 100, 10)

sw = lv.switch_create(lv.scr_act())
lv.obj_center(sw)
lv.obj_add_state(sw, lv.STATE_CHECKED)
lv.obj_add_event(sw, sw_event_cb, lv.EVENT_VALUE_CHANGED, None)


while True:
    time.sleep(0.001)
    lv.tick_inc(1)
    lv.task_handler()


