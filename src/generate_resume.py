import re
import logging
from dotenv import load_dotenv
from openai import OpenAI

from src.scrape_in import get_linkedin_data

load_dotenv()
model_api_client = OpenAI()
MODEL = "gpt-4"
HELPER_MODEL = "gpt-3.5-turbo"

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
        personal_info += '\nX.com profile: ' + user_data['twitter']
    if user_data['additionals']:
        personal_info += '\n##Additional information, projects etc.: \n' + user_data['additionals']

    return personal_info
    

def create_prompt(job_desc: str, personal_info: str, linkedin_data: str):
    prompt = f"Please create a custom resume in Markdown format for a position described below.\
        Here are the details to include:\n\
        '{personal_info}\n{linkedin_data}'\n\
        Job description:\n\
        '{job_desc}'\n\
        Please structure the resume to highlight my qualifications effectively, with a professional\
        layout suitable for a given job application. Include emojis to make it more colorful😊🚀\
        don't include any unnecessary informations🔥."
    return prompt


def prompt_llm(prompt, model=MODEL):
    logger.info(f"Prompting the LLM, model🦾: {model}")
    chat_completion = model_api_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    finish_reason = chat_completion.choices[0].finish_reason
    logger.info(f"Completion finished🏁, reason {finish_reason}")
    logger.info(f"Completion usage📶: {chat_completion.usage}")
    
    output = chat_completion.choices[0].message.content

    return output


def postprocess(resume_content):
    markdown_content = re.search(r'.*```markdown(.*?)```', resume_content, re.DOTALL)
    if markdown_content:
        resume_content = markdown_content.group(1)
    else:
        markdown_content = re.search(r'.*```md(.*?)```', resume_content, re.DOTALL)
        if markdown_content:
            resume_content = markdown_content.group(1)

    resume_content = re.sub(r'```', '', resume_content)
    resume_content = re.sub(r'\:[a-z_]*\:', '', resume_content)
    resume_content = re.sub(r':\W+:', '', resume_content)
    return resume_content


def get_resume_content(user_data: dict) -> tuple([str, str]):
    user_url = user_data['linkedin_url']
    linkedin_data = get_linkedin_data(user_url)
    personal_info = convert_user_data_to_string(user_data)

    prompt = create_prompt(user_data['job_description'], personal_info, linkedin_data)
    resume_content = prompt_llm(prompt)

    try:
        clean_resume_content = postprocess(resume_content)
    except Exception as e:
        logger.error(f'Error with postprocessing: {e}')
        clean_resume_content = resume_content
    
    try:
        prompt = f"Summarize the following job descrption in 5 words:\n{user_data['job_description']}"
        summary = prompt_llm(prompt, model=HELPER_MODEL)
        if len(summary.split(' ')) >= 10:
            summary = ' '.join(summary.split(' ')[:10])
    except Exception as e:
        logger.error(f'Error with prompting of {HELPER_MODEL} -- {e}')
        summary = ''

    return clean_resume_content, summary


def regenerate_resume_content(user_data:dict, old_resume_content: str, job_desc:str):

    linkedin_data = get_linkedin_data(user_data['linkedin_url'])
    personal_info = convert_user_data_to_string(user_data)
    
    # prompt = create_prompt(job_desc, personal_info, linkedin_data)
    prompt = f"Given this job description: \"{job_desc}\"\
    and follwoing candidate information: \"'{personal_info}\n{linkedin_data}'\n\"\
        you have provided following resume:\n```{old_resume_content}```\n\
        Please improve it and retur new version in markdown format."
    
    new_resume = prompt_llm(prompt, model=MODEL)

    try:
        clean_resume_content = postprocess(new_resume)
    except Exception as e:
        logger.error(f'Error with postprocessing: {e}')
        clean_resume_content = new_resume

    return clean_resume_content
