import cv2
import os

# Create folder for face images
os.makedirs("faces", exist_ok=True)
mrn = input("Enter Patient MRN: ")

# Open camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not found!")
else:
    print("Press S to save your face photo")
    print("Press Q to quit")

    while True:
        success, frame = camera.read()

        if not success:
            break

        cv2.imshow("Smart Hospital - Face Registration", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            
            cv2.imwrite(f"faces/{mrn}.jpg", frame)
            print("Face photo saved successfully!")
            break

        if key == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()