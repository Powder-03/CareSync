from fastapi import FastAPI, HTTPException , Path
import json
import os

app = FastAPI()

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

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

mnnnnnnn
