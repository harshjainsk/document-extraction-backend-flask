import numpy as np
import cv2
import re


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def get_cropped_image(image, bounding_box):
    x1 = np.int32(bounding_box[0])
    y1 = np.int32(bounding_box[1])
    x2 = np.int32(bounding_box[2])
    y2 = np.int32(bounding_box[3])
    
    cropped_image = image[y1:y2, x1:x2]
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
    return cropped_image


def get_cropped_image(image, bounding_box):
    x1 = np.int32(bounding_box[0])
    y1 = np.int32(bounding_box[1])
    x2 = np.int32(bounding_box[2])
    y2 = np.int32(bounding_box[3])
    
    cropped_image = image[y1:y2, x1:x2]
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
    return cropped_image


def extract_details_from_aadhar(text):
    text_list = text.split(" ")
    try:
        text_list.pop(text_list.index("Government"))
        text_list.pop(text_list.index("of"))
        text_list.pop(text_list.index("India"))
        text_list.pop(text_list.index("Issue"))
        text_list.pop(text_list.index("Download"))
        text_list.pop(text_list.index("Date"))
        text_list.pop(text_list.index("Name"))
    except Exception as e:
        print(e)
    text = " ".join(text_list)
    
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

    # extract date of birth
    date = "No date"
    text_list_for_date = text.split(" ")
    for i in text_list:
        if 'DOB' in i:
            date = i
    


    # extract gender

    if 'Male' in text:
        gender = 'Male'
    else:
        gender = 'Female'

    # extract Aadhar number
    aadhar_pattern = r"\d{4} \d{4} \d{4}"
    aadhar_match = re.search(aadhar_pattern, text)
    if aadhar_match:
        aadhar_number = aadhar_match.group(0)
    else:
        aadhar_pattern = r"\d{12}"
        aadhar_match = re.search(aadhar_pattern, text)
        if aadhar_match:
            aadhar_number = aadhar_match.group(0)
        else:
            aadhar_number = "No data extracted"

    print("Name:", name)
    print("Date of Birth:", date)
    print("Gender:", gender)
    print("Aadhar Number:", aadhar_number)
    
    return {
        "name" : name,
        "dob" : date,
        "gender" : gender,
        "aadhaar_number" : aadhar_number
    }


def give_detection_results(image):
    image = cv2.resize(image, (640, 640))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model(image)
    print(results)
    # return results
    print(results)
    bbox = results.xyxy[0][0]
    cropped_image = get_cropped_image(image, bbox)
    detected_class = int(results.xyxy[0][0][-1])
    detected_class = names[detected_class]
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
    result = ocr.ocr(cropped_image, cls=True)
    extraction = ""
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            extraction += line[-1][0]
            extraction += ' '
    print(extraction)

    if detected_class == 'aadhar card':
        info = extract_details_from_aadhar(extraction)
    elif detected_class == 'driving license':
        info = extract_details_from_aadhar(extraction)
    elif detected_class == 'pan card':
        return extraction
    elif detected_class == 'salary slip':
        info = extract_details_from_aadhar(extraction)
    else:
        info = extract_details_from_aadhar(extraction)


    return info