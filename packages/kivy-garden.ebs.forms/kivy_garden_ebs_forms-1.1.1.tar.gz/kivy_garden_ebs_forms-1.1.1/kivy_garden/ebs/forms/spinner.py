from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner

from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty


class LabelledSpinner(BoxLayout):
    label_text = StringProperty("Label:")
    spinner = ObjectProperty(None)
    values = ListProperty([])

    def __init__(self, label_text="Label:", values=None, default=None, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, **kwargs)
        self.label_text = label_text
        self.values = values or []

        # Label at the top
        self.label = Label(
            text=self.label_text,
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='bottom',
        )
        self.label.bind(size=self._update_label_text_size)

        # Spinner below
        self.spinner = Spinner(
            text=default or (self.values[0] if self.values else ""),
            values=self.values,
            size_hint_y=None,
            height=dp(36),
            font_size=dp(18),
        )

        self.add_widget(self.label)
        self.add_widget(self.spinner)

        # Auto-fit the height based on children
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

