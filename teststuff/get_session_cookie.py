import requests

session = requests.Session()

resp = session.get("https://opinion.lawmaking.go.kr/better/main")

print(session.cookies)

print('done')