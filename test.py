import lvgl as lv
import time


lv.init()
print('LVGL initilized')

disp = lv.sdl_window_create(480, 320)
print('disp:', disp)

group = lv.group_create()
print('group:', group)

lv.group_set_default(group)

mouse = lv.sdl_mouse_create()
print('mouse:', mouse)

keyboard = lv.sdl_keyboard_create()
print('keyboard:', keyboard)

lv.indev_set_group(keyboard, group)
print('lv_indev_set_group')

screen = lv.scr_act()

btn = lv.btn_create(screen)
lv.obj_set_pos(btn, 10, 10)
lv.obj_set_size(btn, 120, 50)

label = lv.label_create(btn)
lv.obj_center(btn)

lv.label_set_text(label, "Button")
lv.obj_center(label)

start = time.time()

while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
