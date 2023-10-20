format = {
    "topic_0": ["list of scraped text related to topic_0"],
    "topic_1": ["list of scraped text related to topic_1"]
}


SIMPLE_TS_PROMPTS = """
You will be provided with a RAW_TEXT corpus containing some useful educational information. Your task is to segregate the text into different topics.

For example, if you are given the raw text from past 5 days news scraping, your task will be to segregate the text into topics like "Politics", "Sports", "Business", etc.

Here is the input format.

RAW_TEXT
//raw//

[RAW TEXT HERE]

//raw//


OUTPUT FORMAT:
{
    "topic_0": ["list of scraped sentences or paragraphs related to topic_0"],
    "topic_1": ["list of scraped sentences or paragraphs related to topic_1"]
}


NOTE: You must only response with the json output, and nothing else.

"""

SIMPLE_TS_WITH_REF_PROMPTS = """
You will be provided with a RAW_TEXT corpus containing some useful educational information. Your task is to segregate the text into different topics.

For example, if you are given the raw text from past 5 days news scraping, your task will be to segregate the text into topics like "Politics", "Sports", "Business", etc. as per the reference provided to you.

The reference may contain information about the number of topics to segregate to, specific topics to segregate, and whether you need to segregate the complete text when provided with specific topics.

Here is the input format.

RAW_TEXT
//raw//

[RAW TEXT HERE]

//raw//

REFERENCE:

[SOME REFERENCE HERE]

OUTPUT FORMAT:
{
    "topic_0": ["list of scraped sentences or paragraphs related to topic_0"],
    "topic_1": ["list of scraped sentences or paragraphs related to topic_1"]
}


NOTE: You must only response with the proper json output, and nothing else. All json format rules must be followed in order to avoid JSONDecodeErrors.

"""