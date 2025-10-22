from googletrans import Translator
import re
from datetime import datetime
import gender_guesser.detector as gender
import pycountry
from rapidfuzz import fuzz
from idvpackage.common import *


def convert_expiry_date(input_date):
    day = input_date[4:6]
    month = input_date[2:4]
    year = input_date[0:2]

    current_year = datetime.now().year
    current_century = current_year // 100
    current_year_last_two_digits = current_year % 100
    century = current_century

    if int(year) <= current_year_last_two_digits:
        century = current_century
    else:
        century = current_century
    final_date = f"{day}/{month}/{century}{year}"

    return final_date


def get_dates_to_generic_format(date):
    formats = ["%d/%m/%Y", "%Y/%m/%d", "%d %m %Y", "%Y %m %d"]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return None


def validate_date(date):
    try:
        date = datetime.strptime(date, "%d-%m-%Y")
        return date.strftime("%d-%m-%Y")
    except ValueError:
        try:
            date = datetime.strptime(date, "%d/%m/%Y")
            return date.strftime("%d/%m/%Y")
        except:
            return ''

def identify_gender(name):
    d = gender.Detector()
    gender_prediction = d.get_gender(name)
    return gender_prediction


def translated_gender_identifier(passport_text):
    translator = Translator()
    try:
        trans_res = translator.translate(passport_text, src='ar', dest='en').text 
    except:
        from deep_translator import GoogleTranslator
        trans_res = GoogleTranslator('ar', 'en').translate(passport_text)
        
    if re.search('male', trans_res, re.IGNORECASE):
        return 'M'
    if re.search('female', trans_res, re.IGNORECASE):
        return 'F'

    return ''


def extract_names(passport_text):
    lines = passport_text.split('\n')
    first_name_mrz, father_name, surname = '', '', ''
    
    for i, line in enumerate(lines):
        if 'First name' in line:
            first_name_mrz = lines[i + 1].strip() if i + 1 < len(lines) else ''
        elif 'Father name' in line:
            father_name = lines[i + 1].strip() if i + 1 < len(lines) else ''
        elif 'Name' in line and not 'First name' in line and not 'Father name' in line:
            surname = lines[i + 1].strip() if i + 1 < len(lines) else ''
    
    return first_name_mrz, father_name, surname
    

def check_name_criteria(name):
    return (
        bool(re.search(r'\d', name)) or 
        bool(re.search(r'[\u0600-\u06FF]', name)) or 
        len(name) < 2
    )


def filter_names(names_list, names_to_remove):
    filtered_names = []
    for name in names_list:
        if len(name) <= 3:
            continue

        keep_name = True
        for to_remove in names_to_remove:
            score = fuzz.WRatio(name, to_remove)
            if score > 90 and abs(len(name) - len(to_remove)) <= 1:
                keep_name = False
                break

        if keep_name:
            filtered_names.append(name)

    return filtered_names


def find_and_filter_names(text):
        """
        Finds all uppercase names in the text and filters out common non-name uppercase abbreviations.
        """
        names_to_remove = ['WYNAND', 'LLA', 'LBN', 'FO', 'P', 'CAN', 'W', 'ALL', 'SUZA', 'UROS', 'CONGO', "SA", "ORAS", "CRONO", "ASSO", "TER", "AN", "MAI", "COF", "OROS", "GDGS", "SDGS", "ETTA", 'UZZA']
        names_list = re.findall(r'\b[A-Z]{2,}\b', text)
        return filter_names(names_list, names_to_remove)

def convert_to_mrz_date(date_str):
    month, day, year = date_str.split('/')

    year_last_two_digits = year[-2:]

    mrz_date = year_last_two_digits + month.zfill(2) + day.zfill(2)

    return mrz_date

