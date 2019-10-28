import json
import time
import os.path
from termcolor import \
    colored  # https://pypi.org/project/termcolor/ # print(colored("XXX", color='magenta', on_color='on_green'))
from declarations import *


def set_output_path():
    area_of_interest = read_json(path_area_of_interest)
    path_RESULTS = 'output/' + area_of_interest['location_name'] + '/'
    os.makedirs(path_RESULTS, exist_ok=True)
    print(colored("Output path set to: {}".format(path_RESULTS), color='blue'))
    return path_RESULTS


def set_search_dates():
    dataset = read_json(path_dataset)
    dates = {"from": dataset["startDatetime"][:10],
             "to": dataset["endDatetime"][:10]
             }
    return dates


def read_json(file_path):
    assert os.path.exists(file_path), "File does not exist" + file_path
    with open(file_path, 'r') as f:
        data = f.read()
    return json.loads(data)


def write_json(data, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, indent=2)


def token_seems_valid(TOKEN):
    if 'id_token' in TOKEN \
            and 'token_type' in TOKEN \
            and 'access_token' in TOKEN:
        if 'timestamp' in TOKEN:
            timestamp = float(TOKEN['timestamp'])
            timeleft = time.time() - timestamp
            if timeleft < 36000:
                print(colored(str("Token still valid for: " + str((36000 - timeleft) / 3600) + " hours\n"),
                              color='green'))
                valid = True
            else:
                print(colored("Token not valid anymore", color='red'))
                valid = False
        else:
            valid = False
    else:
        valid = False
    return valid


def go_through_all(status):
    all_resolved = ""
    for stat in status:
        assert status[stat].get('status'), print(colored("Error in pipeline, NO pipeline/task status", color='red'))
        if status[stat]['status'] == 'RESOLVED':
            print(colored('RESOLVED ', color='green'), end='')
        else:
            print(status[stat]['status'] + ' ', end='')
    print()
    for stat in status:
        if status[stat]['status'] == 'RESOLVED':
            all_resolved = 'RESOLVED'
        else:
            if status[stat]['status'] == 'FAILED':
                all_resolved = 'FAILED'
            else:
                all_resolved = 'PROCESSING'
            break
    return all_resolved
