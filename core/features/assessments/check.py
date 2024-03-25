import os
import io
import re
import csv
import json
import asyncio
from tqdm import tqdm
from typing import Dict

from core.features.assessments.prompts import SIMPLE_ASSIGNMENT_CHECK_PROMPT
from core.features.utils import add_dicts, calculate_cost_gpt4_turbo
from core.features.provider import async_creator, text_model_defaults


class AssignmentCheck:

    def __init__(self) -> None:
        self.duplicates = []
        self.gpt_report = []
        # self.context = {}

    def question_or_answer_cell(self, s: str):

        """
        Function to check the correct tag for a question or an answer cell.
        Must match - "#q<some + integer>" or "#a<some + integer>"
        """

        pattern = r"^#[aq]\d+"
        s = s.strip()
        return bool(re.match(pattern, s))
    
    def answer_cell(self, s: str):

        """
        Function to check the correct tag for answer cell.
        Must match - "#a<some + integer>"
        """

        pattern = r"^#[a]\d+"
        s = s.strip()
        return bool(re.match(pattern, s))


    def qna_extraction(self, file_path: str, context: Dict):
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
            if cell['source'] and self.question_or_answer_cell(cell['source'][0]):
                qnas[cell['source'][0].strip('#\n')] = "".join(cell['source'][1:])

        final_qnas = {}
        for key in context.keys():
            final_qnas[key] = qnas.get(key)
            final_qnas[key.replace('q', 'a')] = qnas.get(key.replace('q', 'a'))

        return final_qnas


    async def question_answer_check(self, qna_dict: Dict, tag: str):

        """
        v1 Function to check the solution of the question
        provide obtained marks and feedback

        id: combined id of notebook name + question tag (file.ipynb?q1)
        content: content of the id contains question, description, max_marks and submitted solution 
        """

        conversation = [{"role": "system", "content": SIMPLE_ASSIGNMENT_CHECK_PROMPT}]
        user_input = f"""{qna_dict}"""

        user_message = {'role': 'user', 'content': user_input}
        conversation.append(user_message)

        response = await async_creator(
            **text_model_defaults,
            messages=conversation,
            max_tokens=999
        )    
        response = response.model_dump()
        output = response["choices"][0]["message"]["content"]
        token_usage = response["usage"]
        
        return {
            "gpt_response": response,
            "output": output,
            "tag": tag,
            "qna_dict": qna_dict,
            "token_usage": token_usage
            }
    
    async def question_answer_check2(self, id, content):

        """
        v2 Function to check the solution of the answer
        provide obtained marks and feedback

        id: combined id of notebook name + question tag (file.ipynb?q1)
        content: content of the id contains question, description, max_marks and submitted solution 
        """

        conversation = [{"role": "system", "content": SIMPLE_ASSIGNMENT_CHECK_PROMPT}]
        user_input = f"""{content}"""

        user_message = {'role': 'user', 'content': user_input}
        conversation.append(user_message)

        response = await async_creator(
            **text_model_defaults,
            messages=conversation,
            max_tokens=999
        )    
        response = response.model_dump()
        output = response["choices"][0]["message"]["content"]
        token_usage = response["usage"]
        
        return {
            "gpt_response": response,
            "output": output,
            "id": id,
            "token_usage": token_usage
        }


    async def notebook_check(self, file, qnas, context):

        """
        This function takes the set of questions and answers as per notebook basis
        and provide a dict with remarks of all questions

        NOTE: Don't use this function if question_answer_check2 is being used

        file: name of the file
        qnas: questions and answers from the notebook file with tag mapping
        context: context about each question (max_marks and description)
        """

        token_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        remarks = {}
        tasks = []
        for i in range(1, len(context)+1):
            qna_dict = {
                "question": qnas[f"q{i}"],
                "description": context[f"q{i}"]['description'],
                "max_marks": context[f"q{i}"]['max_marks'],
                "solution": qnas[f"a{i}"]
            }

            tag = f"q{i}"
            task = self.question_answer_check(qna_dict=qna_dict, tag=tag, file=file)
            tasks.append(task) 
                     
        results = await asyncio.gather(*tasks)
        for result in results:
            gpt_response, output, usage, tag, qna_dict = result['gpt_response'], json.loads(result['output']), result['token_usage'], result['tag'], result['qna_dict']
            token_usage = add_dicts(token_usage, usage)
            qna_dict.update(output)
            remarks[tag] = qna_dict

        return {file: remarks}, token_usage
    

    async def batch_assessment_check(self, path, remarks_filename="remarks.json", check_duplicates: bool=False):
        """
        This function is the main batch processing function for assessment
        Takes path of folder, find duplicate notebooks and qnas 
        Check all the questions of all the notebooks and provide a combined json for remarks
        Also, adds remarks to exact copy of input notebooks after each answer cell

        path: path of a folder full of jupyter notebooks and one context.json file
        remarks_filename: file name for remarks file to be saved
        check_duplicates: check if duplicates are present in the folder
        """
        
        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        final_remarks = {}

        if os.path.isdir(path):
            file_paths = [os.path.join(path, _file) for _file in os.listdir(path) if _file.endswith('.ipynb')]
            context_file = next((os.path.join(path, _file) for _file in os.listdir(path) if _file == "context.json"), None)

            if context_file is not None:
                with open(context_file, 'r') as f:
                    context = json.load(f)
            else:
                raise FileNotFoundError("context.json file not found")

            print(f"GOT {len(file_paths)} notebooks in total")
            files_and_qnas = {os.path.basename(file_path): self.qna_extraction(file_path, context) for file_path in file_paths}
            print(files_and_qnas)
            # print("GOT QNAS:", len(files_and_qnas))
            reformed, duplicate_qnas = self.qna_reformation(files_qnas=files_and_qnas, context=context, find_duplicates=True)
            # print("DUPLICATE QNAS", duplicate_qnas)
            
            duplicate_notebooks_dict = self.duplicates_checker(files_and_qnas)
            # print(f"FOUND DUPLICATE NOTEBOOKS: {duplicate_notebooks_dict}")

        else:
            raise ValueError('path should be a directory')
        

        """
        Below commented code was previously used 
        Nested appraoch (traverse Notebooks and then questions)
        Wasn't good for finding and handling duplicate qnas
        """
        # tasks = []
        # for file in tqdm(duplicate_notebooks_dict.keys()):
        #     task = self.notebook_check(file, files_and_qnas[file], context)
        #     tasks.append(task)
        # results = await asyncio.gather(*tasks)
        
        # for remarks, tokens in results:
        #     final_remarks.update(remarks)
        #     total_tokens = add_dicts(total_tokens, tokens)

        # for original_notebook, copied_notebooks in duplicate_notebooks_dict.items():
        #     if copied_notebooks:
        #         orig_content = final_remarks[original_notebook]
        #         for notebook in copied_notebooks:
        #             final_remarks[notebook] = orig_content
        
        """
        Below un-commented code is preferable 
        Direct appraoch - Traversing all QnAs with unique id.
        Helpful in detecting duplicate content 
        """

        tasks = []
        for id in tqdm(duplicate_qnas.keys()):
            task = self.question_answer_check2(id, reformed[id])
            tasks.append(task)
        results = await asyncio.gather(*tasks)

        qna_remarks = {}
        api_call_count = len(results)
        for result in results:
            gpt_response, remarks, id, tokens = result['gpt_response'], result['output'], result['id'], result['token_usage']
            qna_dict = reformed[id]
            qna_dict.update(json.loads(remarks))
            qna_remarks[id] = qna_dict
            total_tokens = add_dicts(total_tokens, tokens)
            self.gpt_report.append({'id': id, 'tokens': tokens, "created": gpt_response['created']})

        for original_qna_id, copied_qnas_ids in duplicate_qnas.items():
            if copied_qnas_ids:
                orig_content = qna_remarks[original_qna_id]
                for qna_id in copied_qnas_ids:
                    qna_remarks[qna_id] = orig_content

        for id, remark in qna_remarks.items():
            file, tag = id.split("?")
            final_remarks.setdefault(file, {})[tag] = remark

        self.add_remarks_to_ipynb(final_remarks, path)
        print("ADDED REMARKS TO IPYNB")

        # creating results folder inside path location
        results_path = os.path.join(path, 'results')
        os.makedirs(results_path, exist_ok=True)
        print("CREATED RESULTS FOLDER")

        # saving the remarks
        json_remarks = json.dumps(final_remarks, indent=4)
        with open(os.path.join(results_path, remarks_filename), 'w') as f:
            f.write(json_remarks)

        csv_remarks = self.json_to_csv_remarks(remarks = final_remarks, context = context)
        with open(os.path.join(results_path, remarks_filename.replace('.json', '.csv')), 'w') as f:
            f.write(csv_remarks)

        gpt_cost = calculate_cost_gpt4_turbo(total_tokens)
        if check_duplicates:
            # saving the duplicate notebooks and qnas info  
            with open(os.path.join(results_path, 'duplicates.json'), 'w') as f:
                dup_json = {'duplicate_files': duplicate_notebooks_dict, "duplicate_qnas": duplicate_qnas}
                f.write(json.dumps(dup_json))

        print("DONE!")
        return total_tokens, gpt_cost, self.gpt_report, api_call_count
    
    def qna_reformation(self, files_qnas: Dict, context: Dict, find_duplicates = True):

        """
        Function to reform the structure of qna dict, and duplicate qnas

        convert {filename: {qtag: q, atag: a}} to {id: qna}
        where id is filename+tag and qna is a dict of ques, ans, max_marks and
        solution basically combines context as well 
        
        And now that we have all the qna info at same level, we find out the duplicates easily
        """
        
        # reformation
        reformed = {}
        for file, qnas in files_qnas.items():
            # l = len(qnas)
            # for i in range(1, l//2 + 1):
            #     reformed[file + "?" + f"q{i}"] = {
            #                             "question": qnas.get(f"q{i}"),
            #                             "description": context[f"q{i}"]['description'],
            #                             "max_marks": context[f"q{i}"]['max_marks'],
            #                             "solution": qnas.get(f"a{i}")
            #                         }

            for i in qnas.keys():
                if i.startswith("q"):
                    reformed[file + "?" + f"{i}"] = {
                                            "question": qnas.get(f"{i}"),
                                            "description": context[f"{i}"]['description'],
                                            "max_marks": context[f"{i}"]['max_marks'],
                                            "solution": qnas.get(f"{i.replace('q', 'a')}")
                                        }
        
        # finding duplicates
        """
        Duplicates structure - {qna-id: null if not similar qna, qna-id: [qna-ids of all similar qnas]}
        """
        if find_duplicates:
            qna_to_ids = {}
            for id, qna in reformed.items():
                qna_to_ids.setdefault(str(qna), []).append(id)

            duplicates = [id for id in qna_to_ids.values()]
            dup_dict = {}
            for dup in duplicates:
                if len(dup) > 1:
                    dup_dict[dup[0]] = dup[1:]
                else:
                    dup_dict[dup[0]] = None
            return reformed, dup_dict 
        return reformed

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

        duplicates = [filenames for filenames in content_to_filenames.values()]
        dup_dict = {}
        for dup in duplicates:
            if len(dup) > 1:
                dup_dict[dup[0]] = dup[1:]
            else:
                dup_dict[dup[0]] = None

        return dup_dict # mapping of one of duplicate notebooks with other notebooks
    

    def add_remarks_to_ipynb(self, remarks: Dict, folder_path):
        
        """
        Function to add remarks to the exact copy of notebooks after answer each cell with r tag
        """
        
        check_nb_folder_path = os.path.join(folder_path, "checked_notebooks")
        os.makedirs(check_nb_folder_path, exist_ok=True)

        file_paths = [os.path.join(folder_path, _file) for _file in os.listdir(folder_path) if _file.endswith('.ipynb')]
        for file_path in file_paths:
            """
            traverse all files, find filename, and respective generated remarks
            """
            if file_path.endswith(".ipynb"):
                with open(file_path, "r", encoding='utf-8') as f:
                    nb = json.load(f)
            
                file_name = os.path.basename(file_path)
                file_remarks = remarks[file_name]

                for tag, qna_remark in file_remarks.items():
                    """
                    traverse file_remarks to find remark for each question
                    create the remark cell r, and add after respective answer tag
                    """
                    to_add = {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [
                            f"#{tag.replace('q', 'r')}\n",
                            f"- marks = {qna_remark['marks']}\n",
                            "\n",
                            f"- feedback = {qna_remark['feedback']}"
                        ]
                    }
                    tag = f"{tag.replace('q', 'a')}"

                    for i, cell in enumerate(nb['cells']):
                        """
                        traverse through each notebook cell to find where to place the
                        remark cell, place and then break this loop
                        """
                        if cell['source'] and tag == cell['source'][0].strip('#\n'):
                            nb['cells'].insert(i+1, to_add)
                            break

                checked_nb_path = os.path.join(check_nb_folder_path, file_name)
                with open(checked_nb_path, 'w') as outfile:
                    outfile.write(json.dumps(nb, indent=4))

    
    def json_to_csv_remarks(self, remarks: Dict, context: Dict):

        questions = []
        question_keys = []
        for q, data in context.items():
            question_keys.append(q)
            questions.append(f'{q} ({data["max_marks"]})')
        questions = sorted(questions)
        question_keys = sorted(question_keys)

        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)

        # Writing header
        writer.writerow(['file_name'] + questions)

        # Writing rows for each file
        for file_name, file_data in remarks.items():
            row = [file_name] + [file_data.get(q, {'marks': None})['marks'] for q in question_keys]
            writer.writerow(row)

        return output.getvalue()
    

    def summarize_remarks(self, remarks: Dict, context: Dict):
        pass

