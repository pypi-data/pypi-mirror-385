

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from ebs.linuxnode.core.basenode import BaseIoTNode
from ebs.linuxnode.core.config import ElementSpec
from ebs.linuxnode.core.config import ItemSpec


class BaseGuiStructureMixin(BaseIoTNode):

    def __init__(self, *args, **kwargs):
        self._gui_root = None
        self._gui_fixed_structure_root = None
        self._gui_structure_heights = {}
        self._gui_structure_root = None
        self._gui_primary_anchor = None
        self._gui_footer = None
        self._gui_footer_users = set()
        self._gui_anchor_br = None
        self._gui_anchor_bl = None
        self._gui_anchor_tr = None
        self._gui_status_row = None
        self._gui_notification_row = None
        self._gui_debug_stack = None
        self._gui_content_root = None
        self._gui_main_content = None
        self._gui_sidebar = None
        self._gui_sidebar_users = set()
        self._gui_animation_layer = None
        super(BaseGuiStructureMixin, self).__init__(*args, **kwargs)

    def install(self):
        super(BaseGuiStructureMixin, self).install()
        _elements = {
            'sidebar_width': ElementSpec('display', 'sidebar_width', ItemSpec(float, fallback=0.3)),
            'sidebar_height_specific': ElementSpec('display', 'sidebar_height', ItemSpec(float, fallback=0.0)),
            'sidebar_height': ElementSpec('_derived', self._sidebar_height),
            'gui_overlay_mode': ElementSpec('display', 'overlay_mode', ItemSpec(bool, fallback=False)),
        }
        for name, spec in _elements.items():
            self.config.register_element(name, spec)

    @property
    def _gui_supports_overlay_mode(self):
        return self.config.gui_overlay_mode

    def _sidebar_height(self, config):
        if config.sidebar_height_specific:
            return config.sidebar_height_specific
        else:
            return config.sidebar_width

    @property
    def gui_root(self):
        if not self._gui_root:
            self._gui_root = FloatLayout()
        return self._gui_root

    @property
    def gui_fixed_structure_root(self):
        if not self._gui_fixed_structure_root:
            self._gui_fixed_structure_root = BoxLayout(orientation='vertical')
            self.gui_root.add_widget(self._gui_fixed_structure_root,
                                     len(self.gui_root.children) - 1)
        return self._gui_fixed_structure_root

    @property
    def gui_content_root(self):
        if not self._gui_content_root:
            params = {'spacing': 0}
            if self.config.portrait or self.config.os_rotation:
                params['orientation'] = 'vertical'
            else:
                params['orientation'] = 'horizontal'
            self._gui_content_root = BoxLayout(**params)
            self.gui_fixed_structure_root.add_widget(self._gui_content_root)
        return self._gui_content_root

    @property
    def gui_main_content(self):
        if not self._gui_main_content:
            self._gui_main_content = RelativeLayout()
            self.gui_content_root.add_widget(self._gui_main_content)
        return self._gui_main_content

    @property
    def gui_structure_root(self):
        # Structural components overlaid on top of the content if overlay,
        # if not comes at bottom of content
        if not self._gui_structure_root:
            self._gui_structure_root = BoxLayout(orientation='vertical')
            if self._gui_supports_overlay_mode:
                self.gui_root.add_widget(self._gui_structure_root)
            else:
                self._gui_structure_root.size_hint = (1, None)
                self._gui_structure_root.padding = [0, 0, 0, 0]
                self._gui_structure_root.height = 0
                self.gui_fixed_structure_root.add_widget(self._gui_structure_root)
        return self._gui_structure_root

    def _gui_redraw_structure(self):
        if self._gui_supports_overlay_mode:
            return
        self._gui_structure_root.height = max([
            self._gui_structure_heights.get('status', 0),
            self._gui_structure_heights.get('notification', 0), \
            self._gui_structure_heights.get('footer', 0)])

    @property
    def gui_primary_anchor(self):
        if not self._gui_primary_anchor:
            self._gui_primary_anchor = FloatLayout()
            self.gui_structure_root.add_widget(self._gui_primary_anchor)
            _ = self.gui_anchor_top_right
            _ = self.gui_anchor_bottom_left
            _ = self.gui_anchor_bottom_right
        return self._gui_primary_anchor

    @property
    def gui_anchor_bottom_right(self):
        if not self._gui_anchor_br:
            self._gui_anchor_br = AnchorLayout(anchor_x='right',
                                               anchor_y='bottom',
                                               pos_hint={'pos': [0, 0]})
            self.gui_primary_anchor.add_widget(self._gui_anchor_br)
        return self._gui_anchor_br

    @property
    def gui_anchor_bottom_left(self):
        if not self._gui_anchor_bl:
            self._gui_anchor_bl = AnchorLayout(anchor_x='left',
                                               anchor_y='bottom',
                                               pos_hint={'pos': [0, 0]})
            self.gui_primary_anchor.add_widget(self._gui_anchor_bl)
        return self._gui_anchor_bl

    @property
    def gui_anchor_top_right(self):
        if not self._gui_anchor_tr:
            self._gui_anchor_tr = AnchorLayout(anchor_x='right',
                                               anchor_y='top',
                                               pos_hint={'pos': [0, 0]})
            self.gui_primary_anchor.add_widget(self._gui_anchor_tr)
        return self._gui_anchor_tr

    @property
    def gui_tag_alpha(self):
        if self._gui_supports_overlay_mode:
            return 0.4
        else:
            return 0.8

    @property
    def gui_status_row(self):
        if not self._gui_status_row:
            self._gui_status_row = StackLayout(orientation='rl-bt',
                                               padding='5sp')
            self.gui_anchor_bottom_right.add_widget(self._gui_status_row)
            self._gui_status_row.bind(children=lambda *args: self._gui_status_row_update(args[1]))
        return self._gui_status_row

    def _gui_status_row_update(self, contents):
        if len(contents):
            self._gui_structure_heights['status'] = 60
        else:
            self._gui_structure_heights['status'] = 0
        self._gui_redraw_structure()

    @property
    def gui_notification_row(self):
        if not self._gui_notification_row:
            self._gui_notification_row = StackLayout(orientation='lr-bt',
                                                     spacing='8sp', padding='5sp')
            self.gui_anchor_bottom_left.add_widget(self._gui_notification_row)
            self._gui_notification_row.bind(children=lambda *args: self._gui_notification_row_update(args[1]))
        return self._gui_notification_row

    def _gui_notification_row_update(self, contents):
        if len(contents):
            self._gui_structure_heights['notification'] = 60
        else:
            self._gui_structure_heights['notification'] = 0
        self._gui_redraw_structure()

    def gui_notification_update(self):
        self.gui_notification_row.do_layout()

    @property
    def gui_debug_stack(self):
        if not self._gui_debug_stack:
            self._gui_debug_stack = StackLayout(orientation='tb-rl',
                                                padding='8sp')
            self.gui_anchor_top_right.add_widget(self._gui_debug_stack)
        return self._gui_debug_stack

    @property
    def gui_footer(self):
        if not self._gui_footer:
            _ = self.gui_primary_anchor
            self._gui_footer = BoxLayout(
                orientation='vertical', size_hint=(1, None),
                height=60, padding=['0sp', '0sp', '0sp', '0sp']
            )
        return self._gui_footer

    def _gui_footer_show(self):
        if not self.gui_footer.parent:
            self._gui_structure_heights['footer'] = 60
            if self._gui_supports_overlay_mode:
                self.gui_structure_root.add_widget(self.gui_footer)
            else:
                self.gui_primary_anchor.add_widget(self.gui_footer, index=len(self.gui_primary_anchor.children))

    def _gui_footer_hide(self):
        if self.gui_footer.parent:
            self._gui_structure_heights['footer'] = 0
            if self._gui_supports_overlay_mode:
                self.gui_structure_root.remove_widget(self.gui_footer)
            else:
                self.gui_primary_anchor.remove_widget(self.gui_footer)

    def _gui_footer_trigger(self):
        if len(self._gui_footer_users):
            self._gui_footer_show()
        else:
            self._gui_footer_hide()
        self._gui_redraw_structure()

    def gui_footer_show(self, user):
        if user not in self._gui_footer_users:
            self._gui_footer_users.add(user)
            self._gui_footer_trigger()

    def gui_footer_hide(self, user):
        if user in self._gui_footer_users:
            self._gui_footer_users.remove(user)
            self._gui_footer_trigger()

    @property
    def gui_sidebar(self):
        if not self._gui_sidebar:
            if self.config.portrait or self.config.os_rotation:
                orientation = "horizontal"
                y_hint = self.config.sidebar_height / (1 - self.config.sidebar_height)
                size_hint = (1, y_hint)
            else:
                orientation = "vertical"
                x_hint = self.config.sidebar_width / (1 - self.config.sidebar_width)
                size_hint = (x_hint, 1)
            self._gui_sidebar = BoxLayout(orientation=orientation,
                                          size_hint=size_hint)
        return self._gui_sidebar

    def gui_sidebar_show(self, key):
        if not key:
            key = 'unspecified'
        self._gui_sidebar_users.add(key)
        if not self.gui_sidebar.parent:
            self.log.debug("Showing sidebar")
            self.gui_content_root.add_widget(self.gui_sidebar)

    def gui_sidebar_hide(self, key):
        if key not in self._gui_sidebar_users:
            return
        self._gui_sidebar_users.remove(key)
        if len(self._gui_sidebar_users):
            return
        if self.gui_sidebar.parent:
            self.log.debug("Hiding sidebar")
            self.gui_content_root.remove_widget(self.gui_sidebar)

    @property
    def gui_animation_layer(self):
        if not self._gui_animation_layer:
            self._gui_animation_layer = FloatLayout()
            self.gui_root.add_widget(self._gui_animation_layer,
                                     len(self.gui_root.children) - 1)
        return self._gui_animation_layer

    @property
    def window_size(self):
        return Window.size

    @property
    def window_height(self):
        return self.window_size[1]

    @property
    def window_width(self):
        return self.window_size[0]

    def geometry_transform(self, x, y, width, height):
        if self.config.os_rotation:
            return x, y, width, height
        if self.config.flip:
            x = self.window_width - width - x
            y = self.window_height - height - y
        if self.config.portrait:
            x, y, width, height = y, x, height, width
        return x, y, width, height
