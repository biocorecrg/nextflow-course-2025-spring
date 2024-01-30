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
from etl_peem import normalize_img
#from etl_peem import save_hdf5_img, show_images

# -----------------------------------------------------------------------------
# user defined paths
# -----------------------------------------------------------------------------
NORM_PATH = "." # folder the normalization data (image taken without a sample)
OUT_PATH = "."
# -----------------------------------------------------------------------------
# global parameters (modify them only if required)
# -----------------------------------------------------------------------------


# check that a file name is provided and that its extension is ".dat"
if len(sys.argv)<2 or sys.argv[1].split('.')[-1].lower() != "npy":
    print("please enter the image to normalize (numpy array format .npy)")
    sys.exit(1)
else:
    DATA_IMG = sys.argv[1] # input; a single XAS image (.dat), that can have been denoised before
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
    global_params['workdir_norm'] = os.path.abspath(NORM_PATH)
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
    all_img_norm : numpy array
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


    # NS simplified
    iexp = 'xas'
    all_img = np.load(input_img)
    #all_img = all_img.astype(float)
    print("input_img", all_img)

    # -------------------------------------------------------------------------
    # read normalization image
    # -------------------------------------------------------------------------
    workdir_norm = global_params['workdir_norm']

    if os.path.exists(workdir_norm) is False:
        raise TypeError(f"Path {workdir_norm} does not exist")
    else:
        print(f"Reading normalization image from \n{workdir_norm}")

    # fh, ih, fileContent, fh_vars_dict, fh_vars_list
    # have the same values for all Uview images
    *_, norm_img, iexp_norm = read_uview(workdir_norm)
    print("norm_img", norm_img)


    # -------------------------------------------------------------------------
    # normalise image
    # -------------------------------------------------------------------------


    if global_params['normalize'] is True:
        print(f"Normalizing {input_img}")
        all_img_norm = normalize_img(all_img, norm_img, iexp)
        print(all_img_norm)
    else:
        all_img_norm = all_img # no normalization

    # -------------------------------------------------------------------------
    # save_image as _norm.npy
    # ------------------------------------------------------------------------- 
    outname = filename + "_norm"
    print(f"Saving normalized imaged as {outname}.npy")
    np.save(os.path.join(out_path,outname), all_img_norm)


    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    end = time.time()

    print(f"Total execution time (s) = {end - start:8.3f}")

    return all_img_norm, iexp



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
