import tempfile
import os
import cv2
from google.cloud import vision_v1
import logging
import time

def check_for_liveness(self, similarity, video_bytes, face_match_threshold=0.59):
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
            # print("Unable to open video file.")
            return None

        liveness_result_list = []
        frames = self.frame_count_and_save(cap)
        frame_count = len(frames)
        # print(f"FRAMES: {frame_count}")

        frames_to_process = [frames[0], frames[-1]] if frame_count > 1 else [frames[0]]
        previous_landmarks = None
        previous_face = None

        for frame in frames_to_process:
            _, buffer = cv2.imencode('.jpg', frame)
            image_data = buffer.tobytes()
            image = vision_v1.Image(content=image_data)
            response = self.client.face_detection(image=image)
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
                    eyebrow_movement = self.calculate_landmarks_movement(current_landmarks[:10], previous_landmarks[:10])
                    nose_movement = self.calculate_landmarks_movement(current_landmarks[10:20], previous_landmarks[10:20])
                    lip_movement = self.calculate_landmarks_movement(current_landmarks[20:28], previous_landmarks[20:28])
                    face_movement = self.calculate_face_movement(current_face, previous_face)

                    liveness_result = self.calculate_liveness_result(eyebrow_movement, nose_movement, lip_movement, face_movement)
                    liveness_result_list.append(liveness_result)

                previous_landmarks = current_landmarks
                previous_face = current_face

        cap.release()  # Release the video capture

        liveness_check_result = 'clear' if any(liveness_result_list) else 'consider'

        return liveness_check_result

    finally:
        # Ensure the temporary file is deleted
        if os.path.exists(temp_video_file_path):
            os.remove(temp_video_file_path)
            # print(f"Temporary file {temp_video_file_path} has been deleted.") 