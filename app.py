import os
import sys
import json
import cv2
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ================= PATHS =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATIENTS_FILE = os.path.join(BASE_DIR, "patients.json")
APPOINTMENTS_FILE = os.path.join(BASE_DIR, "appointments.json")
FACES_DIR = os.path.join(BASE_DIR, "faces")
FACE_SCRIPT = os.path.join(BASE_DIR, "face_recognize.py")

os.makedirs(FACES_DIR, exist_ok=True)

# ================= COLORS =================

NAVY = "#101D35"
SIDEBAR = "#14243E"
BLUE = "#3478F6"
GREEN = "#10B981"
PURPLE = "#8B5CF6"
RED = "#DC3545"
BG = "#F3F6FB"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#718096"
BORDER = "#E5EAF2"

# ================= DOCTORS =================

DOCTORS = [
    ("D001", "Dr. Ahmed", "Cardiology", "Available"),
    ("D002", "Dr. Sarah", "Dermatology", "Available"),
    ("D003", "Dr. Mohammed", "Orthopedics", "Available"),
    ("D004", "Dr. Fatima", "Pediatrics", "Available"),
    ("D005", "Dr. Khalid", "Neurology", "Available"),
    ("D006", "Dr. Maryam", "General Medicine", "Available"),
]

# ================= APP =================

app = tk.Tk()
app.title("SmartHospital Pro | Management Dashboard")
app.geometry("1200x760")
app.minsize(1000, 650)
app.configure(bg=BG)

# ================= DATA =================

def load_json(path):
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        messagebox.showerror(
            "Data Error",
            "Invalid data format."
        )

    except (OSError, json.JSONDecodeError) as error:
        messagebox.showerror("Data Error", str(error))

    return None


def save_json(path, data):
    temporary_path = path + ".tmp"

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    os.replace(temporary_path, path)


def load_patients():
    return load_json(PATIENTS_FILE)


def load_appointments():
    return load_json(APPOINTMENTS_FILE)


# ================= HELPERS =================

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


def page_heading(title, subtitle):
    tk.Label(
        content,
        text=title,
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 25, "bold")
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        content,
        text=subtitle,
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 11)
    ).pack(anchor="w", pady=(0, 25))


def action_button(parent, text, command, color=BLUE):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=WHITE,
        activebackground=color,
        activeforeground=WHITE,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        bd=0,
        padx=16,
        pady=10,
        cursor="hand2"
    )


def make_card(parent):
    return tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )


def create_table(parent, columns, widths=None, height=8):
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Hospital.Treeview",
        background=WHITE,
        fieldbackground=WHITE,
        foreground=TEXT,
        rowheight=36,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Hospital.Treeview.Heading",
        background=NAVY,
        foreground=WHITE,
        font=("Segoe UI", 10, "bold")
    )

    table = ttk.Treeview(
        parent,
        columns=columns,
        show="headings",
        style="Hospital.Treeview",
        height=height
    )

    for index, column in enumerate(columns):
        table.heading(column, text=column)
        table.column(
            column,
            anchor="center",
            width=widths[index] if widths else 150
        )

    return table


# ================= CAMERA =================

