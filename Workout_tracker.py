import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

FILE = "workouts.json"


def normalize_exercise(name):
    return (
        name.lower()
        .replace("_", " ")
        .replace("-", " ")
        .strip()
    )


def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            raw_data = json.load(f)

        normalized_data = {}

        for exercise, sessions in raw_data.items():
            normalized_name = normalize_exercise(exercise)

            if normalized_name not in normalized_data:
                normalized_data[normalized_name] = []

            normalized_data[normalized_name].extend(sessions)

        return normalized_data

    return {}


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def title_name(name):
    return name.title()


class WorkoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout Tracker")
        self.root.geometry("650x650")

        self.data = load_data()
        save_data(self.data)

        self.main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_screen()

        title = tk.Label(self.root, text="Workout Tracker", font=("Arial", 24, "bold"))
        title.pack(pady=30)

        tk.Button(self.root, text="Add Session", width=25, height=2, command=self.add_session_screen).pack(pady=8)
        tk.Button(self.root, text="Show Exercise", width=25, height=2, command=self.show_exercise_screen).pack(pady=8)
        tk.Button(self.root, text="Visualization Dashboard", width=25, height=2, command=self.visualization_dashboard).pack(pady=8)
        tk.Button(self.root, text="Delete Session", width=25, height=2, command=self.delete_session_screen).pack(pady=8)
        tk.Button(self.root, text="Delete Exercise", width=25, height=2, command=self.delete_exercise_screen).pack(pady=8)
        
        tk.Button(self.root, text="Exit", width=25, height=2, command=self.root.quit).pack(pady=8)
        

    def back_button(self):
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=15)

    def visualization_dashboard(self):
        self.clear_screen()

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", pady=5)

        tk.Button(
            top_frame,
            text="← Back",
            command=self.main_menu
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            top_frame,
            text="Visualization Dashboard",
            font=("Arial", 20, "bold")
        ).pack(side=tk.LEFT, padx=20)

        if len(self.data) == 0:
            tk.Label(self.root, text="No workout data found.").pack(pady=20)
            return

        graph_frame = tk.Frame(self.root)
        graph_frame.pack(pady=10)

        current_canvas = {"canvas": None}

        def clear_graph():
            for widget in graph_frame.winfo_children():
                widget.destroy()

            if current_canvas["canvas"] is not None:
                current_canvas["canvas"].get_tk_widget().destroy()
                current_canvas["canvas"] = None

        def calculate_1rm(weight, reps):
            return weight * (1 + reps / 30)

        def show_strength_progression():
            clear_graph()

            fig, ax = plt.subplots(figsize=(7, 4))

            lifts_to_show = ["bench press", "squat", "deadlift"]

            for lift in lifts_to_show:
                if lift in self.data:
                    sorted_sessions = sorted(
                        self.data[lift],
                        key=lambda s: datetime.strptime(s["date"], "%Y-%m-%d")
                    )

                    dates = []
                    one_rep_maxes = []

                    for session in sorted_sessions:
                        dates.append(session["date"])
                        one_rep_maxes.append(
                            calculate_1rm(session["weight"], session["reps"])
                        )

                    ax.plot(dates, one_rep_maxes, marker="o", label=title_name(lift))

            ax.set_title("Strength Progression: Estimated 1RM")
            ax.set_xlabel("Date")
            ax.set_ylabel("Estimated 1RM")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            current_canvas["canvas"] = canvas

        def show_weekly_volume():
            clear_graph()

            weekly_volume = {}

            for exercise, sessions in self.data.items():
                for session in sessions:
                    date_obj = datetime.strptime(session["date"], "%Y-%m-%d")
                    week = date_obj.strftime("%Y-W%U")

                    volume = session["sets"] * session["reps"] * session["weight"] if "sets" in session else session["reps"] * session["weight"]

                    if week not in weekly_volume:
                        weekly_volume[week] = 0

                    weekly_volume[week] += volume

            weeks = sorted(weekly_volume.keys())
            volumes = [weekly_volume[week] for week in weeks]

            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar(weeks, volumes)

            ax.set_title("Weekly Training Volume")
            ax.set_xlabel("Week")
            ax.set_ylabel("Volume: sets × reps × weight")
            ax.tick_params(axis="x", rotation=45)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            current_canvas["canvas"] = canvas

        def show_workout_frequency():
            clear_graph()

            weekly_frequency = {}

            for exercise, sessions in self.data.items():
                for session in sessions:
                    date_obj = datetime.strptime(session["date"], "%Y-%m-%d")
                    week = date_obj.strftime("%Y-W%U")

                    if week not in weekly_frequency:
                        weekly_frequency[week] = 0

                    weekly_frequency[week] += 1

            weeks = sorted(weekly_frequency.keys())
            frequencies = [weekly_frequency[week] for week in weeks]

            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar(weeks, frequencies)

            ax.set_title("Workout Frequency Per Week")
            ax.set_xlabel("Week")
            ax.set_ylabel("Number of Sessions")
            ax.tick_params(axis="x", rotation=45)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            current_canvas["canvas"] = canvas

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Strength Progression",
            command=show_strength_progression
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Weekly Volume",
            command=show_weekly_volume
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Workout Frequency",
            command=show_workout_frequency
        ).pack(side=tk.LEFT, padx=5)

    def get_selected_exercise(self, listbox):
        selection = listbox.curselection()

        if not selection:
            messagebox.showerror("Error", "Please select an exercise.")
            return None

        exercises = list(self.data.keys())
        return exercises[selection[0]]

    def exercise_listbox(self):
        listbox = tk.Listbox(self.root, width=40, height=10)

        for exercise in self.data.keys():
            listbox.insert(tk.END, title_name(exercise))

        listbox.pack(pady=10)
        return listbox

    def add_session_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Add Session", font=("Arial", 20, "bold")).pack(pady=15)

        if len(self.data) > 0:
            tk.Label(self.root, text="Choose an exercise or create a new one:").pack()
            listbox = self.exercise_listbox()
        else:
            listbox = None
            tk.Label(self.root, text="No exercises found. Create a new one.").pack(pady=10)

        def create_new_exercise():
            name = simpledialog.askstring("New Exercise", "Enter new exercise name:")

            if not name:
                return None

            exercise = normalize_exercise(name)

            if exercise not in self.data:
                self.data[exercise] = []
                save_data(self.data)

            return exercise

        def continue_add():
            if listbox is not None and listbox.curselection():
                exercise = self.get_selected_exercise(listbox)
            else:
                exercise = create_new_exercise()

            if exercise is None:
                return

            reps = simpledialog.askinteger("Reps", "Enter reps:")
            if reps is None:
                return

            weight = simpledialog.askinteger("Weight", "Enter weight:")
            if weight is None:
                return

            while True:
                date_input = simpledialog.askstring("Date", "Enter date in YYYY-MM-DD format:")

                if date_input is None:
                    return

                try:
                    datetime.strptime(date_input, "%Y-%m-%d")
                    break
                except ValueError:
                    messagebox.showerror("Invalid Date", "Please use YYYY-MM-DD format.\nExample: 2026-04-23")

            self.data[exercise].append({
                "reps": reps,
                "weight": weight,
                "date": date_input
            })

            save_data(self.data)
            messagebox.showinfo("Success", "Session added.")
            self.main_menu()

        tk.Button(self.root, text="Add to Selected / New", command=continue_add).pack(pady=10)
        self.back_button()

    def show_exercise_screen(self):
        self.clear_screen()

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", pady=5)

        tk.Button(
            top_frame,
            text="← Back",
            command=self.main_menu
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            top_frame,
            text="Show Exercise",
            font=("Arial", 20, "bold")
        ).pack(side=tk.LEFT, padx=20)

        if len(self.data) == 0:
            tk.Label(self.root, text="No exercises found.").pack(pady=10)
            return

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=5)

        tk.Label(list_frame, text="Exercises").pack()

        listbox = tk.Listbox(list_frame, width=30, height=6)

        for exercise in self.data.keys():
            listbox.insert(tk.END, title_name(exercise))

        listbox.pack()

        output = tk.Text(self.root, width=70, height=6)
        output.pack(pady=5)

        graph_frame = tk.Frame(self.root)
        graph_frame.pack(pady=5)

        def calculate_1rm(weight, reps):
            return weight * (1 + reps / 30)

        def show_sessions():
            exercise = self.get_selected_exercise(listbox)
            if exercise is None:
                return

            output.delete("1.0", tk.END)

            dates = []
            one_rep_maxes = []

            output.insert(tk.END, f"{title_name(exercise)} Sessions:\n\n")

            for i, session in enumerate(self.data[exercise]):
                reps = session["reps"]
                weight = session["weight"]
                date = session["date"]

                one_rm = calculate_1rm(weight, reps)

                output.insert(
                    tk.END,
                    f"{i}: {date} - {reps} reps x {weight} lbs | Estimated 1RM: {one_rm:.1f} lbs\n"
                )

                dates.append(date)
                one_rep_maxes.append(one_rm)

            for widget in graph_frame.winfo_children():
                widget.destroy()

            if len(dates) > 0:
                fig, ax = plt.subplots(figsize=(5.5, 2.5))
                ax.plot(dates, one_rep_maxes, marker="o")
                ax.set_title(f"{title_name(exercise)} Estimated 1RM Progress")
                ax.set_xlabel("Date")
                ax.set_ylabel("Estimated 1RM")
                ax.tick_params(axis="x", rotation=45)
                fig.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack()

        tk.Button(
            top_frame,
            text="Show Sessions",
            command=show_sessions
        ).pack(side=tk.LEFT, padx=10)

    def delete_session_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Delete Session", font=("Arial", 20, "bold")).pack(pady=15)

        if len(self.data) == 0:
            tk.Label(self.root, text="No exercises found.").pack(pady=10)
            self.back_button()
            return

        exercise_listbox = self.exercise_listbox()

        session_listbox = tk.Listbox(self.root, width=55, height=8)
        session_listbox.pack(pady=10)

        selected_exercise = {"name": None}

        def load_sessions():
            exercise = self.get_selected_exercise(exercise_listbox)
            if exercise is None:
                return

            selected_exercise["name"] = exercise
            session_listbox.delete(0, tk.END)

            for i, session in enumerate(self.data[exercise]):
                session_listbox.insert(
                    tk.END,
                    f"{i}: {session['date']} - {session['reps']} reps x {session['weight']} lbs"
                )

        def delete_selected_session():
            exercise = selected_exercise["name"]

            if exercise is None:
                messagebox.showerror("Error", "Please load sessions first.")
                return

            selection = session_listbox.curselection()

            if not selection:
                messagebox.showerror("Error", "Please select a session to delete.")
                return

            idx = selection[0]

            confirm = messagebox.askyesno("Confirm Delete", "Delete this session?")

            if confirm:
                self.data[exercise].pop(idx)

                if len(self.data[exercise]) == 0:
                    del self.data[exercise]

                save_data(self.data)
                messagebox.showinfo("Deleted", "Session deleted.")
                self.main_menu()

        tk.Button(self.root, text="Load Sessions", command=load_sessions).pack(pady=5)
        tk.Button(self.root, text="Delete Selected Session", command=delete_selected_session).pack(pady=5)
        self.back_button()

    def delete_exercise_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Delete Exercise", font=("Arial", 20, "bold")).pack(pady=15)

        if len(self.data) == 0:
            tk.Label(self.root, text="No exercises found.").pack(pady=10)
            self.back_button()
            return

        listbox = self.exercise_listbox()

        def delete_exercise():
            exercise = self.get_selected_exercise(listbox)
            if exercise is None:
                return

            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Delete ALL sessions for {title_name(exercise)}?"
            )

            if confirm:
                del self.data[exercise]
                save_data(self.data)
                messagebox.showinfo("Deleted", "Exercise deleted.")
                self.main_menu()

        tk.Button(self.root, text="Delete Selected Exercise", command=delete_exercise).pack(pady=10)
        self.back_button()


root = tk.Tk()
app = WorkoutApp(root)
root.mainloop()