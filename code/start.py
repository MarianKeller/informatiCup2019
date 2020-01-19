import subprocess
import requests

from time import sleep

print("")
subprocess.call(['python', 'genetic.py'], shell=True)
sleep(5)
print(requests.post('http://localhost:50122/main', json={}))