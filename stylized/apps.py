from django.apps import AppConfig
#from .models import create_model
#from .options.test_options import TestOptions

class StylizedConfig(AppConfig):
    name = 'stylized'

    """def ready(self):
        opt = TestOptions().parse()  # get test options
        # hard-code some parameters for test
        opt.model = 'test'
        opt.isTrain = False
        opt.model_name = 'test'
        opt.no_dropout = True
        opt.preprocess = 'none'
        opt.num_threads = 0   # test code only supports num_threads = 1
        opt.batch_size = 1    # test code only supports batch_size = 1
        opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
        opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
        opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.
        opt.dataroot = './stylized/dataset/single'

        model = create_model(opt)"""
