#!/usr/bin/env python
#
# Copyright 2020 John T. Foster
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests
import json
import re
import os
import time

from mdutils.mdutils import MdUtils
import pypandoc

class Canvas():

    def __init__(self, token, base_url='https://utexas.instructure.com/api/v1/', verbose=False):

        self.headers = {
            'Authorization' : 'Bearer ' + token,
            "Content-Type" : "application/json",
            "Accept" : "application/json",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36' 
        }

        self.base_url = base_url

        self.id = self.get_id()

        self.students = {}
        self.verbose = verbose

        return

        
    def check_token(self):

        response = requests.get(self.base_url, headers = self.headers)

        return response.status_code == 200


    def create_gradebook_column(self, course_id):

        # response = requests.post(self.base_url + course_id + '/custom_gradebook_columns', 
                                 # headers = self.headers, 
                                 # params = {'column[title]' : 'assignment100'})
        response = requests.delete(self.base_url + 'courses/' + course_id + '/custom_gradebook_columns/2281', 
                                 headers = self.headers)

        print(response.json())

        return

    def get_id(self):

        response = requests.get(self.base_url + 'course_accounts', headers = self.headers)

        return response.json()[0]['id']


    def get_students(self, course_id):

        response = requests.get(self.base_url + 'courses/' + course_id + '/enrollments', headers = self.headers, params = {'per_page' : 10000})

        students = response.json()

        for student in students:

            self.students[str(student['sis_user_id'])] = student['user_id']


    def get_assignment_id(self, course_id, assignment_name):

        response = requests.get(self.base_url + 'courses/' + course_id + '/assignments', headers = self.headers, params = {'per_page' : 10000})

        assignments = response.json()

        for assignment in assignments:

            if str(assignment['name']) == assignment_name:
                return assignment['id']
        
        print("No assignment id with corresponding name: " + assignment_name)

        return


    def update_assignment_grade(self, course_id, assignment_name, student_id, grade):

        assignment_id = self.get_assignment_id(course_id, assignment_name)

        response = requests.post(self.base_url + 'courses/' + course_id + '/assignments/' + str(assignment_id) + '/submissions/update_grades', 
                headers = self.headers, 
                params = {'grade_data[{}][posted_grade]'.format(student_id) : grade})

        if self.verbose:
            print("Updated grade: " + str(student_id) + " = " + str(grade))

        return

    def get_course_quizzes(self, course_id, search_term=None):

        response = requests.get('{}courses/{}/quizzes'.format(self.base_url, course_id), 
                headers = self.headers,
                params = {'search_term' : search_term})

        return response.json()

    def get_course_quiz_ids(self, course_id, search_term=None):

        response = self.get_course_quizzes(course_id, search_term)

        ids = [item['id'] for item in response]

        return ids

    def get_quiz(self, course_id, quiz_id):

        response = requests.get('{}courses/{}/quizzes/{}'.format(self.base_url, course_id, quiz_id), 
                headers = self.headers)

        return response.json() 

    def get_quiz_questions(self, course_id, quiz_id):

        response = requests.get('{}courses/{}/quizzes/{}/questions'.format(self.base_url, course_id, quiz_id), 
                headers = self.headers)

        return response.json() 

    def export_quiz(self, export_filename, course_id, quiz_id, output_format='md'):

        questions = self.get_quiz_questions(course_id, quiz_id)

        md_file = MdUtils(file_name=export_filename)

        for question in questions:
            question_string = ''
            question_string += '1.  {}\n'.format(question['question_text'])
            for answer in question['answers']:
                question_string += '    a.  {}\n'.format(answer['text'])
            md_file.new_paragraph(question_string)

        md_file.create_md_file()
        if output_format == 'pdf':
            output_filename = export_filename.split('.')[0] + '.pdf'
            output = pypandoc.convert_file(export_filename, 'pdf', outputfile=output_filename)
            os.remove(export_filename)


if __name__ == "__main__":
    token = os.environ['CANVAS_TOKEN']
    classroom = Canvas(token, verbose=True)
    # classroom.create_gradebook_column('1207029')
    # classroom.get_students('1207029')
    # print(classroom.get_assignment_id('1207029', 'assignment2'))
    # print(classroom.students)
    # classroom.update_assignment_grade('1207029', 'assignment1', classroom.students['sa42284'], 1)

