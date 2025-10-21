
import requests
import json
import pandas as pd
from math import floor

class coziehelper:
    """
    Class to retrieve and process Cozie-Apple data
    """
    def __init__(self):
        return  

    def watch_survey_checker(self, file_path=None, file_url=None, stop='first'):
        """
        Function to check if a watch survey file is valid.
        
        Arguments
        ----------
        - file_path, str, Path to watch survey file
        - file_url, str, URL to watch survey file
        - stop, str, Stop at first error or last error

        Returns
        -------
        - ws_valid, bool, True if watch survey is valid, False if not
        """
        output = ''
        ws_valid = False
        errors_found = 0

        # Parse input parameters
        if file_path is not None:
            with open(file_path) as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError as e:
                    print('Invalid JSON syntax:', e)
                    return ws_valid

        elif file_url is not None:
            try:
                response = requests.get(file_url)
            except requests.exceptions.RequestException as e:
                print(f'Watch survey file not reachable. ({e})')
                return ws_valid
            try:
                data = json.loads(response.text)
            except json.JSONDecodeError as e:
                print('Invalid JSON syntax:', e)
                return ws_valid
        else:
            print('No file path or URL provided')
            return ws_valid

        # Check watch survey
        output += 'survey_name: ' + data['survey_name'] + '\n'
        output += 'survey_id: ' + data['survey_id'] + '\n'
        
        number_of_response_options = 0
        for i, question in enumerate(data['survey']):
            flag_missing = False
            number_of_questions = i + 1
            output += f"\n{question['question']}  [{question['question_id']}]\n"

            for response in question['response_options']:
                output += ' ' + f'{response["text"]}  [{response["next_question_id"]}]'

                flag_found = False
                for question2 in data['survey']:
                    if question2['question_id'] == response['next_question_id']:
                        # print(' ', '(found)')
                        output += '\n'
                        flag_found = True
                        if response['next_question_id'] != '':
                            number_of_response_options += 1

                if flag_found == False:
                    number_of_response_options += 1
                    if response['next_question_id'] == '':
                        output += ' (end of survey)\n'
                    else:
                        output += f' (missing) <=========================================== {errors_found}\n'
                        flag_missing = True
            
            if (flag_missing == True):
                errors_found += 1
            if (flag_missing == True) & (stop == 'first'):
                # Stop loop on first error
                break

        if errors_found == 0:
            print('\n #######################\n ### No Errors found ###\n #######################')
            print('\n Number of questions:', number_of_questions)
            print(' Number of response options:', number_of_response_options)
            print(' Average number response options per question:', floor(number_of_response_options / number_of_questions * 10) / 10)
            ws_valid = True
        else:
            print(output)
            print('\n ----------------------')
            print(f' --- {errors_found} Errors found ---')
            print(' ----------------------')


        return ws_valid
    