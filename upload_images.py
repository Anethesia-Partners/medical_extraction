from gcloud import storage
import argparse
from enum import Enum
import io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import os
import tempfile
from pdf2image import convert_from_path, convert_from_bytes

def convert_pdf(file_path, output_path=None):
    # save temp image files in temp dir, delete them after we are finished
    with tempfile.TemporaryDirectory() as temp_dir:
        # convert pdf to multiple image
        images = convert_from_path(file_path, output_folder=temp_dir)
        # save images to temporary directory
        temp_images = []
        for i in range(len(images)):
            image_path = f'{temp_dir}/{i}.jpg'
            images[i].save(image_path, 'JPEG')
            temp_images.append(image_path)
        # read images into pillow.Image
        imgs = list(map(Image.open, temp_images))
    # find minimum width of images
    min_img_width = min(i.width for i in imgs)
    # find total height of all images
    total_height = 0
    for i, img in enumerate(imgs):
        total_height += imgs[i].height
    # create new image object with width and total height
    merged_image = Image.new(imgs[0].mode, (min_img_width, total_height))
    # paste images together one by one
    y = 0
    for img in imgs:
        merged_image.paste(img, (0, y))
        y += img.height
    # save merged image
    merged_image.save(output_path, 'JPEG')
    return merged_image


if __name__ == '__main__':

    data_path = '/Users/rhettd/Documents/Fall2019/MED_CONSULT/Data/fwdfacesheets/'
    file_name = 'BARNEY SORT#732_21580'

    image = convert_pdf(data_path + file_name+'.pdf', data_path + file_name+'.jpg')

    client = storage.Client(project='medical-extraction')
    bucket = client.get_bucket('report-ap')
    blob = bucket.blob('test_image.jpg')
    blob.upload_from_filename(data_path + file_name+'.jpg')
