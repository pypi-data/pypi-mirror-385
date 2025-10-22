from google.cloud import vision_v1
import re
import io
from deep_translator import GoogleTranslator
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import cv2
from dateutil.parser import parse
from idvpackage.common import eastern_arabic_to_english, english_to_eastern_arabic

def extract_text_from_image_data(client, image):
    """Detects text in the file."""

    with io.BytesIO() as output:
        image.save(output, format="PNG")
        content = output.getvalue()

    image = vision_v1.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    return texts[0].description

def detect_id_card(client, image_data, id_text):

    if id_text:
        vertices = id_text[0].bounding_poly.vertices
        left = vertices[0].x
        top = vertices[0].y
        right = vertices[2].x
        bottom = vertices[2].y

        padding = 30
        left -= padding
        top -= padding
        right += padding
        bottom += padding

        with Image.open(io.BytesIO(image_data)) as img:
            id_card = img.crop((max(0, left), max(0, top), right, bottom))

            enhanced_img = enhance_quality(np.array(id_card))
            enhanced_img_pil = Image.fromarray(enhanced_img)

            # second_part_text = extract_text_from_image_data(client, enhanced_img_pil)
            try:
                part_text = extract_text_from_image_data(client, id_card)
            except:
                part_text = id_text[0].description

            return id_text, id_card, part_text
    else:
        print('No text found in the image.')


