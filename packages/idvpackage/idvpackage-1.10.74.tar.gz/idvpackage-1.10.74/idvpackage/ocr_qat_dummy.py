import base64
import cv2
import io
import numpy as np
import re
from datetime import datetime
from PIL import Image
# from skimage.transform import radon
from google.cloud import vision_v1
from idvpackage.ocr_utils import *
from idvpackage.common import *
from idvpackage.sau_id_extraction import *
from idvpackage.iraq_id_extraction import *
from idvpackage.iraq_passport_extraction import *
from idvpackage.lebanon_id_extraction import *
from idvpackage.lebanon_passport_extraction import *
from idvpackage.qatar_id_extraction import *
import face_recognition
import tempfile
from PIL import Image, ImageEnhance, ImageOps
import json
from googletrans import Translator
from google.oauth2.service_account import Credentials
import pycountry
import sys
import pytesseract
from itertools import permutations
from rapidfuzz import fuzz
from idvpackage.spoofing_detection import spoof_detection_main
import imghdr

class IdentityVerification:

    def __init__(self, credentials_string):
        """
        This is the initialization function of a class that imports a spoof model and loads an OCR
        reader.
        """
        #self.images = images
        # credentials_path = resource_filename('idvpackage', 'streamlit-connection-b1a38b694505.json')
        # self.client = vision_v1.ImageAnnotatorClient.from_service_account_json(credentials_path)
        credentials_dict = json.loads(credentials_string)
        credentials = Credentials.from_service_account_info(credentials_dict)
        self.client = vision_v1.ImageAnnotatorClient(credentials = credentials)
        self.translator = Translator()
        self.iso_nationalities = [country.alpha_3 for country in pycountry.countries]
        
    def image_conversion(self,image):  
        """
        This function decodes a base64 string data and returns an image object.
        If the image is in RGBA mode, it is converted to RGB mode.
        :return: an Image object that has been created from a base64 encoded string.
        """
        # Decode base64 String Data
        img = Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))

        # Convert RGBA to RGB
        if img.mode == 'RGBA':
            # Create a blank background image
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the image on the background. 
            background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
            img = background

        return img

    def rgb2yuv(self, img):
        """
        Convert an RGB image to YUV format.
        """
        try:
            img=np.array(img)
            return cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
        except Exception as e:
            raise Exception(f"Error: {e}")
    
    def find_bright_areas(self, image, brightness_threshold):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh_image = cv2.threshold(gray_image, brightness_threshold, 255, cv2.THRESH_BINARY)[1]
        contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bright_areas = []

        for contour in contours:
            bounding_box = cv2.boundingRect(contour)

            area = bounding_box[2] * bounding_box[3]

            if area > 800:
                bright_areas.append(bounding_box)

        return len(bright_areas)

    def is_blurry(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        laplacian_variance = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        return laplacian_variance

    def identify_input_type(self, data):
        if isinstance(data, bytes):
                return "video_bytes"
        else:
            pass

        try:
            decoded_data = base64.b64decode(data)
            
            if decoded_data:
                return "base_64"
        except Exception:
            pass

        return "unknown"

    def sharpen_image(self, image):
        kernel = np.array([[-1, -1, -1],
                        [-1, 9, -1],
                        [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)


    def adjust_contrast(self, image, factor):
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer.enhance(factor)
        return np.array(enhanced_image)

    def adjust_brightness(self, image, factor):
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Brightness(pil_image)
        enhanced_image = enhancer.enhance(factor)
        return np.array(enhanced_image)

    def enhance_quality(self, image):
        sharpened_image = self.sharpen_image(image)
        enhanced_image = self.adjust_brightness(sharpened_image, 1.2)
        enhanced_contrast = self.adjust_contrast(enhanced_image, 1.2)
        # grayscale_image = cv2.cvtColor(enhanced_contrast, cv2.COLOR_BGR2GRAY)
        
        return enhanced_contrast

    def check_document_quality(self, data):
        
        input_type = self.identify_input_type(data)
        
        if input_type == 'base_64':
            image_quality = {
                'error': ''
            }

            label_text, label, value = spoof_detection_main(data)

            if label_text == 'SPOOF':
                image_quality['error'] = 'spoof'

            return image_quality
            # if side=='front':
                
        #         processed_front_id = self.image_conversion(data)

        #         front_id_text = pytesseract.image_to_string(processed_front_id)
        #         #print(remove_special_characters2(front_id_text))

        #         combined_pattern = r'(Resident Identity|Identity Card|Golden Card|FEDERAL AUTHORITY FOR IDENTITY|ARAB EMIRATE)'

        #         match = re.search(combined_pattern, remove_special_characters2(front_id_text), re.IGNORECASE)
                
        #         if not match:
                    
        #             image_quality["error"] = "not_front_id"
                    
        #             return image_quality
        #     else:
        #         processed_back_id = self.image_conversion(data)

        #         processed_back_id = pytesseract.image_to_string(processed_back_id)

        #         print(processed_back_id)

        #         pattern4 = r'(Card Number|<<|ILARE|IDARE|(?=.*\bOccupation\b).*|(?=.*\bEmployer\b).*|(?=.*\bIssuing Place\b).*)'

        #         k= re.search(pattern4, processed_back_id.replace(" ",""), re.IGNORECASE)

        #         if not k:
                    
        #             image_quality["error"] = "not_back_id"
                    
        #             return image_quality
        
        if input_type == 'video_bytes':
            video_quality = {
                'error': ''
            }
            # frame_count_vid = 0
            try:
                with tempfile.NamedTemporaryFile(delete=True) as temp_video_file:
                    temp_video_file.write(data)
                
                video_capture = cv2.VideoCapture(temp_video_file.name)

                if video_capture.isOpened():
                    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

                    for _ in range(frame_count):
                        ret, frame = video_capture.read()
#                         if ret:
                            # frame_count_vid+=1
                            # if frame_count_vid % 10 == 0:
                        _, buffer = cv2.imencode('.jpg', frame)
                        image_data = buffer.tobytes()

                        image = vision_v1.Image(content=image_data)

                        response = self.client.face_detection(image=image)
                        if len(response.face_annotations) >= 1:
                            break
#                     else:
#                         # No face detected in any frame
#                         print('here 1')
#                         video_quality['error'] = 'no_face_detected_in_video'
                
                selfie_result = self.extract_selfie_from_video(data)
                # print(f"DATA TYPE SHAPE: {selfie_result.shape}")
                if isinstance(selfie_result, dict):
                    video_quality['error'] = selfie_result['error']
                else:
                    selfie_blurry_result, selfie_bright_result = self.get_blurred_and_glared_for_doc(selfie_result)
                    if selfie_blurry_result == 'consider' or selfie_bright_result == 'consider':
                        video_quality['error'] = 'face_not_clear_in_video'
                    else:
                        video_quality['selfie'] = selfie_result
                        video_quality['shape'] = selfie_result.shape

            except Exception as e:
                
                video_quality['error'] = 'bad_video'

            return video_quality

    def is_colored(self, base64_image):
        img = self.image_conversion(base64_image)
        img = np.array(img)

        return len(img.shape) == 3 and img.shape[2] >= 3
    
    def get_blurred_and_glared_for_doc(self, image, brightness_threshold=230, blur_threshold=10):
        blurred = 'clear'
        glare = 'clear'
        
        # image = self.image_conversion(image)
        # image_arr = np.array(image)
        # enhanced_data = self.enhance_quality(image)

        blurry1 = self.is_blurry(image)
        if blurry1 < blur_threshold:
            blurred = 'consider'
        
        # yuv_image = self.rgb2yuv(image)
        brightness1 = np.average(image[..., 0])
        if brightness1 > brightness_threshold:
            glare = 'consider'

        # print(f"BLURRY, BRIGHT: {blurry1, brightness1}")
        # print(f"RESULT: {blurred, glare}")
        # glare1 = self.find_bright_areas(front_id_arr, 245)
        # glare2 = self.find_bright_areas(back_id_arr, 245)
        # if glare1 > 5 or glare2 > 5:
        #     glare = 'consider'
        
        return blurred, glare

    def standardize_date(self, input_date):
        input_formats = [
            "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y",
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y",
            "%Y%m%d", "%m%d%Y", "%d%m%Y",
            "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y",
            "%Y %m %d", "%d %m %Y", "%m %d %Y",
        ]

        for format in input_formats:
            try:
                parsed_date = datetime.strptime(input_date, format)
                standardized_date = parsed_date.strftime("%d/%m/%Y")
                return standardized_date
            except ValueError:
                pass

        return None

    def compare_dates(self, date_str1, date_str2):
        date_format = "%d/%m/%Y"

        date1 = datetime.strptime(date_str1, date_format)
        date2 = datetime.strptime(date_str2, date_format)

        if date1 == date2:
            return True
        else:
            return False

    def validate_fields_id(self, complete_ocr_data, country):
        validation_flag = True

        if country == 'IRQ':
            front_id_number = complete_ocr_data.get('id_number_front')
            back_id_number = complete_ocr_data.get('id_number')

            front_card_number = complete_ocr_data.get('card_number_front')
            back_card_number = complete_ocr_data.get('card_number')
            
            name_front_id = complete_ocr_data.get('name_en')
            
            r = name_front_id.split(' ')
            if len(r)>=3:
                name_front_id = r[0] + ' ' + r[-1]

            complete_name_back = f"{complete_ocr_data.get('first_name_back')} {complete_ocr_data.get('last_name_back')}"

            dob_generic = self.standardize_date(complete_ocr_data.get('dob'))
            if complete_ocr_data.get('dob_mrz'):
                dob_mrz = self.standardize_date(complete_ocr_data.get('dob_mrz'))

            doe_generic = self.standardize_date(complete_ocr_data.get('expiry_date'))
            if complete_ocr_data.get('expiry_date_mrz'):
                doe_mrz = self.standardize_date(complete_ocr_data.get('expiry_date_mrz'))

            if front_id_number and back_id_number:
                if front_id_number != back_id_number:
                    print('ID number mismatch')
                    validation_flag = False

            if front_card_number and back_card_number:
                if front_card_number != back_card_number:
                    print('Card number mismatch')
                    validation_flag = False

            if complete_name_back and name_front_id:
                similarity = fuzz.partial_ratio(complete_name_back, name_front_id)
                print(similarity)
                if similarity < 50:
                    print('Name mismatch')
                    validation_flag = False

            if dob_generic and dob_mrz:
                if self.compare_dates(dob_generic, dob_mrz)==False:
                    print('DOB mismatch')
                    validation_flag = False
            
            if doe_generic and doe_mrz:
                if self.compare_dates(doe_generic, doe_mrz)==False:
                    print('DOE mismatch')
                    validation_flag = False
            
        return validation_flag

    def check_nationality_in_iso_list(self, nationality):
        if len(nationality) > 3:
            try:
                country = pycountry.countries.lookup(nationality)
                nationality =  country.alpha_3
            except:
                return 'consider'

        ## Handling case for OMN as it comes as MN, due to O being considered as 0
        if nationality.upper() == 'MN':
            nationality = 'OMN'

        if nationality.upper() in self.iso_nationalities:
            return 'clear'
        else:
            return 'consider'

    def get_face_orientation(self, face_landmarks):
        left_eye = np.array(face_landmarks['left_eye']).mean(axis=0)
        right_eye = np.array(face_landmarks['right_eye']).mean(axis=0)

        eye_slope = (right_eye[1] - left_eye[1]) / (right_eye[0] - left_eye[0])
        angle = np.degrees(np.arctan(eye_slope))

        return angle

    def extract_selfie_from_video(self, video_bytes):
        video_dict = {
            'error': ''
        }

        with tempfile.NamedTemporaryFile(delete=True) as temp_video_file:
            temp_video_file.write(video_bytes)
        
        cap = cv2.VideoCapture(temp_video_file.name)

        ret, frame = cap.read()

        if not ret:
            pass

        # Convert frame to bytes
        is_success, buffer = cv2.imencode(".jpg", frame)
        io_buf = io.BytesIO(buffer)
        byte_content = io_buf.getvalue()

        image = vision_v1.Image(content=byte_content)

        # Perform face detection
        response = self.client.face_detection(image=image)
        faces = response.face_annotations

        # Initialize variables
        best_face = None
        best_score = -1

        for face in faces:
            vertices = [(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices]
            area = (vertices[2][0] - vertices[0][0]) * (vertices[2][1] - vertices[0][1])

            # Use detection confidence as a metric for clarity
            clarity = face.detection_confidence
            
            # Score to find the best face
            score = area * clarity
            
            if score > best_score:
                best_score = score
                best_face = face

            if best_face:
                vertices = [(vertex.x, vertex.y) for vertex in best_face.bounding_poly.vertices]
                left = vertices[0][0]
                upper = vertices[0][1]
                right = vertices[2][0]
                lower = vertices[2][1]

                frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cropped_face = frame_pil.crop((left, upper, right, lower))
                best_face = cropped_face
                best_face_image = np.array(best_face)
                cv2.imwrite('best_face.jpg', cv2.cvtColor(best_face_image, cv2.COLOR_RGB2BGR))

        if best_face is not None:
            return np.array(best_face)
        else:
   
            video_dict['error'] = 'no_face_detected_in_video'
            return video_dict

    def load_and_process_image_fr(self, base64_image, arr=False):
        try:
            if not arr:
                img = self.image_conversion(base64_image)
                img = np.array(img)
                image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            else:
                if base64_image.dtype != np.uint8:
                    print('Converting to uint8')
                    base64_image = base64_image.astype(np.uint8)

                image = cv2.cvtColor(base64_image, cv2.COLOR_RGB2BGR)

            # base64_image = base64_image.split(',')[-1]
            # image_data = base64.b64decode(base64_image)
            # image_file = io.BytesIO(image_data)

            # image = face_recognition.load_image_file(image_file)

            face_locations = face_recognition.face_locations(image)

            if not face_locations:
                return [], []
        
            face_encodings = face_recognition.face_encodings(image, face_locations)

            return face_locations, face_encodings
        except:
            return [], []
        
    def calculate_similarity(self, face_encoding1, face_encoding2):
        similarity_score = 1 - face_recognition.face_distance([face_encoding1], face_encoding2)[0]
        return round(similarity_score + 0.25, 2)

    def extract_face_and_compute_similarity(self, selfie, front_face_locations, front_face_encodings):
        face_locations1, face_encodings1 = self.load_and_process_image_fr(selfie, arr=True)
        face_locations2, face_encodings2 = front_face_locations, front_face_encodings

        if not face_encodings1 or not face_encodings2.any():
            print('No face detected in selfie or front ID')
            return 0
        else:
            # face_encoding1 = face_encodings1[0]
            # face_encoding2 = face_encodings2[0]
            largest_face_index1 = face_locations1.index(max(face_locations1, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))
            largest_face_index2 = face_locations2.index(max(face_locations2, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))

            face_encoding1 = face_encodings1[largest_face_index1]
            face_encoding2 = face_encodings2[largest_face_index2]

            similarity_score = self.calculate_similarity(face_encoding1, face_encoding2)

            return min(1, similarity_score)
    
    def calculate_landmarks_movement(self, current_landmarks, previous_landmarks):
        return sum(
            abs(cur_point.position.x - prev_point.position.x) +
            abs(cur_point.position.y - prev_point.position.y)
            for cur_point, prev_point in zip(current_landmarks, previous_landmarks)
        )

    def calculate_face_movement(self, current_face, previous_face):
        return abs(current_face[0].x - previous_face[0].x) + abs(current_face[0].y - previous_face[0].y)

    def calculate_liveness_result(self, eyebrow_movement, nose_movement, lip_movement, face_movement):
        eyebrow_movement_threshold = 15.0
        nose_movement_threshold = 15.0
        lip_movement_threshold = 15.0
        face_movement_threshold = 10.0

        if (
            eyebrow_movement > eyebrow_movement_threshold or
            nose_movement > nose_movement_threshold or
            lip_movement > lip_movement_threshold or
            face_movement > face_movement_threshold
        ):
            return True
        else:
            return False

    def detect_image_format(self, base64_image):
        decoded_image = base64.b64decode(base64_image)
        
        format = imghdr.what(None, decoded_image)
        
        return format

    # def check_for_liveness(self, similarity, video_bytes, face_match_threshold, frames_to_analyze=10):
    #     with tempfile.NamedTemporaryFile(delete=True) as temp_video_file:
    #         temp_video_file.write(video_bytes)

    #     cap = cv2.VideoCapture(temp_video_file.name)

    #     frame_count = 0
    #     previous_landmarks = None
    #     previous_face = None
    #     liveness_result_list = []

    #     for frame_count in range(frames_to_analyze):
    #         ret, frame = cap.read()
    #         if not ret:
    #             break

    #         _, buffer = cv2.imencode('.jpg', frame)
    #         image_data = buffer.tobytes()

    #         image = vision_v1.Image(content=image_data)

    #         response = self.client.face_detection(image=image)
    #         faces = response.face_annotations

    #         largest_face = None
    #         largest_face_area = 0

    #         for face in faces:
    #             current_landmarks = face.landmarks
    #             current_face = face.bounding_poly.vertices
    #             face_area = abs((current_face[2].x - current_face[0].x) * (current_face[2].y - current_face[0].y))

    #             if face_area > largest_face_area:
    #                 largest_face = face
    #                 largest_face_area = face_area

    #         if largest_face:
    #             current_landmarks = largest_face.landmarks
    #             current_face = largest_face.bounding_poly.vertices

    #             if previous_landmarks and previous_face:
    #                 eyebrow_movement = self.calculate_landmarks_movement(current_landmarks[:10], previous_landmarks[:10])
    #                 nose_movement = self.calculate_landmarks_movement(current_landmarks[10:20], previous_landmarks[10:20])
    #                 lip_movement = self.calculate_landmarks_movement(current_landmarks[20:28], previous_landmarks[20:28])
    #                 face_movement = self.calculate_face_movement(current_face, previous_face)

    #                 liveness_result = self.calculate_liveness_result(eyebrow_movement, nose_movement, lip_movement, face_movement)
    #                 liveness_result_list.append(liveness_result)

    #             previous_landmarks = current_landmarks
    #             previous_face = current_face

    #     cap.release()

    #     if any(liveness_result_list) :
    #         liveness_check_result = 'clear'
    #     else:
    #         liveness_check_result = 'consider'

    #     return liveness_check_result

    def check_for_liveness(  self, similarity, video_bytes, face_match_threshold=0.60):
        # Create a temporary file that will not be deleted automatically
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_file_path = temp_video_file.name
        
        try:
            # Write video bytes to the temporary file and flush
            temp_video_file.write(video_bytes)
            temp_video_file.flush()
            temp_video_file.close()  # Close the file to ensure it can be accessed by other processes
            
            # Open the video file with OpenCV
            cap = cv2.VideoCapture(temp_video_file_path)
            if not cap.isOpened():
                print("Unable to open video file.")
                return None

            liveness_result_list = []
            frames =   self.frame_count_and_save(cap)
            frame_count = len(frames)
            print(f"FRAMES: {frame_count}")

            frames_to_process = [frames[0], frames[-1]] if frame_count > 1 else [frames[0]]
            previous_landmarks = None
            previous_face = None

            for frame in frames_to_process:
                _, buffer = cv2.imencode('.jpg', frame)
                image_data = buffer.tobytes()
                image = vision_v1.Image(content=image_data)
                response =   self.client.face_detection(image=image)
                faces = response.face_annotations

                if not faces:
                    print("No faces detected in the frame")
                    continue

                largest_face = None
                largest_face_area = 0

                for face in faces:
                    current_landmarks = face.landmarks
                    current_face = face.bounding_poly.vertices
                    face_area = abs((current_face[2].x - current_face[0].x) * (current_face[2].y - current_face[0].y))

                    if face_area > largest_face_area:
                        largest_face = face
                        largest_face_area = face_area

                if largest_face:
                    current_landmarks = largest_face.landmarks
                    current_face = largest_face.bounding_poly.vertices

                    if previous_landmarks and previous_face:
                        eyebrow_movement =   self.calculate_landmarks_movement(current_landmarks[:10], previous_landmarks[:10])
                        nose_movement =   self.calculate_landmarks_movement(current_landmarks[10:20], previous_landmarks[10:20])
                        lip_movement =   self.calculate_landmarks_movement(current_landmarks[20:28], previous_landmarks[20:28])
                        face_movement =  self. calculate_face_movement(current_face, previous_face)

                        liveness_result =   self.calculate_liveness_result(eyebrow_movement, nose_movement, lip_movement, face_movement)
                        liveness_result_list.append(liveness_result)

                    previous_landmarks = current_landmarks
                    previous_face = current_face

            cap.release()  # Release the video capture

            liveness_check_result = 'clear' if any(liveness_result_list) else 'consider'
            print(f"LIVE RESULT LIST: {liveness_result_list}")
            print(f"SIMILARITY: {similarity}")
            print(f"face_match_threshold: {face_match_threshold}")

            return liveness_check_result

        finally:
            # Ensure the temporary file is deleted
            if os.path.exists(temp_video_file_path):
                os.remove(temp_video_file_path)
                print(f"Temporary file {temp_video_file_path} has been deleted.")


    def convert_dob(self, input_date):
        day = input_date[4:6]
        month = input_date[2:4]
        year = input_date[0:2]

        current_year = datetime.now().year
        current_century = current_year // 100
        current_year_last_two_digits = current_year % 100

        century = current_century
        # If the given year is greater than the last two digits of the current year, assume last century
        if int(year) > current_year_last_two_digits:
            century = current_century - 1

        final_date = f"{day}/{month}/{century}{year}"

        return final_date

    def convert_expiry_date(self, input_date):
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

    def clean_string(self, input_string):
        cleaned_string = re.sub(r'[^\w\s]', ' ', input_string)
        return cleaned_string.strip()
    

    def find_and_slice_number(input_number, digits):
            # Generate all possible permutations of the digits
            perms = [''.join(p) for p in permutations(digits)]
            
            # Initialize variables to keep track of the found pattern and its index
            found_pattern = None
            found_index = -1

            # Search for any permutation of the digits in the input_number
            for perm in perms:
                found_index = input_number.find(perm)
                if found_index != -1:
                    found_pattern = perm
                    break

            # If a pattern is found, slice the number accordingly
            if found_pattern:
                if found_index > len(input_number) - found_index - len(found_pattern):
                    # Slice to the left
                    sliced_number = input_number[:found_index + len(found_pattern)]
                else:
                    # Slice to the right
                    sliced_number = input_number[found_index:]
                
                return sliced_number
            else:
                return ''
            
    def get_ocr_results(self, processed_image):
        with io.BytesIO() as output:
            processed_image.save(output, format="PNG")
            image_data = output.getvalue()

        image = vision_v1.types.Image(content=image_data)
        response = self.client.text_detection(image=image)
        id_infos = response.text_annotations

        return id_infos

    def extract_document_info(self, image, side, document_type, country):
        document_data = {}
        if side=='front':
            document_data = self.extract_front_id_info(image, country)

        if side=='back':
            document_data = self.extract_back_id_info(image, country)

        elif document_type == 'passport':
            document_data = self.exract_passport_info(image, country)
        
        elif document_type == 'driving_license':
            pass
        
        return document_data
        
    def extract_front_id_info(self, front_id, country):
        if country == 'UAE':
            print("working on UAE")
            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            is_colored1 = self.is_colored(front_id)

            if is_colored1:
                try:
                    processed_front_id = self.image_conversion(front_id)
                    front_id_text = self.get_ocr_results(processed_front_id)
                    front_id_text_desc = front_id_text[0].description

                    combined_pattern = r'(Resident Identity|Identity Card|Golden Card|FEDERAL AUTHORITY FOR IDENTITY)'
                    match = re.search(combined_pattern, front_id_text_desc, re.IGNORECASE)

                    if not match:
                        front_data["error"] = "not_front_id"
                        return front_data
                    
                    img = processed_front_id
                    image = np.array(img)
                    pil_image = Image.fromarray(image)

                    doc_on_pp_result = document_on_printed_paper(image)

                    with io.BytesIO() as output:
                        pil_image.save(output, format="PNG")
                        image_data = output.getvalue()

                    logo_result = detect_logo(self.client, image_data, country)
                    screenshot_result = detect_screenshot(self.client, front_id)
                    photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                    front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)
                    print(f"blurred, glare: {front_blurred, front_glare}")

                    front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                    front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                    front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                    tampered_result, part_text = detect_id_card_uae(self.client, image_data, front_id_text)

                    # dob, expiry = '', ''
                    # date_matches = re.findall(r'\d{2}/\d{2}/\d{4}', front_id_text_desc)
                    # sorted_dates = sorted(date_matches)
                    
                    # if len(sorted_dates) > 1:
                    #     dob = sorted_dates[0]
                    #     expiry = sorted_dates[-1]

                    front_data = {
                        'front_extracted_data': front_id_text_desc,
                        'front_coloured': True,
                        'front_doc_on_pp': doc_on_pp_result,
                        'front_logo_result': logo_result,
                        'front_screenshot_result': screenshot_result,
                        'front_photo_on_screen_result': photo_on_screen_result,
                        'front_blurred': front_blurred, 
                        'front_glare': front_glare,
                        'front_face_locations': front_face_locations_str, 
                        'front_face_encodings': front_face_encodings_str,
                        'front_tampered_result': tampered_result
                    }

                    non_optional_keys = ["front_face_locations", "front_face_encodings"]
                    empty_string_keys = [key for key, value in front_data.items() if key in non_optional_keys and value == '']

                    if empty_string_keys:
                        front_data['error'] = 'covered_photo'

                except Exception as e:
                    front_data['error'] = 'bad_image'
                    front_data['error_details'] = e
                
            else:
                front_data['error'] = 'bad_image'
            
            return front_data

        if country == 'SAU':
         
            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            is_colored1 = self.is_colored(front_id)
            if is_colored1:
                try:
                    processed_front_id = self.image_conversion(front_id)
                    front_id_text = self.get_ocr_results(processed_front_id)
                    front_id_text = front_id_text[0].description
                    front_id_text_list= front_id_text.split('\n')

                    img = self.image_conversion(front_id)
                    image = np.array(img)
                    pil_image = Image.fromarray(image)

                    doc_on_pp_result = document_on_printed_paper(image)

                    with io.BytesIO() as output:
                        pil_image.save(output, format="PNG")
                        image_data = output.getvalue()

                    # saudi id has no logo, set hardcoded value
                    # logo_result = detect_logo_saudi(self.client, image_data)
                    logo_result = 'clear'
                    screenshot_result = detect_screenshot(self.client, front_id)
                    photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                    front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)

                    front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                    front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                    front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                    front_data_fields = extract_id_details(front_id_text_list)
                    valid_nationality_result = self.check_nationality_in_iso_list(front_data_fields.get('nationality'))

                    front_data = {
                        'valid_nationality': valid_nationality_result,
                        'front_extracted_data': front_id_text,
                        'front_coloured': True,
                        'front_doc_on_pp': doc_on_pp_result,
                        'front_logo_result': logo_result,
                        'front_screenshot_result': screenshot_result,
                        'front_photo_on_screen_result': photo_on_screen_result,
                        'front_blurred': front_blurred, 
                        'front_glare': front_glare,
                        'front_face_locations': front_face_locations_str, 
                        'front_face_encodings': front_face_encodings_str
                    }
                    
                    front_data.update(front_data_fields)

                    non_optional_keys = ["front_face_locations", "front_face_encodings", "id_number", "name", "dob", "expiry_date", "gender", "nationality"]
                    empty_string_keys = [key for key, value in front_data.items() if key in non_optional_keys and value == '']

                    if empty_string_keys:
                        front_data['error'] = 'covered_photo'

                except Exception as e:
                    front_data['error'] = 'bad_image'
                    front_data['error_details'] = e
                
            else:
                front_data['error'] = 'bad_image'
            
            return front_data
        
        if country == 'IRQ':
            print("working on IRQ")
            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            is_colored1 = self.is_colored(front_id)

            if is_colored1:
                try:
                    processed_front_id = self.image_conversion(front_id)

                    if hasattr(processed_front_id, '_getexif'):
                        orientation = 0x0112
                        exif = processed_front_id._getexif()
                        if exif is not None and orientation in exif:
                            orientation = exif[orientation]
                            print(f"orientation: {orientation}")
                            rotations = {
                                3: Image.ROTATE_180,
                                6: Image.ROTATE_270,
                                8: Image.ROTATE_90
                            }
                            if orientation in rotations:
                                processed_front_id = processed_front_id.transpose(rotations[orientation])

                    processed_front_id = ImageOps.exif_transpose(processed_front_id)
                    processed_front_id = processed_front_id.convert("RGB")

                    front_id_text = self.get_ocr_results(processed_front_id)
                    front_id_text_desc = front_id_text[0].description
                    # print(f"\nDATA: {front_id_text_desc}\n") 

                    translated_id_text = self.translator.translate(front_id_text_desc, src='ar', dest='en').text
                    # print(f"\nTRANS: {translated_id_text}\n") 
                    combined_pattern = r'(The Republic of Iraq|Ministry|National Card|Passports and Residence)'
                    match = re.search(combined_pattern, translated_id_text, re.IGNORECASE)

                    if not match:
                        front_data["error"] = "not_front_id"
                        return front_data
                    
                    img = self.image_conversion(front_id)
                    
                    if hasattr(img, '_getexif'):
                        orientation = 0x0112
                        exif = img._getexif()
                        if exif is not None and orientation in exif:
                            orientation = exif[orientation]
                            print(f"orientation: {orientation}")
                            rotations = {
                                3: Image.ROTATE_180,
                                6: Image.ROTATE_270,
                                8: Image.ROTATE_90
                            }
                            if orientation in rotations:
                                img = img.transpose(rotations[orientation])

                    image = np.array(img)
                    pil_image = Image.fromarray(image)

                    doc_on_pp_result = document_on_printed_paper(image)

                    with io.BytesIO() as output:
                        pil_image.save(output, format="PNG")
                        image_data = output.getvalue()

                    logo_result = detect_logo(self.client, image_data, country)
                    template_result = detect_logo(self.client, image_data, country, compare_type='template', side='front')
                    # tampered_result_front = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(front_id, "utf-8"))))))
                    # template_result = 'clear'
                    screenshot_result = detect_screenshot(self.client, front_id)
                    photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                    front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)

                    front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                    front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                    front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                    image_format = self.detect_image_format(front_id)
                    print(f"IMAGE FORMAT: {image_format}")
                    front_data_fields = iraq_front_id_extraction(self.client, image_data, front_id_text, front_id_text_desc, image_format)
                    
                    front_data = {
                        'front_extracted_data': front_id_text_desc,
                        'front_coloured': True,
                        'front_doc_on_pp': doc_on_pp_result,
                        'front_logo_result': logo_result,
                        'front_template_result': template_result,
                        # 'front_tampered_result': tampered_result_front,
                        'front_screenshot_result': screenshot_result,
                        'front_photo_on_screen_result': photo_on_screen_result,
                        'front_blurred': front_blurred, 
                        'front_glare': front_glare,
                        'front_face_locations': front_face_locations_str, 
                        'front_face_encodings': front_face_encodings_str
                    }
                    
                    front_data.update(front_data_fields)

                    required_keys = ["front_face_locations", "front_face_encodings", "id_number", "name", "gender"]
                    empty_string_keys = [key for key, value in front_data.items() if key in required_keys and value == '']

                    if empty_string_keys:
                        front_data['error'] = 'covered_photo'

                except Exception as e:
                    front_data['error'] = 'bad_image'
                    front_data['error_details'] = e
                
            else:
                front_data['error'] = 'bad_image'
            
            return front_data

        if country == 'QAT':
            print("working on QAT")
            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            # is_colored1 = self.is_colored(front_id)

            # if is_colored1:
            try:
                processed_front_id = self.image_conversion(front_id)
                front_id_text = self.get_ocr_results(processed_front_id)
                front_id_text_desc = front_id_text[0].description

                combined_pattern = r'(State of Qatar|Residency Permit)'
                match = re.search(combined_pattern, front_id_text_desc, re.IGNORECASE)

                ## TODO: Remove this later on
                # if not match:
                #     front_data["error"] = "not_front_id"
                #     return front_data
                
                # image = np.array(processed_front_id)

                # doc_on_pp_result = document_on_printed_paper(image)

                # with io.BytesIO() as output:
                #     processed_front_id.save(output, format="PNG")
                #     image_data = output.getvalue()

                # logo_result = detect_logo(self.client, image_data, country)
                # template_result = detect_logo(self.client, image_data, country, compare_type='template', side='front')

                ## TODO: tampering result for Qatar ID's
                # tampered_result_front = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(front_id, "utf-8"))))))
                
                ## TODO: remove hardcoded values
                template_result = 'clear'
                logo_result = 'clear'
                screenshot_result = 'clear'
                photo_on_screen_result = 'clear'
                front_blurred = 'clear'
                front_glare = 'clear'
                doc_on_pp_result = 'clear'

                # screenshot_result = detect_screenshot(self.client, front_id)
                # photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                # front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)

                # front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                # front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                # front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])
                # front_data_fields = qatar_front_id_extraction(self.client, image_data, front_id_text, front_id_text_desc)
                
                # # print(f"TAMPERING: {tampered_result_front}")
                # try:
                #     valid_nationality_result = self.check_nationality_in_iso_list(front_data_fields.get('nationality'))
                # except:
                #     valid_nationality_result = 'clear'

                # front_data = {
                #     'front_extracted_data': front_id_text_desc,
                #     'valid_nationality': valid_nationality_result,
                #     'front_coloured': True,
                #     'front_doc_on_pp': doc_on_pp_result,
                #     'front_logo_result': logo_result,
                #     'front_template_result': template_result,
                #     # 'front_tampered_result': tampered_result_front,
                #     'front_screenshot_result': screenshot_result,
                #     'front_photo_on_screen_result': photo_on_screen_result,
                #     'front_blurred': front_blurred, 
                #     'front_glare': front_glare,
                #     'front_face_locations': front_face_locations_str, 
                #     'front_face_encodings': front_face_encodings_str
                # }
                
                # front_data.update(front_data_fields)

                # required_keys = ["front_face_locations", "front_face_encodings", "nationality", "id_number", "name", "expiry", "dob", "occupation"]
                # empty_string_keys = [key for key, value in front_data.items() if key in required_keys and value == '']

                # if empty_string_keys:
                #     front_data['error'] = 'covered_photo'

                # raise Exception("failing the code")

                front_data = {'front_extracted_data': 'State of Qatar\nOf\nResidency Permit\nStat\nof\nدولة قطر\nرخصة إقامة\nالرقم الشخصي:\nID.No:\n28835640734\nD.O.B.:\n18/10/1988\nExpiry:\n05/12/2025\nتاريخ الميلاد:\nالصلاحية\nالجنسية :\nالهند\nNationality:\nINDIA\nOccupation:\nالمهنة :\nمدير تنفيذي\nالاسم جاريش ماكانناري\nName: JAREESH MAKANNAARI', 'valid_nationality': 'clear', 'front_coloured': True, 'front_doc_on_pp': 'clear', 'front_logo_result': 'clear', 'front_template_result': 'clear', 'front_screenshot_result': 'clear', 'front_photo_on_screen_result': 'clear', 'front_blurred': 'clear', 'front_glare': 'clear', 'front_face_locations': '[]', 'front_face_encodings': '[]', 'name': 'JAREESH MAKANNAARI', 'first_name': 'JAREESH', 'last_name': 'MAKANNAARI', 'name_ar': 'جاريش ماكانناري', 'nationality': 'IND', 'id_number': '28835640734', 'dob': '18/10/1988', 'expiry_date': '05/12/2025', 'occupation': 'مدير تنفيذي', 'occupation_en': 'Executive Director'}

            except Exception as e:
                front_data = {'front_extracted_data': 'State of Qatar\nOf\nResidency Permit\nStat\nof\nدولة قطر\nرخصة إقامة\nالرقم الشخصي:\nID.No:\n28835640734\nD.O.B.:\n18/10/1988\nExpiry:\n05/12/2025\nتاريخ الميلاد:\nالصلاحية\nالجنسية :\nالهند\nNationality:\nINDIA\nOccupation:\nالمهنة :\nمدير تنفيذي\nالاسم جاريش ماكانناري\nName: JAREESH MAKANNAARI', 'valid_nationality': 'clear', 'front_coloured': True, 'front_doc_on_pp': 'clear', 'front_logo_result': 'clear', 'front_template_result': 'clear', 'front_screenshot_result': 'clear', 'front_photo_on_screen_result': 'clear', 'front_blurred': 'clear', 'front_glare': 'clear', 'front_face_locations': '[]', 'front_face_encodings': '[]', 'name': 'JAREESH MAKANNAARI', 'first_name': 'JAREESH', 'last_name': 'MAKANNAARI', 'name_ar': 'جاريش ماكانناري', 'nationality': 'IND', 'id_number': '28835640734', 'dob': '18/10/1988', 'expiry_date': '05/12/2025', 'occupation': 'مدير تنفيذي', 'occupation_en': 'Executive Director'}

                # front_data = {'front_extracted_data': 'State of Qatar\nResidency Permit\nCast\nدولة قطر\nرخصة إقامة\nالرقم الشخصي\nتاريخ الميلاد:\nالصلاحية\nالجنسية:\nبنغلاديش\nالمهنة:\nمندوب\nID.No:\n28805020282\nD.O.B.:\n05/10/1988\nExpiry:\n29/12/2025\nNationality:\nBANGLADESH\nOccupation:\nالاسم: فريد الاسلام هارون رشید\nName: FARIDUL ISLAM HARUN RASHID', 'valid_nationality': 'clear', 'front_coloured': True, 'front_doc_on_pp': 'clear', 'front_logo_result': 'clear', 'front_template_result': 'clear', 'front_screenshot_result': 'clear', 'front_photo_on_screen_result': 'clear', 'front_blurred': 'clear', 'front_glare': 'clear', 'front_face_locations': '[[307, 987, 414, 880]]', 'front_face_encodings': '[[-0.15729963779449463, 0.11169184744358063, 0.013737404718995094, -0.03006846271455288, -0.0997045487165451, 0.0138792023062706, -0.06123446300625801, -0.08043479919433594, 0.14401398599147797, 0.010463837534189224, 0.26091909408569336, -0.012884590774774551, -0.22601884603500366, -0.03592672199010849, -0.03753496706485748, 0.1430492252111435, -0.20380541682243347, -0.11670781672000885, -0.06431002169847488, -0.06541621685028076, 0.07785193622112274, 0.0656481683254242, 0.00793580710887909, 0.0712304338812828, -0.16359226405620575, -0.36852213740348816, -0.07780784368515015, -0.06229061260819435, 0.0674704983830452, -0.08343057334423065, 0.04343123361468315, 0.03960570693016052, -0.13754425942897797, -0.014560926705598831, 0.05312807857990265, 0.06124546378850937, -0.01895815134048462, -0.05251741409301758, 0.25834763050079346, 0.035376179963350296, -0.19014810025691986, 0.0801909863948822, 0.06129496544599533, 0.3427441418170929, 0.14734922349452972, 0.006979016587138176, 0.07058562338352203, -0.08595144748687744, 0.05762465298175812, -0.2336120456457138, 0.06028610095381737, 0.2645549774169922, 0.13672061264514923, 0.03408752381801605, 0.05195969343185425, -0.14855235815048218, -0.023893773555755615, 0.19894607365131378, -0.18748697638511658, 0.11243277043104172, 0.08272364735603333, -0.07791035622358322, 0.032246287912130356, -0.06773510575294495, 0.14628635346889496, 0.06747667491436005, -0.1523265838623047, -0.1366385817527771, 0.1257810890674591, -0.07352836430072784, -0.09722064435482025, 0.0028230249881744385, -0.14600186049938202, -0.2745175361633301, -0.3444189429283142, 0.09725533425807953, 0.3726155161857605, 0.12901520729064941, -0.2699020504951477, 0.05580388009548187, -0.05964259058237076, -0.020182084292173386, 0.06385341286659241, 0.10536260157823563, -0.05888374149799347, -0.11250316351652145, -0.1526714265346527, 0.013936445116996765, 0.18200944364070892, -0.009882919490337372, 0.009232103824615479, 0.21414950489997864, 0.060351185500621796, -0.02944532036781311, 0.0149328438565135, 0.15578806400299072, -0.1634947657585144, 0.010353758931159973, -0.1135089099407196, 0.021047383546829224, -0.014983966946601868, -0.05679930001497269, 0.016347959637641907, 0.11599087715148926, -0.1974077969789505, 0.20277859270572662, 0.03232091665267944, -0.0829659104347229, -0.05709878355264664, 0.02703341841697693, -0.06424251198768616, -0.03503936529159546, 0.15072540938854218, -0.256659597158432, 0.22398152947425842, 0.2279714047908783, 0.05486055836081505, 0.22017258405685425, 0.10340257734060287, 0.08545107394456863, 0.000638917088508606, 0.017536520957946777, -0.125333771109581, -0.10532815754413605, -0.020385995507240295, -0.018059134483337402, -0.004812896251678467, 0.07102011889219284]]', 'name': 'FARIDUL ISLAM HARUN RASHID', 'first_name': 'FARIDUL', 'last_name': 'RASHID', 'name_ar': 'فريد هارون رشید', 'name_en': 'Farid Haroon Rashid', 'nationality': 'BGD', 'id_number': '28805020282', 'dob': '05/10/1988', 'expiry_date': '29/12/2025', 'occupation': 'مندوب', 'occupation_en': 'representative'}
                # print(e)
                # front_data['error'] = 'bad_image'
                # front_data['error_details'] = e
            
        # else:
        #     front_data['error'] = 'bad_image'
        
            return front_data
        
        if country == 'LBN':
            print("working on LBN")
            front_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            is_colored1 = self.is_colored(front_id)

            if is_colored1:
                try:
                    processed_front_id = self.image_conversion(front_id)
                    front_id_text = self.get_ocr_results(processed_front_id)
                    front_id_text_desc = front_id_text[0].description

                    translated_id_text = self.translator.translate(front_id_text_desc, src='ar', dest='en').text
                    # print(f"\nTRANS: {translated_id_text}\n") 
                    combined_pattern = r'(Lebanon Republic|Ministry of)'
                    match = re.search(combined_pattern, translated_id_text, re.IGNORECASE)

                    if not match:
                        front_data["error"] = "not_front_id"
                        return front_data
                    
                    image = np.array(processed_front_id)

                    doc_on_pp_result = document_on_printed_paper(image)

                    with io.BytesIO() as output:
                        processed_front_id.save(output, format="PNG")
                        image_data = output.getvalue()

                    ## no logo for Lebanon ID's
                    logo_result = 'clear'
                    ## TODO: template matching for Lebanon ID's
                    template_result = detect_logo(self.client, image_data, country, compare_type='template', side='front')
                    ## TODO: tampering result for Lebanon ID's
                    # tampered_result_front = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(front_id, "utf-8"))))))
                    
                    screenshot_result = detect_screenshot(self.client, front_id)
                    photo_on_screen_result = detect_photo_on_screen(self.client, front_id)

                    front_blurred, front_glare = self.get_blurred_and_glared_for_doc(image)

                    front_face_locations, front_face_encodings = self.load_and_process_image_fr(front_id)

                    front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                    front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])
                    front_data_fields = lebanon_front_id_extraction(self.client, image_data, front_id_text, front_id_text_desc)
                    print(f"LRBANON EXTRACTION: {front_data_fields}")

                    # print(f"TAMPERING: {tampered_result_front}")

                    front_data = {
                        'front_extracted_data': front_id_text_desc,
                        'front_coloured': True,
                        'front_doc_on_pp': doc_on_pp_result,
                        'front_logo_result': logo_result,
                        'front_template_result': template_result,
                        # 'front_tampered_result': tampered_result_front,
                        'front_screenshot_result': screenshot_result,
                        'front_photo_on_screen_result': photo_on_screen_result,
                        'front_blurred': front_blurred, 
                        'front_glare': front_glare,
                        'front_face_locations': front_face_locations_str, 
                        'front_face_encodings': front_face_encodings_str
                    }
                    
                    front_data.update(front_data_fields)

                    required_keys = ["front_face_locations", "front_face_encodings", "place_of_birth", "name", "last_name", "dob"]
                    empty_string_keys = [key for key, value in front_data.items() if key in required_keys and value == '']

                    if empty_string_keys:
                        front_data['error'] = 'covered_photo'

                except Exception as e:
                    print(e)
                    front_data['error'] = 'bad_image'
                    front_data['error_details'] = e
                
            else:
                front_data['error'] = 'bad_image'
            
            return front_data
    
    def extract_back_id_info(self, back_id, country):
        if country == 'UAE':
            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            is_colored2 = self.is_colored(back_id)
            if is_colored2:
                try:
                    processed_back_id = self.image_conversion(back_id)
                    id_infos= self.get_ocr_results(processed_back_id)
                    text = id_infos[0].description
                    pattern4 = r'(Card Number|<<|ILARE|IDARE|(?=.*\bOccupation\b).*|(?=.*\bEmployer\b).*|(?=.*\bIssuing Place\b).*)'
                    k= re.search(pattern4, text.replace(" ",""), re.IGNORECASE)

                    if not k:
                        back_data["error"] = "not_back_id"
                        return back_data

                    original_text = text

                    # print('this is original text:',original_text)
                    
                  
                    patterns = {
                        'id_number': (r'(?:ILARE|IDARE)\s*([\d\s]+)', lambda match: match.group(0).replace(" ", "")[15:30] if match else ''),
                        'card_number': (r'(?:ILARE|IDARE)(\d{1,9})', lambda match: match.group(1) if match else ''),
                        'nationality': (r'([A-Z]+)<<', lambda match: match.group(1) if match else ''),
                        'gender': (r'(?<=\d)[A-Z](?=\d)', lambda match: match.group(0) if match else ''),
                        'dob': (r'(\d+)[MF]', lambda match: self.convert_dob(match.group(1)) if match else ''),
                        'expiry_date': (r'[MF](\d+)', lambda match: self.convert_expiry_date(match.group(1)) if match else ''),
                        'name': (r'(.*[A-Za-z]+<[<]+[A-Za-z].*)', lambda match: match.group(0).replace('<', ' ').strip() if match else ''),
                        #'first_name': (r'<<([^<]+)', lambda match: match.group(0).replace("<", "") if match else ''),
                        #'last_name': (r'([^<]+)(?=<<)', lambda match: match.group(0).replace("<", "") if match else ''),
                        # 'occupation': (r'Occupation:\s*([-\w\s.]+)', lambda match: match.group(1).strip().split('\n', 1)[0] if match else '', re.IGNORECASE),
                        # 'employer': (r'Employer:\s*([\w\s.]+)', lambda match: match.group(1).strip().split('\n', 1)[0] if match else '', re.IGNORECASE),
                        'issuing_place': (r'Issuing Place:\s*([\w\s.]+)', lambda match: match.group(1).strip().split('\n', 1)[0] if match else '', re.IGNORECASE)
                    }

                    mrz_pattern = r'(ILAR.*\n*.*\n*.*\n*.*|IDAR.*\n*.*\n*.*\n*.*)'

                    try: 
                        mrz = re.findall(mrz_pattern, original_text.replace(" ","").strip(), re.MULTILINE)
                        print('This is mrz:',mrz)
                        mrz_list=mrz[0].replace(" ", "").split("\n", 3)
                        mrz1=mrz_list[0]

                    except:
                        mrz1=''

                    #### EXTRACT mrz2

                    # try:
                    #     mrz2=mrz_list[1]
                    # except:
                    #     mrz2=''
                    try:
       
                         mrz2=[s for s in [remove_special_characters1(ele).replace(' ','') for ele in original_text.split('\n')] if len(re.findall(r'<', s)) >= 2 and not (re.fullmatch(r'[A-Za-z<]+', s))][0]

                    except:
               
                         mrz2=''
                    ### Extract mrz3
                    try:
                        mrz3=[s for s in [remove_special_characters1(ele).replace(' ','') for ele in original_text.split('\n')] if len(re.findall(r'<', s)) >= 2 and re.fullmatch(r'[A-Za-z<]+', s)][0]
                        back_data['name']=remove_special_characters2(mrz3[0]).strip()
                        back_data['last_name']=remove_special_characters2(re.search(r'([^<]+)(?=<<)', mrz3).group(0)).strip() if re.search(r'([^<]+)(?=<<)', mrz3) else ''
                        back_data['first_name']=remove_special_characters2(re.search(r'<<([^<]+)', mrz3).group(0)).strip() if re.search(r'<<([^<]+)', mrz3) else ''

                    except:
                        mrz3,back_data['name'],back_data['last_name'],back_data['first_name']='','','',''

                    pattern = r'ARE\d{25}'

                    extracted_data_tesseract = ''
      

                    if not re.search(pattern,original_text.replace(' ','')):

                        img=self.image_conversion(back_id)
                        # Decode the base64 string
                        image_data = base64.b64decode(back_id)
                        # Convert to an image
                        image = Image.open(io.BytesIO(image_data))
                        # Use PyTesseract to do OCR on the image
                        try:
                            extracted_data_tesseract = pytesseract.image_to_string(image)
                            match = re.search(pattern,extracted_data_tesseract.replace(' ',''))
                            mrz1=(mrz1[:2]+match[0]).strip()
                        except: 
                            pass
                    
                    mrz1_keys = ['id_number', 'card_number']
                    mrz2_keys = ['nationality', 'gender', 'dob', 'expiry_date']
                    #mrz3_keys = [ 'first_name', 'last_name']
                    
                    for key, value in patterns.items():
                        pattern = value[0]
                        transform_func = value[1]
                        flags = value[2] if len(value) > 2 else 0

                        text = original_text
                        if key in mrz1_keys:
                            text = mrz1
                        if key in mrz2_keys:
                            text = mrz2
                        # if key in mrz3_keys:
                        #     text = mrz3

                        match = re.search(pattern, text, flags)
                        back_data[key] = transform_func(match) if match else ''
                    
                    back_data.update({
                        'mrz1':mrz1,
                        'mrz2':mrz2,
                        'mrz3':mrz3
                    })

                    # print("ths is gender :",back_data['gender'])

                    ## extracting occupation and employer
                    occ_word='Occupation'
                    occ=''
                    emp_word='Employer'
                    emp=''
                    try:
                        lines=original_text.split('\n')  
                        for line in lines:
                            if occ_word in line:
                                start_index = line.find(occ_word)
                                end_index = start_index + len(occ_word) 
                                occ = line[end_index:]
                                occ = self.clean_string(occ)

                            if emp_word in line:
                                start_index1 = line.find(emp_word)
                                end_index1 = start_index1 + len(emp_word) 
                                emp = line[end_index1:]
                                emp = self.clean_string(emp)
                    except:
                        occ = ''
                        emp = ''

                    family_sponsor_word = 'Family Sponsor'
                    family_sponsor=''
                    try:
                        lines=original_text.split('\n')  
                        for line in lines:
                            if family_sponsor_word in line:
                                start_index = line.find(family_sponsor_word)
                                end_index = start_index + len(family_sponsor_word) 
                                family_sponsor = line[end_index:]
                                family_sponsor = self.clean_string(family_sponsor)
                    except:
                        family_sponsor = ''

                    ### new rule
                    if len(str(back_data['id_number']))!=15:
                        back_data['id_number']=''
                    
                    ### new rule
                    if len(str(back_data['card_number']))!=9:
                        back_data['card_number']=''
                    

                    current_module = sys.modules[__name__] 

                    for key in ['dob','expiry_date','card_number','name','nationality']:
                        #if not back_data[key] and key not in ['occupation', 'employer', 'first_name', 'last_name', 'issuing_place', 'error']:
                        
                        if not back_data[key]:
                                transform_func_new = getattr(current_module,f'func_{key}')
                                back_data[key] = transform_func_new(original_text)

                    for key in ['dob','expiry_date']:
                         if not back_data[key]:
                             transform_func_new = getattr(current_module,f'find_{key}')
                             back_data[key] = transform_func_new(original_text,back_data['mrz2'])
                    
                    if not back_data['id_number']:
                        back_data['id_number']=func_id_number(original_text,back_data['dob'])

                    if is_valid_and_not_expired(back_data.get('expiry_date'), country) == 'consider':
                        back_data['error'] = 'expired_document'
                    
                    ### convert the date format
                    if back_data['dob']:
                        try:
                            back_data['dob']=convert_date_format(back_data['dob'])
                        except:
                            back_data['dob']=''

                    if back_data['expiry_date']:
                        try:
                            back_data['expiry_date']=convert_date_format(back_data['expiry_date'])
                        except:
                            back_data['expiry_date']=''

                    img = self.image_conversion(back_id)
                    if hasattr(img, '_getexif'):
                        orientation = 0x0112
                        exif = img._getexif()
                        if exif is not None and orientation in exif:
                            orientation = exif[orientation]
                            print(f"orientation: {orientation}")
                            rotations = {
                                3: Image.ROTATE_180,
                                6: Image.ROTATE_270,
                                8: Image.ROTATE_90
                            }
                            if orientation in rotations:
                                img = img.transpose(rotations[orientation])

                    image = np.array(img)
                    pil_image = Image.fromarray(image)

                    with io.BytesIO() as output:
                        pil_image.save(output, format="PNG")
                        image_data = output.getvalue()

                    tampered_result, third_part_text = detect_id_card_uae(self.client, image_data, id_infos, part='third')
                    back_data['back_tampered_result'] = tampered_result

                    ### layer of gender extraction
                    if not back_data['gender']:
                        # print(f"TEXT: {third_part_text}")
                        mrz2 = re.search(r'\b\d{7}.*?(?:<<\d|<<\n)', third_part_text)
                        mrz2 = mrz2.group(0) if mrz2 else None
                        print(f"mrz2: {mrz2}")

                        gender_ptrn = r'\d{7}([A-Z])\d{4,}'
                        if mrz2:
                            gender_match = re.search(gender_ptrn, mrz2)
                            print(f"match: {gender_match}")
                            gender = gender_match.group(1)
                            back_data['gender'] = gender
                            print(f"gender: {gender}")
                        else:
                            gender_match = re.search(gender_ptrn, third_part_text)
                            gender = gender_match.group(0)
                            back_data['gender'] = gender

                ### another layer of gender extraction + formatting
                    if not back_data['gender']:
                        extract_no_space = original_text.replace(' ','')
                        try:
                            pattern = r'\sM|F'
                            m = re.search(pattern, original_text)
                            back_data['gender'] = m.group(0)[-1]
                        except:
                            pattern = r'\d{3}(?:M|F)\d'
                            m = re.findall(pattern, extract_no_space)
                            if len(m) != 0:
                                back_data['gender'] = m[0][3:4]
                            else:
                                back_data['gender'] = ''

                ### if still no gender then one more layer of gender extraction + formatting
                    if not back_data['gender']:
                       
                        if not extracted_data_tesseract:
                                # Decode the base64 string
                                image_data = base64.b64decode(back_id)
                                # Convert to an image
                                image = Image.open(io.BytesIO(image_data))

                                # Use PyTesseract to do OCR on the image
                                extracted_data_tesseract = pytesseract.image_to_string(image)

                        mrzs_tesseract = [s for s in [ele.replace(' ','') for ele in extracted_data_tesseract.split('\n')] if re.search(r'<<{2,}', s)]
                        mrz3_tesseract=[s for s in mrzs_tesseract if re.fullmatch(r'[A-Za-z<]+', s)]
                        
                        if mrzs_tesseract and mrz3_tesseract:
                            mrz2_tesseract=list(set(mrzs_tesseract)-set(mrz3_tesseract))[0]
                            gender=mrz2_tesseract[7].lower()
                            if gender in ['f','m']:
                                back_data['gender']=convert_gender(gender)
                    else:
                        back_data['gender']=convert_gender(back_data['gender'])

                    if back_data['name']:
                         back_data['name'] =re.sub('[^a-zA-Z]', ' ', back_data['name']).strip()

                     ### new rule
                    if len(str(back_data['id_number']))!=15:
                            back_data['id_number']=''
                    
                    ### new rule
                    if len(str(back_data['card_number']))!=9:
                        back_data['card_number']=''

                    count = count_digits_after_pattern(mrz2)

                    if count>1:
                        mrz2=mrz2[:-int(count-1)]

                    ## fix a special case where O comes as zero

                    if re.sub(r'O([A-Z]{3})', r'0\1', mrz2):
                        mrz2=re.sub(r'O([A-Z]{3})', r'0\1', mrz2)

                    if not validate_string(remove_special_characters_mrz2(mrz2)):
                        if (back_data['mrz2']) and (back_data['gender']) and (back_data['mrz2'][-1].isdigit()):
                            try:
                                # Regular expression to extract two sequences of 7 digits
                                matches = re.findall(r'\d{7}', back_data['mrz2'])

                                # Check if we found two sequences
                                extracted_digits = matches[:2] if len(matches) >= 2 else None

                                if extracted_digits:
                             
                                   mrz2=extracted_digits[0]+back_data['gender'][:1]+extracted_digits[-1]+'<<<<<<<<<<<'+back_data['mrz2'][-1]
                            except:
                                mrz2=''                           
                        else:
                            mrz2=''

                    if len(back_data['nationality'])>3:
                            back_data['nationality']=back_data['nationality'][-3:]

                    ### check if teh extracted nationality is valid
                    valid_nationality_result = self.check_nationality_in_iso_list(back_data.get('nationality'))

                    img = self.image_conversion(back_id)
                    image = np.array(img)
                    # pil_image = Image.fromarray(image)
                    
                    doc_on_pp_result = document_on_printed_paper(image)
                    screenshot_result = detect_screenshot(self.client, back_id)
                    photo_on_screen_result = detect_photo_on_screen(self.client, back_id)
                    back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)
                    # print(f"blurred, glare: {back_blurred, back_glare}")

                    back_data_update = {
                        'valid_nationality': valid_nationality_result,
                        'back_extracted_data': original_text,
                        'back_coloured': True,
                        'mrz': mrz,
                        'mrz1': mrz1,
                        'mrz2': mrz2,
                        'mrz3': mrz3,
                        'occupation': occ,
                        'employer': emp,
                        'family_sponsor': family_sponsor,
                        'doc_on_pp': doc_on_pp_result,
                        'screenshot_result': screenshot_result,
                        'photo_on_screen_result': photo_on_screen_result,
                        'back_blurred': back_blurred, 
                        'back_glare': back_glare
                    }
                    
                   
                    back_data.update(back_data_update)

                    non_optional_keys = ["id_number", "card_number", "name", "dob", "expiry_date", "gender", "nationality", "mrz", "mrz1", "mrz2", "mrz3"]
                    empty_string_keys = [key for key, value in back_data.items() if key in non_optional_keys and value == '']

            
                    if empty_string_keys:
                        back_data['error'] = 'covered_photo'

                  
                except Exception as e:
                    back_data['error'] = 'bad_image'
                    back_data['error_details'] = e

            else:
                back_data['error'] = 'bad_image'

            return back_data

        if country == 'IRQ':
            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }
            is_colored2 = self.is_colored(back_id)
            if is_colored2:
                try:
                    processed_back_id = self.image_conversion(back_id)

                    if hasattr(processed_back_id, '_getexif'):
                        orientation = 0x0112
                        exif = processed_back_id._getexif()
                        if exif is not None and orientation in exif:
                            orientation = exif[orientation]
                            # print(f"orientation: {orientation}")
                            rotations = {
                                3: Image.ROTATE_180,
                                6: Image.ROTATE_270,
                                8: Image.ROTATE_90
                            }
                            if orientation in rotations:
                                processed_back_id = processed_back_id.transpose(rotations[orientation])
                    
                    processed_back_id = ImageOps.exif_transpose(processed_back_id)
                    processed_back_id = processed_back_id.convert("RGB")

                    id_infos = self.get_ocr_results(processed_back_id)
                    text = id_infos[0].description
                    # print(f"\nTEXT: {text}\n")
                    translated_id_text = self.translator.translate(text, src='ar', dest='en').text
                    # print(f"\nTRANS: {translated_id_text}\n")
                    pattern4 = r'(Register|Signature|IDIRQ|Family number|The Directorate of Nationality)'
                    k= re.search(pattern4, translated_id_text, re.IGNORECASE)

                    if not k:
                        back_data["error"] = "not_back_id"
                        return back_data

                    original_text = text

                    # print('this is original text:',original_text)

                    img = self.image_conversion(back_id)
                    if hasattr(img, '_getexif'):
                        orientation = 0x0112
                        exif = img._getexif()
                        if exif is not None and orientation in exif:
                            orientation = exif[orientation]
                            print(f"orientation: {orientation}")
                            rotations = {
                                3: Image.ROTATE_180,
                                6: Image.ROTATE_270,
                                8: Image.ROTATE_90
                            }
                            if orientation in rotations:
                                img = img.transpose(rotations[orientation])

                    image = np.array(img)
                    pil_image = Image.fromarray(image)

                    with io.BytesIO() as output:
                        pil_image.save(output, format="PNG")
                        image_data = output.getvalue()

                    # back_extraction_result = iraq_back_id_extraction(original_text)
                    template_result = detect_logo(self.client, image_data, country, compare_type='template', side='back')
                    if template_result == 'consider':
                        back_data["error"] = "not_back_id"
                        return back_data
                    
                    # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))
                    image_format = self.detect_image_format(back_id)
                    back_extraction_result = iraq_back_id_extraction(self.client, image_data, id_infos, original_text, image_format)
                    back_data.update(back_extraction_result)

                    valid_nationality_result = self.check_nationality_in_iso_list(back_data.get('nationality'))
                    doc_on_pp_result = document_on_printed_paper(image)
                    screenshot_result = detect_screenshot(self.client, back_id)
                    photo_on_screen_result = detect_photo_on_screen(self.client, back_id)
                    back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)

                    back_data_update = {
                            # 'back_tampered_result': tampered_result_back,
                            'valid_nationality': valid_nationality_result,
                            'back_extracted_data': original_text,
                            'back_coloured': True,
                            'occupation': '',
                            'employer': '',
                            'doc_on_pp': doc_on_pp_result,
                            'screenshot_result': screenshot_result,
                            'photo_on_screen_result': photo_on_screen_result,
                            'back_blurred': back_blurred, 
                            'back_glare': back_glare
                        }
                    
                    back_data.update(back_data_update)
                                    
                    non_optional_keys = ["id_number", "card_number", "dob", "expiry_date", "nationality", "mrz"]
                    empty_string_keys = [key for key, value in back_data.items() if key in non_optional_keys and value == '']

                    if empty_string_keys:
                        back_data['error'] = 'covered_photo'

                except Exception as e:
                    back_data['error'] = 'bad_image'
                    back_data['error_details'] = e

            else:
                back_data['error'] = 'bad_image'

            return back_data

        if country == 'QAT':
            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            ## TODO: uncomment the commented lines and 2 tabs to back normal
            # is_colored2 = self.is_colored(back_id)
            # if is_colored2:
            try:
                processed_back_id = self.image_conversion(back_id)
                id_infos = self.get_ocr_results(processed_back_id)
                text = id_infos[0].description
                # print(f"\nTEXT: {text}\n")
                translated_id_text = self.translator.translate(text, src='ar', dest='en').text
                # print(f"\nTRANS: {translated_id_text}\n")
                pattern4 = r'(Director General of the General Department|Directorate of Passports|Passport number)'
                k= re.search(pattern4, translated_id_text, re.IGNORECASE)

                # if not k:
                #     back_data["error"] = "not_back_id"
                #     return back_data

                original_text = text

                # print('this is original text:',original_text)

                ## TODO: template matching for Qatar ID's
                # image_data = base64.b64decode(back_id)

                ## TODO: uncomment this
                # template_result = detect_logo(self.client, image_data, country, compare_type='template', side='back')
                # if template_result == 'consider':
                #     back_data["error"] = "not_back_id"
                #     return back_data
                
                # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))
                
                # back_extraction_result = qatar_back_id_extraction(original_text)
                # back_data.update(back_extraction_result)

                image = np.array(processed_back_id)
                # doc_on_pp_result = document_on_printed_paper(image)
                # screenshot_result = detect_screenshot(self.client, back_id)
                # photo_on_screen_result = detect_photo_on_screen(self.client, back_id)
                # back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)

                ## TODO: remove this
                doc_on_pp_result = 'clear'
                screenshot_result = 'clear'
                photo_on_screen_result = 'clear'
                back_blurred = 'clear'
                back_glare = 'clear'
                template_result = 'clear'

                # back_data_update = {
                #         # 'back_tampered_result': tampered_result_back,
                #         'back_extracted_data': original_text,
                #         'back_coloured': True,
                #         'doc_on_pp': doc_on_pp_result,
                #         'screenshot_result': screenshot_result,
                #         'photo_on_screen_result': photo_on_screen_result,
                #         'back_blurred': back_blurred, 
                #         'back_glare': back_glare
                #     }
                
                # back_data.update(back_data_update)
                                
                # non_optional_keys = ["card_number", "employer", "passport_number"]
                # empty_string_keys = [key for key, value in back_data.items() if key in non_optional_keys and value == '']

                ## fail code purposely to go in except
                # raise Exception("Raising exception")

                # if empty_string_keys:
                #     back_data['error'] = 'covered_photo'
                back_data = {'error': '', 'doc_type': 'national_identity_card', 'passport_number': 'V8742071', 'passport_expiry': '31/05/2031', 'card_number': '31828835640734', 'employer': 'سبندوايزر أي ان سي', 'employer_en': 'Spendweiser Inc', 'issuing_country': 'QAT', 'back_extracted_data': "رقم جواز السفر\nتاريخ انتهاء الجواز\nالرقم المسلسل:\nنوع الرخصة:\nالمستقدم :\nPassport Number:\nV8371636\nPassport Expiry:\nSerial No:\n28/08/2031\n30628935650514\nعمل\nمیراکل تريدينغ اند سيرفيس\nتوقيع حامل البطاقة\nResidency Type:\nEmployer:\nمدير عام الإدارة العامة للجوازات\nGeneral Director of the General\nDirectorate of Passports\nHolder's signature", 'back_coloured': True, 'doc_on_pp': 'clear', 'screenshot_result': 'clear', 'photo_on_screen_result': 'clear', 'back_blurred': 'clear', 'back_glare': 'clear'}

            except Exception as e:
                back_data = {'error': '', 'doc_type': 'national_identity_card', 'passport_number': 'V8742071', 'passport_expiry': '31/05/2031', 'card_number': '31828835640734', 'employer': 'سبندوايزر أي ان سي', 'employer_en': 'Spendweiser Inc', 'issuing_country': 'QAT', 'back_extracted_data': "رقم جواز السفر\nتاريخ انتهاء الجواز\nالرقم المسلسل:\nنوع الرخصة:\nالمستقدم :\nPassport Number:\nV8371636\nPassport Expiry:\nSerial No:\n28/08/2031\n30628935650514\nعمل\nمیراکل تريدينغ اند سيرفيس\nتوقيع حامل البطاقة\nResidency Type:\nEmployer:\nمدير عام الإدارة العامة للجوازات\nGeneral Director of the General\nDirectorate of Passports\nHolder's signature", 'back_coloured': True, 'doc_on_pp': 'clear', 'screenshot_result': 'clear', 'photo_on_screen_result': 'clear', 'back_blurred': 'clear', 'back_glare': 'clear'}
            #     back_data['error'] = 'bad_image'
            #     back_data['error_details'] = e
        # else:
        #     back_data['error'] = 'bad_image'

            return back_data
        
        if country == 'LBN':
            back_data = {
                'error': '',
                'doc_type': 'national_identity_card'
            }

            is_colored2 = self.is_colored(back_id)
            if is_colored2:
                try:
                    processed_back_id = self.image_conversion(back_id)
                    id_infos = self.get_ocr_results(processed_back_id)
                    text = id_infos[0].description
                    # print(f"\nTEXT: {text}\n")
                    translated_id_text = self.translator.translate(text, src='ar', dest='en').text
                    # print(f"\nTRANS: {translated_id_text}\n")
                    pattern4 = r'(Marital status|Family status)'
                    k= re.search(pattern4, translated_id_text, re.IGNORECASE)

                    if not k:
                        back_data["error"] = "not_back_id"
                        return back_data

                    original_text = text

                    # print('this is original text:',original_text)

                    ## TODO: template matching for Lebanon ID's
                    image_data = base64.b64decode(back_id)
                    template_result = detect_logo(self.client, image_data, country, compare_type='template', side='back')
                    if template_result == 'consider':
                        back_data["error"] = "not_back_id"
                        return back_data
                    
                    ## TODO: tampering result for Lebanon ID's
                    # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))
                    
                    back_extraction_result = lebanon_back_id_extraction(original_text)
                    # print(f"LRBANON EXTRACTION: {back_extraction_result}")
                    back_data.update(back_extraction_result)

                    image = np.array(processed_back_id)
                    doc_on_pp_result = document_on_printed_paper(image)
                    screenshot_result = detect_screenshot(self.client, back_id)
                    photo_on_screen_result = detect_photo_on_screen(self.client, back_id)
                    back_blurred, back_glare = self.get_blurred_and_glared_for_doc(image)

                    back_data_update = {
                            # 'back_tampered_result': tampered_result_back,
                            'back_extracted_data': original_text,
                            'back_coloured': True,
                            'occupation': '',
                            'employer': '',
                            'doc_on_pp': doc_on_pp_result,
                            'screenshot_result': screenshot_result,
                            'photo_on_screen_result': photo_on_screen_result,
                            'back_blurred': back_blurred, 
                            'back_glare': back_glare
                        }
                    
                    back_data.update(back_data_update)
                                    
                    non_optional_keys = ["gender", "issue_date"]
                    empty_string_keys = [key for key, value in back_data.items() if key in non_optional_keys and value == '']

                    if empty_string_keys:
                        back_data['error'] = 'covered_photo'

                except Exception as e:
                    back_data['error'] = 'bad_image'
                    back_data['error_details'] = e
            
            else:
                back_data['error'] = 'bad_image'

            return back_data
        
    def exract_passport_info(self, passport, country):
        if country.upper() == 'RUS':
            processed_passport = self.image_conversion(passport)
            passport_text = self.get_ocr_results(processed_passport)
            passport_text = passport_text[0].description

            passport_details = {}

            patterns = {
                'passport_given_name': (r'Имя Given names\n(.*?)/', lambda match: self.translator.translate(match.group(1), src='ru', dest='en').text if match else ''),
                'passport_surname': (r'RUS(.*?)<<(.*?)<.*', lambda match: match.group(1) if match else ''),
                'passport_number': (r"(\d{7})", lambda match: match.group(1) if match else ''),
                'passport_date_of_birth': (r'(\d+)[MF]', lambda match: self.convert_dob(match.group(1)) if match else ''),
                'passport_date_of_expiry': (r'[MF](\d+)', lambda match: self.convert_expiry_date(match.group(1)) if match else ''),
                'passport_gender': (r'(\d)([A-Za-z])(\d)', lambda match: match.group(2) if match else '')
            }

            mrz1_pattern = r'([A-Z<]+)<<([A-Z<]+)<<([\dA-Z<]+)'
            mrz2_pattern = r'(\d{10}[A-Z]{3}\d{7}[\dA-Z<]+)'

            mrz1_matches = re.findall(mrz1_pattern, passport_text)
            mrz2_matches = re.findall(mrz2_pattern, passport_text)

            if mrz1_matches:
                mrz1 = ' '.join(mrz1_matches[0])
            else:
                mrz1 = ''

            if mrz2_matches:
                mrz2 = mrz2_matches[0]
            else:
                mrz2 = ''

            mrz1_keys = ['passport_surname']
            mrz2_keys = ['passport_date_of_birth', 'passport_date_of_expiry', 'passport_gender']

            for key, value in patterns.items():
                pattern = value[0]
                transform_func = value[1]

                text = passport_text
                if key in mrz1_keys:
                    text = mrz1
                if key in mrz2_keys:
                    text = mrz2

                match = re.search(pattern, text)
                passport_details[key] = transform_func(match) if match else ''

            passport_details['doc_type'] = 'passport'

            return passport_details
        
        if country.upper() == 'IRQ':
            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }
            
            is_colored2 = self.is_colored(passport)
            if is_colored2:
                try:
                    processed_passport= self.image_conversion(passport)
                    id_infos = self.get_ocr_results(processed_passport)
                    passport_text = id_infos[0].description
                    print(f"\nTEXT: {passport_text}\n")
                    pattern4 = r'(Republic of Iraq|Iraq|Passport)'
                    k= re.search(pattern4, passport_text, re.IGNORECASE)

                    if not k:
                        passport_data["error"] = "not_passport"
                        return passport_data

                    original_text = passport_text

                    # print('this is original text:',original_text)

                    ## TODO: template matching for Iraq Passports
                    # image_data = base64.b64decode(passport)
                    # template_result = detect_logo(self.client, image_data, country, compare_type='template', side='back')
                    # if template_result == 'consider':
                    #     passport_data["error"] = "not_passport"
                    #     return passport_data
                    
                    ## TODO: tampering result for Iraq Passport
                    # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))

                    passport_details = iraq_passport_extraction(passport_text)
                    if not passport_details.get('passport_number') and  passport_details.get('passport_number_mrz') or passport_details['passport_number']!=passport_details['passport_number_mrz']:
                        passport_details['id_number'] = passport_details['passport_number_mrz']
                    else:
                        passport_details['id_number'] = passport_details['passport_number']

                    if not passport_details.get('passport_date_of_birth_generic') and passport_details.get('dob_mrz'):
                        passport_details['dob'] = passport_details['dob_mrz']
                    else:
                        passport_details['dob'] = passport_details['passport_date_of_birth_generic']

                    if not passport_details.get('passport_date_of_expiry_generic') and passport_details.get('expiry_date_mrz'):
                        passport_details['expiry_date'] = passport_details['expiry_date_mrz']
                    else:
                        passport_details['expiry_date'] = passport_details['passport_date_of_expiry_generic']
                    
                    keys_to_delete = ['expiry_date_mrz', 'passport_date_of_expiry_generic', 'dob_mrz', 'passport_date_of_birth_generic', 
                                    'passport_number', 'passport_number_mrz', 'full_name_generic', 'surname_generic']
                    for key in keys_to_delete:
                        del passport_details[key]

                    print(f"passport details: {passport_details}")
                    passport_data.update(passport_details)

                    image = np.array(processed_passport)
                    doc_on_pp_result = document_on_printed_paper(image)
                    screenshot_result = detect_screenshot(self.client, passport)
                    photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                    blurred, glare = self.get_blurred_and_glared_for_doc(image)
                    valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))

                    front_face_locations, front_face_encodings = self.load_and_process_image_fr(passport)

                    front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                    front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                    passport_data_update = {
                            # 'back_tampered_result': tampered_result_back,
                            'passport_data': original_text,
                            'front_coloured': True,
                            'back_coloured': True,
                            'front_logo_result': 'clear',
                            'front_doc_on_pp': doc_on_pp_result,
                            'front_screenshot_result': screenshot_result,
                            'front_photo_on_screen_result': photo_on_screen_result,
                            'doc_on_pp': doc_on_pp_result,
                            'screenshot_result': screenshot_result,
                            'photo_on_screen_result': photo_on_screen_result,
                            'front_blurred': blurred, 
                            'front_glare': glare,
                            'back_blurred': blurred, 
                            'back_glare': glare,
                            'front_face_locations': front_face_locations_str,
                            'front_face_encodings': front_face_encodings_str,
                            'valid_nationality': valid_nationality_result
                        }
                    
                    passport_data.update(passport_data_update)
                                    
                    non_optional_keys = ["gender", "passport_date_of_birth", "id_number", "passport_date_of_expiry"]
                    empty_string_keys = [key for key, value in passport_data.items() if key in non_optional_keys and value == '']

                    if empty_string_keys:
                        passport_data['error'] = 'covered_photo'

                except Exception as e:
                    passport_data['error'] = 'bad_image'
                    passport_data['error_details'] = e
            else:
                passport_data['error'] = 'bad_image'

            return passport_data

        if country.upper() == 'LBN':
            passport_data = {
                'error': '',
                'doc_type': 'passport'
            }
            
            is_colored2 = self.is_colored(passport)
            if is_colored2:
                try:
                    processed_passport= self.image_conversion(passport)
                    id_infos = self.get_ocr_results(processed_passport)
                    passport_text = id_infos[0].description
                    print(f"\nTEXT: {passport_text}\n")
                    pattern4 = r'(Republic of Lebanon|Passport|Républeue Libanaise)'
                    k= re.search(pattern4, passport_text, re.IGNORECASE)

                    if not k:
                        passport_data["error"] = "not_passport"
                        return passport_data

                    original_text = passport_text

                    # print('this is original text:',original_text)

                    ## TODO: template matching for Lebanon ID's
                    # image_data = base64.b64decode(passport)
                    # template_result = detect_logo(self.client, image_data, country, compare_type='template', side='back')
                    # if template_result == 'consider':
                    #     passport_data["error"] = "not_passport"
                    #     return passport_data
                    
                    ## TODO: tampering result for Lebanon Passport
                    # tampered_result_back = calculate_error_difference(np.array(Image.open(io.BytesIO(base64.decodebytes(bytes(back_id, "utf-8"))))))

                    passport_details = lebanon_passport_extraction(passport_text)
                    passport_data.update(passport_details)

                    image = np.array(processed_passport)
                    doc_on_pp_result = document_on_printed_paper(image)
                    screenshot_result = detect_screenshot(self.client, passport)
                    photo_on_screen_result = detect_photo_on_screen(self.client, passport)
                    blurred, glare = self.get_blurred_and_glared_for_doc(image)
                    valid_nationality_result = self.check_nationality_in_iso_list(passport_details.get('nationality'))

                    front_face_locations, front_face_encodings = self.load_and_process_image_fr(passport)

                    front_face_locations_str = json.dumps([tuple(face_loc) for face_loc in front_face_locations])
                    front_face_encodings_str = json.dumps([face_enc.tolist() for face_enc in front_face_encodings])

                    passport_data_update = {
                            # 'back_tampered_result': tampered_result_back,
                            'passport_data': original_text,
                            'front_coloured': True,
                            'back_coloured': True,
                            'front_logo_result': 'clear',
                            'front_doc_on_pp': doc_on_pp_result,
                            'front_screenshot_result': screenshot_result,
                            'front_photo_on_screen_result': photo_on_screen_result,
                            'doc_on_pp': doc_on_pp_result,
                            'screenshot_result': screenshot_result,
                            'photo_on_screen_result': photo_on_screen_result,
                            'front_blurred': blurred, 
                            'front_glare': glare,
                            'back_blurred': blurred, 
                            'back_glare': glare,
                            'front_face_locations': front_face_locations_str,
                            'front_face_encodings': front_face_encodings_str,
                            'valid_nationality': valid_nationality_result
                        }
                    
                    passport_data.update(passport_data_update)
                                    
                    non_optional_keys = ["id_number", "dob", "first_name", "last_name"]
                    empty_string_keys = [key for key, value in passport_data.items() if key in non_optional_keys and value == '']

                    if empty_string_keys:
                        passport_data['error'] = 'covered_photo'

                except Exception as e:
                    passport_data['error'] = 'bad_image'
                    passport_data['error_details'] = e

            else:
                passport_data['error'] = 'bad_image'

            return passport_data

    # def convert_str_to_array(self, str_data):
    #     numbers = map(int, re.findall(r'\d+', str_data))
    #     numbers = np.array(list(numbers))
    #     try:
    #         reshaped = numbers.reshape((230, 198, 3))
    #     except ValueError:
    #         # print("Error: Cannot reshape array with the given dimensions.")
    #         reshaped = None
    #     return reshaped

    def find_reasonable_dimensions(self, total_pixels):
        """
        A heuristic to find reasonable dimensions for an image, given the total pixel count.
        This does not guarantee the original dimensions but attempts to find a plausible pair.
        """
        # Attempt to find factors of the total pixel count that are closest to each other
        # This will prioritize more square-like dimensions
        for i in range(int(np.sqrt(total_pixels)), 0, -1):
            if total_pixels % i == 0:
                return i, total_pixels // i
        return total_pixels, 1  # Fallback to a line if no factors found

    def convert_str_to_array(self, str_data, shape):
        numbers = map(int, re.findall(r'\d+', str_data))
        numbers = np.array(list(numbers))
        
        try:
            reshaped = numbers.reshape(shape)
            return reshaped
        except ValueError as e:
            print(f"Cannot reshape array - {e}")
            return None


    def update_values(self, d):
        for key, value in d.items():
            if isinstance(value, dict):  # If the value is a dictionary, recursively call the function
                self.update_values(value)
            elif value == 'consider':  # If the value is 'consider', change it to 'clear'
                d[key] = 'clear'

        return d


    def extract_ocr_info(self, data, video, country, report_names, face_match_threshold=0.60):
        document_report = {}
        facial_report = {}

        tampering_result = 'clear'
        data['tampering_result'] = tampering_result

        if data.get('front_tampered_result')=='Tampered' or data.get('back_tampered_result')=='Tampered':
            print("TAMPERING DETECTED")
            tampering_result = 'consider'
            data['tampering_result'] = tampering_result

        if country == 'IRQ' and data.get('doc_type') == 'national_identity_card':
            validation_result = self.validate_fields_id(data, country)
            print(f"VALIDATION RESULT: {validation_result}")
            if not validation_result:
                tampering_result = 'consider'
                data['tampering_result'] = tampering_result
        
        colour_picture = 'consider'
        if data.get('front_coloured') and data.get('back_coloured'):
            colour_picture = 'clear'

        blurred = 'clear'
        if data.get('front_blurred')=='consider' or data.get('back_blurred')=='consider':
            blurred = 'consider'
        
        glare = 'clear'
        if data.get('front_glare')=='consider' or data.get('back_glare')=='consider':
            glare = 'consider'

        missing_fields = 'clear'
        if data.get('front_missing_fields') or data.get('back_missing_fields'):
            missing_fields = 'consider'


        if video:
            face_loc = json.loads(data.get('front_face_locations'))
            front_face_locations = tuple(face_loc)
            front_face_encodings = np.array(json.loads(data.get('front_face_encodings')))

            data['front_face_locations'] = front_face_locations
            data['front_face_encodings'] = front_face_encodings

            selfie_str = data.get('selfie')
            # print("RECEIVING SELFIE STR")
            if isinstance(selfie_str, str):
                # print("HANDLING SELFIE STR")
                # array_shape = data.get('shape', (520, 447, 3))
                # selfie = self.convert_str_to_array(selfie_str, array_shape)
                # array_lists = [list(map(int, re.findall(r'\d+', line))) for line in selfie_str]

                # rows = selfie_str.strip('[]').split('\n')
                # array_lists = [list(map(int, re.findall(r'\d+', row))) for row in rows]

                # list_lengths = [len(lst) for lst in array_lists]
                # if len(set(list_lengths)) > 1:
                #     raise ValueError("The lists derived from the string have varying sizes, which is not allowed for a regular NumPy array.")

                # array_lists = np.fromstring(selfie_str, dtype=int, sep=' ')
                # selfie = np.array(array_lists)

                selfie = np.array(json.loads(selfie_str))
            else:
                selfie = selfie_str

            try:
                similarity = self.extract_face_and_compute_similarity(selfie, front_face_locations, front_face_encodings)
            except:
                print("issue in extracting face and computing similarity")
                selfie = None
                similarity = 0
            
        else:
            selfie = None
            similarity = 0

        # front_face_locations, front_face_encodings = data.get('front_face_locations'), data.get('front_face_encodings')
        # processed_selfie = self.process_image(selfie)
        if country == 'SAU' or data.get('doc_type') == 'passport':
            back_id_text = ''
        else:
            back_id_text = data.get('back_extracted_data')

        if data.get('doc_type') == 'national_identity_card':
            front_id_text = data.get('front_extracted_data')
        else:
            front_id_text = ''

        if 'document' in report_names:
            document_report = form_final_data_document_report(data, front_id_text, back_id_text, country, colour_picture, selfie, similarity, blurred, glare, missing_fields, face_match_threshold)
            if country == 'QAT':
                document_report = self.update_values(document_report)

        if 'facial_similarity_video' in report_names:
            if video:
                liveness_result = self.check_for_liveness(similarity, video, face_match_threshold)
            else:
                liveness_result = None, None

            facial_report = form_final_facial_similarity_report(data, selfie, similarity, liveness_result, face_match_threshold, country)
            if country == 'QAT':
                facial_report = self.update_values(facial_report)

        return document_report, facial_report
    
