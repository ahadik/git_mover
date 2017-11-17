import requests
'''
INPUT: an API endpoint for posting data
OUTPUT: the request object containing the posted data response for successful requests. If a request fails, False is returnedself.
'''
def patch_req(url, data, credentials, accept_content_type = 'application/vnd.github.v3.html+json'):
    r = requests.patch(url=url, data=data, auth=(credentials['user_name'], credentials['token']), headers={'Content-type': 'application/json', 'Accept': accept_content_type})
    return r
