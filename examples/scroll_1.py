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


def scroll_event(e):
    cont_a = lv.area_t()
    lv.obj_get_coords(cont, cont_a)
    cont_y_center = cont_a.y1 + lv.area_get_height(cont_a) // 2

    r = lv.obj_get_height(cont) * 7 // 10

    for chld in buttons:
        child_a = lv.area_t()
        lv.obj_get_coords(chld, child_a)

        child_y_center = child_a.y1 + lv.area_get_height(child_a) // 2

        diff_y = child_y_center - cont_y_center
        diff_y = abs(diff_y)

        # Get the x of diff_y on a circle.
        # If diff_y is out of the circle use the last point of the circle (the radius)
        if diff_y >= r:
            x = r
        else:
            # Use Pythagoras theorem to get x from radius and y
            x_sqr = r * r - diff_y * diff_y
            res = lv.sqrt_res_t()
            lv.sqrt(x_sqr, res, 0x8000)   # Use lvgl's built in sqrt root function
            x = r - res.i

        # Translate the item by the calculated X coordinate
        lv.obj_set_style_translate_x(chld, x, 0)

        # Use some opacity with larger translations
        opa = lv.map(x, 0, r, lv.OPA_TRANSP, lv.OPA_COVER)
        lv.obj_set_style_opa(chld, lv.OPA_COVER - opa, 0)


cont = lv.obj_create(lv.scr_act())
lv.obj_set_size(cont, 200, 200)
lv.obj_center(cont)
lv.obj_set_flex_flow(cont, lv.FLEX_FLOW_COLUMN)
lv.obj_add_event(cont, scroll_event, lv.EVENT_SCROLL, None)
lv.obj_set_style_radius(cont, lv.RADIUS_CIRCLE, 0)
lv.obj_set_style_clip_corner(cont, True, 0)
lv.obj_set_scroll_dir(cont, lv.DIR_VER)
lv.obj_set_scroll_snap_y(cont, lv.SCROLL_SNAP_CENTER)
lv.obj_set_scrollbar_mode(cont, lv.SCROLLBAR_MODE_OFF)

buttons = []

for i in range(20):
    btn = lv.btn_create(cont)
    buttons.append(btn)
    lv.obj_set_width(btn, lv.pct(100))

    label = lv.label_create(btn)
    lv.label_set_text(label, "Button " + str(i))

    # Update the buttons position manually for first*
    lv.obj_send_event(cont, lv.EVENT_SCROLL, None)

    # Be sure the fist button is in the middle
    lv.obj_scroll_to_view(lv.obj_get_child(cont, 0), lv.ANIM_OFF)


start = time.time()

while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