def capture_patient_photo():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        messagebox.showerror(
            "Camera Error",
            "Unable to open the camera."
        )
        return None

    captured_frame = None

    try:
        while True:
            success, frame = camera.read()

            if not success:
                break

            cv2.imshow(
                "SmartHospital | S = Capture | Q = Cancel",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("s"):
                captured_frame = frame.copy()
                break

            if key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    return captured_frame


# ================= DASHBOARD =================

def show_dashboard():
    clear_content()

    page_heading(
        "Dashboard Overview",
        "Welcome to SmartHospital Pro."
    )

    patients = load_patients()
    appointments = load_appointments()

    if patients is None or appointments is None:
        return

    stats = tk.Frame(content, bg=BG)
    stats.pack(fill="x", pady=(0, 30))

    items = [
        ("Total Patients", len(patients), BLUE),
        ("Appointments", len(appointments), PURPLE),
        ("Doctors", len(DOCTORS), GREEN)
    ]

    for index, (title, value, color) in enumerate(items):
        stats.grid_columnconfigure(index, weight=1)

        card = make_card(stats)
        card.grid(
            row=0,
            column=index,
            sticky="nsew",
            padx=(0, 15) if index < 2 else 0
        )

        tk.Frame(
            card,
            bg=color,
            height=5
        ).pack(fill="x")

        tk.Label(
            card,
            text=title,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(20, 8))

        tk.Label(
            card,
            text=str(value),
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 20))

    tk.Label(
        content,
        text="Quick Actions",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 18, "bold")
    ).pack(anchor="w", pady=(0, 15))

    actions = tk.Frame(content, bg=BG)
    actions.pack(fill="x")

    options = [
        (
            "Register Patient",
            "Register and photograph a patient.",
            BLUE,
            show_registration
        ),
        (
            "Appointments",
            "Book, edit and cancel appointments.",
            PURPLE,
            show_appointments
        ),
        (
            "Doctors List",
            "View doctors and specialties.",
            GREEN,
            show_doctors
        )
    ]

    for index, (title, description, color, command) in enumerate(options):
        actions.grid_columnconfigure(index, weight=1)

        card = make_card(actions)
        card.grid(
            row=0,
            column=index,
            sticky="nsew",
            padx=(0, 15) if index < 2 else 0
        )

        tk.Label(
            card,
            text=title,
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=15, pady=(20, 8))

        tk.Label(
            card,
            text=description,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 10),
            wraplength=190,
            justify="left"
        ).pack(anchor="w", padx=15)

        action_button(
            card,
            "OPEN  →",
            command,
            color
        ).pack(anchor="w", padx=15, pady=20)


# ================= REGISTER PATIENT =================

def show_registration():
    clear_content()

    page_heading(
        "Register New Patient",
        "Enter patient information and capture a photo."
    )

    card = make_card(content)
    card.pack(fill="x")

    form = tk.Frame(card, bg=WHITE)
    form.pack(anchor="w", padx=35, pady=20)

    fields = {}

    for label in ["Patient Name", "Patient MRN", "Patient Age"]:
        tk.Label(
            form,
            text=label,
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))

        entry = tk.Entry(
            form,
            font=("Segoe UI", 12),
            width=43,
            relief="solid",
            bd=1
        )

        entry.pack(ipady=7, pady=(0, 12))
        fields[label] = entry

    photo_state = {
        "frame": None,
        "mrn": None
    }

    status_label = tk.Label(
        form,
        text="No patient photo captured",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 10)
    )

    status_label.pack(anchor="w", pady=(0, 10))

    def capture_photo():
        mrn = fields["Patient MRN"].get().strip()

        if not mrn.isdigit():
            messagebox.showerror(
                "Invalid MRN",
                "Enter a numeric demo MRN first."
            )
            return

        patients = load_patients()

        if patients is None:
            return

        if any(str(p.get("mrn")) == mrn for p in patients):
            messagebox.showerror(
                "Duplicate MRN",
                "This MRN is already registered."
            )
            return

        frame = capture_patient_photo()

        if frame is not None:
            photo_state["frame"] = frame
            photo_state["mrn"] = mrn

            status_label.config(
                text="Patient photo captured successfully",
                fg=GREEN
            )

    def save_patient():
        name = fields["Patient Name"].get().strip()
        mrn = fields["Patient MRN"].get().strip()
        age = fields["Patient Age"].get().strip()

        if not all([name, mrn, age]):
            messagebox.showerror(
                "Missing Information",
                "Please complete all fields."
            )
            return

        if not mrn.isdigit():
            messagebox.showerror(
                "Invalid MRN",
                "MRN must contain numbers only."
            )
            return

        if not age.isdigit() or int(age) > 120:
            messagebox.showerror(
                "Invalid Age",
                "Enter a valid age."
            )
            return

        patients = load_patients()

        if patients is None:
            return

        if any(str(p.get("mrn")) == mrn for p in patients):
            messagebox.showerror(
                "Duplicate MRN",
                "This MRN already exists."
            )
            return

        if photo_state["frame"] is None or photo_state["mrn"] != mrn:
            messagebox.showerror(
                "Photo Required",
                "Capture a photo before saving."
            )
            return

        photo_path = os.path.join(FACES_DIR, f"{mrn}.jpg")

        if os.path.exists(photo_path):
            messagebox.showerror(
                "Photo Exists",
                "A photo already exists for this MRN."
            )
            return

        if not cv2.imwrite(photo_path, photo_state["frame"]):
            messagebox.showerror(
                "Save Error",
                "Unable to save patient photo."
            )
            return

        patients.append({
            "name": name,
            "mrn": mrn,
            "age": age
        })

        try:
            save_json(PATIENTS_FILE, patients)

        except OSError as error:
            if os.path.exists(photo_path):
                os.remove(photo_path)

            messagebox.showerror(
                "Save Error",
                str(error)
            )
            return

        messagebox.showinfo(
            "Success",
            "Patient and photo saved successfully!"
        )

        show_dashboard()

    action_button(
        form,
        "CAPTURE PATIENT PHOTO",
        capture_photo,
        GREEN
    ).pack(anchor="w", pady=(0, 12))

    action_button(
        form,
        "SAVE PATIENT",
        save_patient,
        BLUE
    ).pack(anchor="w")


