from .demuxer import *
from .reader import *
from .stream_buffer import *

import os
import PIL
import numpy

def unpack_sample(filename):
    destdir = os.path.splitext(filename)[0]
    if not os.path.isdir(destdir):
        os.mkdir(destdir)

    with Reader(filename) as reader:
        for framecounter, main, depth, saliency, mask, meta in reader.get_samples(compute_mask = False):
            timestamp = str(framecounter).zfill(4)
            main.save(os.path.join(destdir, f"{timestamp}-main.jpg"))
            if mask != None:
                mask.save(os.path.join(destdir, f"{timestamp}-mask.png"))

                main_cropped = numpy.zeros((main.height, main.width, 4))
                main_cropped[:,:,0:3] = numpy.asarray(main)
                main_cropped[:,:,3] = numpy.asarray(mask)[:,:,0]
                cropped_zeroes = main_cropped[:,:,3] <= 5
                main_cropped[cropped_zeroes, 0:3] = 0

                main_cropped = PIL.Image.fromarray(main_cropped.astype(numpy.uint8))
                main_cropped.save(os.path.join(destdir, f"{timestamp}-cropped.png"))
            if depth != None:
                depth.save(os.path.join(destdir, f"{timestamp}-depth.png"))
            if saliency != None:
                saliency.save(os.path.join(destdir, f"{timestamp}-saliency.png"))
            with open(os.path.join(destdir, f"{timestamp}-meta.json"), 'w') as f:
                json.dump(meta, f)
            print(timestamp)

        logo = reader.get_recycling_logo()
        if logo != None:
            logo.save(os.path.join(destdir, "recycling-logo.png"))


