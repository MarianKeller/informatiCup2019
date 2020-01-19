import subprocess
import requests

subprocess.call(['python', 'genetic.py'])
requests.post('http://localhost:50122/main', json={})