#! /usr/bin/env python

"""
Module containing an example of an ETL pipeline to process PEEM images. (photoemission electron microscopy)

Created on Tue Jan 23 10:30:08 2024

@author: Fernan Saiz, PhD
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
from etl_peem import normalize_img, denoise_img
from etl_peem import save_hdf5_img, show_images

# -----------------------------------------------------------------------------
# user defined paths
# -----------------------------------------------------------------------------
OUT_PATH = "./"
DATA_PATH = sys.argv[1] # folder containing the denoised and normalized images

# check that a file name is provided and that its extension is ".dat"
if len(sys.argv)<2 or not os.path.exists(DATA_PATH):
    print("please enter a folder name containing the images to aggregate")
    sys.exit(1) 
# -----------------------------------------------------------------------------
# global parameters (modify them only if required)
# -----------------------------------------------------------------------------
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
    global_params['workdir_img'] = os.path.abspath(DATA_PATH)
    global_params['normalize'] = False # NS False on purpose
    global_params['denoise'] = False # NS False on purpose
    global_params['ishow_images'] = False
    global_params['out_path'] = os.path.abspath(OUT_PATH)
    global_params['file_path_nxs'] = os.path.join(global_params['out_path'], 'example.nxs')

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
    # read images and retrieve them as numpy arrays
    # -------------------------------------------------------------------------

    workdir_img = global_params['workdir_img']
    iexp = "xas"
    out_path = global_params['out_path']

    if not os.path.exists(out_path):
        print(f"Creating directory {out_path}")
        os.makedirs(out_path)

    if os.path.exists(workdir_img) is False:
        raise TypeError("Folder \n{0:s} \n does not exist".format(workdir_img))
    else:
        print(f"Reading npy images from {workdir_img}")

    # Reading all denoised and normalized numpy saved images
    all_imgs = []
    for file in os.listdir(workdir_img):
        if file.endswith(".npy"):
            print("Adding", file)
            np_array = np.load(os.path.join(workdir_img, file))
            all_imgs.append(np_array)


    # and aggregate them in the single array
    combined_data = np.concatenate(all_imgs, axis=0)
    print(f"Obtained a combined numpy array of shape {combined_data.shape}")

    # -------------------------------------------------------------------------
    # save images as an HDF5
    # -------------------------------------------------------------------------

    #save_hdf5_img(all_img_den, all_img, norm_img,
    #              iexp, global_params['file_path_nxs'], global_params)

    # record the combined images as if they were raw
    # we don't need to know whether of not they have been denoised or normalized
    # that's why the corresponding parameters in global_params have been set to False
    # (decoupling of functions)

    print(f"Saving the NeXus/HDF5 file to {out_path}")
    save_hdf5_img(None, combined_data, None,
                  iexp, global_params['file_path_nxs'], global_params)

    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    end = time.time()

    print('')
    print('Total execution time (s) = {0:8.2f}'.format(end - start))




# -----------------------------------------------------------------------------
# call pipeline function
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    # global parameters to control execution
    global_params = set_global_params()

    # run pipeline
    # images are being read and manipulated as numpy arrays
    # finally they get written to a NeXus/HDF5 file
    example_pipeline(global_params)
