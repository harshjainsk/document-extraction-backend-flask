import numpy as np
from PIL import Image
import cv2
import torch
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
from model_utils import get_cropped_image
import re


model = torch.hub.load('ultralytics/yolov5', 'custom', path = '150-epochs-best.pt', force_reload = True)
ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
names = ['aadhar card', 'driving license', 'pan card', 'salary slip', 'voter id']


image = cv2.imread("testing-images/9b5ee2dd759ebd6ab10442c3bac0b823.jpg")
image = cv2.resize(image, (640, 640))
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
results = model(image)
print(results)
# return results
print(results)
bbox = results.xyxy[0][0]
print(np.int32(bbox))
cropped_image = get_cropped_image(image, bbox)
detected_class = int(results.xyxy[0][0][-1])
detected_class = names[detected_class]
# cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
cv2.imshow("cropped_image", cropped_image)
cv2.waitKey(0)


result = ocr.ocr(cropped_image, cls=True)
extraction = ""
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        extraction += line[-1][0]
        extraction += ' '
print(extraction)


text = extraction
# text = " ".join(text_list)
    
# name
match = re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)
if match:
    name = match.group()
    # print(name)  # Output: Harsh Kumar Jain
else:
    match = re.search(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text)
    if match:
        name = match.group()
        # print(name)
    else:
        name = "No name detected"

date_regex = r"\b(\d{2}/\d{2}/\d{4})\b"

matches = re.findall(date_regex, text)
if matches:
    date = matches[0]
    print(date)
else:
    print("No date found.")


print("Name:", name)
print("Date of Birth:", date)



# tensor([118.16742,  21.73656, 558.43317, 531.13373,   0.97069,   2.00000])
# tensor([1.81895e+01, 1.63337e+02, 6.07965e+02, 4.45462e+02, 5.48408e-01, 0.00000e+00])
# [ 18 163 607 445   0   0]



# text = "Ccbhie PXIH. HCbR INCOME TAX DEPARTMENT GOVTOFINDIA nechs Permanent Account Number Card BFAPL9762A SELHUVO LOHE /Name fT T/Father's Name CHINEYILOHE 16012020 Date of Birth 3.dohe 10/09/2001 /Signature"
# text_list = text.split(" ")
# try:
#     text_list.pop(text_list.index("INCOME"))
#     text_list.pop(text_list.index("TAX"))
#     text_list.pop(text_list.index("DEPARTMENT"))
#     text_list.pop(text_list.index("GOVTOFINDIA"))

# except Exception as e:
#     print(e)

# print(text_list)

# "FERHTST HRGRGR INCOMETAX DEPARTMENT GOVT.OFINDIA NITIN JITURI TULSIDAS VENKUSA JITUR 25/06/1981 Permanent Account Number ALAPJ944OL"