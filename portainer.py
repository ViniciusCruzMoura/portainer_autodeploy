import json, datetime, sys, os, fnmatch
#Set .venv packages
try:
    for py_ver in fnmatch.filter(os.listdir(os.path.join(os.getcwd(), ".venv", "lib")), 'python3.*'):
        sys.path.append(os.path.join(os.getcwd(), ".venv", "lib", py_ver, "site-packages"))
        break
except Exception as err:
    print(sys.path)
    print(err)
    sys.exit(1)
import requests
from decouple import config

#Configs
PORTAINER_HOSTNAME = config("PORTAINER_HOSTNAME")
PORTAINER_LOGIN = config("PORTAINER_LOGIN")
PORTAINER_PASSWORLD = config("PORTAINER_PASSWORLD")
PORTAINER_TOKEN = None

GITHUB_API_HOSTNAME = "https://api.github.com"
GITHUB_OWNER = "viniciuscruzmoura"
GITHUB_REPO = "portainer_autodeploy"
SOFTWARE_VERSION = "23.12.12"

def get_token(login, passworld) -> str:
    if login is None or passworld is None:
        return None
    url = f"{PORTAINER_HOSTNAME}/api/auth"
    payload = json.dumps({
        "username": login,
        "password": passworld
    })
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code >= 300:
        print(response.text)
        return None
    token = response.json().get("jwt")
    return token

