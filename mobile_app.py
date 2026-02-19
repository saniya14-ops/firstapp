import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


SERVER_URL = "http://127.0.0.1:5000"


class LoginScreen(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.add_widget(Label(text="Society Guard AI"))

        self.username = TextInput(hint_text="Username")
        self.add_widget(self.username)

        self.password = TextInput(hint_text="Password", password=True)
        self.add_widget(self.password)

        self.login_btn = Button(text="Login")
        self.login_btn.bind(on_press=self.login)
        self.add_widget(self.login_btn)

        self.result = Label(text="")
        self.add_widget(self.result)

    def login(self, instance):

        data = {
            "username": self.username.text,
            "password": self.password.text
        }

        try:
            r = requests.post(SERVER_URL + "/login", data=data)

            if r.status_code == 200:
                self.result.text = "Login successful"
            else:
                self.result.text = "Login failed"

        except:
            self.result.text = "Server not running"


class SocietyApp(App):

    def build(self):
        return LoginScreen()


SocietyApp().run()
