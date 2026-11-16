import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_ui.settings')
django.setup()

from preparation_ab.models import InterviewQuestion

hr_questions = [
    "Tell me about yourself.",
    "What are your greatest strengths?",
    "What are your weaknesses?",
    "Why do you want to work at this company?",
    "Where do you see yourself in five years?",
    "Why should we hire you?",
    "Describe a difficult work situation and how you handled it.",
    "How do you handle stress and pressure?",
    "What are your salary expectations?",
    "Do you have any questions for us?",
    "Give an example of a goal you reached and tell me how you achieved it.",
    "Give an example of how you worked on a team.",
    "Share an example of how you were able to motivate employees or co-workers.",
    "Tell me about a time you made a mistake.",
    "Enumerate a time you showed leadership.",
    "Describe how you handle a situation where you have too much work to do.",
    "Tell me about a time you had to deal with a difficult customer or coworker.",
    "What is your greatest professional achievement?",
    "What are you looking for in a new position?",
    "What is your dream job?"
]

tech_questions = [
    "Explain the concept of Object-Oriented Programming (OOP) and its pillars.",
    "What is the difference between a list and a tuple in Python?",
    "How does memory management work in Python?",
    "What are the different types of joins in SQL?",
    "Explain the MVC architecture which Django follows.",
    "What is the difference between REST and SOAP?",
    "What is an API, and how does it work?",
    "Explain the difference between a process and a thread.",
    "What is time complexity, and how do you calculate it?",
    "Describe how a hash table works internally.",
    "What is a deadlock in OS?",
    "Explain the concept of normalization in databases.",
    "What is polymorphism in OOP?",
    "Explain the difference between shallow copy and deep copy.",
    "What are decorators in Python?",
    "Explain the working of a DNS.",
    "What is the difference between TCP and UDP?",
    "What is Git and how does it handle branching?",
    "Explain the concept of acid properties in DBMS.",
    "What is the difference between primary key, unique key and foreign key?"
]

def seed():
    # HR Questions
    for q_text in hr_questions:
        InterviewQuestion.objects.get_or_create(round_type='HR', text=q_text)
    
    # Technical Questions
    for q_text in tech_questions:
        InterviewQuestion.objects.get_or_create(round_type='Technical', text=q_text)
    
    print(f"Successfully seeded {len(hr_questions)} HR and {len(tech_questions)} Technical questions.")

if __name__ == "__main__":
    seed()