# ================= PATIENT RECORDS =================

def show_records():
    clear_content()

    page_heading(
        "Patient Records",
        "Search patients and update their photos."
    )

    card = make_card(content)
    card.pack(fill="both", expand=True)

    search_bar = tk.Frame(card, bg=WHITE)
    search_bar.pack(fill="x", padx=25, pady=20)

    tk.Label(
        search_bar,
        text="Search by MRN",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 11, "bold")
    ).pack(side="left", padx=(0, 15))

    search_entry = tk.Entry(
        search_bar,
        font=("Segoe UI", 12),
        width=20
    )

    search_entry.pack(side="left", ipady=7)

    table = create_table(
        card,
        ("MRN", "Name", "Age"),
        (170, 260, 120)
    )

    table.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 15)
    )

    def refresh():
        table.delete(*table.get_children())

        patients = load_patients()

        if patients is None:
            return

        query = search_entry.get().strip().lower()

        for patient in patients:
            mrn = str(patient.get("mrn", ""))

            if not query or query in mrn.lower():
                table.insert(
                    "",
                    "end",
                    values=(
                        mrn,
                        patient.get("name", ""),
                        patient.get("age", "")
                    )
                )

    action_button(
        search_bar,
        "SEARCH",
        refresh
    ).pack(side="left", padx=10)

    def show_all():
        search_entry.delete(0, tk.END)
        refresh()

    action_button(
        search_bar,
        "SHOW ALL",
        show_all,
        GREEN
    ).pack(side="left")

    def update_patient_photo():
        selected = table.selection()

        if not selected:
            messagebox.showerror(
                "Select Patient",
                "Select a patient first."
            )
            return

        values = table.item(selected[0], "values")

        mrn = str(values[0])
        name = str(values[1])

        if not messagebox.askyesno(
            "Update Patient Photo",
            f"Capture a new photo for {name}?"
        ):
            return

        frame = capture_patient_photo()

        if frame is None:
            return

        photo_path = os.path.join(FACES_DIR, f"{mrn}.jpg")
        temporary_path = os.path.join(
            FACES_DIR,
            f"{mrn}.tmp.jpg"
        )

        try:
            if not cv2.imwrite(temporary_path, frame):
                raise OSError("Unable to save new photo.")

            os.replace(temporary_path, photo_path)

            messagebox.showinfo(
                "Success",
                "Patient photo updated successfully!"
            )

        except OSError as error:
            messagebox.showerror("Error", str(error))

        finally:
            if os.path.exists(temporary_path):
                os.remove(temporary_path)

    action_button(
        card,
        "UPDATE PATIENT PHOTO",
        update_patient_photo,
        PURPLE
    ).pack(pady=(0, 20))

    search_entry.bind(
        "<Return>",
        lambda event: refresh()
    )

    refresh()


