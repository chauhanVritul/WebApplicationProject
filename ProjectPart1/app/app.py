from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, validator
from uuid import uuid4

app=FastAPI()

class Healthcare_Provider(BaseModel):
    active : Optional[bool] = True
    name : str
    qualification : str
    speciality : str
    phone : str
    department : Optional[str] = None
    organization : str
    location : Optional[str] = None
    address : str

    @validator('phone')
    def phone_10Digits(cls, val):
        if len(val) != 10:
            raise ValueError('Phone must be 10 digits long')
        return val

data = {
    "032cb8ca8845a49ba9f669538620aa074000": {
        "providerID": "032cb8ca8845a49ba9f669538620aa074000",
        "active": True,
        "name": "John Cooper",
        "qualification": "deg1,deg2,deg4",
        "speciality": "spec1,spec3",
        "phone": "1238987987",
        "department": "Department_A",
        "organization": "Organization_Z",
        "location": "Bengaluru",
        "address": "Street 5, Town 2, Bengaluru, Karnataka"
    },
    "00b76d7ee122fa477ab1d52df31abd3bbc01": {
        "providerID": "00b76d7ee122fa477ab1d52df31abd3bbc01",
        "active": True,
        "name": "Alice Barmer",
        "qualification": "deg2,deg3",
        "speciality": "spec1,spec2,spec4",
        "phone": "2346872346",
        "department": "Department_C",
        "organization": "Organization_X",
        "location": "Mumbai",
        "address": "Building 7, City 4, Mumbai, Maharashtra"
    },
    "2c5d1811da18485ca384853d9e12a801": {
        "providerID": "2c5d1811da18485ca384853d9e12a801",
        "active": True,
        "name": "Kevin Pitt",
        "qualification": "deg2,deg4",
        "speciality": "spec4",
        "phone": "4730786325",
        "department": "Department_B",
        "organization": "Organization_Z",
        "location": "Bengaluru",
        "address": "Street 5, Town 2, Bengaluru, Karnataka"
    },
    "055ca722bdef4abc96f8a41ab40769aa": {
        "providerID": "055ca722bdef4abc96f8a41ab40769aa",
        "active": False,
        "name": "Melissa Anderson",
        "qualification": "deg1",
        "speciality": "spec1,spec2",
        "phone": "3678826746",
        "department": "Department_B",
        "organization": "Organization_Y",
        "location": None,
        "address": "Street 1, Building 7, Town 2, New Delhi"
    },
    "6635e834e24943f181422b0e68a04ea7": {
        "providerID": "6635e834e24943f181422b0e68a04ea7",
        "active": False,
        "name": "Jonathan Jostar",
        "qualification": "a,b,c",
        "speciality": "a,b,c",
        "phone": "1856274967",
        "department": "a",
        "organization": "a",
        "location": "a",
        "address": "a"
    },
    "4eb4597ea50049a59faafdf2b1aa8d64": {
        "providerID": "4eb4597ea50049a59faafdf2b1aa8d64",
        "active": True,
        "name": "Bob Tres",
        "qualification": "b,v,c",
        "speciality": "b,m,n",
        "phone": "3456832854",
        "department": "b",
        "organization": "b",
        "location": "b",
        "address": "b"
    },
    "8067973e4d88409ab65f44bcf3b4888d": {
        "providerID": "8067973e4d88409ab65f44bcf3b4888d",
        "active": True,
        "name": "Keanu Reeves",
        "qualification": "b,c,z",
        "speciality": "r,t,y",
        "phone": "1727678926",
        "department": "b",
        "organization": "b",
        "location": "b",
        "address": "b"
    },
    "f1203f26a69a4809aa29370b25d29d5e": {
        "providerID": "f1203f26a69a4809aa29370b25d29d5e",
        "active": False,
        "name": "popeye",
        "qualification": "q,r,t",
        "speciality": "y,u,n,f",
        "phone": "87656784569",
        "department": "dtgfhj",
        "organization": "fdvgbhjm",
        "location": "fvgbhj",
        "address": "vfchb, gfg hgft"
    }
}


