import requests

url = "http://localhost:8000/api/v1/record/documents/descargar/6693ac20-87fa-4f77-a4c7-c9f22ea7ff70/"

payload = {}
headers = {
  'Authorization': 'Token 74df839455374152e23f5d1caf6684a9ea72fe53'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
