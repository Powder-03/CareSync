from fastapi import FastAPI, HTTPException , Path  , Query
import json
import os
from pydantic import BaseModel , Field , computed_field 
from typing import Annotated , Literal , Optional
from fastapi.responses import JSONResponse

app = FastAPI()


class Patient(BaseModel):
    id : Annotated[str, Path(... , description="The ID of the patient ", example=['P001', 'P002'])]
    name: Annotated[str, Path(... , description="The name of the patient", example='John Doe')]
    city: Annotated[str, Path(... , description="The city of the patient", example='New York')]
    age: Annotated[int, Path(... , gt = 0 , lt = 120 ,description="The age of the patient", example=30)]
    gender: Annotated[Literal['male' , 'female' , 'other'], Field(... , description="Gender of the patient")]
    
    height: Annotated[float, Field(... , gt = 0 ,description="The height of the patient in mtrs", example=1.5)]
    weight: Annotated[float, Field(... , gt = 0 ,description="The weight of the patient in kgs", example=70.0)]
    
    @computed_field
    @property
    
    def bmi(self) -> float :
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    # sabse phle code verdict ko trigger krega aur use krne me self.bmi ko use krega toh bmi ki value calculate ho jayegi
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"
        
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default = None)]
    city: Annotated[Optional[str], Field(default = None)]
    age: Annotated[Optional[int], Field( default = None , gt = 0)]
    gender: Annotated[Optional[Literal['male' , 'female' , 'other']], Field(default = None)]
    height: Annotated[Optional[float], Field(default = None, gt = 0)]
    weight: Annotated[Optional[float], Field(default = None, gt = 0)]
    # bmi and verdict are computed fields, so we don't need to include them in the update model
    

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data


def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/")

def hello():
    return {"message": "Patient Management System API"}



@app.get('/about')
def about():
    return {"message": "A fully functional API to manage your patient record."}


@app.get('/view')
def view():
    data = load_data()
    return data
# get the patient with the given id
@app.get('/patient/{patient_id}')
def view_patient(patient_id: str =Path(...,description="The ID of the patient in the DB" , example = 'P001')):
    
    
    #load all the patient
    data = load_data()
    for patient in data:
        
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(sort_by:str = Query(... , description = 'Sort on the basis of height , weight or bmi'), order:str = Query('asc', description = 'Sort in ascending or descending order')):
    
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail = f'Invalid sort field. Valid fields are {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail = 'Invalid order. Valid orders are asc and desc')
    
    data = load_data()
    # sort the data based on the given field and order
    
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.value(),key = lambda x: x.get(sort_by , 0), reverse = sort_order)
    return sorted_data


@app.post('/create')

def create_patient(patient : Patient): # agr sab shi hoga toh process aage jaigi vrna yhin pe error aayega
    
    # load existing data
    data = load_data()
    
    
    #check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    
    # new patient add to the database
    
    data[patient.id] = patient.model_dump(exclude = ['id'])
    
    
    
    #save the data to the file
    save_data(data)
    
    return JSONResponse(status_code=201, content={"message": "Patient created successfully", "patient": patient.model_dump()})
        
        
        
        
    
    
    # client ne jab data bheja toh usme bmi aur verdict ni tha lekin hme uski tension lene ki jarurat nhi pdegi
    
    
@app.put('/edit/{patient_id}')
def  update_patient(patient_id: str , patient_update: PatientUpdate):
    # load existing data
    data = load_data()
    
    # check if the patient exists
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # update the patient data
    existing_patient_info = data[patient_id]
    
    updated_patient_info = patient_update.model_dump(exclude_unset=True)
    # update only the fields that are provided in the request
    
    # Loop through each key-value pair in the updated_patient_info dictionary
    for key , value in updated_patient_info.items():
        # If the value is not None (i.e., the field was provided in the update request)
        if value is not None:
            # Update the corresponding field in the existing_patient_info dictionary
            existing_patient_info[key] = value
            
    
    # existing_patient_info -> pydantic object -> updated bmi + verdict -> pydantic object ->dict
    existing_patient_info['id'] = patient_id # because we are updating the patient, we need to set the id again we can't create  a object of patient class without id
    patient_pydantic_obj = Patient(**existing_patient_info)
    
    existing_patient_info = patient_pydantic_obj.model_dump(exclude=['id'])  # Convert the Pydantic object to a dictionary, excluding the id field
    
    
    
    data[patient_id] = existing_patient_info
    
    save_data(data)
    # save the updated data to the file
    
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully", "patient": existing_patient_info})



@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    # load existing data
    data = load_data()
    
    # check if the patient exists
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # delete the patient from the data
    del data[patient_id]
    
    # save the updated data to the file
    save_data(data)
    
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})