#! /usr/bin/env python

"""
Module containing the scripts to:
    . Extract data and metadata from Uview *.dat files from Elmitec
    . Transform (process) PEEM images, e.g. denoising with Non-local means
    . Load as visualization (on-the-fly in Spyder or another IDE) or writing
      raw and transformed PEEM images in an HDF5 file with silx

Created on Thu Jan 25 11:27:00 2024

@author: Fernan Saiz, PhD
Scientific Data Management Section (SDM), Computing Division
ALBA synchrotron

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# -----------------------------------------------------------------------------
# import packages
# -----------------------------------------------------------------------------

from importUview_v3 import fileHeader, imageHeader
from pathlib import Path
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.metrics import peak_signal_noise_ratio
from nexusformat.nexus import NXroot, NXdata, NXentry, NXinstrument, NXdetector

import os
import matplotlib.pyplot as plt  # only necessary to display images in python
import numpy as np
import struct  # for unpacking binary data
import time


# -----------------------------------------------------------------------------
# read Uview file function
# -----------------------------------------------------------------------------


def readUview(fc, fh, ih):
    """
    Read Uview file function.

    Parameters
    ----------
    fc : binary file object
        file Content in binary
    fh : fileHeader (object)
        self-explanatory
    ih : imageHeader
        Metadata with all the header

    Returns
    -------
    img : reshaped image
        2D numpy array with size imageWidth*imageHeight (Nx * Ny)

    """
    totalHeaderSize = fh.headerSize + ih.imageHeadersize + \
        ih.attachedMarkupSize + ih.LEEMDataVersion

    img = np.reshape(struct.unpack(str(fh.imageWidth*fh.imageHeight)+'H',
                                   fc[totalHeaderSize:]),
                     (fh.imageHeight, fh.imageWidth))

    return img


# -----------------------------------------------------------------------------
# dump all the information in an object, e.g. fileheader
# -----------------------------------------------------------------------------

def dump_info(obj):
    """
    Dump all the information in an object, e.g. fileheader.

    Parameters
    ----------
    obj : object
        Metadata structure in header of the image.

    Returns
    -------
    work_dict : working dictionary
        Metadata about Image Settings
    work_list: 2D List
       Metadata about Image Settings

    """
    work_dict = {}
    work_list = []

    for attr in dir(obj):
        # without built-in functions
        if not attr[0] in "_":
            # print("obj.%s = %r" % (attr, getattr(obj, attr)))
            key = attr
            value = getattr(obj, attr)

            work_dict[key] = value
            work_list.append([key, value])

    return work_dict, work_list

# -----------------------------------------------------------------------------
# get information from the image file
# -----------------------------------------------------------------------------


def retr_file_info(datFileName):
    """
    Get information from the image file.

    Parameters
    ----------
    datFileName : string
        Name of image file to read

    Returns
    -------
    fh : fileHeader Object of importUview_v3.py
        fileheader
    ih : imageHeader Object of importUview_v3.py
        Image metadata
    img : 2D Numpy array
        Image matrix Nx * Ny
    fileContent : object
        self-explainatory
    fh_vars_dict : dictionary
        Metadata about Image Settings
    fh_vars_list : 2D List
        Metadata about Image Settings

    """
    with open(datFileName, mode='rb') as file:  # b is important -> binary
        fileContent = file.read()

    # read the headers
    fh = fileHeader(fileContent)
    ih = imageHeader(fileContent, fh)

    # read the image
    img = readUview(fileContent, fh, ih)
    fh_vars_dict, fh_vars_list = dump_info(fh)

    # show the image
    # plt.imshow(img, cmap=plt.cm.gray)
    # plt.show()

    # return these global variables to make them appear in Spyder's
    # Variable Explorer panel
    return fh, ih, fileContent, fh_vars_dict, fh_vars_list, img

# -----------------------------------------------------------------------------
# Define a class with investigation attributes.
# -----------------------------------------------------------------------------


class invest_attrs():
    """
    Define a class with investigation attributes.
    This class is properly defined if the full path is maintained from
    /beamlines/bl24.
    """

    def __init__(self, bl, cycle, username, exp_data, sample_name):
        self.bl = bl
        self.cycle = cycle
        self.username = username
        self.exp_data = exp_data
        self.sample_name = sample_name


# -----------------------------------------------------------------------------
# read the *.dat image files
# -----------------------------------------------------------------------------

def retr_list_of_files(workdir, sample_name):
    """
    Read the *.dat image files in workdir and return them as 2D numpy arrays.

    It is needed to detect whether workdir contains duplicated images from
    XMLD or XMCD experiments with plus and minus polarisations or single
    images for e.g. XAS.

    Parameters
    ----------
    workdir : string
        Full path to the folder with the *.dat image files.

    Parameters
    ----------
    workdir : TYPE
        DESCRIPTION.
    sample_name : TYPE
        DESCRIPTION.

    Returns
    -------
    all_files : list
        List of all local files found in workdir
    iexp : string
        Experiment Flag iexp set to XAS

    """
    # -------------------------------------------------------------------------
    # loop over *.dat files in workdir
    # -------------------------------------------------------------------------

    all_files = []

    #NS edited
    if workdir.endswith(".dat"): #if we provide one image instead of a working dir
        all_files.append(os.path.abspath(workdir))
    else:
        for file in os.listdir(workdir):
            # if file.startswith(sample_name):
            if file.endswith(".dat"):
                all_files.append(os.path.join(workdir, file))

        nfiles = len(all_files)
        if nfiles == 0:
            msg = "No images read in folder \n:{0:s} Aborting program."
            raise TypeError(msg.format(workdir))

    # -------------------------------------------------------------------------
    # test if images are XMLD/XMCD or XAS
    # -------------------------------------------------------------------------

    # by default idichroism and iexp will be set to 0
    idichroism = 0

    for file in all_files:
        if "plus" in file:
            idichroism += 1
            break

    for file in all_files:
        if "min" in file:
            idichroism += 1
            break

    # capture normalization image
    for file in all_files:
        if "norm" in file:
            idichroism = -1
            break

    if idichroism == -1:
        iexp = 'norm'
    if idichroism == 2:
        iexp = 'xmcd'
    elif idichroism == 0:
        iexp = 'xas'
    elif idichroism == 1:
        iexp = 'xas'
        msg = 'Experiment Flag iexp set to XAS \n Check filenames in {0:s}'
        print(msg.format(workdir))

    # sanity check
    nfiles = len(all_files)

    if nfiles == 0:
        msg = 'Error: No files read in :\n{0:s}\n Aborting program'
        raise Exception(msg.format(workdir))
    else:
        msg = 'Number of images to read = {0:5d} in mode: {1:s}'
        print(msg.format(nfiles, iexp))

    return all_files, iexp

# -----------------------------------------------------------------------------
# retrieve experiment attributes from full path: the bl, cycle, username
# -----------------------------------------------------------------------------


def retr_invest_attrs(workdir):
    """
    Retrieve experiment attributes from full path: the bl, cycle, username.

    Parameters
    ----------
    workdir : string
        Full path to the folder with the *.dat image files.

    Returns
    -------
    exp_attrs : object
        Experiment attributes (bl, cycle, username, experiment date)

    """

    # split the full path to get the sample name
    workdir_split = Path(workdir).parts
    # print(workdir_split)
    sample_name = workdir_split[-1]

    # initialize values
    bl = ''
    cycle = ''
    username = ''
    exp_date = ''

    i = 0

    for folder in workdir_split:
        if 'bl' in folder:
            bl = folder
        if 'cycle' in folder:
            cycle = folder
        if 'DATA' in folder:
            username = workdir_split[i-1]
            exp_date = workdir_split[i+1]

        i += 1

    exp_attrs = invest_attrs(bl, cycle, username, exp_date, sample_name)
    return exp_attrs


# -----------------------------------------------------------------------------
# Function to read Uview files
# -----------------------------------------------------------------------------

def read_dat_images(all_files, iexp):
    """
    read Uview files for each type of PEEM experiment.

    Parameters
    ----------
    all_files : list
        List of all local files found in workdir
    iexp : string
        Experiment Flag iexp set to XAS

    Returns
    -------
    fh : fileHeader Object of importUview_v3.py
        fileheader
    ih : imageHeader Object of importUview_v3.py
        Image metadata
    fileContent : object
        self-explainatory
    fh_vars_dict : dictionary
        Metadata about Image Settings
    fh_vars_list : 2D List
        Metadata about Image Settings
    all_img : numpy array
        Images for no dichroism experiment (e.g. XAS)
    """
    # -------------------------------------------------------------------------
    # record execution of reading images
    # -------------------------------------------------------------------------

    start = time.time()

    # -------------------------------------------------------------------------
    # read images
    # -------------------------------------------------------------------------

    # image resolution
    res_img = np.uint16

    icount_read = 0
    nfiles = len(all_files)
    iplus = 0
    imin = 0

    # if platform.system() == "Windows":
    #     pathChar = r"\\"
    # else:
    #     pathChar = "/"

    # loop over all images
    for i in range(0, nfiles):
        filename = all_files[i]
        local_filename = Path(filename).parts
        # print(local_filename)
        local_filename = local_filename[-1]
        # print(filename)

        ii = i+1
        if ii % 50 == 0:
            print("Reading file {0:4d} of {1:4d}".format(ii, nfiles))
        elif ii == nfiles-1:
            print("Reading file {0:4d} of {1:4d}".format(ii, nfiles))

        # ---------------------------------------------------------------------
        # get metadata (fh, ih, fileContent, fh_vars_dict, fh_vars_list)
        # and data (img_raw) for each image *.dat file
        # ---------------------------------------------------------------------
        fh, ih, fileContent, fh_vars_dict, fh_vars_list, img_raw = \
            retr_file_info(filename)

        if icount_read == 0:
            nx = len(img_raw)
            ny = len(img_raw[0])

            # Uview generates 16-bit images, hence, np.int16 is needed
            if iexp == 'xmcd':
                nhalf = int(nfiles*0.5)
                all_img = np.zeros(shape=(nhalf, nx, ny, 2), dtype=res_img)
            else:
                all_img = np.zeros(shape=(nfiles, nx, ny), dtype=res_img)

        # ---------------------------------------------------------------------
        # store data
        # assign type of polarization and img for each polarization
        # ---------------------------------------------------------------------

        if 'min' in local_filename:
            all_img[iplus, :, :, 0] = img_raw
            print
            iplus += 1
        elif 'plus' in local_filename:
            all_img[imin, :, :, 1] = img_raw
            imin += 1
        else:
            all_img[icount_read, :, :] = img_raw[:, :]

        icount_read += 1

    end = time.time()
    msg = 'Number of images read    = {0:5d} in mode: {1:s} in {2:5.1f} sec'
    print(msg.format(icount_read, iexp, end-start))

    return fh, ih, fileContent, fh_vars_dict, fh_vars_list, all_img

# -----------------------------------------------------------------------------
# Sanity check: equal number of images for plus and minus polazations
# -----------------------------------------------------------------------------


def check_num_files(all_files, iexp):
    """
    Check for equal number of images for plus and minus polazations.

    Parameters
    ----------
    all_files : list
        List of all local files found in workdir
    iexp : string
        Experiment Flag iexp set to XAS

    Returns
    -------
    nfiles : integer
        Number of all dat files found in workdir

    """
    if iexp == 'xmcd':
        nfiles = np.zeros(2)
    elif iexp == 'xas':
        nfiles = 0

    if iexp is None:
        msg = "No experiment value assigned"
        raise TypeError(msg)

    for file in all_files:
        file_split = Path(file).parts
        filename = file_split[-1]

        if iexp == 'xmcd':
            if 'plus' in filename:
                nfiles[0] += 1
            if 'min' in filename:
                nfiles[1] += 1
        elif iexp == 'xas':
            nfiles += 1
            print(nfiles)

    if iexp == 'xmcd':
        if nfiles[0] != nfiles[1]:
            msg = "Different number of images for plus and minus polazations"
            raise TypeError(msg)

    return nfiles

# -----------------------------------------------------------------------------
# workflow function to read data and metadata from Uview *.dat files
# -----------------------------------------------------------------------------


def read_uview(workdir):
    """
    Workflow function to read data and metadata from Uview *.dat files.

    Parameters
    ----------
    workdir : string
        Full path to the folder with the *.dat image files.

    Returns
    -------
    fh : fileHeader Object of importUview_v3.py
        fileheader
    ih : imageHeader Object of importUview_v3.py
        Image metadata
    fileContent : object
        self-explainatory
    fh_vars_dict : dictionary
        Metadata about Image Settings
    fh_vars_list : 2D List
        Metadata about Image Settings
    all_img : numpy array
        Images for no dichroism experiment (e.g. XAS)
    all_img_plus : numpy array
        All images with plus polarization in XMLD/XMCD measurements
    all_img_min : numpy array
        All images with minus polarization in XMLD/XMCD measurements
    iexp : string
        Experiment Flag iexp set to XAS

    """
    # retrieve investigation attributes from full path: the bl, cycle, username
    exp_attrs = retr_invest_attrs(workdir)

    # read list of *.dat images and detect type of experiments
    all_files, iexp = retr_list_of_files(workdir, exp_attrs.sample_name)

    # Sanity check for XMLD/XMCD
    # check_num_files(all_files, iexp)

    # read *.dat images and convert them into 2D numpy array
    fh, ih, fileContent, fh_vars_dict, fh_vars_list, \
        all_img = read_dat_images(all_files, iexp)

    # show images to test
    # show_images(all_img, iexp)

    return fh, ih, fileContent, fh_vars_dict, fh_vars_list, all_img, iexp


# -----------------------------------------------------------------------------
# denoise images
# -----------------------------------------------------------------------------


def denoise(img_raw, ialgo):
    """
    Denoise image with non-local means.

    Parameters
    ----------
    img_raw : numpy array
        Raw image
    ialgo : integer
        Type of non-local means algorithm to apply for denoising

    Returns
    -------
    denoise : numpy array
        Denoised image
    psnr : float
        peak signal to noise ratio
    """
    # estimate the noise standard deviation from the noisy image
    sigma_est = np.mean(estimate_sigma(img_raw))  # norm_img
    # print(f'estimated noise standard deviation = {sigma_est}')

    patch_kw = dict(patch_size=5,      # 5x5 patches
                    patch_distance=6)  # 13x13 search area

    # slow algorithm
    if ialgo == 1:
        img_denoise = denoise_nl_means(img_raw, h=1.15 * sigma_est,
                                       fast_mode=False, **patch_kw)
    # slow algorithm, sigma provided
    elif ialgo == 2:
        img_denoise = denoise_nl_means(img_raw, h=0.8 * sigma_est,
                                       sigma=sigma_est,
                                       fast_mode=False, **patch_kw)
    # fast algorithm
    elif ialgo == 3:
        img_denoise = denoise_nl_means(img_raw, h=0.8 * sigma_est,
                                       fast_mode=True, **patch_kw)
    # fast algorithm, sigma provided
    elif ialgo == 4:
        img_denoise = denoise_nl_means(img_raw, h=0.6 * sigma_est,
                                       sigma=sigma_est,
                                       fast_mode=True, **patch_kw)
    else:
        raise TypeError('Invalid value {0:3d} for ialgo'.format(ialgo))

    # -------------------------------------------------------------------------
    # convert img_denoise from float64 to int16
    # -------------------------------------------------------------------------

    # normalize the data to 0 - 1
    min_val = np.min(img_denoise)
    max_val = np.max(img_denoise)
    scaled_data = (img_denoise - min_val) / (max_val - min_val)

    # 2**16 = 1024
    img_denoise = (1024-1) * scaled_data  # Now scale by 1023
    img_denoise = img_denoise.astype(np.uint16)

    # print(np.dtype(img_raw[0, 0]), np.dtype(img_denoise[0, 0]))

    # -------------------------------------------------------------------------
    # print PSNR metric for each case
    # -------------------------------------------------------------------------

    psnr = peak_signal_noise_ratio(img_raw, img_denoise)

    return img_denoise, psnr


def denoise_img(all_img, iexp):
    """
    Denoise PEEM images.

    Parameters
    ----------
    all_img : numpy array
        PEEM Images
        Shape = nimages * npixels_x * npixels_y for XAS
        Shape = nimages * npixels_x * npixels_y * 2 polarizations for XMC(L)D
    iexp : string
        Flag for experiment type

    Returns
    -------
    all_img_den : numpy array
        Denoised PEEM images
    """
    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    start = time.time()

    # -------------------------------------------------------------------------
    # run checks and loop to denoise images
    # -------------------------------------------------------------------------

    shape = np.shape(all_img)
    nimages = shape[0]
    all_img_den = all_img.copy()

    # choose type of algorithm for non-local denoising
    ialgo = 3  # fast algorithm

    all_psnr = []

    if iexp == 'xas':
        for i in range(nimages):
            all_img_den[i, :, :], psnr = denoise(all_img[i, :, :], ialgo)
            all_psnr.append(psnr)
            msg = "PSNR = {0:8.3f} for image {1:4d} of {2:4d}"
            print(msg.format(psnr, i+1, nimages))

    elif iexp == 'xmcd':
        for i in range(nimages/2):
            # xmcd (or xmld) image with minus polarization
            all_img_den[i, :, :, 0], psnr_minus = \
                denoise(all_img[i, :, :, 0], ialgo)
            # xmcd (or xmld) image with plus polarization
            all_img_den[i, :, :, 1], psnr_plus = \
                denoise(all_img[i, :, :, 1], ialgo)
            all_psnr.append([psnr_minus, psnr_plus])
            msg = 'Images {0:4d} (+) and (-): PSNR = {1:8.3f} {2:8.3f}'
            msg += 'of {3:4d}'
            print(msg.format(i, psnr_plus, psnr_minus, nimages/2))

    all_psnr = np.array(all_psnr)

    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    end = time.time()

    print("Execution time for denoising (s) = {0:8.3f}".format(end - start))

    return all_img_den, all_psnr

# -----------------------------------------------------------------------------
# normalize images
# -----------------------------------------------------------------------------


def normalize_img(all_img, norm_img, iexp):
    """
    Normalize PEEM images.

    Parameters
    ----------
    all_img : numpy array
        PEEM Images
        Shape = nimages * npixels_x * npixels_y for XAS
        Shape = nimages * npixels_x * npixels_y * 2 polarizations for XMC(L)D
    norm_img : numpy array
        Normalization image
    iexp : string
        Flag for experiment type

    Returns
    -------
    all_img_norm : numpy array
        Normalized PEEM images
    """
    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    start = time.time()

    # -------------------------------------------------------------------------
    # run checks and loop to normalize images
    # -------------------------------------------------------------------------

    shape = np.shape(all_img)
    nimages = shape[0]
    all_img_norm = all_img.copy().astype("uint16")
    norm_img_shape = np.shape(norm_img[0, :, :])

    if iexp == 'xas':
        img_shape = np.shape(all_img[0, :, :])

        if img_shape != norm_img_shape:
            msg = 'XAS {0} and Normalization {1} Images have'
            msg += 'different size!'
            raise TypeError(msg.format(img_shape, norm_img_shape))
        else:
            for i in range(nimages):
                all_img_norm[i, :, :] = np.divide(all_img[i, :, :], norm_img)*1023
    elif iexp == 'xmcd':
        img_shape = np.shape(all_img[0, :, :, 0])
        if img_shape != norm_img_shape:
            msg = 'XMC(L)D {0} and Normalization {1} Images have'
            msg += 'different size!'
            raise TypeError(msg.format(img_shape, norm_img_shape))
        else:
            for i in range(nimages/2):
                # xmcd (or xmld) image with minus polarization
                all_img_norm[i, :, :, 0] = \
                    np.divide(all_img[i, :, :, 0], norm_img)
                # xmcd (or xmld) image with plus polarization
                all_img_norm[i, :, :, 1] = \
                    np.divide(all_img[i, :, :, 1], norm_img)

    # -------------------------------------------------------------------------
    # record execution time
    # -------------------------------------------------------------------------

    end = time.time()

    print("Execution time for normalizing (s) = {0:8.3f}".format(end - start))

    return all_img_norm


# -----------------------------------------------------------------------------
# plot images
# -----------------------------------------------------------------------------


def show_images(all_img, iexp):
    """
    Plot PEEM images side by side for XMC(L)D (2 images) or XAS (1 image).

    Parameters
    ----------
    all_img : numpy array
        PEEM Images
        Shape = nimages * npixels_x * npixels_y for XAS
        Shape = nimages * npixels_x * npixels_y * 2 polarizations for XMC(L)D
    iexp : string
        Flag for experiment type

    Returns
    -------
    int
        DESCRIPTION.

    """
    # -------------------------------------------------------------------------
    # retrieve the number of images
    # -------------------------------------------------------------------------

    img_shape = np.shape(all_img)
    nfiles = img_shape[0]

    # -------------------------------------------------------------------------
    # plot images
    # -------------------------------------------------------------------------

    if iexp == 'xmcd':
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

        for i1 in range(0, nfiles):
            image1 = all_img[i1, :, :, 0]
            image2 = all_img[i1, :, :, 1]
            images = [image1, image2]

            # ax.set_title(i1, fontsize=10)
            for j in range(2):
                ax[j].imshow(images[j], cmap='gray')

            # fig.tight_layout()
            plt.title('XMC(L)D images number {0:4d}'.format(i1), fontsize=10)
            plt.imshow(images, cmap=plt.cm.gray)
            plt.show()

    elif iexp == 'xas':  # this could refer to XPS or LEEM
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 6))

        for i1 in range(0, nfiles):

            # ax.set_title('XAS image number {0:6d}'.format(i1), fontsize=10)
            # ax.imshow(image1, cmap='gray')
            image1 = all_img[i1, :, :]
            fig.tight_layout()
            plt.title('XAS image number {0:4d}'.format(i1), fontsize=10)
            plt.imshow(image1, cmap=plt.cm.gray)
            plt.show()
            # print(i1)

    return 0


# -----------------------------------------------------------------------------
# Save images in an HDF5 file
# -----------------------------------------------------------------------------


def save_hdf5_img(all_img_den, all_img_raw, norm_img, iexp, file_path_nxs,
                  global_params):
    """
    Save images in an HDF5 file

    Parameters
    ----------
    all_img : numpy array
        Denoised PEEM Images
    all_img_raw : numpy array
        Raw PEEM Images
    norm_img : numpy array
        Normalization image
    iexp : string
        Flag for experiment type
    file_path_nxs : string
        Full path to the NXmpes_file to be created with images and metadata
    global_params : dictionary
        Global parameters

    Returns
    -------
    None

    """
    # -------------------------------------------------------------------------
    # delete existing NXfile
    # -------------------------------------------------------------------------

    if os.path.exists(file_path_nxs) is True:
        os.remove(file_path_nxs)

    # -------------------------------------------------------------------------
    # declare NXroot object
    # -------------------------------------------------------------------------

    root = NXroot()

    # write general information for this beamline
    root['entry'] = NXentry()
    root['entry/bl'] = 'bl24'

    # declare NXdata for processed data
    root['entry/data'] = NXdata()

    # declare NXinstrument for raw data under NXdetector
    root['entry/instrument'] = NXinstrument()
    root['entry/instrument/detector'] = NXdetector()

    # -------------------------------------------------------------------------
    # write raw images
    # -------------------------------------------------------------------------

    if iexp == 'xas':
        inst_entry = 'entry/instrument/detector/images'
        root[inst_entry] = all_img_raw
        root['entry/data/images'] = inst_entry

    elif iexp == 'xmcd':
        inst_entry_plus = 'entry/instrument/detector/images_plus'
        inst_entry_minus = 'entry/instrument/detector/images_minus'
        root[inst_entry_plus] = all_img_raw[:, :, :, 1]
        root[inst_entry_minus] = all_img_raw[:, :, :, 0]
        root['entry/data/images_plus'] = inst_entry_plus
        root['entry/data/images_minus'] = inst_entry_minus

    # -------------------------------------------------------------------------
    # write denoised images
    # -------------------------------------------------------------------------

    if global_params['denoise'] is True:
        if iexp == 'xas':
            root['entry/data/denoised_images'] = all_img_den
        elif iexp == 'xmcd':
            root['entry/data/denoised_images_plus'] = all_img_raw[:, :, :, 1]
            root['entry/data/denoised_images_minus'] = all_img_raw[:, :, :, 0]

    # -------------------------------------------------------------------------
    # write denoised images
    # -------------------------------------------------------------------------

    if global_params['normalize'] is True:
        root['entry/data/normalization_image'] = norm_img

    # -------------------------------------------------------------------------
    # write all metadata and data to HDF5 file
    # -------------------------------------------------------------------------

    # print(root.tree)
    root.save(file_path_nxs)
    print('Data written in HDF5  file:\n{0:s}'.format(file_path_nxs))

    return 0

# -----------------------------------------------------------------------------
# get general parameters
# -----------------------------------------------------------------------------


def main():
    workdir = '/home/fsaiz/work/beamlines/bl24/projects/cycle2023-II/2023027537-svelez/DATA/20231126/068_Cu_962'
    # workdir = '/home/fsaiz/work/beamlines/bl24/projects/cycle2023-II/2023027537-svelez/DATA/20231126/002_XAS_Cu_CN'

    if os.path.exists(workdir) is False:
        raise TypeError("Path {0:s} does not exist".format(workdir))

    return workdir

# -----------------------------------------------------------------------------
# call extract_uview function
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    # call general parameters in the main function to restrict their scope
    workdir = main()

    # read images and retrieve them as numpy arrays
    fh, ih, fileContent, fh_vars_dict, fh_vars_list, all_img, iexp = \
        read_uview(workdir)

    # create additional arrays to navigate throught them in Spyder
    # as 3D matrices
    if iexp == 'xmcd':
        img_plus = all_img[:, :, :, 1]
        img_minus = all_img[:, :, :, 0]
