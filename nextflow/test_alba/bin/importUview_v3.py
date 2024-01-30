#! /usr/bin/env python

# -*- coding: utf-8 -*-
"""
Copyright 2016 Dr. Helder Marchetto.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"dat" files from Uview contain a file header and each image has its own
image header. This version only deals with single images.
"""

# -------------------------------------------------------------------------
# import packages
# -------------------------------------------------------------------------

import struct
import numpy as np
# import matplotlib.pyplot as plt  # only necessary to display images in python

# "dat" files from Uview contain a file header and each image has its own
# image header.
# This version only deals with single images.

# class that reads the file header

# -------------------------------------------------------------------------
# class definitions
# -------------------------------------------------------------------------


class fileHeader():
    """Define a class for file header of Elmitec files."""

    def __init__(self, fc, verbose=False):

        # must supply the file contents (fc). These are read with the open
        # command in 'rb' mode

        self.UK_id = "".join(map(chr, fc[0:fc.index(0)]))
        self.UK_size = int.from_bytes(fc[20:22], byteorder='little')
        self.UK_version = int.from_bytes(fc[22:24], byteorder='little')
        self.UK_bitsPerPixel = int.from_bytes(fc[24:26], byteorder='little')

        if self.UK_version >= 8:
            self.UK_cameraBitsPerPixel = int.from_bytes(
                fc[26:28], byteorder='little')
            self.MCPDiameterInPixels = int.from_bytes(
                fc[28:30], byteorder='little')
            self.hBinning = int.from_bytes(fc[30:31], byteorder='little')
            self.vBinning = int.from_bytes(fc[31:32], byteorder='little')
        else:
            voidNr = int(0)
            self.UK_cameraBitsPerPixel = voidNr
            self.MCPDiameterInPixels = voidNr
            self.hBinning = voidNr
            self.vBinning = voidNr

        if self.UK_version >= 2:
            self.imageWidth = int.from_bytes(fc[40:42], byteorder='little')
            self.imageHeight = int.from_bytes(fc[42:44], byteorder='little')
            self.nrImages = int.from_bytes(fc[44:46], byteorder='little')
        else:
            voidNr = int(0)
            self.imageWidth = voidNr
            self.imageHeight = voidNr
            self.nrImages = voidNr

        if self.UK_version >= 7:
            self.attachedRecipeSize = int.from_bytes(
                fc[46:48], byteorder='little')
        else:
            self.attachedRecipeSize = int(0)

        self.hasRecipe = self.attachedRecipeSize > 0
        self.fixedRecipeSize = 128

        if self.hasRecipe:
            self.headerSize = 104+128
        else:
            self.headerSize = 104

        if verbose:
            print('headerSize = %i' % self.headerSize)
            print('UK_id = '+self.UK_id)
            print('UK_size = '+str(self.UK_size))
            print('UK_version = '+str(self.UK_version))
            print('UK_bitsPerPixel = '+str(self.UK_bitsPerPixel))
            print('UK_cameraBitsPerPixel = '+str(self.UK_cameraBitsPerPixel))
            print('MCPDiameterInPixels = '+str(self.MCPDiameterInPixels))
            print('hBinning = '+str(self.hBinning))
            print('vBinning = '+str(self.vBinning))
            print('imageWidth = '+str(self.imageWidth))
            print('imageHeight = '+str(self.imageHeight))
            print('nrImages = '+str(self.nrImages))
            print('attachedRecipeSize = '+str(self.attachedRecipeSize))
            print('hasRecipe = '+str(self.hasRecipe))

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------


class imageHeader():
    """Define a class for Elmitec image headers."""

    def __init__(self, fc, fh, verbose=False):
        fp = fh.headerSize  # file pointer
        self.imageHeadersize = int.from_bytes(
            fc[fp:fp + 2], byteorder='little')
        self.version = int.from_bytes(fc[fp + 2:fp + 4], byteorder='little')
        self.colorScaleLow = int.from_bytes(
            fc[fp + 4:fp + 6], byteorder='little')
        self.colorScaleHigh = int.from_bytes(
            fc[fp + 6:fp + 8], byteorder='little')
        self.imageTime = int.from_bytes(fc[fp + 8:fp+16], byteorder='little')
        self.maskXShift = int.from_bytes(fc[fp+16:fp+18], byteorder='little')
        self.maskYShift = int.from_bytes(fc[fp+18:fp+20], byteorder='little')
        self.rotateMask = int.from_bytes(
            fc[fp+20:fp+22], byteorder='little', signed=False)
        self.attachedMarkupSize = int.from_bytes(
            fc[fp+22:fp+24], byteorder='little')
        self.hasAttachedMarkup = self.attachedMarkupSize != 0

        if self.hasAttachedMarkup:
            self.attachedMarkupSize = 128*((self.attachedMarkupSize//128)+1)

        self.spin = int.from_bytes(fc[fp+24:fp+26], byteorder='little')
        self.LEEMDataVersion = int.from_bytes(
            fc[fp+26:fp+28], byteorder='little')
        fp = fp+28

        if self.version > 5:
            self.LEEMData = struct.unpack('240c', fc[fp:fp+240])
            fp = fp+240
            self.appliedProcessing = fc[fp]
            self.grayAdjustZone = fc[fp+1]
            self.backgroundvalue = int.from_bytes(
                fc[fp+2:fp+4], byteorder='little', signed=False)
            self.desiredRendering = fc[fp+4]
            self.desired_rotation_fraction = fc[fp+5]
            self.rendering_argShort = int.from_bytes(
                fc[fp+6:fp+8], byteorder='little')
            self.rendering_argFloat = struct.unpack('f', fc[fp+8:fp+12])[0]
            self.desired_rotation = int.from_bytes(
                fc[fp+12:fp+14], byteorder='little')
            self.rotaion_offset = int.from_bytes(
                fc[fp+14:fp+16], byteorder='little')
            # spare 4
        else:
            voidNr = int(0)
            self.LEEMData = struct.unpack('240c', '\x00'*240)
            self.appliedProcessing = b''
            self.grayAdjustZone = b''
            self.backgroundvalue = voidNr
            self.desiredRendering = b''
            # spare 1
            self.rendering_argShort = voidNr
            self.rendering_argFloat = 0.0
            self.desired_rotation = voidNr
            self.rotaion_offset = voidNr

        if verbose:
            print('imageHeadersize = '+str(self.imageHeadersize))
            print('version = '+str(self.version))
            print('colorScaleLow = '+str(self.colorScaleLow))
            print('colorScaleHigh = '+str(self.colorScaleHigh))
            print('imageTime = '+str(self.imageTime))
            print('maskXShift = '+str(self.maskXShift))
            print('maskYShift = '+str(self.maskYShift))
            print('rotateMask = '+str(self.rotateMask))
            print('attachedMarkupSize = '+str(self.attachedMarkupSize))
            print('hasAttachedMarkup = '+str(self.hasAttachedMarkup))
            print('spin = '+str(self.spin))
            print('LEEMDataVersion = '+str(self.LEEMDataVersion))

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------


def readUview(fc, fh, ih):
    """Read Uview Elmitec images."""
    totalHeaderSize = fh.headerSize + ih.imageHeadersize + \
        ih.attachedMarkupSize + ih.LEEMDataVersion

    return np.reshape(struct.unpack(str(fh.imageWidth*fh.imageHeight)+'H',
                                    fc[totalHeaderSize:]),
                      (fh.imageHeight, fh.imageWidth))


# -*- coding: utf-8 -*-
"""
Copyright 2016 Dr. Helder Marchetto
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
