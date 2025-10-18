import DidengAPI
apis = DidengAPI.client.DidengAPI()
try:
    api = (str(str((apis.get_info())["CA-Library-IDE"]["best_version"])).split("v")[1])
except:
    api = "Get API version failed"