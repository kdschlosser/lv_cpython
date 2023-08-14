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


def slider_event_cb(e):
    s = lv.event_get_target_obj(e)

    # Refresh the text
    lv.label_set_text(label, str(lv.slider_get_value(s)))


# Create a slider in the center of the display
slider = lv.slider_create(lv.scr_act())
lv.obj_set_width(slider, 200)
lv.obj_center(slider)
lv.obj_add_event(slider, slider_event_cb, lv.EVENT_VALUE_CHANGED, None)

# Create a label above the slider
label = lv.label_create(lv.scr_act())
lv.label_set_text(label, "0")
lv.obj_align_to(label, slider, lv.ALIGN_OUT_TOP_MID, 0, -15)


while True:
    time.sleep(0.001)
    lv.tick_inc(1)
    lv.task_handler()
