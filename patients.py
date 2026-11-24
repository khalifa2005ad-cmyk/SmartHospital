import json
import os

FILE_NAME = "patients.json"

def register_patient():
    name = input("Enter patient name: ")
    mrn = input("Enter patient MRN: ")
    age = input("Enter patient age: ")

    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            patients = json.load(file)
    else:
        patients = []

    patient = {
        "name": name,
        "mrn": mrn,
        "age": age
    }

    patients.append(patient)

    with open(FILE_NAME, "w") as file:
        json.dump(patients, file, indent=4)

    print("Patient registered successfully!")
    
register_patient()