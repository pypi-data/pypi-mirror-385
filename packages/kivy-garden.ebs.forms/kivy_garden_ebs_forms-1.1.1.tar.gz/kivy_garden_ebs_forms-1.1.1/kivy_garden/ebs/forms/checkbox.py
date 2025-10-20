from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox

from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty


class LabelledCheckBox(BoxLayout):
    label_text = StringProperty("Label:")
    check = ObjectProperty(None)

    def __init__(self, label_text="Label:", default=False, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, **kwargs)
        self.label_text = label_text

        self.label = Label(
            text=self.label_text,
            size_hint_y=None,
            size_hint_x=None,
            height=dp(20),
            halign='right',
            valign='middle',
        )
        self.label.bind(size=self._update_label_text_size)

        self.check = CheckBox(
            active=default,
            size_hint_y=None,
            size_hint_x=None,
            height=dp(20),
            width=dp(20),
        )
        self.add_widget(self.label)
        self.add_widget(self.check)

        # Let height automatically fit both children
        self.bind_children_height()

    def _update_label_text_size(self, *args):
        self.label.text_size = self.label.size

    def bind_children_height(self):
        """Auto-adjust widget height based on children."""
        def update_height(*_):
            self.height = sum(c.height for c in self.children)
        for c in self.children:
            c.bind(height=update_height)
        update_height()
