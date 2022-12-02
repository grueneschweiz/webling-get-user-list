# Webling Get User List

Export a list of all users from Webling, including their groups (roles), last 
login timestamp and MFA status.

## Why is this needed

As of 02.12.22, the provided export function in the GUI does not include the 
roles.

## What it does

Generate a CSV file containing a list of all users with the following columns:
- name
- email
- group_names
- mfa
- last login

## Installation

```
# Clone this repository
git clone git@github.com:grueneschweiz/webling-get-user-list.git

# Create a [virtual environment](https://docs.python.org/3/library/venv.html)
python3 -m venv venv

# Load the virtual environment (for Bash on GNU/Linux and MacOS)
# Other environments: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment
source venv/bin/activate

# Install requirements 
pip3 install -r requirements.txt

# Set API_URL and API_KEY
echo "API_KEY=***" > .env
echo "API_URL=https://***.webling.ch/api/1" >> .env
chmod 600 .env
```

The API_KEY must have the following permissions:

- Administrator


## Usage

```
# Load the virtual environment (for Bash on GNU/Linux and MacOS)
# Other environments: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment
source venv/bin/activate

# help
python3 -u main.py -h

# run
python3 -u main.py /path/to/output/file.csv
```