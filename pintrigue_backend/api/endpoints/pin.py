# pin endpoints

import os
from dotenv import load_dotenv

from fastapi import HTTPException, APIRouter, Request, UploadFile, File, Depends
from fastapi.encoders import jsonable_encoder

from pintrigue_backend.database.google_cloud.google_cloud import upload_blob, get_image_url
from pintrigue_backend.database.mongodb.db import get_pins, get_pin_by_id, get_pins_by_category, create_pin, get_pin, \
    delete_pin, update_pin_image
from pintrigue_backend.schemas.schemas import PinInDB, PinCreate, Pin

load_dotenv()

# env variables
BUCKET_NAME = os.getenv('BUCKET_NAME')

router = APIRouter(
    prefix="/api/pins",
    tags=["pins"]
)


@router.get("/")
def api_get_pins():
    pins_per_page = 20

    (pins, total_num_entries) = get_pins(filters=None, page=0, pins_per_page=pins_per_page)

    response = {
        "pins": pins,
        "page": 0,
        "filters": {},
        "entries_per_page": pins_per_page,
        "total_results": total_num_entries
    }
    return jsonable_encoder(response)


@router.get("/search")
def api_search_pins(request: Request):
    """
    Search end point, can search by posted_by or category
    :param request:
    :return:
    """
    default_pins_per_page = 20

    # get the current page
    try:
        page = int(request.path_params.get("page", 0))
    except (TypeError, ValueError) as e:
        print('Got a bad value: ', e)
        page = 0

    # get the filters
    filters = {}
    filter_results = {}
    category = request.path_params.fromkeys('category')
    posted_by = request.path_params.fromkeys('posted_by')
    if category:
        filters["category"] = category
        filter_results["category"] = category
    if posted_by:
        filters["posted_by"] = posted_by
        filter_results["posted_by"] = posted_by

    # query the database and get the necessary info
    (pins, total_num_entries) = get_pins(filters, page, default_pins_per_page)

    response = {
        "pins": pins,
        "page": page,
        "filters": filter_results,
        "entries_per_page": default_pins_per_page,
        "total_results": total_num_entries
    }

    return jsonable_encoder(response)


@router.get("/<pin_id>")
def api_search_pin_by_id(pin_id):
    pin = get_pin_by_id(pin_id)
    print(f"Returned pin info: {pin}")
    if pin is None:
        return {"Error": "Pin not found"}
    else:
        return pin


@router.get("/category")
def api_get_pins_by_category(request: Request):
    print("Response received: ", request)
    try:
        categories = request.query_params['category']
        print("Categories: ", categories)
        results = get_pins_by_category(categories=categories)
        print("Results sent: ", results)
        return jsonable_encoder(results)
    except Exception as e:
        response = {"Error": e}
        return jsonable_encoder(response)


@router.post("/upload_image")
def api_upload_image(file: UploadFile = File(...)):
    """
    - Using UploadFile, intake the file and then upload to Google Cloud Storage
    - Once blob has been uploaded use the get_image_url function to create a URL and return as response
    :param file:
    :return:
    """
    upload_blob(source_file_name=file.file, destination_blob_name=file.filename)
    image_id = get_image_url(source_blob_name=file.filename)
    return image_id


@router.put("/update_pin_image", response_model=Pin)
def api_update_pin_image(pin_id, image_id: str = Depends(api_upload_image)):
    response = update_pin_image(pin_id=pin_id, image_id=image_id)
    if response:
        pin = get_pin_by_id(pin_id=pin_id)
        return pin
    raise HTTPException(400, "Something went wrong")


@router.post("/create_pin", response_model=PinInDB)
def api_create_pin(pin: PinCreate, postedby: str):
    """
    All newly created pins have the "no image" url in the image_id
    Using the Pin schema, input all pin fields in order to create a pin using create_pin
    :param pin:
    :param postedby:
    :return:
    """
    image_id = f"https://storage.googleapis.com/{BUCKET_NAME}/No_image_available.svg.png"
    response = create_pin(title=pin.title, about=pin.about, category=pin.category,
                          image_id=image_id, posted_by=postedby)
    print("Response received:", response)
    if response:
        new_pin = get_pin(title=pin.title, posted_by=postedby)
        return jsonable_encoder(new_pin)
    raise HTTPException(400, "Something went wrong")


@router.delete("/delete_pin/<pin_id>")
def api_delete_pin(pin_id):
    """
    Using the pin_id, delete the pin from the pins collection
    :param pin_id:
    :return:
    """
    response = delete_pin(pin_id)
    if response:
        return {"success": True}
    raise HTTPException(400, "Something went wrong, pin was not deleted")
