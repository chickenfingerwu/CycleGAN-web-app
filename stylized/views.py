from django.shortcuts import render
from django.http import HttpResponse
from .serializers import ImageSerializer
from .image_models import ImageInfo
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .apps import StylizedConfig
from .models import create_model
from .image_models import Test
from .data import create_dataset
from .options.test_options import TestOptions
from .util.visualizer import save_images
from .util import html
from . import caching
from django.core.cache import cache
from django.core.files import File
from PIL import Image
import os
import base64
import shutil

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser])
def style_transfer_image(request):

    mydir = 'stylized/dataset/single/'

    if request.method == 'POST':
        img_name = str(request.data.__getitem__('image'))
        img = Image.open(request.data.__getitem__('image'))
        style = request.data.__getitem__('style')

        model = cache.get(caching.model_cache_key) # get model from cache
        opt = cache.get(caching.option_cache_key)

        path = mydir + img_name
        if not os.path.exists(mydir + img_name):
            print('doesnt exist')
            #ImageInfo.objects.all().delete()
            if len(os.listdir(mydir)) > 0:
                filelist = [ f for f in os.listdir(mydir)]
                for f in filelist:
                    os.remove(os.path.join(mydir, f))
            if len(os.listdir(opt.results_dir)) > 0:
                filelist = [ f for f in os.listdir(opt.results_dir)]
                for f in filelist:
                    shutil.rmtree(os.path.join(opt.results_dir, f))
            #serializers = ImageSerializer(data=request.data)
            img.save(mydir + img_name)
            """if serializers.is_valid():
                serializers.save()
                path = str(serializers.data['image'])
            else:
                return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)"""

        img_name = img_name.split('.')
        check_img_exist_path = '%s%s2photo/test_latest/images/%s_fake.png' % (opt.results_dir, style, img_name[0])
        if os.path.exists(check_img_exist_path):
            response_img = open(check_img_exist_path, 'rb')
            response_img = base64.b64encode(response_img.read())
            return HttpResponse(response_img, status=status.HTTP_200_OK)

        if '%s2photo' % style != opt.name:
            print('RELOADING')
            opt.name = "%s2photo" % style
            model = create_model(opt)      # create a model given opt.model and other options
            model.setup(opt)               # regular setup: load and print networks; create schedulers

            cache.set(caching.model_cache_key, model, None) # save in the cache
            cache.set(caching.option_cache_key, opt, None)

        dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
        #model = create_model(opt)      # create a model given opt.model and other options
        result_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))

        web_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch)) # define the website directory
        response_img_path = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch)) + '/images/%s_fake.png' % img_name[0]
        img_real_path = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch)) + '/images/%s_real.png' % img_name[0]
        print(response_img_path)
        if opt.load_iter > 0:  # load_iter is 0 by default
            web_dir = '{:s}_iter{:d}'.format(web_dir, opt.load_iter)
        print('creating web directory', web_dir)
        webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.epoch))

        if opt.eval:
            model.eval()
        for i, data in enumerate(dataset):
            if i >= opt.num_test:  # only apply our model to opt.num_test images.
                break
            model.set_input(data)  # unpack data from data loader
            model.test()           # run inference
            visuals = model.get_current_visuals()  # get image results
            img_path = model.get_image_paths()     # get image paths
            if i % 5 == 0:  # save images to an HTML file
                print('processing (%04d)-th image... %s' % (i, img_path))
            save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
        webpage.save()  # save the HTML

        response_img = []
        if os.path.exists(response_img_path):
            response_img = open(response_img_path, 'rb')
            response_img = base64.b64encode(response_img.read())
            return HttpResponse(response_img, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HttpResponse('Hello world!')
# Create your views here
