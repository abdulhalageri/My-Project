import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_ui.settings')
django.setup()

from preparation_ab.models import CodingProblem

def seed():
    problems = [
        # TCS
        {
            "title": "Reverse a Linked List",
            "description": "Given the head of a singly linked list, reverse the list and return the reversed list.\n\nInput: head = [1,2,3,4,5]\nOutput: [5,4,3,2,1]",
            "difficulty": "Basic",
            "company_tag": "TCS",
            "time_limit_minutes": 30,
            "sample_input": "1 2 3 4 5",
            "sample_output": "5 4 3 2 1",
            "test_cases": [{"input": "1 2 3", "expected_output": "3 2 1"}, {"input": "1", "expected_output": "1"}]
        },
        {
            "title": "Fibonacci Series",
            "description": "Find the Nth Fibonacci number.\n\nInput: N = 5\nOutput: 5",
            "difficulty": "Basic",
            "company_tag": "TCS",
            "time_limit_minutes": 20,
            "sample_input": "5",
            "sample_output": "5",
            "test_cases": [{"input": "10", "expected_output": "55"}]
        },
        # Infosys
        {
            "title": "Longest Palindromic Substring",
            "description": "Given a string s, return the longest palindromic substring in s.\n\nInput: s = 'babad'\nOutput: 'bab'",
            "difficulty": "Intermediate",
            "company_tag": "Infosys",
            "time_limit_minutes": 30,
            "sample_input": "babad",
            "sample_output": "bab",
            "test_cases": [{"input": "cbbd", "expected_output": "bb"}]
        },
        {
            "title": "Matrix Rotation",
            "description": "Rotate a given NxN matrix by 90 degrees clockwise.",
            "difficulty": "Intermediate",
            "company_tag": "Infosys",
            "time_limit_minutes": 40,
            "sample_input": "[[1,2],[3,4]]",
            "sample_output": "[[3,1],[4,2]]",
            "test_cases": [{"input": "[[1,2,3],[4,5,6],[7,8,9]]", "expected_output": "[[7,4,1],[8,5,2],[9,6,3]]"}]
        },
        # Accenture
        {
            "title": "Balanced Parentheses",
            "description": "Determine if the input string containing characters '()[]{}' is valid.",
            "difficulty": "Basic",
            "company_tag": "Accenture",
            "time_limit_minutes": 20,
            "sample_input": "()[]{}",
            "sample_output": "true",
            "test_cases": [{"input": "([)]", "expected_output": "false"}]
        },
        {
            "title": "Nth Smallest Element",
            "description": "Find the Nth smallest element in an unsorted array.",
            "difficulty": "Basic",
            "company_tag": "Accenture",
            "time_limit_minutes": 25,
            "sample_input": "arr=[7,10,4,3,20,15], N=3",
            "sample_output": "7",
            "test_cases": [{"input": "arr=[1,2,3,4,5], N=1", "expected_output": "1"}]
        },
        # Wipro
        {
            "title": "Two Sum",
            "description": "Find indices of two numbers in an array that add up to a target.",
            "difficulty": "Basic",
            "company_tag": "Wipro",
            "time_limit_minutes": 25,
            "sample_input": "nums=[2,7,11,15], target=9",
            "sample_output": "[0,1]",
            "test_cases": [{"input": "nums=[3,2,4], target=6", "expected_output": "[1,2]"}]
        },
        {
            "title": "String Anagrams",
            "description": "Check if two strings are anagrams of each other.",
            "difficulty": "Basic",
            "company_tag": "Wipro",
            "time_limit_minutes": 20,
            "sample_input": "s1='listen', s2='silent'",
            "sample_output": "true",
            "test_cases": [{"input": "s1='hello', s2='world'", "expected_output": "false"}]
        },
        # Cognizant
        {
            "title": "Bubble Sort Implementation",
            "description": "Implement the bubble sort algorithm to sort an array in ascending order.",
            "difficulty": "Basic",
            "company_tag": "Cognizant",
            "time_limit_minutes": 25,
            "sample_input": "[5,1,4,2,8]",
            "sample_output": "[1,2,4,5,8]",
            "test_cases": [{"input": "[3,0,2,5,-1]", "expected_output": "[-1,0,2,3,5]"}]
        },
        {
            "title": "Factorial Calculation",
            "description": "Write a program to find the factorial of a given number N.",
            "difficulty": "Basic",
            "company_tag": "Cognizant",
            "time_limit_minutes": 15,
            "sample_input": "5",
            "sample_output": "120",
            "test_cases": [{"input": "0", "expected_output": "1"}]
        },
        # HCL
        {
            "title": "Check Prime Number",
            "description": "Given a number N, check if it is prime.",
            "difficulty": "Basic",
            "company_tag": "HCL",
            "time_limit_minutes": 15,
            "sample_input": "11",
            "sample_output": "true",
            "test_cases": [{"input": "4", "expected_output": "false"}]
        },
        {
            "title": "Reverse Words in String",
            "description": "Reverse the words in a given string sentence.",
            "difficulty": "Basic",
            "company_tag": "HCL",
            "time_limit_minutes": 20,
            "sample_input": "Welcome to HCL",
            "sample_output": "HCL to Welcome",
            "test_cases": [{"input": "Hello World", "expected_output": "World Hello"}]
        }
    ]

    for p_data in problems:
        CodingProblem.objects.update_or_create(
            title=p_data['title'],
            company_tag=p_data['company_tag'],
            defaults=p_data
        )
    print(f"Seeded {len(problems)} coding problems successfully!")

if __name__ == "__main__":
    seed()
