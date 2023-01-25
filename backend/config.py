import requests
from requests.auth import HTTPBasicAuth

endPoint = 'https://api.auth.bismarck.xyz'
webPoint = 'http://auth.bismarck.xyz'
publicKey = requests.get(
    f'{endPoint}/getPublicKey',
    headers={'origin': webPoint},
    auth=HTTPBasicAuth(username='ckyf-auth', password='73de730aa315bca1939d302ba72e0f1b'),
    verify=True
).text