# ================= FACE RECOGNITION =================

def start_face_recognition():
    if not os.path.exists(FACE_SCRIPT):
        messagebox.showerror(
            "Error",
            "face_recognize.py was not found."
        )
        return

    try:
        subprocess.Popen(
            [sys.executable, FACE_SCRIPT],
            cwd=BASE_DIR
        )

    except OSError as error:
        messagebox.showerror("Error", str(error))


def show_face_page():
    clear_content()

    page_heading(
        "Face Recognition",
        "Identify registered demo patients."
    )

    card = make_card(content)
    card.pack(fill="x")

    tk.Label(
        card,
        text="Facial Recognition Scanner",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 21, "bold")
    ).pack(pady=(35, 12))

    tk.Label(
        card,
        text="Scan a registered face to view the patient profile.",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 11)
    ).pack(pady=(0, 20))

    tk.Label(
        card,
        text=(
            "1. Click Start Face Scan\n\n"
            "2. Look directly at the camera\n\n"
            "3. Press S to scan or Q to cancel\n\n"
            "4. Enter the patient's demo MRN"
        ),
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 12),
        justify="left"
    ).pack(pady=15)

    action_button(
        card,
        "START FACE SCAN",
        start_face_recognition,
        GREEN
    ).pack(pady=(15, 35))


# ================= DOCTORS LIST =================

def show_doctors():
    clear_content()

    page_heading(
        "Doctors List",
        "Hospital doctors and their specialties."
    )

    card = make_card(content)
    card.pack(fill="both", expand=True)

    table = create_table(
        card,
        ("Doctor ID", "Doctor Name", "Specialty", "Status"),
        (110, 190, 190, 130),
        height=10
    )

    for doctor in DOCTORS:
        table.insert("", "end", values=doctor)

    table.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=25
    )


# ================= APPOINTMENTS =================

