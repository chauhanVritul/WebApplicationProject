import json
from os import read
from fastapi import FastAPI, Request, HTTPException
from typing import List, Optional
from pydantic import BaseModel, validator
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from uuid import uuid4

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

jsonFileName = "./data.json"


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
    print(data)
    for keys in data.keys():
        if keys in ("active",):
            if not isinstance(data[keys], bool):
                return False
        else:
            if not isinstance(data[keys], str):
                return False
    return True


# read JSON file to dict
def readData(jFile=jsonFileName):
    with open(jFile) as jf:
        loadedJsonData = dict(json.load(jf))
    return loadedJsonData


# write dict to JSON file
def writeData(data, jFile=jsonFileName):
    with open(jFile, 'w') as jf:
        json.dump(data, jf, indent=4)


# fetch keys from JSON file
def getKeys(jFile=jsonFileName):
    with open(jFile) as jf:
        loadedJsonData = dict(json.load(jf))
    return loadedJsonData.keys()




#*--------------------------*#
#*         MAIN PAGE        *#
#*--------------------------*#

@app.get("/index.html", tags=['root'],response_class=HTMLResponse)
def main_Page(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})



#*--------------------------*#
#*       VIEW provider      *#
#*--------------------------*#

#? FRONTEND
@app.get("/views", tags=['frontend'],response_class=HTMLResponse)
def view(request:Request):
    with open('./data.json') as json_file:
        data = dict(json.load(json_file))
    provList = [key for key in data.keys()]
    nameList = [prov['name'] for prov in data.values()]
    return templates.TemplateResponse("viewall.html", {"request":request, "providerList":provList, "nameList":nameList})



#? BACKEND
@app.get("/", tags=['backend'])  
async def view_Provider(providerID: str = None, name: str = None)    ->dict:
    data = readData()
    keys = getKeys()
    
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


#? FRONTEND
@app.get("/viewbyID", tags = ['frontend'], response_class=HTMLResponse)
async def web_view_Provider(request:Request, providerID: str = None, name: str = None):
    return templates.TemplateResponse("viewProviderID.html", {"request":request, "providerID":providerID, "name":name})



#*-----------------------------*#
#*       VIEW ALL provider     *#
#*-----------------------------*#

#? FRONTEND
@app.get("/viewall", tags=['frontend'], response_class=HTMLResponse)
async def web_View_Provider(request: Request):
    data = readData()
    return templates.TemplateResponse("viewAllProvider.html", {"request":request, "data":data})



#*---------------------------*#
#*      CREATE provider      *#
#*---------------------------*#

#? BACKEND
@app.post("/", tags=['backend'])
async def create_Provider_Backend(providerID:str, provider:Healthcare_Provider) -> dict:
    data = readData()
    keys = getKeys()
    # Create new provider object with input 
    new_Data = {"providerID":providerID}
    new_Data.update(provider)

    if providerID not in keys:
        try:
            if not validateCreate(new_Data):
                raise HTTPException(status_code=411, detail="Empty fields. Validation Error")

            # Append new provider to existing data
            data[providerID] = new_Data
            writeData(data)

            return {"response":"success"}

        except HTTPException as e:
            return {"response":e}
    else:
        try:
            raise HTTPException(status_code=400, detail="ProviderID already exist")
        except HTTPException as e: 
            return {"response":e}


#? FRONTEND
@app.get("/create", tags=['frontend'], response_class=HTMLResponse)
async def create_Provider_Frontend(request:Request):
    keys = getKeys()
    
    # Generate unique UUID
    provID = uuid4().hex
    while uuid4 in keys:
        provID = uuid4().hex

    # Render template with generated UUID
    return templates.TemplateResponse("createProvider.html", {"request":request, "providerID":provID}) 



#*---------------------------*#
#*      UPDATE provider      *#
#*---------------------------*#

#? BACKEND
@app.put("/", tags=['backend'])
async def update_Provider_Backend(providerID:str, dataUpdate:dict) -> dict:
    try:
        data = readData()
        keys = getKeys()

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
        
        writeData(data)

        return {"response":"success"}

    except HTTPException as e:
        return {"response":e}


#? FRONTEND
@app.get("/update", tags=['frontend'], response_class = HTMLResponse)
def update_Provider_Frontend(request:Request):
    providerList = getKeys()

    # Render template with keys
    return templates.TemplateResponse("updateProvider.html", {"request":request, "providerList":providerList})



#*---------------------------*#
#*      DELETE provider      *#
#*---------------------------*#

#? BACKEND
@app.delete("/", tags=['backend'])
async def delete_Provider_Backend(providerID:str)   -> dict:
    try:
        data = readData()
        keys = getKeys()

        if providerID not in keys:
            raise HTTPException(status_code=404, detail="ProviderID not found")

        # delete data from local variable and update to the file
        del data[providerID]
        writeData(data)

        return {"response":"success"}

    except HTTPException as e:
        return {"response":e}


#? FRONTEND
@app.get("/delete", tags=['frontend'], response_class = HTMLResponse)
async def delete_Provider_Frontend(request:Request):
    keys = getKeys()

    return templates.TemplateResponse("deleteProvider.html", {"request":request, "providerList":keys})