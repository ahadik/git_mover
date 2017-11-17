import os.path
import sys

def get_destination_username(source_username):
    print "Looking for '%s'" % source_username
    if os.path.isfile("users_map.ini"):
        file_handler = open("users_map.ini", "r", 1)
        file_lines = file_handler.readlines()
        file_handler.close()
        for line in file_lines:
            [source, destination] = (str(line).strip()).split('=')
            if source == source_username:
                print "File matching: "+destination
                return destination

    return source_username

def add_user_to_text(username, text):
    return "Author: @%s\r\n\r\n%s" % (get_destination_username(username), text)
