import pandas as pd
from tkinter import ttk
import customtkinter
import threading
from extractfunctions import extract_skill_names, replace_spaces_in_skills
from load_model import get_model, get_llama_model
from ai import generate_response, compare_skill_lists
from job_scrapper import scrape_jobs
from profile_scrap import profile_scrap

models_loaded_event = threading.Event()

def load_models_in_background():
    global model, llama_model, tokenizer
    model = get_model()
    llama_model, tokenizer = get_llama_model()
    models_loaded_event.set()

threading.Thread(target=load_models_in_background, daemon=True).start()

def run_main_in_thread():
    threading.Thread(target=main_and_notify, daemon=True).start()

def main_and_notify():
    try:
        main()
    finally:
        window.after(0, on_main_done)

def wait_until_models_loaded():
    if models_loaded_event.is_set():
        status_label.configure(text="Matching jobs...")
        window.after(100, run_main_in_thread)
    else:
        window.after(200, wait_until_models_loaded)

# GUI setup
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

def on_main_done():
    status_label.configure(text="✅ Done!")
    submit_button.configure(state="normal")

def on_submit():
    submit_button.configure(state="disabled")
    status_label.configure(text="🔄 Starting...")

    global profile_link, job_name, job_country, job_state, job_type, remote_or_onsite, experience_level
    profile_link = str(profile_link_entry.get().strip())
    job_name = str(Job_Name_entry.get())
    job_country = str(Job_country_entry.get())
    job_state = str(Job_state_entry.get())
    job_type = str(Job_Type_entry.get())
    remote_or_onsite = str(Remote_Onsite_entry.get())
    experience_level = str(Experience_years_entry.get())

    status_label.configure(text="🔍 Scraping profile...")
    window.after(100, run_profile_scrap)

def run_profile_scrap():
    def background():
        profile_scrap(profile_link)
        window.after(0, lambda: status_label.configure(text="📝 Scraping jobs..."))
        window.after(100, run_scrape_jobs)

    threading.Thread(target=background, daemon=True).start()

def run_scrape_jobs():
    def background():
        scrape_jobs(job_name, [job_state, job_country], job_type, remote_or_onsite, experience_level)
        window.after(0, lambda: status_label.configure(text="🤖 Waiting for models..."))
        window.after(100, wait_until_models_loaded)

    threading.Thread(target=background, daemon=True).start()

window = customtkinter.CTk()
window.title("Job Search Assistant")
window.geometry("1000x700")

