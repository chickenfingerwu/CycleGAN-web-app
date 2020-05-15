from django.db import models
from PIL import Image

class ImageInfo(models.Model):
    image = models.ImageField(upload_to="./stylized/dataset/single/")
    style = models.CharField(max_length=255)

class Test(object):
    def __init__(self, image, name):
        self.image = image
        self.name = name