def show_appointments():
    clear_content()

    page_heading(
        "Appointments",
        "Book, edit and cancel patient appointments."
    )

    card = make_card(content)
    card.pack(fill="both", expand=True)

    form = tk.Frame(card, bg=WHITE)
    form.pack(fill="x", padx=25, pady=(15, 5))

    fields = {}

    labels = [
        "Patient MRN",
        "Doctor Name",
        "Date (YYYY-MM-DD)",
        "Time (HH:MM)"
    ]

    for index, label in enumerate(labels):
        tk.Label(
            form,
            text=label,
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=index,
            column=0,
            sticky="w",
            pady=5
        )

        if label == "Doctor Name":
            entry = ttk.Combobox(
                form,
                values=[doctor[1] for doctor in DOCTORS],
                font=("Segoe UI", 11),
                width=26,
                state="readonly"
            )
        else:
            entry = tk.Entry(
                form,
                font=("Segoe UI", 11),
                width=28
            )

        entry.grid(
            row=index,
            column=1,
            padx=15,
            pady=5
        )

        fields[label] = entry

    table = create_table(
        card,
        ("MRN", "Patient", "Doctor", "Date", "Time"),
        (100, 170, 170, 120, 100),
        height=6
    )

    table.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=10
    )

    selected_index = {"value": None}

    # -------- REFRESH --------

    def refresh():
        table.delete(*table.get_children())

        appointments = load_appointments()

        if appointments is None:
            return

        for index, appointment in enumerate(appointments):
            table.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    appointment.get("mrn", ""),
                    appointment.get("patient", ""),
                    appointment.get("doctor", ""),
                    appointment.get("date", ""),
                    appointment.get("time", "")
                )
            )

        selected_index["value"] = None

    # -------- SELECT APPOINTMENT --------

    def on_select(event=None):
        selected = table.selection()

        if not selected:
            return

        index = int(selected[0])
        appointments = load_appointments()

        if appointments is None or index >= len(appointments):
            return

        selected_index["value"] = index
        appointment = appointments[index]

        mapping = [
            ("Patient MRN", "mrn"),
            ("Doctor Name", "doctor"),
            ("Date (YYYY-MM-DD)", "date"),
            ("Time (HH:MM)", "time")
        ]

        for label, key in mapping:
            entry = fields[label]
            value = str(appointment.get(key, ""))

            if isinstance(entry, ttk.Combobox):
                entry.set(value)
            else:
                entry.delete(0, tk.END)
                entry.insert(0, value)

    table.bind("<<TreeviewSelect>>", on_select)

    # -------- VALIDATE --------

    def validate_form(appointments, skip_index=None):
        mrn = fields["Patient MRN"].get().strip()
        doctor = fields["Doctor Name"].get().strip()
        date = fields["Date (YYYY-MM-DD)"].get().strip()
        time = fields["Time (HH:MM)"].get().strip()

        if not all([mrn, doctor, date, time]):
            messagebox.showerror(
                "Missing Information",
                "Please complete all fields."
            )
            return None

        valid_doctors = [doctor[1] for doctor in DOCTORS]

        if doctor not in valid_doctors:
            messagebox.showerror(
                "Invalid Doctor",
                "Select a doctor from the list."
            )
            return None

        patients = load_patients()

        if patients is None:
            return None

        patient = next(
            (
                p for p in patients
                if str(p.get("mrn")) == mrn
            ),
            None
        )

        if patient is None:
            messagebox.showerror(
                "Patient Not Found",
                "No registered patient has this MRN."
            )
            return None

        try:
            parsed_date = datetime.strptime(
                date,
                "%Y-%m-%d"
            ).date()

            parsed_time = datetime.strptime(
                time,
                "%H:%M"
            ).time()

            if parsed_date.strftime("%Y-%m-%d") != date:
                raise ValueError

            if parsed_time.strftime("%H:%M") != time:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Date or Time",
                "Use YYYY-MM-DD and HH:MM."
            )
            return None

        for index, appointment in enumerate(appointments):
            if index == skip_index:
                continue

            if (
                str(appointment.get("doctor", "")).lower()
                == doctor.lower()
                and appointment.get("date") == date
                and appointment.get("time") == time
            ):
                messagebox.showerror(
                    "Appointment Conflict",
                    "This doctor already has an appointment at that time."
                )
                return None

        return {
            "mrn": mrn,
            "patient": patient.get("name", ""),
            "doctor": doctor,
            "date": date,
            "time": time
        }

    # -------- CLEAR FORM --------

    def clear_form():
        selected_index["value"] = None

        for entry in fields.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)

        table.selection_remove(table.selection())

    # -------- BOOK --------

    def book_appointment():
        appointments = load_appointments()

        if appointments is None:
            return

        new_appointment = validate_form(appointments)

        if new_appointment is None:
            return

        appointments.append(new_appointment)

        try:
            save_json(APPOINTMENTS_FILE, appointments)

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                str(error)
            )
            return

        messagebox.showinfo(
            "Success",
            "Appointment booked successfully!"
        )

        refresh()
        clear_form()

    # -------- EDIT --------

    def edit_appointment():
        index = selected_index["value"]

        if index is None:
            messagebox.showerror(
                "Select Appointment",
                "Select an appointment from the table first."
            )
            return

        appointments = load_appointments()

        if appointments is None or index >= len(appointments):
            messagebox.showerror(
                "Error",
                "Appointment not found."
            )
            return

        updated = validate_form(
            appointments,
            skip_index=index
        )

        if updated is None:
            return

        confirm = messagebox.askyesno(
            "Edit Appointment",
            "Save changes to this appointment?"
        )

        if not confirm:
            return

        # Keep any existing extra fields in the record
        appointments[index].update(updated)

        try:
            save_json(APPOINTMENTS_FILE, appointments)

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                str(error)
            )
            return

        messagebox.showinfo(
            "Success",
            "Appointment updated successfully!"
        )

        refresh()
        clear_form()

    # -------- CANCEL --------

    def cancel_appointment():
        index = selected_index["value"]

        if index is None:
            messagebox.showerror(
                "Select Appointment",
                "Select an appointment from the table first."
            )
            return

        appointments = load_appointments()

        if appointments is None or index >= len(appointments):
            messagebox.showerror(
                "Error",
                "Appointment not found."
            )
            return

        appointment = appointments[index]

        confirm = messagebox.askyesno(
            "Cancel Appointment",
            (
                f"Cancel appointment for "
                f"{appointment.get('patient', '')}?\n\n"
                f"Doctor: {appointment.get('doctor', '')}\n"
                f"Date: {appointment.get('date', '')}\n"
                f"Time: {appointment.get('time', '')}"
            )
        )

        if not confirm:
            return

        appointments.pop(index)

        try:
            save_json(APPOINTMENTS_FILE, appointments)

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                str(error)
            )
            return

        messagebox.showinfo(
            "Success",
            "Appointment cancelled successfully!"
        )

        refresh()
        clear_form()

    # -------- BUTTONS --------

    buttons = tk.Frame(card, bg=WHITE)
    buttons.pack(
        fill="x",
        padx=25,
        pady=(0, 15)
    )

    action_button(
        buttons,
        "BOOK APPOINTMENT",
        book_appointment,
        GREEN
    ).pack(side="left", padx=(0, 8))

    action_button(
        buttons,
        "EDIT APPOINTMENT",
        edit_appointment,
        BLUE
    ).pack(side="left", padx=(0, 8))

    action_button(
        buttons,
        "CANCEL APPOINTMENT",
        cancel_appointment,
        RED
    ).pack(side="left", padx=(0, 8))

    action_button(
        buttons,
        "CLEAR",
        clear_form,
        PURPLE
    ).pack(side="left")

    refresh()


