#Test if a response object is valid
def check_res(r):
    #if the response status code is a failure (outside of 200 range)
    if r.status_code < 200 or r.status_code >= 300:
        #print the status code and associated response. Return false
        print "STATUS CODE: "+str(r.status_code)
        print "ERROR MESSAGE: "+r.text
        #if error, return False
        return False
    #if successful, return True
    return True