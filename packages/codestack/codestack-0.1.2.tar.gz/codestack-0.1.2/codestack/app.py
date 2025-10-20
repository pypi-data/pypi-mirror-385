import os
import time
import random
import json
import google.generativeai as genai
from .prompt import system_prompt
from .spinner import spinner
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_code(prompt, output_dir="generated_app"):
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL_NAME"))
    try:
        response = model.generate_content("Just say what is 1+1?")
    except Exception as e:
        print("Please check your GOOGLE_API_KEY and GEMINI_MODEL_NAME in the .env file. If not set, set them correctly in the .env file.\n")
        print(f"Error occurred: {e}")
    
    max_retries=10
    backoff=2
    stop_spinner = spinner("Codestack is building your project (this may take a while)")
    for attempt in range(1, max_retries + 1):
        try:
            #Generate model output
            response = model.generate_content(system_prompt + "\nPrompt:\n" + prompt)
            text_output = (response.text or "").strip()

            #sanitize output
            text_output = text_output.replace("```json", "").replace("```", "").strip()

            #locate JSON block
            first_brace = text_output.find("{")
            if first_brace == -1:
                raise ValueError("No JSON found in response.")
            text_output = text_output[first_brace:]

            #to parse JSON
            data = json.loads(text_output)

            return data

        except Exception:
            sleep_time = backoff + random.uniform(0, 0.3)
            time.sleep(sleep_time)
            backoff *= 2
        finally:
            stop_spinner()
    
def save_files(data, output_dir="generated_app"):
    for f in data.get("files", []):
        filepath = os.path.join(output_dir, f["path"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f["content"])

    print(f"Codestack generated the project in the folder : '{output_dir}'")


def build_project(prompt:str,output_dir:str):
     """
        Generate a complete executable project based on a natural language instructions 
        and save it to the specified output directory.

        This function to create all necessary files 
        for the project, including source code, configuration files, 
        and dependencies, depending on the specified tech stack 
        inferred from the instructions.

        Parameters
        prompt : str
            A natural language description of the project to be generated. 
            For example, "Create a React todo app with Tailwind CSS" or 
            "Build a Python REST API with FastAPI" or 
            "Create a Finance calculator using html, css and javascript".
        
        output_dir : str
            The directory path or the project path where the generated project files 
            will be saved. The directory will be created if it 
            does not exist.

        Returns
        None
            All generated files are saved to the specified output directory.

        Notes
        - It can generate projects in any programming language, technology stack or 
        framework based on the instructions. Codestack is a versatile developer for all your needs.
        - Please be as specific as possible in your prompt to get the best results.
    """
     data = generate_code(prompt, output_dir=output_dir)
     save_files(data, output_dir=output_dir)
    

