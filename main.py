import math
import urllib.parse
import requests
import csv
import os
import argparse
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
api_key = os.getenv('API_KEY')
api_url = os.getenv('API_URL')
headers = {'apikey': api_key}

user_group_names = {}
process_start_time = datetime.now()


def get_api_url(endpoint, params=''):
    endpoint = '/' + endpoint.lstrip('/')

    if params:
        params.lstrip('?')
        params = '?' + urllib.parse.quote(params, safe='&=')

    return api_url + endpoint + params


def get(url):
    response = requests.get(headers=headers, url=url)
    return response.json()


def get_user_ids():
    params = 'order=`title` ASC'

    url = get_api_url('user', params)
    resp = get(url)

    if resp['objects']:
        return resp['objects']
    else:
        return []


def get_cached_user_group_name(user_group_id: int) -> str:
    if user_group_id not in user_group_names:
        url = get_api_url('usergroup/' + str(user_group_id))
        resp = get(url)
        user_group_names[user_group_id] = resp['properties']['title']

    return user_group_names[user_group_id]


def get_cached_user_groups_names(user_group_ids: list) -> list:
    user_groups_names = []
    for user_group_id in user_group_ids:
        user_groups_names.append(get_cached_user_group_name(user_group_id))

    return user_groups_names


def get_eta(current: int, count: int) -> str:
    global process_start_time

    if current <= 0:
        return 'Infinity'

    running_duration = datetime.now() - process_start_time
    estimated_duration = (count / current) * running_duration
    eta = estimated_duration - running_duration

    eta_str = str(eta)

    if ',' in eta_str:
        eta_str = eta_str.split(',')[0]

    if '.' in eta_str:
        eta_str = eta_str.split('.')[0]

    return eta_str


def validate_filename(filename: str) -> bool:
    try:
        f = open(filename, 'x')
        f.close()
    except FileExistsError:
        print(f'ERROR file exists: {filename}')
        print("We won't override files. Please provide a different filename.")
        return False
    except FileNotFoundError:
        print(f'ERROR invalid filename path: {filename}')
        print(f'Make sure the directory exists: {os.path.dirname(filename)}')
        return False

    return True


def run_export(filename: str):
    global process_start_time

    if not validate_filename(filename):
        return

    user_ids = get_user_ids()

    current_user = 1
    total_users = len(user_ids)
    digits = math.ceil(math.log10(total_users))

    data = [['name', 'email', 'group_names', 'mfa', 'last_login']]

    process_start_time = datetime.now()

    for user_id in user_ids:
        user_uri = get_api_url('user/' + str(user_id))

        user = get(user_uri)
        group_names = get_cached_user_groups_names(user['parents'])

        # WARNING: This endpoint is undocumented and may change at any time
        last_login_uri = get_api_url('user/' + str(user_id) + '/lastused')
        last_login = get(last_login_uri)
        timestamp = last_login['timestamp']

        userdata = user['properties']
        name = userdata['title']
        email = userdata['email']
        group_names_string = ', '.join(group_names)
        mfa = userdata['tfaenabled']

        msg = '[ETA {eta}  {current:' + str(digits) + 'd}/{total:' + str(
            digits) + 'd}]    {name:<60}    {email:<60}    {mfa:<}    {timestamp}    {group_names_string}'
        print(msg.format(
            eta=get_eta(current_user, total_users),
            current=current_user,
            total=total_users,
            name=name,
            email=email,
            group_names_string=group_names_string,
            mfa=mfa,
            timestamp=timestamp))

        data.append([name, email, group_names_string, mfa, timestamp])

        current_user += 1

    with open(filename, 'x', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f'Completed. See: {filename}')


parser = argparse.ArgumentParser(
    description='Generate CSV with all Webling users including their groups (roles), last login timestamps and MFA '
                'status.',
    epilog='See https://github.com/grueneschweiz/webling-get-user-list'
)
parser.add_argument('filename', help="Absolute or relative path to output file. The filename must not exist.")
args = parser.parse_args()

run_export(args.filename)
