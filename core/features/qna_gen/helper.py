import os
import requests
import wolframalpha


def get_results_from_wolfram_alpha(queries):
    """This function will return the answer 
    for the input query from the users"""  
  
    # declaring a variable to store the APP ID  
    app_id = os.environ.get("WOLFRAM_ALPHA_APP_ID")
  
    # creating an object of the Client() class using the APP ID  
    the_client = wolframalpha.Client(app_id)  
  
    # storing the responses from wolfram alpha  
    responses = {}
    if isinstance(queries, list):
        for query in queries:
            response = the_client.query(query) 
            answer = next(response.results).text
            responses[query] = answer
    else:
        response = the_client.query(queries) 
        # print(response)
        answer = next(response.results).text
        responses[queries] = answer

    # returning the answer  
    return responses



# def query_wolframalpha(query):
#     base_url = "https://www.wolframalpha.com/api/v1/llm-api"
#     appid = os.environ.get("WOLFRAM_APP_ID")

#     params = {
#         "input": query,
#         "appid": appid
#     }
    
#     response = requests.get(base_url, params=params)

#     print(response)
    
#     if response.status_code == 200:
#         return response.text
#     else:
#         return f"Error: {response.status_code}"
    

def get_results_from_wolfram_cloud(query):
    from wolframclient.evaluation import WolframCloudSession, SecuredAuthenticationKey
    from wolframclient.language import wl, wlexpr

    key = SecuredAuthenticationKey(
        os.environ.get('WOLFRAM_CLOUD_KEY1'),
        os.environ.get('WOLFRAM_CLOUD_KEY2')
    )

    session = WolframCloudSession(credentials=key)

    session.start()
    result = session.evaluate(wlexpr(query))

    return result



function_definitions = {
    "get_results_from_wolfram_alpha": {
        "name": "get_results_from_wolfram_alpha",
        "description": """This function uses wolfram alpha endpoint that Understands natural language queries about entities in chemistry, physics, geography, history, art, astronomy, and more.\n- Performs mathematical calculations, date and unit conversions, formula solving, etc.\n- Convert inputs to simplified keyword queries whenever possible (e.g. convert \"how many people live in France\" to \"France population\").\n- Use ONLY single-letter variable names, with or without integer subscript (e.g., n, n1, n_1).\n- Use named physical constants (e.g., 'speed of light') without numerical substitution.\n- Include a space between compound units (e.g., \"Ω m\" for \"ohm*meter\").\n- To solve for a variable in an equation with units, consider solving a corresponding equation without units; exclude counting units (e.g., books), include genuine units (e.g., kg).""",
        "parameters": {
            "type": "object",
            "properties": {
            "queries": {
                "type": "string",
                "description": """curated natural language queries for wolfram alpha
                for example: "distance from earth to mars; current population of new delhi"."""
            }
            }
        },
            "required": ["queries"]
        },
    "get_results_from_wolfram_cloud":{
        "name": "get_results_from_wolfram_cloud",
        "description": """Use this function for problems solvable with Wolfram Language code.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """the input wolfram language query for mathematical calculations in string. ONLY proper wolfram language queries are supported. Format for Query: "a = Solve[aCoeff1*aVar == Var1 - Offset1 && aCoeff2*aVar == Var1 + Offset2, {aVar, Var1}][[1, 1, 2]]"."""
                }
            }
        },
        "required": ["query"]
    }
}
