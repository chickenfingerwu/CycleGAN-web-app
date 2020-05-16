from django.core.cache import cache
from .options.test_options import TestOptions
from .models import create_model

model_cache_key = 'model_cache'
option_cache_key = 'option_cache'
# this key is used to `set` and `get`
# your trained model from the cache

model = cache.get(model_cache_key) # get model from cache
opt = TestOptions().parse()  # get test options

if model is None:
    # your model isn't in the cache
    # so `set` it
    # hard-code some parameters for test
    opt.name = ''
    opt.model = 'test'
    opt.isTrain = False
    opt.model_name = 'test'
    opt.no_dropout = True
    opt.preprocess = 'resize_and_crop'
    opt.num_threads = 0   # test code only supports num_threads = 1
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
    opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.
    opt.dataroot = './stylized/dataset/single'

    model = create_model(opt)      # create a model given opt.model and other options

    cache.set(model_cache_key, model, None) # save in the cache
    cache.set(option_cache_key, opt, None)
    # in above line, None is the timeout parameter. It means cache forever
