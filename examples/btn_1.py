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


disp = lv.sdl_window_create(480, 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


# Normal button
btn1 = lv.btn_create(lv.scr_act())
lv.obj_set_size(btn1, 100, 40)
lv.obj_align(btn1, lv.ALIGN_CENTER, 0, -70)

label1 = lv.label_create(btn1)
lv.label_set_text(label1, "Normal")
lv.obj_center(label1)

# Set opacity
# The button and the label is rendered
# to a layer first and that layer is blended
btn2 = lv.btn_create(lv.scr_act())
lv.obj_set_size(btn2, 100, 40)
lv.obj_set_style_opa(btn2, lv.OPA_50, 0)
lv.obj_align(btn2, lv.ALIGN_CENTER, 0, 0)

label2 = lv.label_create(btn2)
lv.label_set_text(label2, "Opa:50%")
lv.obj_center(label2)

# Set transformations
# The button and the label is rendered to
# a layer first and that layer is transformed
btn3 = lv.btn_create(lv.scr_act())
lv.obj_set_size(btn3, 100, 40)
lv.obj_set_style_transform_angle(btn3, 150, 0)             # 15 deg
lv.obj_set_style_transform_zoom(btn3, 256 + 64, 0)         # 1.25x
lv.obj_set_style_transform_pivot_x(btn3, 50, 0)
lv.obj_set_style_transform_pivot_y(btn3, 20, 0)
lv.obj_set_style_opa(btn3, lv.OPA_50, 0)
lv.obj_align(btn3, lv.ALIGN_CENTER, 0, 70)

label3 = lv.label_create(btn3)
lv.label_set_text(label3, "Transf.")
lv.obj_center(label3)


while True:
    time.sleep(0.001)
    lv.tick_inc(1)
    lv.task_handler()
