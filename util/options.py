import argparse

def ArgumentParser():
        parser = argparse.ArgumentParser()

        #Arguments for reading data
        parser.add_argument("--input_dir", type=str, default="./data", help="Directory where the images that needs to be anonymized are present")
        parser.add_argument("--input_dir_known_faces", type=str, default="", help="Directory where the images of known persons are present, this creates a database of known persons for facial recognition tool,\
                                                                                                by default same directory as input directory is choosen")
        parser.add_argument("--output_dir", type=str, default="./Anonymized-Results", help="Directory where the anonymized images will be save")
        
        #########################################################
        # Arguments for Blur, pixelation, noise etc
        parser.add_argument('-t',
                        '--threshold',
                        help='Face detection confidence',
                        default=0.4,
                        type=float)
        
        parser.add_argument("-bm","--blur_mode", type=str,
                                help='Options for different level of blurring, selection --> min, mid , high, all',
                                default='all')
        parser.add_argument("-pm","--pixelation_mode", type=str,
                                help='Options for different level of pixelation same as blur modes',
                                default='all')
        parser.add_argument("-boxm","--black_box_mode", type=str,
                                help='Options for different level of blackbox selection --> top, bottom, complete, all',
                                default='all')
        #########################END###########################
        


        #######################################################
        # Arguments for fawkes

        parser.add_argument('--gpu', '-g', type=str,
                                help='the GPU id when using GPU for optimization', default='0')

        parser.add_argument('--mode', '-m', type=str,
                                help='cloak generation mode, select from min, low, mid, high. The higher the mode is, the more perturbation added and stronger protection',
                                default='all')

        parser.add_argument('--feature-extractor', type=str,
                                help="name of the feature extractor used for optimization, currently only support high_extract",
                                default="high_extract")

        parser.add_argument('--th', help='only relevant with mode=custom, DSSIM threshold for perturbation', type=float,
                                default=0.01)
        parser.add_argument('--max-step', help='only relevant with mode=custom, number of steps for optimization', type=int,
                                default=1000)
        parser.add_argument('--sd', type=int, help='only relevant with mode=custom, penalty number, read more in the paper',
                                default=1e9)
        parser.add_argument('--lr', type=float, help='only relevant with mode=custom, learning rate', default=2)

        parser.add_argument('--batch-size', help="number of images to run optimization together", type=int, default=1)
        parser.add_argument('--separate_target', help="whether select separate targets for each faces in the directory",
                                action='store_true')
        parser.add_argument('--no-align', help="whether to detect and crop faces",
                                action='store_true')
        parser.add_argument('--debug', help="turn on debug and copy/paste the stdout when reporting an issue on github",
                                action='store_true')
        parser.add_argument('--format', type=str,
                                help="format of the output image",
                                default="png")
        #########################END###########################
        
        args = parser.parse_args()
        return args