import re

def replace_spaces_in_skills(skills_list):
    return [re.sub(r'(?<!,)\s+(?![,])', '_', skill) for skill in skills_list]


def extract_skill_names(text):
  
    
    matches = re.findall(r"skill_name:\s*([^;]+);", text)
    
    
    skill_names = sorted(set(match.strip() for match in matches))
    skill_names = replace_spaces_in_skills(skill_names)
    return skill_names

import re

def extract_skills_from_prompt(text):
    match = re.search(r"Extracted skills:\s*(.+)", text, re.DOTALL)

    if not match:
        return []

    skills_text = match.group(1)
    skills_list = []
    for skill in skills_text.split(','):
        skill = skill.strip()
        if 2 <= len(skill) <= 25:
            skills_list.append(skill)

    if len(skills_list) < 6:
        return []

    return skills_list


