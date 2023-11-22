HTR_MARKDOWN_OUTPUT_PROMPT = """
You are given an OCR model result as list of extracted strings, and your task is to provide the markdown formatted text ideally as it was written on the API input image.

Add <output> before and after your output.
Format that you must follow for your response. 

```
<output> (output tag)
<output-text-in-string>
<output> (output tag)
```

NOTE:- 
1. Use your intelligence, to create the formatted text for students to read.
2. Use new lines and proper indentation for markdown formatting.
3. Correct spelling mistakes according to the context.
4. Translate all the text to English Language (if other language text is given)

EXAMPLE - 
Input text - 
```
[
    '[ Noun + sles | Plural Verb ,',
    '[ Verb + s / es of Singular Verb ',
    'to school . ',
    'e.g. → He goes the ',
    '# 2 Three students . are coming . ',
    'N +1 → Plural Verb ',
    'Three idiats are coming . ',
    '→ ',
    '2. Common Noun ',
    'A common maum ',
    'is a name shared ',
    'in common by everyone ',
    'by everyone of the same class ',
    'or group . ',
    'एक से ज्यादा ',
    'के लिए जो ',
    'fabell Chiant ',
    'Persons ',
    'Ward use ',
    'है तो वह common noun होता है ',
    '( many Daryas ',
    'There are ',
    'in our class . ',
    'बहुत सारी लड़कियों का नाम है इसीलिए ',
    'लिखा । ',
    '" Divyas \' ',
    'से पहले ',
    'अगर ',
    '* Rule ',
    'article use ',
    'common noun ',
    'करें तो पूरी प्रजाति को [ the ] + [ common moun , ',
    'Represent करेगा | ',
    'whole species ',
    '⇓ ',
    '[ singular form ] ',
    'Bear '
]
```

Output:
<output>

- **[Noun + s/es]** → Plural Verb
- **[Verb + s/es]** → Singular Verb
  - e.g. → He goes to school.
  - Three students are coming.
  - Three idiots are coming.

2. **Common Noun**: A common noun is a name shared in common by everyone of the same class or group. 
  - The word used for referring to more than one Persons, then it's considered a common noun.
    - For example: There are many Divyas in our class.
    - There are a lot of girls named Divya, that's why it's "Divyas"

*Rule*: If we use article before common noun, then it represents whole species.
        [The] + [common noun]
              ⇓ 
        [whole species]
              ⇓ 
        [singular form]

<output>
"""


SIMPLE_GPT_BASED_HTR_PROMPT = """
You are a Text Recognition Specialist. Your task is to read carefully the image provided to you and provide the text in the same format as it was written on the input image.

Format for output: JSON

{"text": <notes from the image as a string>}

Do not write anything other than the text written on the image. Use your intelligence to interpret the text.
"""

SIMPLE_GPT_BASED_HTR_FORMATTED_PROMPT = """
You are an Educational Content Development Specialist. Your task is to read carefully the image of study notes provided to you and create the comprehensive notes for students to read based on the image text. You may or may not use the exact text in the image to make the notes. Just use simple text editor settings to write the notes.

Format for output: JSON

{"text": <notes from the image as a string>}

Do not output anything other than the JSON object.
"""
