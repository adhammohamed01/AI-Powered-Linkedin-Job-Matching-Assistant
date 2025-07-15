import re
import pandas as pd
import customtkinter
from tkinter import filedialog, ttk
from extractfunctions import replace_spaces_in_skills, extract_skill_names
from ai import compare_skill_lists
from load_model import get_model
import threading

# Load AI model
model = None

def load_model_background():
    global model
    model = get_model()
   


# Appearance
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Globals
csv_file_path = None

# ------------------------- Logic Functions -------------------------

def takeskills(text):
    skills = re.findall(r'^\s*(.+?)\s*$', text, re.MULTILINE)
    skills = [skill.lower() for skill in skills]
    return replace_spaces_in_skills(skills)

def load_profile_data(path):
    return pd.read_csv(path)

def match_skills(job_data, profiledata, model):
    results = []
    job_skills = takeskills(job_data)
    profiledata_skills = profiledata['skills']
    profiledata_link = profiledata['profile_link']
    profiledata_name = profiledata['name']

    for i in range(len(profiledata_skills)):
        profile_skills = extract_skill_names(profiledata_skills[i])
        result = compare_skill_lists(job_skills, profile_skills, model)
        result["profile_name"] = profiledata_name[i]
        result["profile_link"] = profiledata_link[i]
        results.append(result)

    results.sort(key=lambda x: x.get("score_out_of_10", 0), reverse=True)
    return results

# ------------------------- GUI Functions -------------------------

def upload_csv():
    global csv_file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        csv_file_path = file_path
        csv_label.configure(text=f"CSV Selected: {file_path.split('/')[-1]}", text_color="lightgreen")

def start_matching():
    match_button.configure(state="disabled")
    result_label.configure(text="Matching profiles, please wait...", text_color="yellow")
    load_model_background()
    threading.Thread(target=run_matching).start()

def run_matching():
    global results_tree
    
    threading.Thread(target=load_model_background, daemon=True).start()
    if not csv_file_path:
        result_label.configure(text="Please upload a CSV file.", text_color="red")
        return

    job_text = job_skills_input.get("1.0", "end").strip()
    if not job_text:
        result_label.configure(text="Please enter job-required skills.", text_color="red")
        return

    try:
        profile_df = load_profile_data(csv_file_path)
        required_columns = {"name", "profile_link", "skills"}
        if not required_columns.issubset(profile_df.columns):
            result_label.configure(text="CSV must contain 'name', 'profile_link', 'skills' columns.", text_color="red")
            return

        results = match_skills(job_text, profile_df, model)

        results.sort(key=lambda x: x['score_out_of_10'], reverse=True)    
        pd.DataFrame(results).to_csv("../data/emloyer_match.csv", index=False)
        # Clear old widgets if re-running
        for widget in tree_frame.winfo_children():
            widget.destroy()

        columns = ("profile_name", "profile_link", "matched_skills", "unmatched_skills", "total_skills", "matched_count", "score_out_of_10")
        results_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        for col in columns:
            results_tree.heading(col, text=col)
            results_tree.column(col, width=150, anchor="w")

        for match in results:
            results_tree.insert("", "end", values=(
                match["profile_name"],
                match["profile_link"],
                ", ".join(match["matched_skills"]),
                ", ".join(match["unmatched_skills"]),
                match["total_skills"],
                match["matched_count"],
                match["score_out_of_10"]
            ))

        results_tree.pack(fill="both", expand=True)

        # Detail box
        detail_box = customtkinter.CTkTextbox(tree_frame, height=200, wrap="word")
        detail_box.pack(fill="x", padx=10, pady=10)

        def on_tree_select(event):
            selected = results_tree.focus()
            if not selected:
                return
            values = results_tree.item(selected, "values")
            detail_box.delete("1.0", "end")
            detail_box.insert("end", f"Name: {values[0]}\nProfile Link: {values[1]}\n\n")
            detail_box.insert("end", f"Matched Skills:\n{values[2]}\n\n")
            detail_box.insert("end", f"Unmatched Skills:\n{values[3]}\n\n")
            detail_box.insert("end", f"Total Skills: {values[4]}\n")
            detail_box.insert("end", f"Matched Count: {values[5]}\n")
            detail_box.insert("end", f"Score (out of 10): {values[6]}\n")

        results_tree.bind("<<TreeviewSelect>>", on_tree_select)

        result_label.configure(text="✅ Matching Complete!", text_color="green")
        match_button.configure(state="normal")

    except Exception as e:
        result_label.configure(text=f"Error: {e}", text_color="red")
        match_button.configure(state="normal")

# ------------------------- GUI Setup -------------------------

app = customtkinter.CTk()
app.title("Skill Matcher – Profiles to Job")
app.geometry("1000x700")

title_label = customtkinter.CTkLabel(app, text="Skill Matcher for Employee Profiles", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

frame = customtkinter.CTkFrame(app)
frame.pack(padx=20, pady=10, fill="both", expand=True)

# Job skill input
job_label = customtkinter.CTkLabel(frame, text="Enter Required Job Skills (one per line):")
job_label.pack(anchor="w", padx=10, pady=(10, 0))

job_skills_input = customtkinter.CTkTextbox(frame, height=150, width=900)
job_skills_input.pack(padx=10, pady=5)

# CSV upload
csv_label = customtkinter.CTkLabel(frame, text="No CSV uploaded yet")
csv_label.pack(pady=5)

upload_button = customtkinter.CTkButton(frame, text="Upload Profile CSV", command=upload_csv)
upload_button.pack(pady=5)

# Match button
match_button = customtkinter.CTkButton(frame, text="Run Matching", command=start_matching)
match_button.pack(pady=10)

# Status label
result_label = customtkinter.CTkLabel(frame, text="", text_color="gray")
result_label.pack(pady=5)

# Treeview frame
tree_frame = customtkinter.CTkFrame(master=app)
tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

app.mainloop()
