import os
import sys
import django

# Setup Django environment
sys.path.append(r'c:\Users\Asus\OneDrive\Desktop\abdul\abdul\portal_ui')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_ui.settings')
django.setup()

from preparation_ab.models import Category, Question

def populate_data():
    # 1. Create Categories
    quant, _ = Category.objects.get_or_create(name="Quantitative Aptitude", description="Numbers, arithmetic, and mathematical problems.")
    logical, _ = Category.objects.get_or_create(name="Logical Reasoning", description="Puzzles, sequences, and logical patterns.")
    verbal, _ = Category.objects.get_or_create(name="Verbal Ability", description="Grammar, vocabulary, and comprehension.")

    print("Categories created/verified.")

    # 2. Add Questions for Quant
    Question.objects.get_or_create(
        category=quant,
        text="If a car travels 300km in 5 hours, what is its average speed?",
        option_a="50 km/h", option_b="60 km/h", option_c="70 km/h", option_d="80 km/h",
        correct_answer="B"
    )
    Question.objects.get_or_create(
        category=quant,
        text="What is 25% of 800?",
        option_a="150", option_b="200", option_c="250", option_d="300",
        correct_answer="B"
    )

    # 3. Add Questions for Logical
    Question.objects.get_or_create(
        category=logical,
        text="Find the missing number in the sequence: 2, 4, 8, 16, ___",
        option_a="24", option_b="30", option_c="32", option_d="36",
        correct_answer="C"
    )
    Question.objects.get_or_create(
        category=logical,
        text="If 'CAT' is coded as 'DBU', how is 'DOG' coded?",
        option_a="EPH", option_b="FOI", option_c="FPH", option_d="GOI",
        correct_answer="A"
    )

    # 4. Add Questions for Verbal
    Question.objects.get_or_create(
        category=verbal,
        text="Select the synonym for 'Abundant'.",
        option_a="Scarce", option_b="Plentiful", option_c="Brief", option_d="Rare",
        correct_answer="B"
    )
    Question.objects.get_or_create(
        category=verbal,
        text="Choose the correct spelling.",
        option_a="Occurrence", option_b="Occurence", option_c="Ocurence", option_d="Occurrance",
        correct_answer="A"
    )

    print("Questions added successfully.")

if __name__ == "__main__":
    populate_data()
