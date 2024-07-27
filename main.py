import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import random

courses = {
    "CS101": [("Monday", "09:00", "10:30"), ("Wednesday", "09:00", "10:30"), ("Friday", "09:00", "10:30")],
    "CS102": [("Tuesday", "11:00", "12:30"), ("Thursday", "11:00", "12:30")],
    "CS103": [("Monday", "13:00", "14:30"), ("Wednesday", "13:00", "14:30"), ("Friday", "13:00", "14:30")],
    "CS104": [("Tuesday", "14:00", "15:30"), ("Thursday", "14:00", "15:30")],
    "CS105": [("Monday", "16:00", "17:30"), ("Wednesday", "16:00", "17:30"), ("Friday", "16:00", "17:30")],
}

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

class CourseSchedulerApp(App):

    def build(self):
        self.selected_courses = []

        self.layout = GridLayout(cols=1, padding=10)

        self.course_input = TextInput(hint_text='Enter course code (e.g., CS101)', multiline=False)
        self.layout.add_widget(self.course_input)

        self.add_button = Button(
            text="Add Course",
            background_color = (0.2, 0.6, 0.8, 1),  # RGBA
            color = (1, 1, 1, 1)  # White text color (RGBA)
        )
        self.add_button.bind(on_press=self.add_course)
        self.layout.add_widget(self.add_button)

        self.submit_button = Button(text="Submit")
        self.submit_button.bind(on_press=self.submit_courses)
        self.layout.add_widget(self.submit_button)

        self.schedule_label = Label(text="")
        self.layout.add_widget(self.schedule_label)

        return self.layout

    def add_course(self, instance):
        course = self.course_input.text.strip()
        if course in courses:
            self.selected_courses.append(course)
            self.schedule_label.text += f"Added {course}\n"
            self.course_input.text = ""
        else:
            self.schedule_label.text += f"Course {course} not available.\n"
            self.course_input.text = ""

    def submit_courses(self, instance):
        course_schedule = assign_courses(self.selected_courses)
        if course_schedule:
            self.schedule_label.text += "\nThese are your courses for the fall semester:\n"
            for course, (day, start_time, end_time) in course_schedule.items():
                self.schedule_label.text += f"{course}: {day} from {start_time} to {end_time}\n"
        else:
            self.schedule_label.text += "\nNo courses were assigned due to scheduling conflicts.\n"

if __name__ == '__main__':
    CourseSchedulerApp().run()
