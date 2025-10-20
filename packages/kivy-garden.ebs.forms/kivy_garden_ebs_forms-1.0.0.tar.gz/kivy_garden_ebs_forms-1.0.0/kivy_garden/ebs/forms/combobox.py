from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from kivy.properties import StringProperty, ListProperty, ObjectProperty


class LabelledComboBox(BoxLayout):
    label_text = StringProperty("Label:")
    options = ListProperty([])
    textinput = ObjectProperty(None)
    dropdown = ObjectProperty(None)

    def __init__(self, label_text="Label:", options=None, default="", **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, **kwargs)
        self.label_text = label_text
        self.options = options or []

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
            multiline=False,
            size_hint_y=None,
            height=dp(36),
            font_size=dp(18),
        )
        self.textinput.bind(focus=self._on_focus)
        self.textinput.bind(text=self._on_text)

        self.dropdown = DropDown()
        self._populate_dropdown(self.options)

        self.add_widget(self.label)
        self.add_widget(self.textinput)
        self.bind_children_height()

    def _update_label_text_size(self, *args):
        self.label.text_size = self.label.size

    def _populate_dropdown(self, options):
        self.dropdown.clear_widgets()
        for opt in options:
            btn = Button(
                text=opt,
                size_hint_y=None,
                height=dp(32),
                halign='left',
            )
            btn.bind(on_release=lambda btn: self._select_option(btn.text))
            self.dropdown.add_widget(btn)

    def _select_option(self, text):
        self.textinput.text = text
        self.dropdown.dismiss()

    def _on_focus(self, instance, focused):
        if focused and self.options:
            self._filter_dropdown(self.textinput.text)
            self.dropdown.open(self.textinput)
        else:
            self.dropdown.dismiss()

    def _on_text(self, instance, value):
        if not self.textinput.focus:
            return
        self._filter_dropdown(value)

    def _filter_dropdown(self, query):
        """Show only options that contain the typed text (case-insensitive)."""
        filtered = [
            opt for opt in self.options
            if query.lower() in opt.lower()
        ] if query else self.options
        self._populate_dropdown(filtered)
        if filtered:
            self.dropdown.open(self.textinput)
        else:
            self.dropdown.dismiss()

    def bind_children_height(self):
        """Auto-adjust widget height based on children."""
        def update_height(*_):
            self.height = sum(c.height for c in self.children)
        for c in self.children:
            c.bind(height=update_height)
        update_height()
