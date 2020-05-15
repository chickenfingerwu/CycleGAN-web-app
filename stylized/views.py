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
from .models import create_model
from .image_models import Test
from .data import create_dataset
from .options.test_options import TestOptions
from .util.visualizer import save_images
from .util import html
from django.core.files import File
from PIL import Image
import os
import re

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser])
def style_transfer_image(request):
    """img = File(open('stylized/dataset/single/portrait.jpg'), 'rb')
    text = File(open('stylized/requirements.txt'), 'rb')
    test_obj = Test(img, text)
    serializers = ImageSerializer(test_obj)
    print(serializers.data)"""
    img_name = ''

    if request.method == 'POST':

        serializers = ImageSerializer(data=request.data)

        if serializers.is_valid():
            serializers.save()
            style = serializers.data['style']
            img_name = str(request.data.__getitem__('image'))
            img_name = img_name.split('.')
            path = str(serializers.data['image'])
            print('%s_fake.png' % img_name[0])
            """with open(path, 'wb') as f:
                for chunk in img.chunks():
                    f.write(chunk)"""

            #experiment_name = request.GET.get('experiment_name')
            opt = TestOptions().parse()  # get test options
            # hard-code some parameters for test
            opt.name = "style_%s_pretrained" % style
            opt.model = 'test'
            opt.isTrain = False
            opt.model_name = 'test'
            opt.no_dropout = True
            opt.preprocess = 'scale_width_and_crop'
            opt.num_threads = 0   # test code only supports num_threads = 1
            opt.batch_size = 1    # test code only supports batch_size = 1
            opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
            opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
            opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.
            opt.dataroot = './stylized/dataset/single'
            #dataset = create_dataset(opt)

            dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
            model = create_model(opt)      # create a model given opt.model and other options
            model.setup(opt)               # regular setup: load and print networks; create schedulers
            #result_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))

            web_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))  # define the website directory
            response_img_path = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch)) + '/images/%s_fake.png' % img_name[0]
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

            if os.path.exists(path):
                os.remove(path)
            else:
                print("The file does not exist")

            response_img = []
            if os.path.exists(response_img_path):
                response_img = Image.open(response_img_path)
                return HttpResponse(response_img, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    #elif request.method == 'POST':
    return HttpResponse('Hello world!')
# Create your views here
