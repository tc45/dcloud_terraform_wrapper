
import requests
import datetime
import json
import os


def get_token(id, secret):
    url = 'https://cloudsso.cisco.com/as/token.oauth2'
    payload = f'grant_type=client_credentials&client_id={id}&client_secret={secret}'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.request('POST', url, data=payload, headers=headers, allow_redirects=False, timeout=30)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Error: {response.text}")
        return False
    else:
        return response.json()['access_token']


def rest_call(token, url, payload=None):
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', "Authorization": "Bearer %s" %token}
    if payload != None:
        response = requests.request('POST', url, data=payload, headers=headers, allow_redirects=False, timeout=30)
    else:
        response = requests.request('POST', url, headers=headers, allow_redirects=False, timeout=30)
    return response.json()


def terraform_apply(file):
        if os.path.isfile(file):
            os.system("terraform init")
            os.system("terraform validate")
            os.system("terraform apply")
            print("Terraform apply complete.")
            return True
        else:
            print(f'File {file} does not exist')
            print("Terraform apply FAILED.")
            return False


def get_time():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")


def get_diff(start, end):
    import datetime
    start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%f")
    end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%f")
    diff = end - start
    return diff.total_seconds()


def get_env_vars():
    try:
        print(os.environ)
        customer_id = os.environ['CISCO_CUSTOMER_ID']
        customer_secret = os.environ['CISCO_CUSTOMER_SECRET']
        customer_dict = {
            "id": customer_id,
            "secret": customer_secret
        }
        return customer_dict
    except KeyError:
        s = f"""
        {'-'*40}'
        The following environment variables are required but were not found:
        
            CISCO_CUSTOMER_ID
            CISCO_CUSTOMER_SECRET
            
        These variables must be set using the `export` command in Linux/Mac or the `set` command in Windows.
        
        To permanently set the variables use the following processes:
            
            Windows - Use the setx command in a command prompt window
                - setx CISCO_CUSTOMER_ID <your customer id>
                - setx CISCO_CUSTOMER_SECRET <your customer secret>
                
            Linux/Mac - Add the export command to the .bashrc file in your home directory
                # Edit the .bashrc file in your home directory
                - nano ~/.bashrc
                - export CISCO_CUSTOMER_ID=<your customer id>
                - export CISCO_CUSTOMER_SECRET=<your customer secret>
                # Reload your bashrc file
                - source ~/.bashrc
                
        If you do not have a Cisco Customer ID (not the same as your username), you can create one at:
        
        https://apiconsole.cisco.com/apps/myapps
        
        To create the app choose the following options:
        
        1. Register a new app
        2. Create a name for the app and a description (i.e. Topology Builder)
        3. Choose 'Service' for Application Type
        4. Choose 'Client Credentials' for Grant Type
        5. Select 'Hello API' for the Select APIs section
        6. Agree to terms of service
        7. Click 'Register'  
        8. Copy the Key (Client ID) and Client Secret to the environment variables above
        {'-'*40}'
        """
        print(s)
        return False


if __name__ == '__main__':
    start_time = get_time()
    env_info = get_env_vars()
    if isinstance(env_info, dict):
        print(f"Using id: {env_info['id']}")
        print(f"Using secret: {env_info['secret']}")
        token = get_token(env_info['id'], env_info['secret'])
        print(token)
        os.environ['TB_AUTH_TOKEN'] = token
        if terraform_apply('my_topology.tf'):
            print('Terraform apply successful')
        else:
            print('Terraform apply failed')
    end_time = get_time()
    print(f"The total runtime is {get_diff(start_time, end_time)}")
