import json
import time
import copy
from utilities import read_json
from utilities import write_json
from utilities import token_seems_valid
from tasks import Task
from termcolor import \
    colored  # https://pypi.org/project/termcolor/ # print(colored("XXX", color='magenta', on_color='on_green'))
from declarations import *


class Authorization:
    def __init__(self, loop):
        self.TOKEN_REQ_URL = "https://spaceknow.auth0.com/oauth/ro"
        self.AUTHORISE_URL = "https://spaceknow-user.appspot.com/user/authorize"
        self.TOKEN = {}
        self.loop = loop
        print(colored("Authorization object created:", color='white', attrs=['bold']))

    def request_token(self, credentials_path):
        credentials = read_json(credentials_path)
        authentication = Task(self.loop)
        hdrs = {'Content-Type': 'application/json'}
        req_auth = authentication.do_the_task(self.TOKEN_REQ_URL, hdrs, json.dumps(credentials))
        self.TOKEN = req_auth[0]
        self.TOKEN['timestamp'] = time.time()
        headers.update({'Authorization': 'Bearer {}'.format(self.TOKEN['id_token'])})
        write_json(self.TOKEN, path_token)
        if 'status_code' in req_auth[0] and req_auth[0]['status_code'] == 200:
            print(colored("New token saved in: {}".format(path_token), color='green'))
        else:
            print(
                colored("New token request Failed, status code: {}".format(req_auth[0]['status_code']), color='red'))

    def check_token(self, TOKEN_path):
        valid = False
        try:
            TOKEN = read_json(TOKEN_path)
            authentication = Task(self.loop)

            if token_seems_valid(TOKEN):
                hdrs = copy.deepcopy(headers)
                hdrs.update({'Authorization': 'Bearer {}'.format(TOKEN['id_token'])})
                auth = authentication.do_the_task(self.AUTHORISE_URL, hdrs,
                                                  json.dumps({"token": TOKEN['id_token']}))

                if 'status_code' in auth[0] and auth[0]['status_code'] == 200:
                    valid = True
                    print(colored("Token authentication successful ", color='green'))
                    self.TOKEN = TOKEN
                    headers.update({'Authorization': 'Bearer {}'.format(self.TOKEN['id_token'])})
                else:
                    print(colored("Token authentication Failed, status code:{}".format(auth[0]['status_code']),
                                  color='red'), colored("\nbut, new Token request will be called", color='blue'))

                    valid = False
            else:
                valid = False
        except:
            print(colored("Token Not found!", color='red'),
                  colored("but, new request will be called", color='blue'))
        finally:
            return valid


if __name__ == "__main__":

    import asyncio
    loop = asyncio.get_event_loop()
    auth = Authorization(loop)
    if not (auth.check_token(path_token)):
        auth.request_token(path_credentials)
    # print(headers)
    loop.close()