def lebanon_passport_extraction(passport_text):
    passport_details = {}

    patterns = {
        'id_number': (r"([A-Za-z]\d{8}|[A-Za-z]\d{7}|[A-Za-z]{2}\d{7})", lambda match: match.group(1) if match else ''),
        'passport_number_mrz': (r"([A-Za-z]\d{8}|[A-Za-z]\d{7})", lambda match: match.group(1) if match else ''),
        'date_of_birth_mrz': (r'(\d+)[MF]', lambda match: convert_dob(match.group(1)) if match else ''),
        'date_of_expiry_mrz': (r'[MF](\d+)', lambda match: convert_expiry_date(match.group(1)) if match else ''),
        'gender': (r'(\d)([A-Za-z])(\d)', lambda match: match.group(2) if match else '')
    }
    
    passport_text_clean = passport_text.replace(" ", "")
    
    mrz1_pattern = r"P<{COUNTRY_CODE}[A-Z<]+<<[A-Z<]+<"
    
    iso_nationalities = [country.alpha_3 for country in pycountry.countries]
    
    name_dict = {}
    for country_code in iso_nationalities:
        current_pattern = mrz1_pattern.format(COUNTRY_CODE=country_code)

        mrz1_match = re.search(current_pattern, passport_text_clean)
        if mrz1_match:
            mrz1 = mrz1_match.group(0)
            
            extracted_text = mrz1.replace('P<','').replace(country_code,'').replace('<', ' ')
            name_list = extracted_text.strip().split()
            name = ' '.join(name_list[1:])
            passport_surname = name_list[0]
            
            if re.search(r'\bal\b', passport_surname.lower()):
                passport_surname = '-'.join(name_list[0:2])
                name = ' '.join(name_list[2:])
            
            if re.search(r'\bel\b', passport_surname.lower()):
                passport_surname = '-'.join(name_list[0:2])
                name = ' '.join(name_list[2:])

            name_dict = {
                'nationality': country_code,
                'first_name_mrz': name,
                'surname': passport_surname
            }

            passport_details.update(name_dict)
        
            break
        else:
            mrz1 = None
    
    if not mrz1:
        pattern = r"P[<\w@<]+<<[\w<]+<"
        matches = re.findall(pattern, passport_text)

        if matches:
            processed_matches = matches[0][5:]
        
            extracted_text = processed_matches.replace('@', '').replace('<', ' ')
            name_list = extracted_text.strip().split()
            name = ' '.join(name_list[1:])
            passport_surname = name_list[0]
            if re.search(r'\bal\b', passport_surname.lower()) or re.search(r'\bl\b', passport_surname.lower()):
                passport_surname = '-'.join(name_list[0:2])
                name = ' '.join(name_list[2:])
                    
            name_dict = {
                    'first_name_mrz': name,
                    'surname': passport_surname
                }
            
            passport_details.update(name_dict)
    
    ## HANDLE NAME GENERIC FOR VALIDATION
    # first_name_mrz, father_name, surname = extract_names(passport_text)
    mother_name = ''
    first_name_mrz, surname = name_dict.get('first_name_mrz'), name_dict.get('surname')

    if not all([first_name_mrz, surname]) or any(check_name_criteria(name) for name in [surname, first_name_mrz]):
        filtered_names = find_and_filter_names(passport_text)
        if len(filtered_names) >= 3:
            surname, first_name_mrz, father_name = filtered_names[1:4]
            if len(filtered_names) > 7 and len(filtered_names) <= 8:
                mother_name = filtered_names[0]
            elif len(filtered_names) > 8:
                if 'LBN' in filtered_names[6]:
                    mother_name = filtered_names[4] + ' ' + filtered_names[5]
                else:
                    mother_name = filtered_names[0] + ' ' + filtered_names[1]
        else:
            print("Error: Could not extract all required names.")
            return None 

        name_dict = {
                'first_name': first_name_mrz,
                'father_name': father_name,
                'last_name': surname,
                'mother_name': mother_name if mother_name else ''
            }

        passport_details.update(name_dict)

    else:
        mother_name = ''
        filtered_names = find_and_filter_names(passport_text)
        ## if mother name page is there in the image
        if len(filtered_names) > 7 and len(filtered_names) <= 8:
            father_name = filtered_names[3]
            mother_name = filtered_names[0]
        elif len(filtered_names) > 8:
            father_name = filtered_names[4]
            # if 'LBN' in filtered_names[6]:
            #     mother_name = filtered_names[4] + ' ' + filtered_names[5]
            # else:
            mother_name = filtered_names[0] + ' ' + filtered_names[1]
        else:
            ## if only father name and no mother name in the doc
            father_name = filtered_names[2]
            
        name_dict = {
                'father_name': father_name,
                'mother_name': mother_name if mother_name else ''
            }

        passport_details.update(name_dict)

    mrz2_pattern = r"\n[A-Z]\d+.*?(?=[<]{2,})"
    mrz2_matches = re.findall(mrz2_pattern, passport_text_clean)
    
    if mrz2_matches:
        mrz2 = mrz2_matches[0][1:]
    else:
        mrz2 = ''

    ## EXTRACTING FIELDS FROM MRZ2
    mrz2_keys = ['gender', 'passport_number_mrz', 'date_of_birth_mrz', 'date_of_expiry_mrz']

    for key, value in patterns.items():
        pattern = value[0]
        transform_func = value[1]

        text = passport_text
        if key in mrz2_keys:
            text = mrz2

        match = re.search(pattern, text)
        passport_details[key] = transform_func(match) if match else ''
    
    if passport_details['passport_number_mrz'] and (passport_details['passport_number_mrz']!=passport_details['id_number']):
        passport_details['id_number'] = passport_details['passport_number_mrz']

    ## HANDLE PASSPORT NO FROM MRZ
    if not passport_details.get('passport_number_mrz'):
        passport_number_pattern = r"([A-Za-z]\d{8,}[A-Za-z]{2,}.*?|[A-Za-z]*\d{8,}[A-Za-z]{2,}.*?)"
        passport_number_match = re.search(passport_number_pattern, passport_text_clean)
        if passport_number_match:
            passport_number = passport_number_match.group(1)
            passport_details['passport_number_mrz'] = passport_number[:9]
        
    ## HANDLE DOB DOE FROM MRZ
    if not (passport_details.get('date_of_birth_mrz') or passport_details.get('date_of_expiry_mrz')):
        dob_pattern = r"(\d{7})[MF]"
        dob_match = re.search(dob_pattern, passport_text_clean)
        if dob_match:
            dob = dob_match.group(1)
            passport_details['date_of_birth_mrz'] = convert_dob(dob)
        else:
            dob_pattern = r'.*?[\S]R[\S](\d{9,})\b'
            dob_match = re.search(dob_pattern, passport_text_clean)
            if dob_match:
                dob = dob_match.group(1)[:7]
                passport_details['date_of_birth_mrz'] = validate_date(convert_dob(dob))
    
        doe_pattern = r"[MF](\d+)"
        doe_match = re.search(doe_pattern, passport_text_clean)
        if doe_match:
            expiry = doe_match.group(1)
            passport_details['date_of_expiry_mrz'] = validate_date(convert_expiry_date(expiry))
        else:
            doe_pattern = r'.*?[\S]R[\S](\d{9,})\b'
            doe_match = re.search(doe_pattern, passport_text_clean)
            if doe_match:
                expiry = doe_match.group(1)[8:]
                passport_details['date_of_expiry_mrz'] = validate_date(convert_expiry_date(expiry))

    ## HANDLE DOB AND DOE CASES FROM GENERIC DATA FOR VALIDATION
    dob = ''
    expiry = ''
    
    try:
        matches = re.findall(r'\b\d{2}[\s/\-.]+\d{2}[\s/\-.]+\d{4}\b', passport_text, re.DOTALL)
        date_objects = [datetime.strptime(re.sub(r'[\s/\-.]+', ' ', date).strip(), '%d %m %Y') for date in matches]
        sorted_dates = sorted(date_objects)
        sorted_date_strings = [date.strftime('%d %m %Y') for date in sorted_dates]

        if len(sorted_date_strings) > 1:
            dob = sorted_date_strings[0]
            issue_date = sorted_date_strings[1]
            expiry = sorted_date_strings[-1]
    except:
        matches = re.findall(r'\b\d{2}[./]\d{2}[./]\d{4}\b', passport_text)
        date_objects = [datetime.strptime(date.replace('.', '/'), '%d/%m/%Y') for date in matches]
        sorted_dates = sorted(date_objects)
        sorted_date_strings = [date.strftime('%d/%m/%Y') for date in sorted_dates]

        if len(sorted_date_strings)>1:
            dob = sorted_date_strings[0]
            issue_date = sorted_date_strings[1]
            expiry = sorted_date_strings[-1]
        else:
            matches = re.findall(r'\d{4}-\d{2}-\d{2}', passport_text)
            date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in matches]
            sorted_dates = sorted(date_objects)
            sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

            if len(sorted_date_strings)>1:
                dob = sorted_date_strings[0].replace('-', '/')
                issue_date = sorted_date_strings[1].replace('-', '/')
                expiry = sorted_date_strings[-1].replace('-', '/')
            
            else:
                matches = re.findall(r'\d{2}-\d{2}-\d{4}', passport_text)
                date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in matches]
                sorted_dates = sorted(date_objects)
                sorted_date_strings = [date.strftime('%d-%m-%Y') for date in sorted_dates]

                if sorted_date_strings:
                    dob = sorted_date_strings[0].replace('-', '/')
                    issue_date = sorted_date_strings[1].replace('-', '/')
                    expiry = sorted_date_strings[-1].replace('-', '/')

    passport_details['dob'] = get_dates_to_generic_format(dob)
    passport_details['expiry_date'] = get_dates_to_generic_format(expiry)
    passport_details['issue_date'] = get_dates_to_generic_format(issue_date)
    
    ## HANDLE MISSED DATE FIELDS
    if not passport_details.get('dob', ''):
        passport_details['dob'] = passport_details.get('date_of_birth_mrz', '')
    if not passport_details.get('expiry_date', '') or (passport_details.get('expiry_date', '') == passport_details.get('issue_date', '')):
        passport_details['expiry_date'] = passport_details['date_of_expiry_mrz']
    
    ## HANDLE MISSED NAME FIELDS
    if not passport_details.get('first_name', ''):
        passport_details['first_name'] = passport_details['first_name_mrz']
    if not passport_details.get('last_name', '') or passport_details.get('last_name', '') != passport_details.get('surname', ''):
        passport_details['last_name'] = passport_details['surname']

    if not passport_details.get('id_number', ''):
        passport_details['id_number'] = passport_details.get('passport_number_mrz', '')

    ## HANDLE GENDER CASES EXCEPTIONS
    if not (passport_details.get('gender', '')):
        gender_pattern = r'(\d)([MFmf])(\d)'
        gender_match = re.search(gender_pattern, passport_text_clean)
        if gender_match:
            passport_details['gender'] = gender_match.group(2)
        else:
            if re.search(r'ذكر', passport_text) or re.search(r'ذکر', passport_text):
                passport_details['gender'] = 'M'

            elif re.search(r'انثى', passport_text):
                passport_details['gender'] = 'F'

            else:
                if passport_details.get('first_name_mrz'):
                    first_name_mrz = passport_details['first_name_mrz'].split()[0].capitalize()
                    predicted_gender = identify_gender(first_name_mrz)
                    passport_details['gender'] = 'M' if predicted_gender.lower() == 'male' else 'F' if predicted_gender.lower() == 'female' and predicted_gender != 'unknown' else translated_gender_identifier(passport_text)

    ## FEED IN MRZ DATA
    if len(mrz1) < 44:
        mrz1 = mrz1 = f"{mrz1}{'<' * (44 - len(mrz1))}"

    if not mrz2:
        try:
            mrz2_pattern = r'LR[A-Z0-9<]{42}|LR[A-Z0-9<]{40}'
            match = re.search(mrz2_pattern, passport_text.replace(" ", ""))
            if match:
                mrz2 = match.group(0)
            else:
                mrz2 = passport_details['id_number'] + passport_details['nationality'] + convert_to_mrz_date(passport_details['dob']) + passport_details['gender'] + convert_to_mrz_date(passport_details['expiry_date'])
        except:
            try:
                mrz2 = passport_details['id_number'] + passport_details['nationality'] + convert_to_mrz_date(passport_details['dob']) + passport_details['gender'] + convert_to_mrz_date(passport_details['expiry_date'])
            except:
                mrz2 = ''

    passport_details['mrz'] = mrz1 + mrz2
    passport_details['mrz1'] = mrz1
    passport_details['mrz2'] = mrz2

    fields_to_remove = [
        "first_name_mrz",
        "surname",
        "passport_number_mrz",
        "date_of_birth_mrz",
        "date_of_expiry_mrz"
    ]

    for field in fields_to_remove:
        if field in passport_details:
            del passport_details[field]

    return passport_details
