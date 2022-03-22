import uuid
import base64
from decouple import config
import cloudinary
import cloudinary.uploader
from cloudinary import CloudinaryImage
from cloudinary.exceptions import Error


def make_request(url="", method="GET"):
    auth = base64.b64encode(
        (config("PublicKey")+"."+config("PrivateKey")).encode("utf-8"))
    url = config('host') + "/merchants/api/v1/pockets/profile/" + \
        config("PublicKey") + url
    headers = {'content-type': 'application/json',
               "authHeader": auth}


def upload_image(image: str, unique_indentifier: str = str(uuid.uuid4())):
    try:
        data_uri = f"{image}"
        response = cloudinary.uploader.upload(
            data_uri,
            public_id=str(unique_indentifier),
            folder='profile-images',
        )
        url = CloudinaryImage(response.get('public_id')).build_url(transformation=[
            {'gravity': "face", 'height': 400, 'width': 400, 'crop': "crop"},
            {'radius': "max"},
            {'width': 200, 'crop': "scale"}
        ], secure=True)
        
        return url
    except Error:
        raise ValueError('Invalid base64')


