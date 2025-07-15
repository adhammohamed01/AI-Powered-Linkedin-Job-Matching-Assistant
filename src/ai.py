from numpy import dot
from numpy.linalg import norm
from extractfunctions import replace_spaces_in_skills
# config = AutoConfig.from_pretrained("llama")
# config.quantization_config = None i think i should delete

# model=get_model()

def Skill_to_list(skills_string):
    return [skill.strip().lower() for skill in skills_string.split(',') if skill.strip()]

def generate_response(prompt,llama_model, tokenizer, max_new_tokens=100):
    # inputs = tokenizer(prompt, return_tensors="pt").to(llama_model.device)
    # with torch.no_grad():
    #     outputs = llama_model.generate(
    #         **inputs,
    #         max_new_tokens=max_new_tokens,
    #         do_sample=False,
    #         eos_token_id=tokenizer.eos_token_id,
    #         pad_token_id=tokenizer.eos_token_id
    #     )

    

    input_ids = tokenizer.apply_chat_template(
        prompt,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(llama_model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    
    outputs = llama_model.generate(
    input_ids,
    max_new_tokens=256,
    eos_token_id=terminators,
    do_sample=False,  
    num_beams=1,      
    pad_token_id=tokenizer.eos_token_id
    )

    response = outputs[0][input_ids.shape[-1]:]
    response =tokenizer.decode(response, skip_special_tokens=True)
    response=Skill_to_list(response)
    response=replace_spaces_in_skills(response)
    return response




#Cosine similarity function
def are_skills_similar(word1, word2,model,threshold=0.7):
    vec1 = model.wv[word1]
    vec2 = model.wv[word2]
    cosine_similarity = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
    return cosine_similarity >= threshold
    

def compare_skill_lists(job_skills,profile_skills,model,threshold=0.7):
    matched_skills = []
    unmatched_skills = []
    if not job_skills or not profile_skills:
        return {
            "total_skills": 0
        }
    for skill2 in job_skills:
        skill2_lower = skill2.lower()
        found_match = False
        for skill1 in profile_skills:
            skill1_lower = skill1.lower()
            if are_skills_similar(skill1_lower, skill2_lower,model,threshold):
                matched_skills.append(skill2)
                found_match = True
                break  
        if not found_match:
            unmatched_skills.append(skill2)

    total = len(job_skills)
    matched = len(matched_skills)
    score = round((matched / total) * 10, 2)

    return {
        "matched_skills": matched_skills,
        "unmatched_skills": unmatched_skills,
        "total_skills": total,
        "matched_count": matched,
        "score_out_of_10": score
    }





# prompt = """Analyze the following text and extract all mentioned job skills, technical competencies,
#     and professional qualifications. Return only a comma-separated list of specific skills,
#     without any additional commentary or explanations. :\nReady to join one of the fastest-growing agencies in the growth space? You've arrived at the right place!

# We are:

# NoGood is an award-winning, tech-enabled growth consultancy that has fueled the success of some of the most iconic brands in Consumer, AI, B2B SaaS and Healthcare. We are a team of seasoned growth leads, creatives, engineers, and data scientists who unlock rapid, measurable growth for some of the world's category-defining brands. We bring together the art and science of strategy, creative, content, and growth expertise into a single cohesive team, powered by robust data analytics and proprietary AI tech.

# Based in NYC, we support partners globally, with a client roster that includes VC-backed startups, scale-ups, and Fortune 500 companies such as Nike, Oura, Spring Health, TikTok, Intuit, P&G, and more.

# Since 2016, we've been delivering what others only promise. Why settle for good enough when you can be up to NoGood!

# We are looking for:

# We're seeking an exceptional Senior Software Engineer to join our rapidly growing AI Lab. You will play a critical role in driving and accelerating the development of cutting-edge AI use cases, working closely with our Product Lead, Designers and Machine Learning Engineers to design and build scalable, industry-leading AI solutions.

# You'll do:


# Lead the development of our AI platform, focusing on scalability, speed, and user experience
# Architect and develop front-end solutions using React to create smooth, engaging, and intentional user experiences
# Implement back-end infrastructure with a focus on speed, scalability, security, and seamless integration with various platforms via robust API connections
# Utilize DevOps practices to manage the deployment pipeline, ensuring efficient, reliable, and secure software delivery
# Collaborate with UX/UI Designers to translate web designs into functional, intuitive user interfaces
# Work closely with Data Scientists to ensure accurate data collection, analysis, and application within the platform
# Participate in the entire application lifecycle, from coding to debugging and testing, with an emphasis on quality and performance
# Maintain and optimize the performance of existing applications
# Stay up-to-date with emerging technologies and explore potential integrations to enhance our operations.


# You have:


# 5+ years of full-stack development experience with a proven track record of building high usage B2B software applications
# Proficiency in React for front-end development, with a strong understanding of how to build responsive, high-performance web applications
# Experience with server-side languages such as Python, Node.js, or Java
# Strong understanding of DevOps practices and experience in software deployment, including CI/CD pipelines, containerization (e.g., Docker), and cloud infrastructure (AWS, Google Cloud, or Azure)
# Solid knowledge of database management systems (e.g., MySQL, PostgreSQL, MongoDB)
# Experience with RESTful APIs, API integration, and data exchange formats (JSON, XML)
# Familiarity with software development best practices, including version control (Git), testing, and continuous integration/deployment (CI/CD)
# Excellent problem-solving skills and the ability to debug complex systems
# Strong leadership and communication skills, with the ability to collaborate effectively with cross-functional teams
# Passion for ad tech and a desire to work in a fast-paced, innovative startup environment
# BSc in Computer Science, Engineering, or a relevant field


# Benefits & Perks of Becoming a NoGoodie:


# Earn More, Together: Base Pay + Profit Sharing & Commissions Opportunities
# Flex Work Environment: Hybrid at HQ and remote globally
# Set Up Shop: Home Office Stipend
# Recharge Anytime: Flexible PTO Plan
# Level Up: Mentorship & Career Growth Support
# Always Be Learning: Access to Top-tier Resources & Industry Experts
# Work Hard, Play Harder: Quarterly Team Trips (Onsite and Offsite)
# Fuel Your Day: Free Lunch, Snacks, Cold Brew, & Happy Hours
# Grow With Us: Endless Opportunities to Lead & Succeed
# Keep on Shining: Ongoing Development Programs
# .\n\nSkills:\n"""
# output = generate_response(prompt)
# print(output)



#Similarity function by the model
# def are_skills_similar(word1, word2, threshold=0.7):
#     try:
#         similarity = model.wv.similarity(word1, word2)
#         return similarity >= threshold
#     except KeyError as e:
#         print(f"Word not found in vocabulary: {e}")
#         return False