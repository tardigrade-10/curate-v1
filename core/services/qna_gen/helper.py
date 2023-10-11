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
