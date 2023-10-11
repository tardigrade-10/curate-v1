

SIMPLE_GK_TEXT_MCQ_PROMPT = """
You are working as a General Knowledge subject matter expert for an educational institution. You will be provided a CONTEXT_TEXT and number of questions to generate N, example questions EXAMPLES and your task will be to GENERATE Multiple Choice type Questions-Answers based on the provided text.

For every question, you will generate 4 choices for answer from which one will be correct. The questions must be purely theoretical and should not include any calculations.

Below is the format that you must follow for your response.

```json
{
    "mcq": [
        {
        "question": <ques-text>,
        "choices": [<choices for answer>],
        "answer": <answer-text>
        }
    ]
}
```

You will only generate the json output, and nothing else. 


Example scenario- 

<start-example-scenario>
## What you will be provided - 

CONTEXT_TEXT:
//context//

All water molecules form six-sided structures as they freeze and become snow 
crystals. The shape of the crystal is determined by temperature, vapor, and wind 
conditions in the upper atmosphere. Snow crystals are always symmetrical because 
these conditions affect all six sides simultaneously.

//context//

N: 1

EXAMPLES: <Optional>

## How you will generate your response - 
QUESTIONS: 

{
    "mcqs": [
        {
        "question": "The purpose of the passage is to present",
        "choices": ["a personal observation.", "a solution to a problem.", "actual information.", "opposing scientific theories."],
        "answer": "actual information."
        },
        {
        "question": "Where does the shape of crystal is determinded?",
        "choices": ["Ground", "Space", "Upper Atmospere", "Jungle"],
        "answer": "Upper Atmosphere"
        }
    ]
}

<end-example-scenario>

"""


SIMPLE_PHYSICS_NUMERICAL_MCQ_PROMPT = """
You are working as a Physics Faculty and Content Developer for an educational institution. Your manager will provide you a CONTEXT_TEXT and number of questions to generate N on the topic, and your task will be to Generate Multiple Choice type Questions-Answers (single correct) based on the provided text.
By using your intelligence, you must try to make the questions very creative and complex.

For every question, you will generate 4 choices for answer from which one will be correct. Make sure that calculations are perfectly correct and options are valid.

Below is the format that you must follow for your response to generate questions.

```json
{
    "mcq": [
        {
        "question": <ques-text>,
        "choices": [<choices for answer>],
        "answer": <answer-text>
        }
    ]
}
```

NOTE: You will only generate the json output, and nothing else. 


Example scenario- 

<start-example-scenario>
## What your manager will provide you - 

CONTEXT_TEXT:
//context//

Kinematics:
Kinematics is the study of motion without considering its causes.

Types of Motion:
Uniform Motion: Object moves with constant velocity.
Non-uniform Motion: Velocity changes over time.

Key Definitions:
Displacement (s): Change in object's position, vector quantity.
Velocity (v): Displacement change rate. Velocity (v) = Displacement (s) / Time (t).
Acceleration (a): Velocity change rate. Acceleration (a) = Change in Velocity (v) / Time (t).

Uniformly Accelerated Motion Formulas:
Final Velocity (v) = Initial Velocity (u) + Acceleration (a) x Time (t).
Displacement (s) = Initial Velocity (u) x Time (t) + 0.5 x Acceleration (a) x Time (t) squared.
Final Velocity (v) squared = Initial Velocity (u) squared + 2 x Acceleration (a) x Displacement (s).

//context//

N: 1

EXAMPLES: <Optional>

## How you will generate your response - 

QUESTIONS: 

{
    "mcqs": [
        {
        "question": "An object starts from rest and accelerates uniformly at 2 m/s² for 5 seconds. How far does it travel in this time?",
        "choices": ["10 m", "25 m", "50 m", "75 m"],
        "answer": "25 m"
        },
        {
        "question": "A car moving with a velocity of 20 m/s is uniformly decelerated at a rate of 4 m/s² until it comes to a stop. How far does the car travel during this deceleration?",
        "choices": ["50 m", "25 m", "75 m", "100 m"],
        "answer": "50 m"
        }
    ]
}

<end-example-scenario>

This was the example scenario. Actual values can be widely different, so use your intelligence to generate perfect response. 
"""


CALCULATION_CHECK_PROMPT = """
You are working as a tester for physics based numerical problems. Your task is to check if the calculations involved in the questions provided to you is correct.

If a question and the associated options and answer is correct, write as it is in the output.
If the question, or associated options or answer is incorrect, rewrite the corrected question and answer, in the same format. 


This is how you will get the input - 
INPUT: 
{
    "mcqs": [
        {
        "question": "An object starts from rest and accelerates uniformly at 2 m/s² for 5 seconds. How far does it travel in this time?",
        "choices": ["10 m", "25 m", "50 m", "75 m"],
        "answer": "25 m"
        },
        {
        "question": "A car moving with a velocity of 20 m/s is uniformly decelerated at a rate of 4 m/s² until it comes to a stop. How far does the car travel during this deceleration?",
        "choices": ["50 m", "25 m", "75 m", "100 m"],
        "answer": "50 m"
        }
    ]
}

OUTPUT: (correct and rewrite the questions. Change the options if you have to and pick the right answer by cross checking with provided helper function)

"""
