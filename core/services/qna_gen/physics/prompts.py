

SIMPLE_PHYSICS_TEXT_MCQ_PROMPT = """
You are working as a Physics subject matter expert for an educational institution. You will be provided a CONTEXT_TEXT and number of questions to generate N, example questions EXAMPLES and your task will be to GENERATE Multiple Choice type Questions-Answers based on the provided text.

For every question, you will generate 4 choices for answer from which one will be correct. The questions must be purely theoretical and should not include any calculations.

Below is the format that you must follow for your response.

```json
{
    "mcqs": [
        {
        "question": <ques-text>,
        "choices": {"a": "choice1", "b": "choice2", "c": "choice3", "d": "choice4"},
        "answer": {<answer-option>: <answer-choice>}
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

N: 2

EXAMPLES: <Optional>

## How you will generate your response - 
QUESTIONS: 

{
    "mcqs": [
        {
        "question": "The purpose of the passage is to present",
        "choices": {"a": "a personal observation.", "b": "a solution to a problem.", "c": "actual information.", "d": "opposing scientific theories."},
        "answer": {"c": "actual information"}
        },
        {
        "question": "Where does the shape of crystal is determinded?",
        "choices": {"a": "Ground", "b": "Space", "c": "Upper Atmospere", "d": "Jungle"},
        "answer": {"c": "Upper Atmosphere"}
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
    "mcqs": [
        {
        "question": <ques-text>,
        "choices": {"a": "choice1", "b": "choice2", "c": "choice3", "d": "choice4"},
        "answer": {<answer-option>: <answer-choice>}
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

N: 2

EXAMPLES: <Optional>

## How you will generate your response - 

QUESTIONS: 

{
    "mcqs": [
        {
        "question": "An object starts from rest and accelerates uniformly at 2 m/s² for 5 seconds. How far does it travel in this time?",
        "choices": {"a": "10 m", "b": "25 m", "c": "50 m", "d": "75 m"},
        "answer": {"b": "25 m"}
        },
        {
        "question": "A car moving with a velocity of 20 m/s is uniformly decelerated at a rate of 4 m/s² until it comes to a stop. How far does the car travel during this deceleration?",
        "choices": {"a": "50 m", "b": "25 m", "c": "75 m", "d": "100 m"},
        "answer": {"a": "50 m"}
        }
    ]
}

<end-example-scenario>

This was the example scenario. Actual values can be widely different, so use your intelligence to generate perfect response. 
"""


CALCULATION_CHECK_PROMPT = """
You are working as a tester for physics based numerical problems. Your task is to check if the calculations involved in the question provided to you is correct.

SAMPLE INPUT:

```json
{
"question": "An object starts from rest and accelerates uniformly at 2 m/s² for 5 seconds. How far does it travel in this time?",
"choices": {"a": "10 m", "b": "25 m", "c": "50 m", "d": "75 m"},
"answer": {"b": "25 m"}
}
```

NOTES:
- You will use an external function to check the calculation.
- If the options and/or answer is correct, write as it is in the output.
- If the options and/or answer is incorrect, use your intelligence to choose the options in a very smart way.
- OUTPUT will be in the exact same format as the input. It will be processed as json.

In case you get unexpected output, for ex. fractions, approximations, etc., you will have to choose the options appropriately.
"""
