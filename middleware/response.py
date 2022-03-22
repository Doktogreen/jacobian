from rest_framework.response import Response
from rest_framework import status


def format_response(success, message, data: dict or list):
    return {
        "success":success,
        "message": message,
        "data": data 
    }

def response(success: bool, message: str, status_code: int, data:dict=None):
    data = format_response(success, message, data)
    return Response(data=data, status=status_code)

def success_response(data: dict=None, success = True, message = "success", status = status.HTTP_200_OK):
    data = format_response(success, message, data)
    return Response(data=data, status=status)

def error_response(status = 500, data: dict = None, success=False, message = 'Oops, An error occurred'):
    data = format_response(success, message, data)
    return Response(data=data, status=status)

def handle_response(success: bool , message: str, status_code: int, data:dict=None):
    data = format_response(success, message, data)
    return Response(data=data, status=status_code)
    


