import requests
url = 'http://127.0.0.1:5000/'
file = {'file':open('../tesseract/urine_test/urine5_cv2.jpeg', 'rb')}
r = requests.post(url, files=file)
print(r.text)
# print(r.json())