def get_stacks() -> dict:
    url = f"{PORTAINER_HOSTNAME}/api/stacks"
    payload = {}
    headers = {
        'Authorization': f'Bearer {PORTAINER_TOKEN}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    list_stacks = []
    for r in response.json():
        can_add = True
        for x in list_stacks:
            if x.get("stack_name") == r.get("Name"):
                can_add = False
        if can_add:
            list_stacks.append(
                {
                    "id_stack": r.get("Id"),
                    "stack_name": r.get("Name"),
                }
            )
    return list_stacks

def has_stack(stack_name) -> bool:
    url = f"{PORTAINER_HOSTNAME}/api/stacks"
    payload = {}
    headers = {
        'Authorization': f'Bearer {PORTAINER_TOKEN}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    for r in response.json():
        if r.get("Name") == stack_name:
            return True
    return False

def get_stack_detail(stack_name) -> dict:
    url = f"{PORTAINER_HOSTNAME}/api/stacks"
    payload = {}
    headers = {
        'Authorization': f'Bearer {PORTAINER_TOKEN}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code >= 300:
        print(response.status_code, response.text)
        return None
    for r in response.json():
        if r.get("Name") == stack_name:
            return r
    return None

def image_build(img_name) -> bool:
    stack_name = img_name
    stack_detail = get_stack_detail(stack_name)
    endpoint = stack_detail.get("EndpointId")
    img_name = str(img_name).replace("_", "").replace(" ", "").replace(".", "").replace("-", "")
    git_conf = get_stack_detail(stack_name).get("GitConfig")
    if git_conf is None:
        return False
    url = f"{PORTAINER_HOSTNAME}/api/endpoints/{endpoint}/docker/build?dockerfile=Dockerfile&remote={git_conf['URL']}%23main&t={img_name}:latest&t={img_name}:{datetime.datetime.today().strftime('%y.%m.%d')}"
    print(url)
    payload = "{}"
    headers = {
      'Authorization': f'Bearer {PORTAINER_TOKEN}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    if response.status_code >= 300:
        print(response.json())
        return False
    return True

def image_deploy(stack_name) -> bool:
    stack_detail = get_stack_detail(stack_name)
    stack_id = stack_detail.get("Id")
    endpoint = stack_detail.get("EndpointId")
    if stack_detail.get("GitConfig") is None:
        return False
    url = f"{PORTAINER_HOSTNAME}/api/stacks/{stack_id}/git/redeploy?endpointId={endpoint}"
    print(url)
    payload = json.dumps({
      "env": stack_detail.get('Env'),
      "prune": False,
      "RepositoryReferenceName": stack_detail.get("GitConfig")["ReferenceName"],
      "RepositoryAuthentication": False,
      "RepositoryUsername": "",
      "RepositoryPassword": "",
      "PullImage": False
    })
    headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {PORTAINER_TOKEN}'
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.status_code)
    if response.status_code >= 300:
        print(response.text)
        return False
    return True

def github_check_new_versions() -> None:
    github_response = requests.get(f"{GITHUB_API_HOSTNAME}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest")
    github_latest_release = github_response.json()["name"]
    software_version = SOFTWARE_VERSION
    if software_version != github_latest_release:
        #print("IMPORTANT MESSAGE!!!\n")
        print(f"New version available '{github_latest_release}', See what's new ('https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}')")
        #print("\n")

def main(args) -> int:
    global PORTAINER_TOKEN, PORTAINER_LOGIN, PORTAINER_PASSWORLD

    if len(args) == 1 or args[1] is None:
        print("Unknown option, Try 'help' for more information.")
        return 1

    if PORTAINER_HOSTNAME is None or PORTAINER_HOSTNAME == "":
        print("missing PORTAINER_HOSTNAME environment variable")
        return 1
    if PORTAINER_LOGIN is None or PORTAINER_LOGIN == "":
        print("missing PORTAINER_LOGIN environment variable")
        return 1
    if PORTAINER_PASSWORLD is None or PORTAINER_PASSWORLD == "":
        print("missing PORTAINER_PASSWORLD environment variable")
        return 1

    if PORTAINER_LOGIN and PORTAINER_PASSWORLD:
        PORTAINER_TOKEN = get_token(PORTAINER_LOGIN, PORTAINER_PASSWORLD)

    github_check_new_versions()

    action = args[1]
    if action == "help":
        print("These are common commands used in various situations:")
        print("COMMAND help")
        print("COMMAND list")
        print("COMMAND update")
        return 0
    elif action == "list":
        print("List of Containers Stacks:")
        for stack in get_stacks():
            print(f"{stack.get('id_stack')} - {stack.get('stack_name')}")
        return 0
    elif action == "status":
        if len(args) == 2 or args[2] is None:
            print("Unknown stack, Try 'list' for more information.")
            return 1
        stack_name = args[2]
        if not has_stack(stack_name):
            print("Stack not found!")
            return 1
        print("Stack details:")
        detail = get_stack_detail(stack_name)
        if detail:
            print("Id: ",detail.get("Id"))
            print("Name: ",detail.get("Name"))
            print("EntryPoint: ",detail.get("EntryPoint"))
            print("EndpointId: ",detail.get("EndpointId"))
            #print("ResourceControl: ",detail.get("ResourceControl"))
            if detail.get("GitConfig") is not None:
                print("GitConfig URL: ",detail.get("GitConfig")['URL'])
                print("GitConfig ReferenceName: ",detail.get("GitConfig")['ReferenceName'])
                print("GitConfig ConfigFilePath: ",detail.get("GitConfig")['ConfigFilePath'])
            #print("Env: ", detail.get("Env"))
            for idx, env in enumerate(detail.get("Env"), start=0):
                if idx == 0:
                    print("Env: ")
                print(" - ", env.get("name"), ":" ,env.get("value"))
        return 0
    elif action == "update":
        if len(args) == 2 or args[2] is None:
            print("Unknown stack, Try 'list' for more information.")
            return 1
        stack_name = args[2]
        if not has_stack(stack_name):
            print("Stack not found!")
            return 1
        build_success = image_build(stack_name)
        if not build_success:
            print("Build failed!")
            return 1
        deploy_success = image_deploy(stack_name)
        if not deploy_success:
            print("Deploy failed!")
            return 1
        print("Success!")
        return 0
    elif action == "rollback":
        #choose a image:version
        return 0
    elif action == "add":
        #add a new stack
        return 0
    elif action == "remove":
        #remove a stack
        return 0
    else:
        print("Unknown option, Try 'help' for more information.")
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))