# CREATE validation for empty fields
def validateCreate(data:dict) -> bool:
    if data['name'] == '':
        return False
    if data['qualification'] == '':
        return False
    if data['speciality'] == '':
        return False
    if data['phone'] == '':
        return False
    if data['organization'] == '':
        return False
    if data['address'] == '':
        return False
    try:
        int(data['phone'])
    except ValueError:
        return False

    return True


# UPDATE validation for data type
def validateUpdate(data:dict)   -> bool:
    for keys in data.keys():
        if keys in ("active",):
            if not isinstance(data[keys], bool):
                return False
        else:
            if not isinstance(data[keys], str):
                return False
    return True

#*--------------------------*#
#*       VIEW provider      *#
#*--------------------------*#

@app.get("/", tags=['backend'])  
async def view_Provider(providerID: str = None, name: str = None)    ->dict:
    keys = data.keys()
    
    if providerID and name:
        return {
            "response":"invalid parameter. only one allowed at a time"
        }
    elif providerID:
        try:
            if providerID not in keys:
                raise HTTPException(status_code=404, detail="providerID not found")
            return {
                    "response" : "success",
                    "data" : data[providerID]
                }
        except HTTPException as e:
            return {"response":e}
    elif name:
        try:
            found = False
            for eachProvider in data.values():
                if name.lower() == eachProvider['name'].lower():
                    return {
                        "response":"success",
                        "data":eachProvider
                    }
            if not found:
                raise HTTPException(status_code=404, detail="provider name not found")
        except HTTPException as e:
            return {"response":e}
    else:
        return {"response":"no arguments provided"}


#*-----------------------------*#
#*       VIEW ALL provider     *#
#*-----------------------------*#

@app.get("/viewall", tags=['backend'])
async def viewall_Provider_Backend() -> dict:
    return {
        "response":"success",
        "data":data
    }


#*---------------------------*#
#*      CREATE provider      *#
#*---------------------------*#

@app.post("/", tags=['backend'])
async def create_Provider_Backend(provider:Healthcare_Provider) -> dict:
    keys = data.keys()

    providerID = uuid4().hex
    while providerID in keys:
        providerID = uuid4().hex
        
    # Create new provider object with input 
    new_Data = {"providerID":providerID}
    new_Data.update(provider)

    if providerID not in keys:
        try:
            if not validateCreate(new_Data):
                raise HTTPException(status_code=411, detail="Empty fields. Validation Error")

            # Append new provider to existing data
            data[providerID] = new_Data

            return {"response":"success"}

        except HTTPException as e:
            return {"response":e}
    else:
        try:
            raise HTTPException(status_code=400, detail="ProviderID already exist")
        except HTTPException as e: 
            return {"response":e}


#*---------------------------*#
#*      UPDATE provider      *#
#*---------------------------*#

@app.put("/", tags=['backend'])
async def update_Provider_Backend(providerID:str, dataUpdate:dict) -> dict:
    try:
        keys = data.keys()

        if providerID not in keys:
            raise HTTPException(status_code=404, detail="providerID not found")

        # Remove unnecessary fields
        dataUpdateValidated = {key : dataUpdate[key] for key in dataUpdate.keys() if key in data[providerID].keys()}
        if "providerID" in dataUpdateValidated.keys():
            del dataUpdateValidated["providerID"]

        if not validateUpdate(dataUpdateValidated):
                raise HTTPException(status_code=411, detail="Wrong input type. Validation Error")

        #update the provider
        for key,value in dataUpdateValidated.items():
            data[providerID][key] = value

        return {"response":"success"}

    except HTTPException as e:
        return {"response":e}


#*---------------------------*#
#*      DELETE provider      *#
#*---------------------------*#

@app.delete("/", tags=['backend'])
async def delete_Provider_Backend(providerID:str)   -> dict:
    try:
        keys = data.keys()

        if providerID not in keys:
            raise HTTPException(status_code=404, detail="ProviderID not found")

        # delete data from local variable and update to the file
        del data[providerID]

        return {"response":"success"}

    except HTTPException as e:
        return {"response":e}