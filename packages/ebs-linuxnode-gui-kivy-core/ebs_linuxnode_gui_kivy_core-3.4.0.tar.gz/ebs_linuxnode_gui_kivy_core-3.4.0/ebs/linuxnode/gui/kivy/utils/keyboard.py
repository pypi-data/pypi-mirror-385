

from kivy.core.window import Window
from kivy.uix.textinput import TextInput

_orig_request_keyboard = Window.request_keyboard

def _single_keyboard_request(callback, target, **kwargs):
    Window.release_all_keyboards()
    keyboard = _orig_request_keyboard(callback, target, **kwargs)
    try:
        if hasattr(keyboard, "widget") and keyboard.widget:
            kb = keyboard.widget
            focus_widget = getattr(target, "_proxy_ref", None) or target
            if hasattr(focus_widget, "to_window"):
                x, y = focus_widget.to_window(focus_widget.x, focus_widget.y)
                w, h = focus_widget.size
                win_w, win_h = Window.size
                kb_w, kb_h = kb.size
                new_x = max(0, min(x, win_w - kb_w))
                new_y = y - kb_h - 10
                if new_y < 0:
                    new_y = y + h + 10
                if new_y + kb_h > win_h:
                    new_y = max(0, win_h - kb_h)
                kb.pos = (new_x, new_y)
    except Exception:
        pass
    return keyboard

Window.request_keyboard = _single_keyboard_request
