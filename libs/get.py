import requests, json
from check_res import check_res
'''
INPUT: an API endpoint for retrieving data
OUTPUT: the request object containing the retrieved data for successful requests. If a request fails, False is returnedself.
'''
def get_req(url, credentials, accept_content_type = 'application/json'):
    return requests.get(url=url, auth=(credentials['user_name'], credentials['token']), headers={'Content-type': 'application/json', "Accept": accept_content_type})

def get_data(url, credentials, accept_content_type = 'application/json'):
    r = get_req(url, credentials, accept_content_type)
    status = check_res(r)
    message = json.loads(r.text)
    if status and len(message) > 0:
        return message
    else:
        return False