title_label = customtkinter.CTkLabel(window, text="Job Search Assistant", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

frame = customtkinter.CTkFrame(master=window)
frame.pack(padx=20, pady=10, fill="both", expand=True)

user_info_frame = customtkinter.CTkFrame(master=frame)
user_info_frame.pack(pady=10, padx=10, fill="x")

# Input fields
profile_link_label = customtkinter.CTkLabel(user_info_frame, text="Profile Link")
profile_link_label.grid(row=0, column=0, sticky="w")
profile_link_entry = customtkinter.CTkEntry(user_info_frame, width=200)
profile_link_entry.grid(row=1, column=0, padx=10, pady=5)

Job_Name_label = customtkinter.CTkLabel(user_info_frame, text="Job Name")
Job_Name_label.grid(row=0, column=1, sticky="w")
Job_Name_entry = customtkinter.CTkEntry(user_info_frame, width=200)
Job_Name_entry.grid(row=1, column=1, padx=10, pady=5)

Experience_years_label = customtkinter.CTkLabel(user_info_frame, text="Years of experience(optional)")
Experience_years_label.grid(row=0, column=2, sticky="w")
Experience_years_entry = customtkinter.CTkComboBox(user_info_frame, values=[
    " ", "from 0 to 6 months", "from 0 to 2 years", "from 2 to 5 years", "from 5 to 10 years", "from 10 to 15 years", "15+ years"
])
Experience_years_entry.grid(row=1, column=2, padx=10, pady=5)

Job_country_label = customtkinter.CTkLabel(user_info_frame, text="Job Country")
Job_country_label.grid(row=2, column=0, sticky="w")
Job_country_entry = customtkinter.CTkEntry(user_info_frame, width=200)
Job_country_entry.grid(row=3, column=0, padx=10, pady=5)

Job_state_label = customtkinter.CTkLabel(user_info_frame, text="State of Job Country")
Job_state_label.grid(row=2, column=1, sticky="w")
Job_state_entry = customtkinter.CTkEntry(user_info_frame, width=200)
Job_state_entry.grid(row=3, column=1, padx=10, pady=5)

Job_Type_label = customtkinter.CTkLabel(user_info_frame, text="Job Type(optional)")
Job_Type_label.grid(row=4, column=1, sticky="w")
Job_Type_entry = customtkinter.CTkComboBox(user_info_frame, values=[
    " ", "full time", "part time", "contract", "temporary", "volunteer", "internship", "other"
])
Job_Type_entry.grid(row=5, column=1, padx=0, pady=0)

Remote_Onsite_label = customtkinter.CTkLabel(user_info_frame, text="Remote or Onsite(optional)")
Remote_Onsite_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
Remote_Onsite_entry = customtkinter.CTkComboBox(user_info_frame, values=[
    " ", "on-site", "remote", "hybrid"
])
Remote_Onsite_entry.grid(row=5, column=0, padx=10, pady=5)

submit_button = customtkinter.CTkButton(frame, text="Submit", command=on_submit)
submit_button.pack(pady=10)
status_label = customtkinter.CTkLabel(frame, text="", font=("Arial", 14), text_color="gray")
status_label.pack(pady=5)

def load_profile_data(csv_path):
    profile_data = pd.read_csv(csv_path)
    return profile_data

def load_job_data(csv_path):
    job_data = pd.read_csv(csv_path)
    return job_data

def main():
    profile_path = "../data/profile_data.csv"
    job_path = "../data/jobs.csv"
    output_path = "../data/matched_results.csv"

    profile_data = load_profile_data(profile_path)
    profile_data = profile_data['skills'][0]

    job_data = load_job_data(job_path)
    job_data_description = job_data['Description']
    job_data_link = job_data['Link']

    profile_skills = extract_skill_names(profile_data)

    results = []
    for i in range(len(job_data)):
        description = job_data_description[i]
        link = job_data_link[i]

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are an AI that extracts only technical skills from job descriptions. "
                    "Return a clean, comma-separated list. Do not add any explanations, intros, or extra text. "
                    "The first word in the output must be a skill. No greetings or summaries."
                )
            },
            {
                "role": "user",
                "content": (
                    "Extract ALL mentioned hard skills, technical skills, tools, programming languages, frameworks, methodologies, "
                    "and professional qualifications from the following job description.\n\n"
                    "Rules:\n"
                    "1. Only extract technical/professional terms — no soft skills.\n"
                    "2. Output only a clean, comma-separated list.\n"
                    "3. No duplicate skills.\n"
                    "4. Exclude general or vague phrases.\n"
                    "5. Include specific technologies only (e.g., 'Angular' not 'JavaScript frameworks').\n"
                    "6. Return the list only — no additional text.\n\n"
                    f"Job description:\n{description}"
                )
            }
        ]

        job_skills = generate_response(prompt, llama_model, tokenizer)
        result = compare_skill_lists(job_skills, profile_skills, model, threshold=0.7)
        result["job_link"] = link
        results.append(result)

    results.sort(key=lambda x: x['score_out_of_10'], reverse=True)
    pd.DataFrame(results).to_csv(output_path, index=False)

    tree_frame = customtkinter.CTkFrame(master=window)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("job_link", "matched_skills", "unmatched_skills", "total_skills", "matched_count", "score_out_of_10")
    global results_tree
    results_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

    for col in columns:
        results_tree.heading(col, text=col)
        results_tree.column(col, width=150, anchor="w")

    for match in results:
        results_tree.insert("", "end", values=(
            match["job_link"],
            match["matched_skills"],
            match["unmatched_skills"],
            match["total_skills"],
            match["matched_count"],
            match["score_out_of_10"]
        ))

    results_tree.pack(fill="both", expand=True)

    detail_box = customtkinter.CTkTextbox(tree_frame, height=200, wrap="word")
    detail_box.pack(fill="x", padx=10, pady=10)

    def on_tree_select(event):
        selected = results_tree.focus()
        if not selected:
            return
        values = results_tree.item(selected, "values")
        if len(values) < 5:
            return

        job_link, matched_skills, unmatched_skills, total_skills, matched_count, score_out_of_10 = values

        detail_box.delete("1.0", "end")
        detail_box.insert("end", f"Job Link: {job_link}\n\n")
        detail_box.insert("end", f"Total Skills: {total_skills}\n")
        detail_box.insert("end", f"Matched Count: {matched_count}\n")
        detail_box.insert("end", f"Score out of 10: {score_out_of_10}\n")
        detail_box.insert("end", "Matched Skills:\n")
        detail_box.insert("end", f"{matched_skills}\n\n")
        detail_box.insert("end", "Unmatched Skills:\n")
        detail_box.insert("end", f"{unmatched_skills}")

    results_tree.bind("<<TreeviewSelect>>", on_tree_select)

window.mainloop()
