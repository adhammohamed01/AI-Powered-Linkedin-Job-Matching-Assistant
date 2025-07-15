import customtkinter
import subprocess
import sys
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

def launch_job_seeker():
    subprocess.Popen([sys.executable, "program_gui.py"])

def launch_employer():
    subprocess.Popen([sys.executable, "employer.py"])

app = customtkinter.CTk()
app.title("Job Assistant Launcher")
app.geometry("400x300")

title = customtkinter.CTkLabel(app, text="Welcome to Job Assistant", font=("Arial", 22, "bold"))
title.pack(pady=30)

btn1 = customtkinter.CTkButton(app, text="🎯 Job Seeker", command=launch_job_seeker)
btn1.pack(pady=10)

btn2 = customtkinter.CTkButton(app, text="🧑‍💼 Employer", command=launch_employer)
btn2.pack(pady=10)

app.mainloop()