# ================= SIDEBAR =================

sidebar = tk.Frame(
    app,
    bg=SIDEBAR,
    width=245
)

sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="✚  SmartHospital",
    bg=SIDEBAR,
    fg=WHITE,
    font=("Segoe UI", 19, "bold")
).pack(anchor="w", padx=20, pady=(35, 8))

tk.Label(
    sidebar,
    text="PRO MANAGEMENT",
    bg=SIDEBAR,
    fg="#8FA4BF",
    font=("Segoe UI", 9, "bold")
).pack(anchor="w", padx=22, pady=(0, 45))


def sidebar_button(text, command):
    tk.Button(
        sidebar,
        text="    " + text,
        command=command,
        bg=SIDEBAR,
        fg="#DCE7F5",
        activebackground="#233B5D",
        activeforeground=WHITE,
        font=("Segoe UI", 12),
        relief="flat",
        bd=0,
        anchor="w",
        padx=12,
        pady=15,
        cursor="hand2"
    ).pack(fill="x", padx=12, pady=4)


sidebar_button("Dashboard", show_dashboard)
sidebar_button("Register Patient", show_registration)
sidebar_button("Patient Records", show_records)
sidebar_button("Face Recognition", show_face_page)
sidebar_button("Appointments", show_appointments)
sidebar_button("Doctors List", show_doctors)

tk.Label(
    sidebar,
    text="STUDENT DEMO  •  v1.1",
    bg=SIDEBAR,
    fg="#8FA4BF",
    font=("Segoe UI", 9)
).pack(side="bottom", pady=25)


# ================= MAIN AREA =================

main = tk.Frame(app, bg=BG)
main.pack(side="right", fill="both", expand=True)

topbar = tk.Frame(
    main,
    bg=WHITE,
    height=65
)

topbar.pack(fill="x")
topbar.pack_propagate(False)

tk.Label(
    topbar,
    text="Healthcare Management Platform",
    bg=WHITE,
    fg=TEXT,
    font=("Segoe UI", 13, "bold")
).pack(side="left", padx=30)

tk.Label(
    topbar,
    text=datetime.now().strftime("%d %B %Y"),
    bg=WHITE,
    fg=MUTED,
    font=("Segoe UI", 10)
).pack(side="right", padx=30)

content = tk.Frame(main, bg=BG)

content.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=30
)

# ================= START =================

show_dashboard()
app.mainloop()