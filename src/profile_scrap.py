    # %%
def profile_scrap(profile_link=""):

    import warnings
    warnings.filterwarnings("ignore")

    # %%
    import os
    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    from time import sleep

    from dotenv import load_dotenv
    load_dotenv(override=True)


    # %%
    os.environ['EMAIL'],os.environ['PASSWORD']

    # %%
    driver = webdriver.Chrome()

    # %%
    driver.get('https://www.linkedin.com/login')

    # %%
    from selenium.webdriver.common.by import By
    email_input = driver.find_element(By.ID, "username")
    email_input.send_keys(os.environ['EMAIL'])
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(os.environ['PASSWORD'])
    driver.find_element(By.CSS_SELECTOR, ".btn__primary--large.from__button--floating").click()


    # %%
    import time
    time.sleep(20)
    driver.get(profile_link)
    

    # %%
    scrapped_data={}
    import time
    time.sleep(15)

    # %%
    import re
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    name = soup.find('h1', {'class': re.compile(r'inline t-24 v-align-middle break-words')})
    name = name.get_text().strip() 
    scrapped_data['name']=name
    scrapped_data['profile_link']=profile_link


    # %%
    headline=soup.find('div',{'class':'text-body-medium break-words'})
    headline=headline.get_text().strip()
    scrapped_data['headline']=headline
    scrapped_data

    # %% [markdown]
    # see more handle
    # 

    # %%
    from selenium.webdriver.common.by import By

    # Find elements (returns a list)
    buttons = driver.find_elements(By.CSS_SELECTOR, ".inline-show-more-text__button.inline-show-more-text__button--light.link")

    # Click only if the button exists
    if buttons:
        for button in buttons:
            button.click()
            print("Button clicked!")
    else:
        print("Button not found, skipping click.")


    # %%
    import time
    time.sleep(10)

    # %%
    import time
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    about=soup.find('div', {'class':'display-flex ph5 pv3'})
    



    # %%
    import time
    time.sleep(11)

    # %%
    try:
        aboutt=about.get_text().strip()
        scrapped_data['about']=aboutt
    except Exception as e:
        print("Error:", e)    
    import time
    time.sleep(10)
    # %%

    # %%
    import time
    driver.get(profile_link)
    time.sleep(10)



    # %%
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    sections = soup.find_all('section', {'class': 'artdeco-card pv-profile-card break-words mt2'})
    for sect in sections:
        if sect.find('div', {'id': 'education'}):
            educations = sect
        
    

    # %%
    try:
        items = educations.find_all(
            "div",
            {"data-view-name": "profile-component-entity"},
            class_=lambda x: x and len("".join(x.split())) > 86
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        items = []  # Assign an empty list to avoid further issues

    
    


    # %%

    def get_edu(item):
        item_dict = {}
        spans = item.find_all('span', {'class': 'visually-hidden'})
        item_dict['college'] = spans[0].get_text().strip()
        item_dict['degree'] = spans[1].get_text().strip()
        item_dict['duration'] = spans[2].get_text().strip()
        return item_dict
    try:
        item_list = []
        for item in items:
            item_list.append(get_edu(item))

        item_list
        scrapped_data['education']=item_list
    except Exception as e:
        print("Error:", e)    
    scrapped_data

    # %%
    import time
    driver.get(profile_link)
    time.sleep(20)

    # %%
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    import time
    from bs4 import BeautifulSoup


    try:
        # Open LinkedIn profile page

        links = []
        sections = []
        skills = None  # Ensure skills is initialized

        try:
            # Find the "Show all skills" button (ignoring the number in ID)
            link = driver.find_element(By.XPATH, "//a[starts-with(@id, 'navigation-index-Show-all-') and contains(@id, '-skills')]")
            
            # Click the button
            link.click()
            print("Link clicked!")

            # Wait for the skills section to load
            time.sleep(10)

            # Get updated page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            # Extract skills section
            skills = soup.find('section', {'class': 'artdeco-card pb3'})

        except Exception as e:
            print("Link not found, skipping click.")

            # Get page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            # Find all sections
            sections = soup.find_all('section', {'class': 'artdeco-card pv-profile-card break-words mt2'})

            for sec in sections:
                if sec.find('div', {'id': 'skills'}):
                    skills = sec
                    break  # Stop once found

        if skills:
            print("Skills section found!")
        else:
            print("Skills section not found.")

    except Exception as e:
        print("Error:", e)




    # %%
    try:
        skills_div=skills.find_all("div", {
            "data-view-name": "profile-component-entity"
        }, class_=lambda x: x and len("".join(x.split())) > 86)
        len(skills_div)
    except Exception as e:
        print("Error:", e)    
    
    # %%

    def get_skill(skill):
        skill_dict = {}

        skill_name = skill.find('div', {'class': 'display-flex flex-wrap align-items-center full-height'})
        if skill_name:
            skill_name = skill_name.find('span', {'class': 'visually-hidden'})
            if skill_name:
                skill_name = skill_name.get_text().strip()
            else:
                skill_name = "N/A"
        else:
            skill_name = "N/A"

        skill_dict['skill_name'] = skill_name

        item_list = []
        spans = skill.find_all('span', {'class': 'visually-hidden'})
        item_dict = {}

        for i in range(len(spans)):
            item_dict[str(i + 1)] = spans[i].get_text().strip()
        
        item_list.append(item_dict)
        skill_dict['info'] = item_list

        return skill_dict

    # Extracting skill details
    skill_list = []
    try:
        for skill in skills_div:  # Make sure skills_div contains the correct elements
            skill_list.append(get_skill(skill))

        scrapped_data['skills'] = skill_list
        scrapped_data
    except Exception as e:
        print("Error:", e)

    # %%
    import time
    driver.get(profile_link)
    time.sleep(10)

    # %%
    print(scrapped_data)

    # %%
 

    # Flatten the dictionary into a list of rows
    import pandas as pd
    import json
    with open('../data/profile_data_tutorial.json', 'w') as f:
        json.dump(scrapped_data, f, indent=4)

    with open('../data/profile_data_tutorial.json', 'r') as f:
        scrapped_data = json.load(f)

    # Function to flatten nested lists into readable text
    def flatten_list(data):
        if isinstance(data, list):
            return "; ".join([flatten_list(item) if isinstance(item, dict) else str(item) for item in data])
        elif isinstance(data, dict):
            return "; ".join([f"{k}: {v}" for k, v in data.items()])
        return str(data)

    # Flattening the data
    flattened_data = {key: flatten_list(value) for key, value in scrapped_data.items()}

    # Convert to DataFrame
    df = pd.DataFrame([flattened_data])

    # Save as CSV
    df.to_csv("../data/profile_data.csv", index=False)

    print("CSV file saved successfully!")




    # %%



