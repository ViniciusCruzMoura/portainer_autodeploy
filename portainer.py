import requests, json, datetime, sys
from decouple import config

#Configs
PORTAINER_HOSTNAME = config("PORTAINER_HOSTNAME")
PORTAINER_LOGIN = config("PORTAINER_LOGIN")
PORTAINER_PASSWORLD = config("PORTAINER_PASSWORLD")
PORTAINER_TOKEN = None

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
    img_name = str(img_name).replace("_", "").replace(" ", "").replace(".", "").replace("-", "")
    url = f"{PORTAINER_HOSTNAME}/api/endpoints/2/docker/build?dockerfile=Dockerfile&remote={get_stack_detail(stack_name).get('GitConfig')['URL']}%23main&t={img_name}:latest&t={img_name}:{datetime.datetime.today().strftime('%y.%m.%d')}"
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
    url = f"{PORTAINER_HOSTNAME}/api/stacks/{stack_id}/git/redeploy?endpointId=2"
    print(url)
    payload = json.dumps({
      "env": stack_detail.get('Env'),
      "prune": False,
      "RepositoryReferenceName": stack_detail.get('GitConfig')['ReferenceName'],
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

def main() -> int:
    global PORTAINER_TOKEN, PORTAINER_LOGIN, PORTAINER_PASSWORLD

    if len(sys.argv) == 1 or sys.argv[1] is None:
        print("Unknown option, Try 'help' for more information.")
        sys.exit()

    if PORTAINER_HOSTNAME is None or PORTAINER_HOSTNAME == "":
        print("missing PORTAINER_HOSTNAME environment variable")
        sys.exit()
    if PORTAINER_LOGIN is None or PORTAINER_LOGIN == "":
        print("missing PORTAINER_LOGIN environment variable")
        sys.exit()
    if PORTAINER_PASSWORLD is None or PORTAINER_PASSWORLD == "":
        print("missing PORTAINER_PASSWORLD environment variable")
        sys.exit()

    if PORTAINER_LOGIN and PORTAINER_PASSWORLD:
        PORTAINER_TOKEN = get_token(PORTAINER_LOGIN, PORTAINER_PASSWORLD)

    action = sys.argv[1]
    if action == "help":
        print("These are common commands used in various situations:")
        print("COMMAND help")
        print("COMMAND list")
        print("COMMAND update")
        sys.exit()
    elif action == "list":
        print("List of Containers Stacks:")
        for stack in get_stacks():
            print(f"{stack.get('id_stack')} - {stack.get('stack_name')}")
        sys.exit()
    elif action == "status":
        if len(sys.argv) == 2 or sys.argv[2] is None:
            print("Unknown stack, Try 'list' for more information.")
            sys.exit()        
        stack_name = sys.argv[2]
        if not has_stack(stack_name):
            print("Stack not found!")
            sys.exit()
        print("Stack details:")
        detail = get_stack_detail(stack_name)
        if detail:
            print("Id: ",detail.get("Id"))
            print("Name: ",detail.get("Name"))
            print("EntryPoint: ",detail.get("EntryPoint"))
            #print("ResourceControl: ",detail.get("ResourceControl"))
            print("GitConfig URL: ",detail.get("GitConfig")['URL'])
            print("GitConfig ReferenceName: ",detail.get("GitConfig")['ReferenceName'])
            print("GitConfig ConfigFilePath: ",detail.get("GitConfig")['ConfigFilePath'])
            #print("Env: ", detail.get("Env"))
        sys.exit()
    elif action == "update":
        if len(sys.argv) == 2 or sys.argv[2] is None:
            print("Unknown stack, Try 'list' for more information.")
            sys.exit()
        stack_name = sys.argv[2]
        if not has_stack(stack_name):
            print("Stack not found!")
            sys.exit()
        build_success = image_build(stack_name)
        if not build_success:
            print("Build failed!")
            sys.exit()
        deploy_success = image_deploy(stack_name)
        if not deploy_success:
            print("Deploy failed!")
            sys.exit()
        print("Success!")
        sys.exit()
    else:
        print("Unknown option, Try 'help' for more information.")
        sys.exit()

if __name__ == '__main__':
    sys.exit(main())