import os
import json
import cv2
import tkinter as tk
from tkinter import messagebox, simpledialog
from deepface import DeepFace

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACES_DIR = os.path.join(BASE_DIR, "faces")
PATIENTS_FILE = os.path.join(BASE_DIR, "patients.json")
CURRENT_FACE = os.path.join(BASE_DIR, "current_face.jpg")

# Colors
NAVY = "#101D35"
BLUE = "#3478F6"
GREEN = "#10B981"
BG = "#F3F6FB"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#64748B"


def create_root():
    root = tk.Tk()
    root.withdraw()
    return root


def show_message(title, text, error=False):
    root = create_root()

    if error:
        messagebox.showerror(title, text, parent=root)
    else:
        messagebox.showinfo(title, text, parent=root)

    root.destroy()


def load_patients():
    with open(PATIENTS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Invalid patient records format.")

    return data


def scan_face():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        show_message(
            "Camera Error",
            "Unable to open the camera.",
            True
        )
        return False

    captured = False

    while True:
        success, frame = camera.read()

        if not success:
            break

        cv2.imshow(
            "SmartHospital Pro | Press S to Scan - Q to Cancel",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            captured = cv2.imwrite(CURRENT_FACE, frame)
            break

        elif key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

    return captured


def show_patient_profile(patient):
    root = create_root()

    profile = tk.Toplevel(root)
    profile.title("SmartHospital Pro | Patient Profile")
    profile.geometry("700x570")
    profile.configure(bg=BG)
    profile.resizable(False, False)

    # Center window
    profile.update_idletasks()

    width = 700
    height = 570

    x = (profile.winfo_screenwidth() - width) // 2
    y = (profile.winfo_screenheight() - height) // 2

    profile.geometry(f"{width}x{height}+{x}+{y}")

    # Header
    header = tk.Frame(
        profile,
        bg=NAVY,
        height=110
    )
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="SMART HOSPITAL",
        font=("Segoe UI", 23, "bold"),
        bg=NAVY,
        fg=WHITE
    ).pack(pady=(20, 5))

    tk.Label(
        header,
        text="Patient Identification System",
        font=("Segoe UI", 11),
        bg=NAVY,
        fg="#CBD5E1"
    ).pack()

    # Page title
    tk.Label(
        profile,
        text="Patient Profile",
        font=("Segoe UI", 25, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(pady=(25, 8))

    # Verification status
    tk.Label(
        profile,
        text="FACE VERIFIED SUCCESSFULLY",
        font=("Segoe UI", 12, "bold"),
        bg=BG,
        fg=GREEN
    ).pack(pady=(0, 20))

    # Patient information card
    card = tk.Frame(
        profile,
        bg=WHITE,
        highlightbackground="#E5EAF2",
        highlightthickness=1
    )
    card.pack(
        padx=55,
        fill="x"
    )

    details = [
        ("PATIENT NAME", patient.get("name", "")),
        ("MEDICAL RECORD NUMBER (MRN)", patient.get("mrn", "")),
        ("PATIENT AGE", patient.get("age", ""))
    ]

    for label, value in details:

        tk.Label(
            card,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=WHITE,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=30,
            pady=(15, 4)
        )

        tk.Label(
            card,
            text=str(value),
            font=("Segoe UI", 17, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=30,
            pady=(0, 10)
        )

    # Close button
    tk.Button(
        profile,
        text="CLOSE PATIENT PROFILE",
        command=profile.destroy,
        font=("Segoe UI", 11, "bold"),
        bg=BLUE,
        fg=WHITE,
        activebackground=NAVY,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        padx=30,
        pady=12
    ).pack(pady=25)

    profile.protocol(
        "WM_DELETE_WINDOW",
        profile.destroy
    )

    profile.grab_set()
    root.wait_window(profile)
    root.destroy()


def recognize_patient():

    if not os.path.isdir(FACES_DIR):
        show_message(
            "Error",
            "Faces folder not found.",
            True
        )
        return

    if not os.path.isfile(PATIENTS_FILE):
        show_message(
            "Error",
            "Patient records not found.",
            True
        )
        return

    if not scan_face():
        return

    matched_mrn = None
    best_distance = float("inf")

    try:
        # Compare captured face with registered images
        for filename in os.listdir(FACES_DIR):

            if not filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            patient_photo = os.path.join(
                FACES_DIR,
                filename
            )

            try:
                result = DeepFace.verify(
                    img1_path=patient_photo,
                    img2_path=CURRENT_FACE,
                    enforce_detection=True
                )

                if (
                    result["verified"]
                    and result["distance"] < best_distance
                ):
                    best_distance = result["distance"]
                    matched_mrn = os.path.splitext(filename)[0]

            except Exception as error:
                print(f"Face comparison error for {filename}: {error}")
                continue
                

        if matched_mrn is None:
            show_message(
                "Face Recognition",
                "Face not recognized!",
                True
            )
            return

        patients = load_patients()

        patient = next(
            (
                p for p in patients
                if str(p.get("mrn")) == matched_mrn
            ),
            None
        )

        if patient is None:
            show_message(
                "Error",
                "Patient record not found!",
                True
            )
            return

        # Ask for MRN
        root = create_root()

        entered_mrn = simpledialog.askstring(
            "MRN Verification",
            "Face matched!\n\nEnter Patient MRN:",
            parent=root
        )

        root.destroy()

        if entered_mrn is None:
            return

        if entered_mrn.strip() != matched_mrn:
            show_message(
                "Verification Failed",
                "MRN does not match the recognized face!",
                True
            )
            return

        # Display professional patient profile
        show_patient_profile(patient)

    except Exception as error:
        show_message(
            "System Error",
            str(error),
            True
        )

    finally:
        if os.path.exists(CURRENT_FACE):
            try:
                os.remove(CURRENT_FACE)
            except OSError:
                pass


if __name__ == "__main__":
    recognize_patient()