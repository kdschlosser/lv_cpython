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

#
# Style a button from scratch
#

# Init the style for the default state
style = lv.style_t()
lv.style_init(style)

lv.style_set_radius(style, 3)

lv.style_set_bg_opa(style, lv.OPA_COVER)
lv.style_set_bg_color(style, lv.palette_main(lv.PALETTE_BLUE))
lv.style_set_bg_grad_color(style, lv.palette_darken(lv.PALETTE_BLUE, 2))
lv.style_set_bg_grad_dir(style, lv.GRAD_DIR_VER)

lv.style_set_border_opa(style, lv.OPA_40)
lv.style_set_border_width(style, 2)
lv.style_set_border_color(style, lv.palette_main(lv.PALETTE_GREY))

lv.style_set_shadow_width(style, 8)
lv.style_set_shadow_color(style, lv.palette_main(lv.PALETTE_GREY))
lv.style_set_shadow_ofs_y(style, 8)

lv.style_set_outline_opa(style, lv.OPA_COVER)
lv.style_set_outline_color(style, lv.palette_main(lv.PALETTE_BLUE))

lv.style_set_text_color(style, lv.color_white())
lv.style_set_pad_all(style, 10)

# Init the pressed style
style_pr = lv.style_t()
lv.style_init(style_pr)

# Add a large outline when pressed
lv.style_set_outline_width(style_pr, 30)
lv.style_set_outline_opa(style_pr, lv.OPA_TRANSP)

lv.style_set_translate_y(style_pr, 5)
lv.style_set_shadow_ofs_y(style_pr, 3)
lv.style_set_bg_color(style_pr, lv.palette_darken(lv.PALETTE_BLUE, 2))
lv.style_set_bg_grad_color(style_pr, lv.palette_darken(lv.PALETTE_BLUE, 4))

# Add a transition to the outline
trans = lv.style_transition_dsc_t()

lv.style_transition_dsc_init(trans, [lv.STYLE_OUTLINE_WIDTH, lv.STYLE_OUTLINE_OPA, 0], lv.anim_path_linear, 300, 0, None)

lv.style_set_transition(style_pr, trans)

btn1 = lv.btn_create(lv.scr_act())
lv.obj_remove_style_all(btn1)  # Remove the style coming from the theme
lv.obj_add_style(btn1, style, 0)
lv.obj_add_style(btn1, style_pr, lv.STATE_PRESSED)
lv.obj_set_size(btn1, lv.SIZE_CONTENT, lv.SIZE_CONTENT)
lv.obj_center(btn1)

label = lv.label_create(btn1)
lv.label_set_text(label, "Button")
lv.obj_center(label)


while True:
    time.sleep(0.001)
    lv.tick_inc(1)
    lv.task_handler()
