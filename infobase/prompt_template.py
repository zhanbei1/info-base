#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> prompt_template
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/10/24 14:35
@Desc   ：使用的prompt
==================================================
"""
# 整个文件进行总结的prompt
LLM_WHOLE_FILE_SUMMARY_PROMPT_TEMPLATE = '''
Analyze the text content of the code for analysis. Analyze by class, function, etc. 
Summarize the main functions of this code：        
{Input}
'''
LLM_WHOLE_FILE_SUMMARY_OUTPUT = '''
{
    "description": "The Calculator class is mainly a class that processes data and provides two functions for integer data operations. One is to add two integers and the other is to subtract two integers",
    "name":"Calculator",
    "type":"class",
    "input_parameter": null,
    "return_obj": null,
    "possible_exception": null,
    "content_description": [{
            "name": "Calculator.add",
            "type":"function",
            "description": "It is to add two integers and return an int type data",
            "input_parameter": "a:int, b:int",
            "return_obj": "int",
            "possible_exception": ["",""],
        }
    ]
}
'''

HYPOTHETICAL_QUESTIONS_PROMPT_TEMPLATE = """
Analyzing and guessing around known information can describe three hypothetical questions that can be answered and provide answers to them：
{description}
"""

# 对函数代码进行总结
LLM_FUNCTION_SUMMARY_PROMPT_TEMPLATE = '''
Analyze the text content of the code for analysis. Analyze by function
Summarize the function name, input parameter type, output parameter type, main purpose,
possible types and information of exceptions that may be reported and hypothetical questions.
Based on the summary description, provide a list of possible hypothetical questions to answer, and only provide three hypothetical questions
Possible_exception and hypothetical_questions list multiple points according to the content to form an array.
Output JSON format, and if no results are analyzed for a certain latitude, it can be blank

Example:
    Input:
        "
        def add(self, a: int, b: int) -> int:
            return a + b
        "
    Output:
        {output_template}

{Input}
'''

LLM_FUNCTION_SUMMARY_OUTPUT = '''
{
    "name": "add",
    "type":"function",
    "description": "It is to add two integers and return an int type data",
    "input_parameter": "a:int, b:int",
    "return_obj": "int",
    "possible_exception": ["",""],
    "hypothetical_questions":["", ""]
}
'''

LLM_DIR_SUMMARY_PROMPT_TEMPLATE = '''
A certain {path_type} contains the following description information. As a intelligent robot, 

Provide a summary description and potential hypothetical questions regarding this description.
Only three hypothetical questions need to be given
Please output strictly in JSON format

Example:
    Input:
        "It is to add two integers and return an int type data",
        "It can to reduce two integers"
    Output:
        {dir_summary_output}
        
please analyze and summarize the {path_type} based on the following known information.
{desc_list}
'''
DIR_SUMMARY_OUTPUT = """
{
	"description": "The program is designed to convert a list of expression tokens into an abstract syntax tree. The class_declaration is responsible for processing various tokens, including structure separators, function opening and closing braces, and array open and close tokens. It also validates function parameters and checks for operator precedence. The program creates operator nodes and pushes them onto the operand stack. It checks if a given token is an operator or not and returns a boolean value.",
	"hypothetical_questions": ["How to Calculate the Addition of Two Numbers"，
		"How to calculate two integers"
	]
}
"""

LLM_QUERY_PROMPT_TEMPLATE = '''
The following information is known : 
{context}
As information administrator robot, please answer:
{query}
'''

LLM_LANGUAGE_TRANSLATOR_PROMPT_TEMPLATE = '''
Translate the following content into {language}:
"{content}"
'''
LLM_MULTI_QUERY_PROMPT_TEMPLATE = """
I already know the following questions and answers：
{multi_query_answer}
As an intelligent robot, please organize known information and answer the following question:
{question}
"""

MULTI_QUERY_PROMPT_TEMPLATE = """
Provide three different latitude questions based on the following known information to assist in answering this question.
Return to me in array format
Original question: 
{question}

 """
MULTI_QUERY_OUTPUT = """
[{
    "need_code": true,
    "question": "Here is a demo example of a problem that requires code, not a real problem",
  },
  {
    "need_code": false,
    "question": "This is an example of a problem that does not require code, not a real code example",
  }
]
"""
