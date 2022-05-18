# pin endpoints

import os
from dotenv import load_dotenv

from fastapi import HTTPException, APIRouter, Request, UploadFile, File, Depends
from fastapi.encoders import jsonable_encoder


from pintrigue_backend.database.google_cloud.google_cloud import upload_blob, get_image_url
from pintrigue_backend.database.mongodb.db_pin import get_pins, get_pin_by_id, get_pins_by_category, create_pin, \
    get_pin, delete_pin, update_pin_image, get_popular_pin_categories, get_all_pins
from pintrigue_backend.schemas.schemas import PinCreate, Pin
from ..image_utils import convert_image

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


@router.get("/all-pins")
def api_get_all_pins():
    response = get_all_pins()
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
        page = int(request.query_params['page'])
        print("Current Page: ", page)
    except (TypeError, ValueError) as e:
        print('Got a bad value: ', e)
        page = 0

    # get the filters
    filters = {}
    filter_results = {}
    category = request.query_params['category']
    print("Received category param ", category)
    posted_by = request.query_params['posted_by']
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


@router.get("/popular")
def api_search_popular_pins(limit: int):
    pin = get_popular_pin_categories(limit=limit)
    print("Popular Pins returned ", pin)
    return jsonable_encoder(pin)


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
    print("Received file", file.filename)
    image_old = file.file
    image_new = f"{file.filename[:-4]}.webp"
    print("New image filename", image_new)
    im = convert_image(image_old=image_old)
    upload_blob(source_file_name=im, destination_blob_name=image_new)
    image_id = get_image_url(source_blob_name=image_new)
    return image_id


@router.put("/update_pin_image", response_model=Pin)
def api_update_pin_image(pin_id, image_id: str = Depends(api_upload_image)):
    response = update_pin_image(pin_id=pin_id, image_id=image_id)
    if response:
        return get_pin_by_id(pin_id=pin_id)
    raise HTTPException(400, "Something went wrong")


@router.post("/create_pin")
def api_create_pin(pin: PinCreate = Depends(PinCreate.as_form)):
    """
    All newly created pins have the "no image" url in the image_id
    Using the Pin schema, input all pin fields in order to create a pin using create_pin
    :param image_id:
    :param pin:
    :return:
    """
    print("Form data received", pin)
    image_id = api_upload_image(pin.image_id)
    print("Image file received: ", image_id)
    response = create_pin(title=pin.title, about=pin.about, category=pin.category.lower(),
                          image_id=image_id, posted_by=pin.postedby)
    print("Response received:", response)
    if response:
        new_pin = get_pin(title=pin.title, posted_by=pin.postedby)
        return new_pin
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
