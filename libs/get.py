import requests
'''
INPUT: an API endpoint for retrieving data
OUTPUT: the request object containing the retrieved data for successful requests. If a request fails, False is returnedself.
'''
def get_req(url, credentials, accept_content_type = 'application/json'):
    r = requests.get(url=url, auth=(credentials['user_name'], credentials['token']), headers={'Content-type': 'application/json', "Accept": accept_content_type})
    return r