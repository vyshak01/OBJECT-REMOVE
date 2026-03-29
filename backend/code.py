from fastapi import FastAPI,HTTPException,UploadFile, File, Request
from models import register, signin,ApplyRequest,BgRequest
from fastapi.middleware.cors import CORSMiddleware
from database import session, engine
import db_model
from sqlalchemy.exc import IntegrityError 
import cv2
import numpy as np
from image_process import obj
import base64

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

db_model.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

user = []

@app.post("/register")
@limiter.limit("5/minute")
def register_user(request: Request, user_data: register):
    db = session()
    try:
        db.add(db_model.register(**user_data.model_dump()))
        db.commit()
        return {"message": "registered"}          
    except IntegrityError:                      
        db.rollback()
        raise HTTPException(status_code=409, detail="user already exists")
    finally:
        db.close()                                

@app.post("/signin")
@limiter.limit("10/minute")
def check(request: Request, user_data: signin):
    db = session()
    result = db.query(db_model.register).filter(
        db_model.register.email == user_data.email
    ).first()
    db.close()

    if not result:
        raise HTTPException(status_code=404, detail="user not found")
    elif result.password != user_data.password:
        raise HTTPException(status_code=401, detail="wrong pass")
    elif result and result.password == user_data.password:
        return {"message": "sign in"}
    
@app.get("/datas")
@limiter.limit("20/minute")
def get_datas(request: Request):
    return user

@app.post("/select")
@limiter.limit("5/minute")
async def select(request: Request, img: UploadFile = File(...)):

    contents = await img.read()
    np_array = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    labels = obj.yolo(image)

    _,buffer = cv2.imencode('.jpg',image)
    image_b64 = base64.b64encode(buffer).decode('utf-8')
    print(labels)
    return {"image":image_b64,"labels":labels}

@app.post("/apply")
@limiter.limit("10/minute")
def apply(request: Request, req: ApplyRequest):
    label = req.label

    # decode base64 → raw image bytes → numpy array → OpenCV image
    img_bytes = base64.b64decode(req.image)
    np_arr    = np.frombuffer(img_bytes, np.uint8)
    img       = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    boxes = obj.Boxes(img,label)
    print(boxes)

    _, buffer   = cv2.imencode(".jpg", img)
    result_b64  = base64.b64encode(buffer).decode("utf-8")

    return {
        "image": result_b64,          
        "bbox": boxes      
    }

@app.post("/remove")
@limiter.limit("10/minute")
def remove(request: Request, data: ApplyRequest):
    label = data.label

    # decode base64 → raw image bytes → numpy array → OpenCV image
    img_bytes = base64.b64decode(data.image)
    np_arr    = np.frombuffer(img_bytes, np.uint8)
    img       = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    painted_image = obj.unet(img,label)

    _, buffer   = cv2.imencode(".jpg", painted_image)
    result_b64  = base64.b64encode(buffer).decode("utf-8")

    return {"image":result_b64}

@app.post("/change_background")
@limiter.limit("10/minute")
def color(request: Request, Color : BgRequest):
    hex_color = Color.color

    img_bytes = base64.b64decode(Color.image)
    np_arr    = np.frombuffer(img_bytes, np.uint8)
    img       = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    painted_image = obj.background_paint(img,hex_color)

    _, buffer   = cv2.imencode(".jpg", painted_image)
    result_b64  = base64.b64encode(buffer).decode("utf-8")

    return {"image":result_b64}

