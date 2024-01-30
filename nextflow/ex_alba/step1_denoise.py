#! /usr/bin/env python

"""
Module containing an example of an ETL pipeline to process PEEM images. (photoemission electron microscopy)

Created on Tue Jan 23 10:30:08 2024

@author: Fernan Saiz, PhD, reshaped for Nextflow course with Nicolas Soler
Scientific Data Management Section (SDM), Computing Division
ALBA synchrotron

-*- coding: utf-8 -*-
"""

# -----------------------------------------------------------------------------
# import packages
# -----------------------------------------------------------------------------
import os, sys
import numpy as np
import time

# Extract, Transform, and Load data
from etl_peem import read_uview
from etl_peem import denoise_img
#from etl_peem import save_hdf5_img, show_images


# -----------------------------------------------------------------------------
# global parameters (modify them only if required)
# -----------------------------------------------------------------------------
OUT_PATH = "./"

# check that a file name is provided and that its extension is ".dat"
if len(sys.argv)<2 or sys.argv[1].split('.')[-1].lower() != "dat":
    print("please enter the image to denoise")
    sys.exit(1)
else:
    DATA_IMG = sys.argv[1] # input; a single XAS image (.dat)
    filename, ext = os.path.splitext(os.path.basename(DATA_IMG))

def set_global_params():
    """
    Create a dictionary as a structure to contain all global parameters
    that control the execution of the ETL pipeline.

    Returns
    -------
    global_params : dictionary
        Global parameters
    """
    #SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

    global_params = {}
    global_params['input_img'] = os.path.abspath(DATA_IMG)
    global_params['normalize'] = True
    global_params['denoise'] = True
    global_params['ishow_images'] = False
    global_params['file_path_nxs'] = 'example.nxs'
    global_params['out_path'] = os.path.abspath(OUT_PATH)

    return global_params

def example_pipeline(global_params):
    """
    Example for ETL pipeline in image processing at CIRCE-PEEM

    Parameters
    ----------
    global_params : dictionary
        Global parameters

    Returns
    -------
    all_img and all_img_den : numpy arrays
        PEEM images
    """
    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    start = time.time()

    # -------------------------------------------------------------------------
    # read one image
    # -------------------------------------------------------------------------

    input_img = global_params['input_img']
    out_path = global_params['out_path']
    if not os.path.exists(out_path):
        print(f"Creating directory {out_path}")
        os.makedirs(out_path)

    if os.path.exists(input_img) is False:
        raise TypeError(f"input image {input_img} \n missing or does not exist, please enter it as an argument")
    else:
        print(f"Reading images from {input_img}")

    #fh, ih, fileContent, fh_vars_dict, fh_vars_list, all_img, iexp = \
    #   read_uview(input_img)

    # NS simplified,all_img is the numpy array we will denoise
    *_, all_img, iexp = read_uview(input_img)
    print("all_img", all_img)

    # -------------------------------------------------------------------------
    # denoise image
    # -------------------------------------------------------------------------

    if global_params['denoise'] is True:
        print(f"Denoising {input_img}")
        all_img_den, all_psnr = denoise_img(all_img, iexp)
        print('')
    # set to False for debugging purposes (do not run denoising)
    else:
        all_img_den = []
        all_psnr = []

    # show images (best when working with an IDE)
    #if global_params['ishow_images'] is True:
    #    show_images(all_img_den, iexp)


    # -------------------------------------------------------------------------
    # save_image as _den.npy
    # ------------------------------------------------------------------------- 

    # the saved file file have a .npy extension appended
    outname = filename + "_den"
    print(f"Saving denoised image as {outname}.npy")
    np.save(os.path.join(out_path,outname), all_img_den)


    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    end = time.time()

    print('')
    print(f"Total execution time (s) = {end - start:8.2f}")

    return all_img_den, iexp




# -----------------------------------------------------------------------------
# call pipeline function
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    # global parameters to control execution
    global_params = set_global_params()

    # run pipeline
    # images are being read and manipulated as numpy arrays
    # finally they get written to a NeXus/HDF5 file
    all_img_den, iexp = example_pipeline(global_params)
