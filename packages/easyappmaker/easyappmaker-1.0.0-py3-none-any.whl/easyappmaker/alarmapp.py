import tkinter as tk
from tkinter import messagebox
import datetime
import threading
from playsound import playsound
import time
import os

alarm_active = False
stop_alarm_flag = False

def play_alarm_sound():
    global stop_alarm_flag
    # Get the folder where this script lives
    folder = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(folder, "alarm.mp3")  # your MP3 inside appmaker

    if not os.path.exists(sound_path):
        print("Error: alarm.mp3 not found at", sound_path)
        return

    while not stop_alarm_flag:
        playsound(sound_path)
        # tiny pause to avoid CPU hog
        import time
        time.sleep(0.1)

def alarm_checker(target_time, btn):
    global alarm_active, stop_alarm_flag
    alarm_active = True
    stop_alarm_flag = False

    while alarm_active:
        now = datetime.datetime.now()
        if now >= target_time:
            btn.config(text="Stop", state="normal", bg="#ff4c4c")
            # Play sound in separate thread
            sound_thread = threading.Thread(target=play_alarm_sound, daemon=True)
            sound_thread.start()
            break
        time.sleep(0.5)  # check twice per second

def run_alarm_app():
    global alarm_active, stop_alarm_flag

    root = tk.Tk()
    root.title("⏰ Modern Alarm App")
    root.geometry("400x250")
    root.resizable(False, False)
    root.configure(bg="#1e1e2f")

    title = tk.Label(root, text="Set Your Alarm", font=("Helvetica", 20, "bold"),
                     bg="#1e1e2f", fg="#ffffff")
    title.pack(pady=15)

    alarm_var = tk.StringVar()
    entry = tk.Entry(root, textvariable=alarm_var, font=("Helvetica", 16),
                     bg="#2b2b44", fg="#ffffff", justify="center", insertbackground="white")
    entry.pack(pady=10)

    info_label = tk.Label(root, text="Enter time like 04:00PM or 04:00AM",
                          font=("Helvetica", 10), bg="#1e1e2f", fg="#bbbbff")
    info_label.pack(pady=5)

    def set_alarm_action():
        global alarm_active, stop_alarm_flag
        if not alarm_active:
            alarm_time_str = alarm_var.get()
            if not alarm_time_str:
                messagebox.showwarning("Error", "Please enter a valid time!")
                return
            try:
                now = datetime.datetime.now()
                alarm_time_obj = datetime.datetime.strptime(alarm_time_str.upper(), "%I:%M%p")
                # combine with today's date
                alarm_time = now.replace(hour=alarm_time_obj.hour,
                                         minute=alarm_time_obj.minute,
                                         second=0, microsecond=0)
                if alarm_time < now:
                    # if the time is already passed today, set for tomorrow
                    alarm_time += datetime.timedelta(days=1)
            except ValueError:
                messagebox.showwarning("Error", "Invalid time format! Use HH:MMAM/PM")
                return

            set_btn.config(state="disabled", bg="#444")
            threading.Thread(target=alarm_checker, args=(alarm_time, set_btn), daemon=True).start()
            messagebox.showinfo("Success", f"Alarm set for {alarm_time_str}")

        else:
            # Stop button pressed
            stop_alarm_flag = True
            set_btn.config(text="Set Alarm", state="normal", bg="#6a5acd")
            alarm_active = False

    set_btn = tk.Button(root, text="Set Alarm", font=("Helvetica", 14, "bold"),
                        bg="#6a5acd", fg="#ffffff", activebackground="#483d8b",
                        command=set_alarm_action)
    set_btn.pack(pady=20)

    root.mainloop()
