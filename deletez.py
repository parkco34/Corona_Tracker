#!/usr/bin/env python
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class Example_Form(BoxLayout):

    def press(instance, value):
        print("YOU CLICKED ME THERE!")

#    def __init__(self, **kwargs):
#        super(Example_Form, self).__init__(**kwargs)
#        self.padding = 40
#        self.add_widget(Label(text="Hello, Friend..."))
#        self.add_widget(Button(text="CLICK THIS!"))
#
def __init__(self, **kwargs):




class Tutorial(App):
#    def build(self):
#        return Label(text="Hello, Friend...")

    def build(self):
        return Example_Form()


if __name__ == "__main__":
    Tutorial().run()

