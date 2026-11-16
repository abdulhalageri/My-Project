import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_ui.settings')
django.setup()

from preparation_ab.models import Category, Question

def populate():
    categories_data = [
        {
            "name": "Quantitative Aptitude",
            "questions": [
                {"text": "A train 120m long passes a pole in 6 seconds. What is the speed of the train?", "options": ["60 km/hr", "72 km/hr", "80 km/hr", "90 km/hr"], "answer": "B"},
                {"text": "Find the average of first five prime numbers.", "options": ["5.5", "5.6", "5.4", "5.2"], "answer": "B"},
                {"text": "What is 25% of 120?", "options": ["20", "25", "30", "35"], "answer": "C"},
                {"text": "If 5 men can build a wall in 12 days, how many men can build it in 10 days?", "options": ["6", "7", "8", "9"], "answer": "A"},
                {"text": "The ratio of two numbers is 3:4. If their sum is 70, find the numbers.", "options": ["30, 40", "35, 35", "20, 50", "25, 45"], "answer": "A"},
                {"text": "Simple interest on $500 for 2 years at 5% per annum is?", "options": ["$40", "$50", "$60", "$70"], "answer": "B"},
                {"text": "The cost price of an article is $200. If it is sold at a 20% profit, the selling price is?", "options": ["$220", "$230", "$240", "$250"], "answer": "C"},
                {"text": "A cube has a side of 4cm. What is its volume?", "options": ["16 cm3", "32 cm3", "64 cm3", "128 cm3"], "answer": "C"},
                {"text": "Find the HCF of 12 and 18.", "options": ["2", "3", "6", "9"], "answer": "C"},
                {"text": "What is the square root of 625?", "options": ["15", "25", "35", "45"], "answer": "B"},
                {"text": "If x + 5 = 12, what is x?", "options": ["5", "6", "7", "8"], "answer": "C"},
                {"text": "A car travels 300km in 5 hours. What is its speed?", "options": ["50 km/hr", "60 km/hr", "70 km/hr", "80 km/hr"], "answer": "B"},
                {"text": "The area of a circle with radius 7cm is? (Use pi = 22/7)", "options": ["154 cm2", "44 cm2", "77 cm2", "144 cm2"], "answer": "A"},
                {"text": "Convert 0.75 into a fraction.", "options": ["1/4", "1/2", "3/4", "2/3"], "answer": "C"},
                {"text": "Find the missing number: 2, 4, 8, 16, ?", "options": ["24", "30", "32", "36"], "answer": "C"},
                {"text": "What is the complementary angle of 30 degrees?", "options": ["60", "90", "120", "150"], "answer": "A"},
                {"text": "If 15% of a number is 45, what is the number?", "options": ["150", "200", "300", "400"], "answer": "C"},
                {"text": "A rectangle has length 10cm and width 5cm. What is its perimeter?", "options": ["15 cm", "30 cm", "40 cm", "50 cm"], "answer": "B"},
                {"text": "What is the sum of angles in a triangle?", "options": ["90", "180", "270", "360"], "answer": "B"},
                {"text": "Calculate (10 + 5) * 2 - 8.", "options": ["15", "22", "30", "25"], "answer": "B"}
            ]
        },
        {
            "name": "Logical Reasoning",
            "questions": [
                {"text": "Point A is to the North of B. C is to the East of B. In which direction is A with respect to C?", "options": ["North-East", "North-West", "South-East", "South-West"], "answer": "B"},
                {"text": "If COLD is coded as DPME, how is HOT coded?", "options": ["IPU", "IQU", "JPV", "JQU"], "answer": "A"},
                {"text": "Which word does NOT belong with the others?", "options": ["Leopard", "Cougar", "Tiger", "Wolf"], "answer": "D"},
                {"text": "Identify the next term: J14, L16, N18, P20, ?", "options": ["R22", "S22", "R24", "S24"], "answer": "A"},
                {"text": "All mangoes are fruits. All fruits are healthy. Conclusion: All mangoes are healthy.", "options": ["True", "False", "Cannot Say", "Partially True"], "answer": "A"},
                {"text": "Find the odd one out: 3, 5, 7, 9, 11", "options": ["3", "7", "9", "11"], "answer": "C"},
                {"text": "If '+' means '*', '-' means '/', '*' means '+' and '/' means '-', what is 10 * 5 + 3?", "options": ["15", "25", "45", "50"], "answer": "B"},
                {"text": "Man : Woman :: King : ?", "options": ["Queen", "Princess", "Duchess", "Empress"], "answer": "A"},
                {"text": "What is next in the sequence: A, C, E, G, ?", "options": ["H", "I", "J", "K"], "answer": "B"},
                {"text": "If 'Blue' is called 'Green', 'Green' is called 'White', 'White' is called 'Black', what is the color of milk?", "options": ["Green", "White", "Black", "Blue"], "answer": "C"},
                {"text": "Pointing to a man, a lady said, 'He is the only son of my mother's husband'. How is the man related to the lady?", "options": ["Brother", "Father", "Cousin", "Son"], "answer": "A"},
                {"text": "In a row of 30 students, Rahul is 12th from the left. What is his position from the right?", "options": ["18th", "19th", "20th", "21st"], "answer": "B"},
                {"text": "Which number replaces the question mark: 4, 9, 16, 25, ?", "options": ["30", "32", "36", "40"], "answer": "C"},
                {"text": "Statement: Some pens are pencils. All pencils are erasers. Conclusion: Some pens are erasers.", "options": ["True", "False", "Maybe", "None"], "answer": "A"},
                {"text": "Dog : Bark :: Cat : ?", "options": ["Mew", "Roar", "Hiss", "Chirp"], "answer": "A"},
                {"text": "Find the missing term: BCD, EFG, HIJ, ?", "options": ["KLM", "LMN", "MNO", "NOP"], "answer": "A"},
                {"text": "If 1st January 2023 was Sunday, what was 8th January 2023?", "options": ["Monday", "Friday", "Sunday", "Saturday"], "answer": "C"},
                {"text": "Slight is to Heavy as Large is to?", "options": ["Small", "Huge", "Wide", "Tall"], "answer": "A"},
                {"text": "Which word can be formed from 'ENVIRONMENT'?", "options": ["ENTER", "MOUNT", "IRON", "All of these"], "answer": "D"},
                {"text": "Clock : Time :: Thermometer : ?", "options": ["Heat", "Radiation", "Temperature", "Energy"], "answer": "C"}
            ]
        },
        {
            "name": "Verbal Ability",
            "questions": [
                {"text": "Choose the synonym of 'ABANDON'.", "options": ["Keep", "Forsake", "Support", "Hold"], "answer": "B"},
                {"text": "Choose the antonym of 'BRIGHT'.", "options": ["Dull", "Shiny", "Luminous", "Vibrant"], "answer": "A"},
                {"text": "Complete the sentence: She is ___ honor to her profession.", "options": ["a", "an", "the", "no article"], "answer": "B"},
                {"text": "Identify the correctly spelled word.", "options": ["Accomodation", "Accommodation", "Acomodation", "Accommadation"], "answer": "B"},
                {"text": "Meaning of the idiom: 'Once in a blue moon'.", "options": ["Every day", "Very rarely", "At night", "Regularly"], "answer": "B"},
                {"text": "Select the proper prefix for 'fortune'.", "options": ["Dis-", "Un-", "Mis-", "In-"], "answer": "C"},
                {"text": "Choose the correct preposition: He is fond ___ music.", "options": ["at", "in", "of", "with"], "answer": "C"},
                {"text": "Identify the part of speech of the underlined word: She sang *sweetly*.", "options": ["Noun", "Adjective", "Adverb", "Verb"], "answer": "C"},
                {"text": "Change to Passive Voice: 'He opens the door'.", "options": ["The door is opened by him", "The door was opened by him", "The door is being opened by him", "The door had been opened"], "answer": "A"},
                {"text": "Synonym of 'GENUINE'.", "options": ["Fake", "Real", "False", "Copy"], "answer": "B"},
                {"text": "Complete the phrase: 'Slow and steady wins the ___'.", "options": ["game", "race", "match", "prize"], "answer": "B"},
                {"text": "Antonym of 'ANCIENT'.", "options": ["Old", "Modern", "Classic", "Antique"], "answer": "B"},
                {"text": "Which is a collective noun?", "options": ["Team", "Happiness", "Water", "Pencil"], "answer": "A"},
                {"text": "Fill in the blank: Neither of the boys ___ present.", "options": ["is", "are", "were", "have"], "answer": "A"},
                {"text": "What is a 'person who loves books' called?", "options": ["Bibliophile", "Philanthropist", "Optimist", "Polyglot"], "answer": "A"},
                {"text": "Identify the error: 'He don't know the answer'.", "options": ["He", "don't", "know", "answer"], "answer": "B"},
                {"text": "Meaning of 'Vague'.", "options": ["Clear", "Uncertain", "Sharp", "Small"], "answer": "B"},
                {"text": "Choose the correct conjunction: Although he is poor, ___ he is honest.", "options": ["but", "yet", "and", "so"], "answer": "B"},
                {"text": "What is the plural of 'Criterion'?", "options": ["Criterions", "Criteria", "Criterias", "Criteri"], "answer": "B"},
                {"text": "Find the word with the prefix 'un-'.", "options": ["Under", "Uncle", "Unhappy", "Unit"], "answer": "C"}
            ]
        },
        {
            "name": "Technical",
            "questions": [
                {"text": "Which language is primarily used for Android App development?", "options": ["Swift", "Kotlin", "C#", "PHP"], "answer": "B"},
                {"text": "What does HTML stand for?", "options": ["Hyper Text Markup Language", "High Text Machine Language", "Hyper Tabular Machine Log", "None"], "answer": "A"},
                {"text": "Which of these is not an Operating System?", "options": ["Windows", "Linux", "Oracle", "macOS"], "answer": "C"},
                {"text": "What is the full form of SQL?", "options": ["Structured Query Language", "Simple Query Language", "Standard Query Link", "Sequential Query List"], "answer": "A"},
                {"text": "Which protocol is used to fetch emails from a server?", "options": ["HTTP", "FTP", "POP3", "SMTP"], "answer": "C"},
                {"text": "In Python, which function is used to get the length of a list?", "options": ["size()", "count()", "len()", "length()"], "answer": "C"},
                {"text": "What is the smallest unit of data in a computer?", "options": ["Byte", "Bit", "Nibble", "Kilobyte"], "answer": "B"},
                {"text": "Which sorting algorithm has the best average time complexity?", "options": ["Bubble Sort", "Selection Sort", "Quick Sort", "Insertion Sort"], "answer": "C"},
                {"text": "What is the time complexity of searching an element in a balanced BST?", "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"], "answer": "C"},
                {"text": "Which keyword is used to define a function in Python?", "options": ["func", "define", "def", "function"], "answer": "C"},
                {"text": "What is a 'Primary Key' in a database?", "options": ["Duplicate entry", "Unique identifier", "Foreign link", "NULL value"], "answer": "B"},
                {"text": "Which data structure follows LIFO principle?", "options": ["Queue", "Stack", "Tree", "Graph"], "answer": "B"},
                {"text": "HTTP port number by default is?", "options": ["21", "25", "80", "443"], "answer": "C"},
                {"text": "What is the main function of CSS?", "options": ["Logic", "Database", "Styling", "Networking"], "answer": "C"},
                {"text": "Which company developed Java?", "options": ["Microsoft", "Google", "Sun Microsystems", "Apple"], "answer": "C"},
                {"text": "What is '404' error?", "options": ["Unauthorized", "Forbidden", "Not Found", "Internal Server Error"], "answer": "C"},
                {"text": "Which part of the computer is the 'Brain'?", "options": ["RAM", "Hard Disk", "CPU", "Motherboard"], "answer": "C"},
                {"text": "What does RAM stand for?", "options": ["Read Access Memory", "Random Access Memory", "Real Action Memory", "None"], "answer": "B"},
                {"text": "Which symbol is used for comments in Python?", "options": ["//", "/*", "#", "--"], "answer": "C"},
                {"text": "What is the binary representation of 10?", "options": ["1001", "1010", "1100", "1111"], "answer": "B"}
            ]
        }
    ]

    for cat_data in categories_data:
        category, _ = Category.objects.get_or_create(name=cat_data["name"])
        for q in cat_data["questions"]:
            Question.objects.get_or_create(
                category=category,
                text=q["text"],
                defaults={
                    "option_a": q["options"][0],
                    "option_b": q["options"][1],
                    "option_c": q["options"][2],
                    "option_d": q["options"][3],
                    "correct_answer": q["answer"]
                }
            )
    print("Successfully seeded questions for all categories.")

if __name__ == "__main__":
    populate()
