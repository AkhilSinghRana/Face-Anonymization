# author: Asmaa Mirkhan ~ 2019
import os
import argparse
import cv2 as cv
from .DetectorAPI import DetectorAPI
import numpy as np
from skimage.util import random_noise

from math import floor

def blurBoxes(image, boxes, mode=5):
    """
    Argument:
    image -- the image that will be edited as a matrix
    boxes -- list of boxes that will be blurred, each box must be int the format (x_top_left, y_top_left, x_bottom_right, y_bottom_right)
    mode  -- Different blurring levels supported one of --> min=5, mid=15 or high=25
    
    Returns:
    image -- the blurred image as a matrix

    """

    for box in boxes:
        # unpack each box
        x1, y1, x2, y2 = [d for d in box]

        # crop the image due to the current box
        sub = image[y1:y2, x1:x2]

        # apply GaussianBlur on cropped area
        blur = cv.blur(sub, (mode, mode))

        # paste blurred image on the original image
        image[y1:y2, x1:x2] = blur

    return image

def pixelateBoxes(image, boxes, blocks=20):
    """
    Argument:
    image  -- the image that will be edited as a matrix
    boxes  -- list of boxes that will be pixelate, each box must be int the format (x_top_left, y_top_left, x_bottom_right, y_bottom_right)
    blocks -- pixelate effect in blocks, #pixels to downscale

    Returns:
    image -- the pixelated image as a matrix
    """


    for box in boxes:
        # unpack each box
        x1, y1, x2, y2 = [d for d in box]

        # crop the image due to the current box
        sub = image[y1:y2, x1:x2]
        height, width, _ = sub.shape

        # divide the input image into NxN blocks
        (h, w) = blocks, blocks
        
        # Resize image to "pixelated" size
        temp = cv.resize(sub, (w, h), interpolation=cv.INTER_LINEAR)

        # Initialize output image
        pixelate = cv.resize(temp, (width, height), interpolation=cv.INTER_NEAREST)

        # paste pixelated image on the original image
        image[y1:y2, x1:x2] = pixelate

    # return the pixelated blurred image
    
    return image

def addNoise(image, boxes, noise_type="gaussian"):
    """
    Argument:
    image  -- the image that will be edited as a matrix
    boxes  -- list of boxes that will be pixelate, each box must be int the format (x_top_left, y_top_left, x_bottom_right, y_bottom_right)
    noise_type -- deafult Salt and Pepper, for more options look documentation of scikit-image

    Returns:
    image -- image as a matrix with noise added to it
    """


    for box in boxes:
        # unpack each box
        x1, y1, x2, y2 = [d for d in box]

        # crop the image due to the current box You can also add noise to the entire image
        sub = image[y1:y2, x1:x2]

        # apply Noise on cropped area
        
        noisy_image = random_noise(sub, mode=noise_type)
        # The above function returns a floating-point image
        # on the range [0, 1], thus we changed it to 'uint8'
        # and from [0,255]
        noise_img = np.array(255*noisy_image, dtype = 'uint8')
        
        # paste blurred image on the original image
        image[y1:y2, x1:x2] = noise_img
    
    return image


def addBlackBar(image, boxes, mode=1):
    """
    Argument:
    image  -- the image that will be edited as a matrix
    boxes  -- list of boxes that will be pixelate, each box must be int the format (x_top_left, y_top_left, x_bottom_right, y_bottom_right)
    mode   -- mode defines how much pixels will be blacked 1=top, 2 = bottom, 3 = all

    Returns:
    image -- image as a matrix with black pixel on the face
    """


    for box in boxes:
        # unpack each box
        x1, y1, x2, y2 = [d for d in box]

        # crop the image due to the current box You can also add noise to the entire image
        if mode == 3:
            #black out entire face
            sub = image[y1:y2, x1:x2] * 0
            
            #Replace the image
            image[y1:y2, x1:x2] = sub
        
        elif mode == 2:
            #black out bottom face #mid mode
            y1, y2 = y1+ floor((y2-y1)/4), floor((y2-y1)/3 * 3.2)
            sub = image[y1: y2, x1:x2] * 0
            #Replace the image
            image[y1: y2, x1:x2] = sub
        
        elif mode == 1:
            #black out top face # min mode
            y1, y2 = y1 + floor((y2-y1)/4) , floor((y2-y1)/3.5 * 3)
            sub = image[y1: y2, x1:x2] * 0
            #Replace the image
            image[y1:y2, x1:x2] = sub
        
        else:
            raise NotImplementedError

        # paste sub image on the original image
    
    return image


def main(args):
    # assign model path and threshold
    model_path = args.model_path
    threshold = args.threshold

    # create detection object
    odapi = DetectorAPI(path_to_ckpt=model_path)

    # open image
    image = cv.imread(args.input_image)

    # real face detection
    boxes, scores, classes, num = odapi.processFrame(image)

    # filter boxes due to threshold
    # boxes are in (x_top_left, y_top_left, x_bottom_right, y_bottom_right) format
    boxes = [boxes[i] for i in range(0, num) if scores[i] > threshold]

    # apply blurring or pixelation
    if args.method_type == "blur":
        image = blurBoxes(image, boxes)
    elif args.method_type == "pixelate":
        print("pixelating image")
        image = pixelateBoxes(image, boxes)


    # if image will be saved then save it
    if args.output_image:
        cv.imwrite(args.output_image, image)
        print('Image has been saved successfully at', args.output_image,
              'path')
    
    # show image
    cv.imshow('blurred', image)

    # when any key has been pressed then close window and stop the program
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    # creating argument parser
    parser = argparse.ArgumentParser(description='Image blurring parameters')

    # adding arguments
    parser.add_argument('-i',
                        '--input_image',
                        help='Path to your image',
                        type=str,
                        required=True)
    parser.add_argument('-m',
                        '--model_path',
                        help='Path to .pb model',
                        type=str,
                        required=True)
    parser.add_argument('-mt',
                        '--method_type',
                        help='blur/pixelate',
                        type=str,
                        required=False,
                        default="blur")
    parser.add_argument('-o',
                        '--output_image',
                        help='Output file path',
                        type=str)
    parser.add_argument('-t',
                        '--threshold',
                        help='Face detection confidence',
                        default=0.7,
                        type=float)
    args = parser.parse_args()
    print(args)
    # if input image path is invalid then stop
    assert os.path.isfile(args.input_image), 'Invalid input file'

    # if output directory is invalid then stop
    if args.output_image:
        assert os.path.isdir(os.path.dirname(
            args.output_image)), 'No such directory'

    main(args)
