

from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.boxlayout import BoxLayout

class LabelledPropSwitch(BoxLayout):
    def __init__(self, label, target_obj, prop_name: str, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height='40dp', **kwargs)

        lbl = Label(text=label, halign='left', valign='middle', size_hint_x=1)
        lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(lbl)

        sw = Switch(size_hint_x=None)
        sw.active = getattr(target_obj, prop_name)
        sw.bind(active=lambda _, v: setattr(target_obj, prop_name, v))
        target_obj.bind(**{prop_name: lambda _, v: setattr(sw, 'active', v)})
        self.add_widget(sw)
