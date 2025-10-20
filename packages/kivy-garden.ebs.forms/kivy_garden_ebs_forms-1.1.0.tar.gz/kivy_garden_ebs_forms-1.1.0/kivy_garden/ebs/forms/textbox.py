from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty


class LabelledTextInput(BoxLayout):
    label_text = StringProperty("Label:")
    textinput = ObjectProperty(None)

    def __init__(self, label_text="Label:", default=None, multiline=False, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, **kwargs)
        self.label_text = label_text

        self.label = Label(
            text=self.label_text,
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='bottom',
        )
        self.label.bind(size=self._update_label_text_size)

        self.textinput = TextInput(
            text=default,
            multiline=multiline,
            size_hint_y=None,
            font_size=dp(24),
        )
        self.textinput.bind(minimum_height=self.textinput.setter("height"))


        self.add_widget(self.label)
        self.add_widget(self.textinput)

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
