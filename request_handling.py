import argparse
from google.cloud import vision
from google.cloud.vision import types


def get_text(image_uri):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = image_uri
    response = client.document_text_detection(image=image)
    document = response
    return response
