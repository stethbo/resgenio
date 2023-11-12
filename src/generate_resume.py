import os
import tempfile
from dotenv import load_dotenv
from openai import OpenAI

from src.scrape_in import get_linkedin_data

load_dotenv()
model_api_client = OpenAI()
MODEL = "gpt-3.5-turbo"


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
    prompt = f"Given the job description:\n'{job_desc}'\n Write a tailored resume / CV, fill free to change the order of the \
    user information and sills, place it in mardown format, you can add some emojis to make it pretty, the candidate information are here: '{personal_info}'\n\n{linkedin_data}"
    return prompt


def prompt_llm(prompt):
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
    print(f"Completion usage: {chat_completion.usage}")
    print(f"Completion finish reason {finish_reason}")
    output = chat_completion.choices[0].message.content

    return output
    

def get_resume_content(user_data: dict):
    user_url = user_data['linkedin_url']
    linkedin_data = get_linkedin_data(user_url)
    personal_info = convert_user_data_to_string(user_data)

    prompt = create_prompt(user_data['job_description'], personal_info, linkedin_data)
    resume_content = prompt_llm(prompt)

    return resume_content
