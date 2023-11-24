import re
import logging
from dotenv import load_dotenv
from openai import OpenAI

from src.scrape_in import get_linkedin_data

load_dotenv()
model_api_client = OpenAI()
MODEL = "gpt-4"

logger = logging.getLogger(__file__)

def convert_user_data_to_string(user_data: dict) -> str:
    personal_info = 'Name: ' + user_data['full_name']
    personal_info += '\nEmail: ' + user_data['email']
    personal_info += '\nPhone number: ' + str(user_data['phone_number'])
    if user_data['github']:
        personal_info += '\nGithub: ' + user_data['github']
    if user_data['personal_website']:
        personal_info += '\nPersonal Website: ' + user_data['personal_website']
    if user_data['twitter']:
        personal_info += '\n==X.com profile: ' + user_data['twitter']

    return personal_info
    

def create_prompt(job_desc: str, personal_info: str, linkedin_data: str):
    prompt = f"Please create a custom resume in Markdown format for a position described below.\
        Here are the details to include:\n\
    {personal_info}\n{linkedin_data}\n\
    **Desired job description**\n\
    {job_desc}\m\
    Please structure the resume to highlight my qualifications effectively, with a professional\
        layout suitable for a given job application. Include emojis to make it more colorful😊🚀"
    return prompt


def prompt_llm(prompt):
    logger.info(f"Prompting the LLM, model🦾: {MODEL}")
    chat_completion = model_api_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt,
            }
        ],
        model=MODEL,
    )
    finish_reason = chat_completion.choices[0].finish_reason
    logger.info(f"Completion finished🏁, reason {finish_reason}")
    logger.info(f"Completion usage📶: {chat_completion.usage}")
    
    output = chat_completion.choices[0].message.content

    return output


def postprocess(resume_content):
    resume_content = re.sub(r'```markdown|```', '', resume_content)
    resume_content = re.sub(r':\W+:', '', resume_content)
    return resume_content


def get_resume_content(user_data: dict):
    user_url = user_data['linkedin_url']
    linkedin_data = get_linkedin_data(user_url)
    personal_info = convert_user_data_to_string(user_data)

    prompt = create_prompt(user_data['job_description'], personal_info, linkedin_data)
    try:
        resume_content = prompt_llm(prompt)
    except Exception as api_error:
        logger.error(f'🫨Error occured while prompting LLM:\n{api_error}')
        resume_content = ''

    resume_content = postprocess(resume_content)

    return resume_content
