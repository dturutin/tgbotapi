from fastapi import APIRouter, File, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
import pickle
import os
from Entities.User import User
from dotenv import load_dotenv
from UseCases.UserService.UserService import UserService
from UseCases.WebScrapping.WebScrapperService import WebScrapperService

router = APIRouter()

load_dotenv()


class UpdateRequest(BaseModel):
    url: str
    email: str
    password: str

class UserRequest(BaseModel):
    url: str
    email: str
    password: str


class SalesRequest(BaseModel):
    from_date: datetime
    to_date: datetime


@router.get("/get_user")
async def get_user(request: UserRequest):
    userService = UserService()
    user = userService.get_user(request.email, request.url, request.password)
    global user_data 
    user_data = user
    return user 

@router.get("/update")
async def update():
    global user_data
    user = user_data
    scrapper = WebScrapperService()
    scrapper.login(address=user.url,
                   email=user.email, password=user.password)
    return {"response": "success"}


@router.get("/scan")
async def scan():
    global user_data
    user = user_data
    scrapper = WebScrapperService()
    scrapper.set_email_url(user.email, user.url)
    scrapper.scan(url=user.url,
                  email=user.email, password=user.password)
    return {"response": "success"}


@router.get("/sales")
async def get_sales(time_period: SalesRequest):
    global user_data
    user = user_data
    scrapper = WebScrapperService()
    sales = scrapper.get_from_to(time_period.from_date, time_period.to_date, user.email, user.url)
    return sales


@router.get("/sales/today")
async def get_sales_today():
    global user_data
    user = user_data
    scrapper = WebScrapperService()
    sales = scrapper.get_today(user.email, user.url)
    return sales


@router.get("/sales/last_month")
async def get_last_month():
    global user_data
    user = user_data
    scrapper = WebScrapperService()
    sales = scrapper.get_last_month(user.email, user.url)
    return sales


@router.get("/download/{file_name}")
async def download_file(file_name: str):
    if os.path.isfile(f"./Storage/{file_name}"):
        return FileResponse(f"./Storage/{file_name}")

    else:
        return HTTPException(status_code=404, detail="File not found")


@router.get("/predict")
async def predict(unique_visitors: int):
    loaded_model = pickle.load(open('./Storage/gradient_boosting_regressor_model_user_1.pkl', 'rb'))

    today = datetime.now()
    one_day = timedelta(1)

    tomorrow = today + one_day

    month = tomorrow.month
    week_day = tomorrow.weekday()
    next_day_features = [[week_day, month, unique_visitors]]
    result = loaded_model.predict(next_day_features)

    result = result[0]

    return {"prediction": result}

# @router.get("/predict")
# async def predict(unique_visitors: int,week_day: int, month: int):
#     with open('./Storage/model.pkl', 'rb') as f:
#         model = pickle.load(f)

#     type(model)
#     prediction = model.predict([week_day, month, unique_visitors])
#     return {"prediction": prediction}
