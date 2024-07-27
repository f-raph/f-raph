import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
import sqlite3
import random

# Set window size explicitly
Window.size = (800, 600)

# Define the data
majors = {
    "Computer Science": ["CS101", "CS102", "CS103", "CS104", "CS105"],
    "Mathematics": ["MATH101", "MATH102", "MATH103", "MATH104"]
}

courses = {
    "CS101": [("Monday", "09:00", "10:30"), ("Wednesday", "09:00", "10:30"), ("Friday", "09:00", "10:30")],
    "CS102": [("Tuesday", "11:00", "12:30"), ("Thursday", "11:00", "12:30")],
    "CS103": [("Monday", "13:00", "14:30"), ("Wednesday", "13:00", "14:30"), ("Friday", "13:00", "14:30")],
    "CS104": [("Tuesday", "14:00", "15:30"), ("Thursday", "14:00", "15:30")],
    "CS105": [("Monday", "16:00", "17:30"), ("Wednesday", "16:00", "17:30"), ("Friday", "16:00", "17:30")],
    "MATH101": [("Monday", "08:00", "09:30"), ("Wednesday", "08:00", "09:30")],
    "MATH102": [("Tuesday", "10:00", "11:30"), ("Thursday", "10:00", "11:30")],
    "MATH103": [("Monday", "11:00", "12:30"), ("Wednesday", "11:00", "12:30")],
    "MATH104": [("Tuesday", "13:00", "14:30"), ("Thursday", "13:00", "14:30")]
}

# Database setup
def setup_database():
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT
        )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error setting up the database: {e}")

def save_user(username, email):
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (username, email) VALUES (?, ?)
        ''', (username, email))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving user data: {e}")

# Function to handle time overlap and scheduling
def time_overlap(t1_start, t1_end, t2_start, t2_end):
    """Check if two time intervals overlap"""
    return max(t1_start, t2_start) < min(t1_end, t2_end)

def convert_to_minutes(time_str):
    """Convert time in HH:MM format to minutes"""
    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes

def assign_courses(selected_courses):
    assigned_times = []
    course_schedule = {}

    for course in selected_courses:
        available_times = courses.get(course, [])
        random.shuffle(available_times)

        assigned = False
        for day, start_time, end_time in available_times:
            start_minutes = convert_to_minutes(start_time)
            end_minutes = convert_to_minutes(end_time)
            overlap = False

            for assigned_day, assigned_start, assigned_end in assigned_times:
                if day == assigned_day and time_overlap(assigned_start, assigned_end, start_minutes, end_minutes):
                    overlap = True
                    break

            if not overlap:
                assigned_times.append((day, start_minutes, end_minutes))
                course_schedule[course] = (day, start_time, end_time)
                assigned = True
                break

        if not assigned:
            print(f"Could not find a time slot for course {course} without overlap.")

    return course_schedule

# Define the Screens
class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, padding=10, spacing=30)

        # Sign-Up Header
        signup_header = Label(text='Sign Up', font_size='24sp', bold=True, size_hint_y=None, height=100)
        self.layout.add_widget(signup_header)

        # User Info
        user_info_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=160)

        self.username_input = TextInput(hint_text='Enter Username', multiline=False, size_hint_y=None, height=60)
        user_info_layout.add_widget(self.username_input)

        self.email_input = TextInput(hint_text='Enter Email', multiline=False, size_hint_y=None, height=60)
        user_info_layout.add_widget(self.email_input)

        self.signup_button = Button(
            text="Sign Up",
            background_color=(0.2, 0.6, 0.8, 1),  # RGBA
            color=(1, 1, 1, 1),  # White text color (RGBA)
            size_hint_y=None, height=60
        )
        self.signup_button.bind(on_press=self.sign_up)
        user_info_layout.add_widget(self.signup_button)

        self.layout.add_widget(user_info_layout)
        self.add_widget(self.layout)

    def sign_up(self, instance):
        username = self.username_input.text.strip()
        email = self.email_input.text.strip()

        if username and email:
            save_user(username, email)
            self.manager.current = 'main'
        else:
            self.manager.get_screen('main').schedule_label.text += "Please enter both username and email.\n"

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_courses = []
        self.layout = GridLayout(cols=1, padding=10, spacing=10)

        # Header
        header = Label(text='Course Scheduler', font_size='24sp', bold=True, size_hint_y=None, height=50)
        self.layout.add_widget(header)

        # Major Selector
        self.major_spinner = Spinner(
            text='Select Major',
            values=list(majors.keys()),
            size_hint_y=None, height=50
        )
        self.major_spinner.bind(text=self.update_courses)
        self.layout.add_widget(self.major_spinner)

        # Available Courses Label
        self.available_courses_label = Label(text='Available Courses: ', font_size='18sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.available_courses_label)

        # Display available courses
        self.available_courses_display = Label(text='', size_hint_y=None, height=500)
        self.layout.add_widget(self.available_courses_display)

        # Course Input
        self.course_input = TextInput(hint_text='Enter course code (e.g., CS101)', multiline=False, size_hint_y=None, height=60)
        self.layout.add_widget(self.course_input)

        self.add_button = Button(
            text="Add Course",
            background_color=(0.2, 0.6, 0.8, 1),  # RGBA
            color=(1, 1, 1, 1),  # White text color (RGBA)
            size_hint_y=None, height=50
        )
        self.add_button.bind(on_press=self.add_course)
        self.layout.add_widget(self.add_button)

        self.submit_button = Button(
            text="Submit",
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None, height=50
        )
        self.submit_button.bind(on_press=self.submit_courses)
        self.layout.add_widget(self.submit_button)

        self.schedule_label = Label(text="", size_hint_y=None, height=200)
        self.layout.add_widget(self.schedule_label)

        self.add_widget(self.layout)

    def update_courses(self, spinner, text):
        if text in majors:
            available_courses = majors[text]
            self.available_courses_display.text = "\n".join(available_courses)

    def add_course(self, instance):
        course = self.course_input.text.strip()
        if course in courses:
            self.selected_courses.append(course)
            self.schedule_label.text += f"Added {course}\n"
            self.course_input.text = ""
        else:
            self.schedule_label.text += f"Course {course} not found\n"

    def submit_courses(self, instance):
        if not self.selected_courses:
            self.schedule_label.text += "No courses selected\n"
            return

        schedule = assign_courses(self.selected_courses)
        self.manager.get_screen('celebration').update_schedule(schedule)
        self.manager.current = 'celebration'

class CelebrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, padding=10, spacing=10)

        # Header
        header = Label(text='Your Final Schedule', font_size='24sp', bold=True, size_hint_y=None, height=40)
        self.layout.add_widget(header)

        self.schedule_label = Label(text="", size_hint_y=None, height=400)
        self.layout.add_widget(self.schedule_label)

        # Return to main button
        self.return_button = Button(
            text="Return to Main",
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None, height=50
        )
        self.return_button.bind(on_press=self.return_to_main)
        self.layout.add_widget(self.return_button)

        self.add_widget(self.layout)

    def update_schedule(self, schedule):
        schedule_text = "Congratulations! Here is your final schedule:\n\n"
        for course, (day, start_time, end_time) in schedule.items():
            schedule_text += f"{course}: {day} from {start_time} to {end_time}\n"
        self.schedule_label.text = schedule_text

    def return_to_main(self, instance):
        self.manager.current = 'main'

class CourseSchedulerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CelebrationScreen(name='celebration'))
        return sm

if __name__ == "__main__":
    setup_database()
    CourseSchedulerApp().run()
