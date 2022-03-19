import subprocess
import json
def curl(content, bearer):
    response = subprocess.run(["curl", content,"-H", "Authorization: Bearer {}".format(bearer)], stdout = subprocess.PIPE)
    return json.loads(response.stdout.decode("utf-8")) 
def curlGet(content, bearer):
    response = subprocess.run(["curl","--request", "GET", content,"-header", "Authorization: Bearer {}".format(bearer)], stdout = subprocess.PIPE)
    return json.loads(response.stdout.decode("utf-8"))
