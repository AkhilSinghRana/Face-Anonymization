import numpy as np
import os, random, math, sys, signal, glob
import cv2 as cv
from shutil import copyfile, move
from importlib import reload
from subprocess import call
import subprocess
import csv  

# for debugging
#import ptvsd
#ptvsd.enable_attach(log_dir= os.path.dirname(__file__))
#ptvsd.wait_for_attach(timeout=15)

from util import options

#Blur,Pixelation and Noise
from Tools.FaceBlurAndPixelation.src.auto_blur_image import blurBoxes, pixelateBoxes, addNoise, addBlackBar
from Tools.FaceBlurAndPixelation.src.DetectorAPI import DetectorAPI

#Fawkes
from fawkes import Fawkes

class FaceAnonymization():
    def __init__(self, args= None):
        """
            Face Anonymization ToolBox 
            args = Initialize the class with arguments that will be used by different functions, arguments are defined inside util/options.py
        """
        self.args = args
        self.image_paths = glob.glob(os.path.join(self.args.input_dir, "*"))
        self.all_blur_modes = {"min":5,"mid":10,"high":25}
        self.all_pixelation_levels = {"min":20,"mid":12,"high":8}
        self.all_black_box_modes = {"top":1, "bottom":2, "complete":3}

    def runTraditionalAnonymization(self):
        """
            Implements traditional methods like blurring, black Block, random Gaussian noise 

        
        """
        model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tools/FaceBlurAndPixelation/face_model", "face.pb")
        threshold = self.args.threshold

        # create detection object
        odapi = DetectorAPI(path_to_ckpt=model_path)

        
        for image_path in self.image_paths:
            # open image
            image = cv.imread(image_path)
            
            # real face detection
            boxes, scores, classes, num = odapi.processFrame(image)

            # filter boxes due to threshold
            # boxes are in (x_top_left, y_top_left, x_bottom_right, y_bottom_right) format
            boxes = [boxes[i] for i in range(0, num) if scores[i] > threshold]

            # Process and save anonymized images
            dest_filename = os.path.join(self.args.output_dir, image_path.split("/")[-1])
            filename = dest_filename.split(".")[-2]
            print("Processing Image --> ", filename)
            
            
            
            #Pixelation
            if self.args.pixelation_mode == "all":
                for mode in self.all_pixelation_levels:
                    del(image)
                    image = cv.imread(image_path)
                    
                    mode_level = self.all_pixelation_levels[mode]
                   
                    pixelated_image = pixelateBoxes(image, boxes, blocks = mode_level)
                    cv.imwrite(dest_filename.replace(filename, filename+"_Pixelated_"+mode), pixelated_image)   
            else:
                pixelated_image = pixelateBoxes(image, boxes, blocks = self.all_pixelation_levels[self.args.pixelation_mode])
                cv.imwrite(dest_filename.replace(filename, filename+"_Pixelated_"+self.args.pixelation_mode), pixelated_image)   
            
            del(image)
            image = cv.imread(image_path)

            #Blur
            if self.args.blur_mode == "all":
                for mode in self.all_blur_modes:
                    del(image)
                    image = cv.imread(image_path)

                    mode_level = self.all_blur_modes[mode]
                   
                    blurred_image = blurBoxes(image, boxes, mode=mode_level)
                    cv.imwrite(dest_filename.replace(filename, filename+"_Blurred_"+mode), blurred_image)    
            else:
                blurred_image = blurBoxes(image, boxes, mode=self.all_blur_modes[self.args.blur_mode])
                cv.imwrite(dest_filename.replace(filename, filename+"_Blurred_"+self.args.blur_mode), blurred_image)


            del(image)
            image = cv.imread(image_path)

            noisy_image = addNoise(image, boxes)
            cv.imwrite(dest_filename.replace(filename, filename+"_SpeckleNoise"), noisy_image)

            del(image)
            image = cv.imread(image_path)

            #Black Box modes
            if self.args.black_box_mode == "all":
                for mode in self.all_black_box_modes:

                    del(image)
                    image = cv.imread(image_path)

                    mode_level = self.all_black_box_modes[mode]
                   
                    black_image = addBlackBar(image, boxes, mode=mode_level)
                    cv.imwrite(dest_filename.replace(filename, filename+"_BlackBar_"+mode), black_image)   
            else:
                black_image = addBlackBar(image, boxes, mode=self.all_black_box_modes[self.args.black_box_mode])
                cv.imwrite(dest_filename.replace(filename, filename+"_BlackBar_"+self.args.black_box_mode), black_image)   

            
            
    def runFawkes(self):
        """
            implements and runs all the images through different fawkes mode
        """
        ##################################################
        #Run the images through fawkes
        
        image_paths = [path for path in self.image_paths if "_cloaked" not in path.split("/")[-1]]
        
        protector = Fawkes(self.args.feature_extractor, self.args.gpu, self.args.batch_size)
        if self.args.mode == 'all':
            for mode in ['min', 'low', 'mid', 'high']:
                print("Fawkes is running in mode: --> ", mode)
                protector.run_protection(image_paths, mode=mode, th=self.args.th, sd=self.args.sd, lr=self.args.lr,
                                        max_step=self.args.max_step,
                                        batch_size=self.args.batch_size, format=self.args.format,
                                        separate_target=self.args.separate_target, debug=self.args.debug, no_align=self.args.no_align)
        else:
            protector.run_protection(image_paths, mode=self.args.mode, th=self.args.th, sd=self.args.sd, lr=self.args.lr,
                                    max_step=self.args.max_step,
                                    batch_size=self.args.batch_size, format=self.args.format,
                                    separate_target=self.args.separate_target, debug=self.args.debug, no_align=self.args.no_align)

        
        image_paths = glob.glob(os.path.join(self.args.input_dir, "*"))
        cloaked_images = [path for path in image_paths if "_cloaked" in path.split("/")[-1]]
        destination_images = [os.path.join(self.args.output_dir, filename.split("/")[-1]) for filename in cloaked_images]

        print("Moving Images to the desired loaction")
        for i, image in enumerate(cloaked_images):
            move(image, destination_images[i])

        print("Fawkes finished")
        ##################################################

    def runFacialRecognitionTool(self):
        """
            Helper funtion to run all the images through facial_recognition tool
        """

        def bash_command(cmd):
            sp = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
            return sp.stdout.readlines()

        
        output = bash_command("face_recognition {} {}".format(self.args.input_dir_known_faces, self.args.output_dir))


        #Now write the output as a CSV file
        
        # field names  
        fields = ['Image', ' Facial Recognition Output']  
            
        # name of csv file  
        filename = os.path.join(self.args.output_dir, "face_recognition.csv")
            
        # writing to csv file  
        with open(filename, 'w') as csvfile:
            # creating a csv writer object  
            csvwriter = csv.writer(csvfile)  
            #Write header
            csvwriter.writerow(fields)

            for row in output:
                row = row.decode("utf-8")    
                row = row.split(",")

                #Writes the row to the file
                csvwriter.writerow(row)



        ##################################################

if __name__ == "__main__":
    
    args = options.ArgumentParser()

    if args.input_dir_known_faces == "":
        args.input_dir_known_faces = args.input_dir
        
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Initialize the toolbox
    face_anonymization = FaceAnonymization(args)
    face_anonymization.runTraditionalAnonymization()
    face_anonymization.runFawkes()
    face_anonymization.runFacialRecognitionTool()

    