def sharpen_image(image):
    kernel = np.array([[-1, -1, -1],
                    [-1, 9, -1],
                    [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)


def adjust_contrast(image, factor):
    pil_image = Image.fromarray(image)
    enhancer = ImageEnhance.Contrast(pil_image)
    enhanced_image = enhancer.enhance(factor)
    return np.array(enhanced_image)

def adjust_brightness(image, factor):
    pil_image = Image.fromarray(image)
    enhancer = ImageEnhance.Brightness(pil_image)
    enhanced_image = enhancer.enhance(factor)
    return np.array(enhanced_image)

def enhance_quality(image):
    sharpened_image = sharpen_image(image)
    enhanced_image = adjust_brightness(sharpened_image, 0.8)
    enhanced_contrast = adjust_contrast(enhanced_image, 0.8)
    # grayscale_image = cv2.cvtColor(enhanced_contrast, cv2.COLOR_BGR2GRAY)
    
    return enhanced_contrast

def extract_personal_info(raw_text):
    name_pattern = r"الاسم\s*:\s*([^\n]+)|الاسم\s*:?([^\n]+)|الاء\s*:\s*([^\n]+)"
    fathers_name_pattern = r"الاب\s*:\s*([^\n]+)|الاب\s*:?([^\n]+)|\s*الأب\s*:?([^\n]+)"
    last_name_pattern = r"الشهرة\s*([^\n]+)|الشهرة\s*:\s*([^\n]+)"

    name_match = re.search(name_pattern, raw_text)
    fathers_name_match = re.search(fathers_name_pattern, raw_text)
    last_name_match = re.search(last_name_pattern, raw_text)

    name = None
    if name_match:
        name = name_match.group(1) or name_match.group(2) or name_match.group(3)
    
    fathers_name = None
    if fathers_name_match:
        fathers_name = fathers_name_match.group(1) or fathers_name_match.group(2) or fathers_name_match.group(3)
    
    last_name = None
    if last_name_match:
        last_name = last_name_match.group(1) or last_name_match.group(2)
        last_name.replace(":", "")

    return {
        "name": name,
        "father_name": fathers_name,
        "last_name": last_name
    }

def extract_id_numbers(raw_data):
    match = re.search(r'[\d٠١٢٣٤٥٦٧٨٩]{7,12}', raw_data)
    
    if match:
        id_number_ar = match.group(0)
        id_number_ar_padded = id_number_ar.zfill(12).replace("0", "٠")
        id_number_ar_padded = english_to_eastern_arabic(id_number_ar_padded)
        id_number_en_padded = eastern_arabic_to_english(id_number_ar_padded)
        # print(id_number_ar_padded, id_number_en_padded)
        return id_number_ar_padded, id_number_en_padded
    else:
        return "", ""


def extract_first_name_ar(text):
    patterns = [
        r"(?:الإسم|الاسم):\s*([^\n]+)",
        r"(?:الإسم|الاسم)\s+([^\n]+)",
        r"(?:سم|اسم)\s+([^\n]+)",
    ]

    for pattern in patterns:
        regex = re.compile(pattern, re.MULTILINE)
        match = regex.search(text)
        if match:
            return match.group(1).strip().replace(":", "")

    return None


def extract_last_name_ar(text):
    patterns = [
        r"(?:الشهرة):\s*([^\n]+)",
        r"(?:الشهرة)\s+([^\n]+)",
    ]

    for pattern in patterns:
        regex = re.compile(pattern, re.MULTILINE)
        match = regex.search(text)
        if match:
            return match.group(1).strip().replace(":", "")

    return None


def extract_fathers_name_ar(text):
    patterns = [
        r"(?:اسم الاب|سم الاب):\s*([^\n]+)",
        r"(?:اسم الاب|سم الاب)\s+([^\n]+)",
    ]

    for pattern in patterns:
        regex = re.compile(pattern, re.MULTILINE)
        match = regex.search(text)
        if match:
            return match.group(1).strip().replace(":", "")

    return None


def lebanon_front_id_extraction(client, image_data, text, desc):
    id_data = {}
    dob, place_of_birth = '', ''

    date_pattern = r"\d{4}/\d{1,2}/\d{1,2}"
    dob_match = re.search(date_pattern, desc)
    if dob_match:
        dob = dob_match.group()
    
    place_of_birth_pattern = r"محل الولادة (.+)|محل الولادة:\s*(.+)|محل الولادة\s*:\s*(.+)"

    place_of_birth = None
    place_of_birth_match = re.search(place_of_birth_pattern, desc)
    if place_of_birth_match:
        place_of_birth = place_of_birth_match.group(1) or place_of_birth_match.group(2) or place_of_birth_match.group(3)
        place_of_birth = place_of_birth.replace(":", "").replace(" ", "")

    id_data['dob'] = dob
    id_data['place_of_birth'] = place_of_birth

    ## CASE 1 - HANDLING
    if not id_data.get('father_name', '') or not id_data.get('last_name', '') or not id_data.get('name', '') or id_data.get('fathers_name', '') == 'اسم':
        id_text, id_card, second_part_text = detect_id_card(client, image_data, text)
        id_data_new = extract_personal_info(second_part_text)
        # print(f"\nID DATA NEW: {id_data_new}\n")
        # print(f"\nORIGINAL DATA: {desc}\n")
        
        if not id_data.get('father_name', '') or id_data.get('father_name', '')=='اسم':
            id_data['father_name'] = id_data_new['father_name']
        if not id_data.get('last_name', ''):
            id_data['last_name'] = id_data_new['last_name']
        if not id_data.get('name', ''):
            id_data['first_name'] = id_data_new['name']

    ## CASE - HANDLING Place Of Birth
    if not second_part_text:
        id_text, id_card, second_part_text = detect_id_card(client, image_data, text)

    extracted_words = [line.split(':', 1)[1].strip() for line in second_part_text.split('\n') if ':' in line]
    extracted_words_original = [line.split(':', 1)[1].strip() for line in desc.split('\n') if ':' in line]

    if not id_data.get('place_of_birth', ''):
        if len(extracted_words) >= 5:
            birth_place = extracted_words[4]
            id_data['place_of_birth'] = birth_place
    
    if not id_data.get('place_of_birth', ''):
        if len(extracted_words_original) >= 5:
            birth_place = extracted_words_original[4]
            id_data['place_of_birth'] = birth_place
    
    if not id_data.get('dob', ''):
        date_pattern = r"\d{4}/\d{1,2}/\d{1,2}"
        dob_match = re.search(date_pattern, second_part_text)
        if dob_match:
            dob = dob_match.group()
            id_data['dob'] = dob



    ## CASE 2 - HANDLING NAMES EMPTY
    if not id_data.get('father_name') or id_data.get('father_name')=='اسم':
        if len(extracted_words) >= 4:
            first_name = extracted_words[0]
            surname = extracted_words[1]
            fathers_name = extracted_words[2]
            try:
                birth_place = extracted_words[4]
            except:
                birth_place = ''

            if not id_data.get('father_name') or id_data.get('father_name')=='اسم':
                id_data['father_name'] = fathers_name

    ## CASE 3 - HANDLING NAMES WITH ORIGINAL DATA
    if not id_data.get('father_name', '') or not id_data.get('last_name', '') or not id_data.get('name', '') or id_data.get('fathers_name', '') == 'اسم' or id_data.get('name', '') == 'الشهرة': 
        id_data_new = extract_personal_info(desc)
        
        if not id_data.get('father_name') or id_data.get('father_name')=='اسم':
            id_data['father_name'] = id_data_new['father_name']
        if not id_data.get('last_name'):
            id_data['last_name'] = id_data_new['last_name']
        if not id_data.get('name') or id_data.get('name')=='الشهرة':
            id_data['first_name'] = id_data_new['name']

    ## fix place of birth
    place_of_birth_value = id_data.get('place_of_birth', '')
    try:
        parsed_pob= parse(place_of_birth_value)

        place_of_birth_pattern = r"محل الولادة (.+)"
        place_of_birth_match = re.search(place_of_birth_pattern, desc)
        if place_of_birth_match:
            place_of_birth = place_of_birth_match.group(1).replace(":", "").replace(" ", "")
            id_data['place_of_birth'] = place_of_birth
    except:
        pass
    
    dob = id_data.get('dob', '')
    try:
        parsed_pob= parse(dob)
    except:
        date_pattern = r"\d{4}/\d{1,2}/\d{1,2}"
        dob_match = re.search(date_pattern, desc)
        if dob_match:
            dob = dob_match.group()
            id_data['dob'] = dob
    
    is_any_empty = any(value == '' for value in id_data.values())
    if is_any_empty:
        date_pattern = r"\d{4}/\d{1,2}/\d{1,2}"
        dob_match = re.search(date_pattern, desc)
        if dob_match:
            dob = dob_match.group()
        
        place_of_birth_pattern = r"محل الولادة (.+)"
        place_of_birth_match = re.search(place_of_birth_pattern, desc)
        if place_of_birth_match:
            place_of_birth = place_of_birth_match.group(1).replace(":", "").replace(" ", "")

        if not id_data.get('dob'):
            id_data['dob'] = dob
        if not id_data.get('place_of_birth'):
            id_data['place_of_birth'] = place_of_birth
        if not id_data.get('place_of_birth'):
            place_of_birth_match = re.search(place_of_birth_pattern, second_part_text)
            if place_of_birth_match:
                place_of_birth = place_of_birth_match.group(1).replace(":", "").replace(" ", "")
            id_data['place_of_birth'] = place_of_birth

    if not id_data['dob']:
        date_pattern = r"\d{4}"
        dob_match = re.search(date_pattern, desc)
        if dob_match:
            dob = dob_match.group()
            id_data['dob'] = dob

    ## SPECIAL CASE TO HANDLE FIRST NAME - OUTLIERS
    if (not id_data['first_name'] and "الاسم" not in desc) or "الشهرة" in id_data['first_name']:
        lines = desc.split("\n")
        first_name = ""
        for i, line in enumerate(lines):
            if "الشهرة" in line:
                first_name = lines[i-1].strip()
                break  

        if 'الداخلية' not in first_name:
            id_data['first_name'] = first_name

    ## FINAL FALLBACK TO HANDLE EMPTY NAME CASES
    if not id_data['first_name']:
        try:
            f_name = extract_first_name_ar(second_part_text)
            if f_name:
                id_data['first_name'] = f_name
        except:
            pass

    if not id_data['father_name']:
        try:
            f_name = extract_fathers_name_ar(second_part_text)
            if f_name:
                id_data['father_name'] = f_name
        except:
            pass

    if not id_data['last_name']:
        try:
            f_name = extract_last_name_ar(second_part_text)
            if f_name:
                id_data['last_name'] = f_name
        except:
            pass
    
    ## TRANSLITERATE EXTRACTED NAMES TO ENGLISH
    if id_data['last_name']:
        id_data['last_name'] = id_data['last_name'].replace(":", "").replace("-", "").replace("_", "")
        try:
            id_data['last_name_en'] = GoogleTranslator(dest = 'en').translate(id_data['last_name'])
        except:
            id_data['last_name_en'] = ''
    else:
        id_data['last_name_en'] = ''

    if id_data['father_name']:
        id_data['father_name'] = id_data['father_name'].replace(":", "").replace("-", "").replace("_", "").replace("الاب", "").replace("الأب", "").replace(" ", "")
        try:
            id_data['fathers_name_en'] = GoogleTranslator(dest = 'en').translate(id_data['father_name'])
        except:
            id_data['fathers_name_en'] = ''
    else:
        id_data['fathers_name_en'] = ''

    if id_data['first_name']:
        id_data['first_name'] = id_data['first_name'].replace(":", "").replace("-", "").replace("_", "")
        try:
            id_data['first_name_en'] = GoogleTranslator(dest = 'en').translate(id_data['first_name'])
        except:
            id_data['first_name_en'] = ''
    else:
        id_data['first_name_en'] = ''

    if id_data['dob']:
        dob = eastern_arabic_to_english(id_data['dob'])
        id_data['dob'] = dob

    if id_data['place_of_birth']:
        id_data['place_of_birth_en'] = GoogleTranslator(dest = 'en').translate(id_data['place_of_birth'])

    id_number_ar, id_number_en = extract_id_numbers(second_part_text)
    if id_number_ar and id_number_en:
        id_data['id_number_ar'] = id_number_ar
        id_data['id_number'] = id_number_en
    else:
        id_number_ar, id_number_en = extract_id_numbers(desc)
        if id_number_ar and id_number_en:
            id_data['id_number_ar'] = id_number_ar
            id_data['id_number'] = id_number_en
        else:
            pass


    name = f"{id_data['first_name']} {id_data['father_name']} {id_data['last_name']}"
    name_en = f"{id_data['first_name_en']} {id_data['fathers_name_en']} {id_data['last_name_en']}"
    id_data['name'] = name
    id_data['name_en'] = name_en

    return id_data

    # except:
    #     return ''

def extract_gender_normalized(extracted_text):
    gender_ar, gender = '', ''
    
    if re.search(r'ذكر', extracted_text) or re.search(r'ذکر', extracted_text):
        gender_ar = 'ذكر'
        gender = 'M'

    elif re.search(r'انثى', extracted_text) or re.search(r'أنثى', extracted_text) or re.search(r'انتی', extracted_text) or re.search(r'انٹی', extracted_text):
        gender_ar = 'انثى'
        gender = 'F'
    
    return gender_ar, gender

def extract_issue_date(extracted_text):
    issue_date = ''
    date_pattern = r"\d{4}/\d{1,2}/\d{1,2}"
    date_match = re.search(date_pattern, extracted_text)
    if date_match:
        issue_date = date_match.group()
        
    return issue_date
    
def lebanon_back_id_extraction(extracted_text):
    gender_pattern = r"(?:الجنس|Gender)\s*:\s*([\w]+)"
    issue_date_pattern = r"تاريخ الإصدار:\s*([\d/]+)"
    registration_number_pattern = r"رقم السجل\s*:?\s*([\d]+)"

    gender_match = re.search(gender_pattern, extracted_text)
    issue_date_match = re.search(issue_date_pattern, extracted_text)
    registration_number_match = re.search(registration_number_pattern, extracted_text)
    
    gender_ar, gender = '', ''
    if gender_match:
        gender_ar = gender_match.group(1)
        gender = GoogleTranslator(dest = 'en').translate(gender_ar)
        if gender.lower() == 'male':
            gender = 'M'
        elif gender.lower() == 'female' or gender.lower() == 'feminine':
            gender = 'F'
    
    if not gender_ar:
        gender_ar, gender = extract_gender_normalized(extracted_text)
    
    issue_date = ''
    if issue_date_match:
        issue_date = issue_date_match.group(1)
    
    if not issue_date:
        issue_date = extract_issue_date(extracted_text)
    
    registration_number = ''
    if registration_number_match:
        registration_number = registration_number_match.group(1)
        registration_number_en = eastern_arabic_to_english(registration_number)

    back_data = {
        'gender_ar': gender_ar,
        'gender': gender,
        'issue_date': eastern_arabic_to_english(issue_date) if issue_date else '',
        'card_number_ar': english_to_eastern_arabic(registration_number),
        'card_number': registration_number_en if registration_number else '',
        'issue_date_ar': english_to_eastern_arabic(issue_date) if issue_date else ''
    }
    
    return back_data
