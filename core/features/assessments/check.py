import os
import re
import time
import json
import asyncio
from tqdm import tqdm
from typing import List, Dict, Any, Tuple, Union

from core.features.assessments.prompts import SIMPLE_ASSIGNMENT_CHECK_PROMPT
from core.features.utils import add_dicts, calculate_cost_gpt4_turbo
from core.features.provider import creator, async_creator, text_model_defaults


class AssignmentCheck:

    def __init__(self) -> None:
        self.duplicates = []


    def question_or_answer_cell(self, s):

        """
        Function to check the correct tag for a question or an answer cell.
        Must match - "#q<some + integer>" or "#a<some + integer>"
        """

        pattern = r"^#[aq]\d+"
        s = s.strip()
        return bool(re.match(pattern, s))
    
    def answer_cell(self, s):

        """
        Function to check the correct tag for a question or an answer cell.
        Must match - "#q<some + integer>" or "#a<some + integer>"
        """

        pattern = r"^#[a]\d+"
        s = s.strip()
        return bool(re.match(pattern, s))


    def qna_extraction(self, file_path):
        """
        Function to extracts question and answers from the jupyter notebook
        cells with #qn tag and #an tag
        return the dict of all the questions and answers 
        """

        if file_path.endswith(".ipynb"):
            with open(file_path, "r", encoding='utf-8') as f:
                nb = json.load(f)
        else:
            ValueError("File type not supported. Must be a valid Jupyter Notebook file.")

        cells = nb['cells']
        qnas = {}
        for cell in cells:
            if self.question_or_answer_cell(cell['source'][0]):
                qnas[cell['source'][0].strip('#\n')] = "".join(cell['source'][1:])  
        return qnas


    async def question_answer_check(self, qna_dict, tag):

        """
        Main function to check the solution of the answer
        provide obtained marks and feedback
        """

        conversation = [{"role": "system", "content": SIMPLE_ASSIGNMENT_CHECK_PROMPT}]
        user_input = f"""
        
        {qna_dict}

        """
        user_message = {'role': 'user', 'content': user_input}
        conversation.append(user_message)

        response = await async_creator(
            **text_model_defaults,
            messages=conversation
        )    
        response = response.model_dump()
        output = response["choices"][0]["message"]["content"]
        total_usage = response["usage"]
        return {"output": output, "tag": tag, "qna_dict":qna_dict, "total_usage": total_usage}


    async def notebook_check(self, file, qnas, marks):

        """
        This function takes the set of questions and answers and provide a dict with remarks of all questions
        """

        total_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        remarks = {}
        tasks = []
        for i in range(1, len(marks)+1):
            qna_dict = {
                "question": qnas[f"q{i}"],
                "solution": qnas[f"a{i}"],
                "max_marks": marks[f"q{i}"]
            }
            task = self.question_answer_check(qna_dict=qna_dict, tag=f"q{i}")
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        
        for result in results:
            output, usage, tag, qna_dict = json.loads(result['output']), result['total_usage'], result['tag'], result['qna_dict']
            total_usage = add_dicts(total_usage, usage)
            qna_dict.update(output)
            remarks[tag] = qna_dict

        return {file: remarks}, total_usage
    

    async def batch_assessment_check(self, path, remarks_filename="remarks.json", check_duplicates: bool=False):
        """
        This function is the main batch processing function for assessment
        Takes path of folder or notebook, check all the questions of all the notebooks and provide a combined json for remarks

        path: path of a folder full of jupyter notebooks and one marks.json file
        remarks_filename: file name for remarks
        check_duplicates: check if duplicates are present in the folder
        """
        
        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        final_remarks = {}

        remarks_path = "/"
        if os.path.isdir(path):
            print("GOT A DIR")
            file_paths = [os.path.join(path, _file) for _file in os.listdir(path) if _file.endswith('.ipynb')]
            marks_file = next((os.path.join(path, _file) for _file in os.listdir(path) if _file == "marks.json"), None)

            if marks_file is not None:
                with open(marks_file, 'r') as f:
                    marks = json.load(f)
            else:
                raise FileNotFoundError("marks.json file not found")

            print(f"GOT {len(file_paths)} notebooks")
            files_and_qnas = {os.path.basename(file_path): self.qna_extraction(file_path) for file_path in file_paths}
            print("EXTRACTED QNAS")
            if check_duplicates:
                self.duplicates = self.duplicates_checker(files_and_qnas)
                print(f"FOUND DUPLICATES: {self.duplicates}")
            results_path = os.path.join(path, 'results')
            os.makedirs(results_path, exist_ok=True)
            print("CREATED RESULTS FOLDER")

        else:
            raise ValueError('path should be a directory')

        tasks = []
        for file, qna in tqdm(files_and_qnas.items()):
            task = self.notebook_check(file, qna, marks)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        
        for remarks, tokens in results:
            final_remarks.update(remarks)
            total_tokens = add_dicts(total_tokens, tokens)

        try:
            self.add_remarks_to_ipynb(final_remarks, path)
            print("ADDED REMARKS TO IPYNB")
        except:
            Exception("some error in adding remarks to ipynb")

        print("PROCESSING COMPLETE")
        # saving the remarks
        json_remarks = json.dumps(final_remarks, indent=4)
        with open(os.path.join(results_path, remarks_filename), 'w') as f:
            f.write(json_remarks)
        
        print("DONE!")
        gpt_cost = calculate_cost_gpt4_turbo(total_tokens)
        
        if check_duplicates:
            with open(os.path.join(results_path, 'duplicates.json'), 'w') as f:
                dup_json = {'duplicates': self.duplicates}
                f.write(json.dumps(dup_json))
        return total_tokens, gpt_cost
    

    def duplicates_checker(self, content: Dict):

        """
        Identifies files with identical contents in the provided dictionary.

        Args
        content: Dict of filename: content (qnas)

        Returns:
        A list of lists, where each sublist contains filenames that have identical contents.
        Returns None if no duplicates are found or if the input is empty.
        """

        if not content:
            return None

        content_to_filenames = {}
        for filename, content in content.items():
            content_to_filenames.setdefault(str(content), []).append(filename)

        duplicates = [filenames for filenames in content_to_filenames.values() if len(filenames) > 1]
        return duplicates if duplicates else None
    
    def add_remarks_to_ipynb(self, remarks, folder_path):
        
        check_nb_folder_path = os.path.join(folder_path, "checked_notebooks")
        os.makedirs(check_nb_folder_path, exist_ok=True)

        file_paths = [os.path.join(folder_path, _file) for _file in os.listdir(folder_path) if _file.endswith('.ipynb')]
        for file_path in file_paths:
            if file_path.endswith(".ipynb"):
                with open(file_path, "r", encoding='utf-8') as f:
                    nb = json.load(f)
            
                file_name = os.path.basename(file_path)
                remark = remarks[file_name]

                for q, rem in remark.items():
                    to_add = {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [
                            f"#{q.replace('q', 'r')}\n", 
                            f"- marks = {rem['marks']}\n",
                            "\n",
                            f"- feedback = {rem['feedback']}"
                        ]
                    }
                    tag = f"{q.replace('q', 'a')}"

                    for i, cell in enumerate(nb['cells']):
                        if tag == cell['source'][0].strip('#\n'):
                            nb['cells'].insert(i+1, to_add)
                            break

                checked_nb_path = os.path.join(check_nb_folder_path, file_name)
                with open(checked_nb_path, 'w') as outfile:
                    outfile.write(json.dumps(nb, indent=4))

        return True

