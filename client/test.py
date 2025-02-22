import requests


def get_anythingllm_online_status():
    try:
        r = requests.get("http://192.168.1.29:3001", timeout=2)
        if (r.status == 200):
            return True
        else:
            return False
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("AnythingLLM Host Offline.")
        return False
    except requests.exceptions.HTTPError:
        print("AnythingLLM Host Error 4xx or 5xx.")
        return False
    else:
        return True

print(get_anythingllm_online_status())
