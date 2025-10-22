"""
validationanalysis.py

ValidationAnalysis is a class including methods for map and map-model validation

Copyright [2013] EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the
"License"); you may not use this file except in
compliance with the License. You may obtain a copy of
the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.

"""

__author__ = 'Zhe Wang'
__email__ = 'zhe@ebi.ac.uk'
__date__ = '2018-07-24'

import numpy as np
import pandas as pd
from numpy.fft import fftshift, fftn
from PIL import Image
import cv2
from scipy.interpolate import RegularGridInterpolator
from scipy import ndimage
from collections import OrderedDict
from math import floor, ceil, log10, pi
import json
import codecs
import matplotlib as mpl
import bisect
import math
import traceback
import xml.etree.ElementTree as ET
import gc

mpl.use('Agg')
import matplotlib.pyplot as plt
import os, timeit, sys, glob, subprocess
from six import iteritems
# from distutils.spawn import find_executable
import re
import logging
import sys
import mrcfile
from memory_profiler import profile
from Bio.PDB import PDBParser as orgPDBParser
from Bio.PDB import MMCIFParser
from Bio.PDB.mmcifio import MMCIFIO
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from scipy.fftpack import fftn, fftshift
from va.metrics.strudel import run_strudel
# from va.metrics.emda_mmcc import run_realmmcc
from va.metrics.emringer import run_emringer
from va.metrics.threedfsc import run_threedfsc
from va.metrics.smoc import run_smoc
from va.metrics.phenix_cc import *
from va.metrics.phenix_mm import *
from va.metrics.resmap import *
from va.metrics.bars import *
from va.metrics.phaserandomization import *
from va.utils.stars import *
from va.utils.misc import *
from va.utils.log_utils import *
from va.metrics.contour_level_predicator import *
from va.metrics.projections import *
from va.metrics.residue_locres import *
from va.utils.Checker import *
from va.utils.ChimeraxViews import *
from va.metrics.qscore import *
from va.metrics.inclusion import *
from va.metrics.connected_percentage import *
import va

try:
    from PATHS import MAP_SERVER_PATH
    from PATHS import PROSHADEPATH
    from PATHS import MESHMAKERPATH
    from PATHS import CHIMERA
    from PATHS import OCHIMERA
    from PATHS import LIB_STRUDEL_ROOT
    from PATHS import RESMAP
except ImportError:
    MAP_SERVER_PATH = None
    PROSHADEPATH = None
    CHIMERA = None
    MESHMAKERPATH = None
    OCHIMERA = None
    LIB_STRUDEL_ROOT = None
    RESMAP = None

try:
    import vtk
except ImportError:
    print('ChimeraX will be used to produce for the surface view.')
RESIDUE_DENSITY = 0.907


##############################

# def pssum(i, dist, indiaxis, indiaxist, psmap):
#     if i != len(indiaxis) - 1:
#         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
#
#         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
#         return psum


# test 3

def pssum(a, indiaxis, indiaxist, shared_array):
    res = []
    for i in a:
        if i != len(indiaxis) - 1:
            indices = np.argwhere((shared_array > indiaxist[i]) & (shared_array <= indiaxist[i + 1]))
            if i == 0 or i == 1:
                print(np.ndarray.tolist(indices))
                print(len(indices[0]))
                print('indiaxist[{}]={}, indiaxist[{}+1]'.format(i, indiaxist[i], indiaxist[i+1] ))
            res.append(indices)
    return res


# def pcal(a, indiaxis, dist, indiaxist):
#     b = []
#     for i in a:
#         b.append(pssum(i, indiaxis, dist, indiaxist))
#     return b

# def pssum(lenind, psmap):
#     psum = log10(psmap.sum() / len(lenind))
#     return psum
#
# def pcal(a, allindices, allpsmap):
#     b = []
#     print('indside pcal')
#     print(len(allindices))
#     for i in a:
#
#         lenind = allindices[i]
#         psmap = allpsmap[i]
#
#         b.append(pssum(lenind, psmap))
#     return b




############################

class ValidationAnalysis:
    """
    Validation Analysis class

    """

    def __init__(self, map=None, model=None, pid=None, halfeven=None, halfodd=None, rawmap=None, contourlevel=None,
                 emdid=None, workdir=None, met=None, resolution=None, fscfile=None, masks=None, modelsmaps=None,
                 onlybar=False, strudellib=None, threedfscdir=None, platform=None, queue=None,
                 update_resolution_bin_file=None):
        """

            Constructor function of ValidationAnalysis class

        :param map: Map instance from TEMPy package
        :param model: Model instance from TEMPy CIF file parser
        :param pid: structure id
        :param halfmap: Map instance for FSC calculation
        :param contourlevel: Float value which recommended by the author or EMDB
        """

        self.models = model
        self.map = map
        self.mapname = os.path.basename(map.fullname)
        self.pid = pid
        self.emdid = emdid
        self.hmeven = halfeven
        self.hmodd = halfodd
        self.rawmap = rawmap
        self.met = met
        self.resolution = resolution
        self.fscfile = fscfile
        self.allmasks = masks
        self.modelsmaps = modelsmaps
        self.onlybar = onlybar
        self.strudellib = strudellib
        self.threedfscdir = threedfscdir
        self.platform = platform
        if contourlevel is not None:
            self.cl = float(contourlevel)
        else:
            self.cl = contourlevel
        if self.emdid:
            digits = [i for i in str(self.emdid)]
            if len(digits) == 4:
                subdir = '{}/{}/'.format(digits[0] + digits[1], self.emdid)
                self.workdir = MAP_SERVER_PATH + subdir + 'va/'
            elif len(digits) == 5:
                subdir = '{}/{}/{}/'.format(digits[0] + digits[1], digits[2], self.emdid)
                self.workdir = MAP_SERVER_PATH + subdir + 'va/'
            else:
                pass
            self.queue = queue
        else:
            self.workdir = workdir
        self.check_dir = create_directory(f'{self.workdir}/checks/')
        self.update_resolution_bin_file = update_resolution_bin_file
        self.get_resolution()
        self.relion_mask = None
        self.masked_rawmap = None
        if self.rawmap:
            self.relion_mask = self.get_relion_mask()
        # make a symbolic link for relion_mask in the va folder
        if self.relion_mask:
            mask_name = os.path.basename(self.relion_mask)
            link_name = f'{self.workdir}/{mask_name}'
            create_symbolic_link(self.relion_mask, link_name)
            self.relion_mask = link_name
        # The read masked raw map here is only used in line 455 for produce the masked raw map glow image
        if self.rawmap and self.relion_mask:
            maskedrawmap = MapProcessor.mask_map(self.rawmap._iostream.name, self.relion_mask)
            self.masked_rawmap = mrcfile.mmap(maskedrawmap, mode='r+')
            self.masked_rawmap.fullname = maskedrawmap
        else:
            print('There is no raw map or relion mask to produce the masked raw map !!!')


    def get_resolution(self):
        """
            Get the input resolution to the output JSON file
        :return: JSON file name
        """

        if self.resolution:
            res_dict = {'resolution': {'value': self.resolution}}
            output_json_name = f'{self.workdir}{self.mapname}_resolution.json'
            out_json(res_dict, output_json_name)
        else:
            print('There is no resolution saved !!!')

    def get_lowpassed_map(self, rawmapname, resolution=None):
        """
            Get the lowpassed map from the map instance
        """
        res = float(resolution) if resolution is not None else float(self.resolution)
        low_pass = 15.0 if res < 8.0 else res * 2.0
        filtered_rawmap_name = f'{rawmapname}_lowpassed.mrc'
        try:
            rawmap_mrc = f'{rawmapname[:-3]}mrc'
            create_symbolic_link(rawmapname, rawmap_mrc)
            lowpassed_rawmap = MapProcessor.low_pass_filter_relion(rawmap_mrc, low_pass, filtered_rawmap_name)
            if MapProcessor.check_map_zeros(lowpassed_rawmap):
                raise RuntimeError(f'Lowpassed raw map {lowpassed_rawmap} contains only zeros.')
        except Exception as e:
            lowpassed_rawmap = MapProcessor.low_pass_filter_map(self.rawmap, low_pass, filtered_rawmap_name)
            print(f'Relion low-pass filter failed: {e}. Using own version.')
        if not MapProcessor.check_map_starts(filtered_rawmap_name, rawmapname):
            print('Relion mask does not have the same nstarts as the original map.')
            MapProcessor.update_map_starts(rawmapname, filtered_rawmap_name)
        print(f'Filtered raw map is {filtered_rawmap_name}.')

        return filtered_rawmap_name

    @profile_peak_memory()
    @execution_time('Relion masking')
    def get_relion_mask(self):
        """
            Get the relion mask from the map instance
        :return: relion mask
        """

        # create all Relion fsc and mask folder
        relion_fsc_dir, relion_mask_dir = create_relion_folders(self.workdir, self.mapname, 'fsc')

        try:
            if relion_fsc_dir and relion_mask_dir:
                # Calculate FSC and get the resolution of the map
                oddmap = self.hmodd._iostream.name
                evenmap = self.hmeven._iostream.name
                try:
                    relion_fsc(oddmap, evenmap, None, relion_fsc_dir)
                except:
                    print('Relion fsc calculation failed. Please check the input maps.')

                star_file_dir = f'{relion_fsc_dir}/fsc.star'
                star = GetStars(star_file_dir)
                nomask_resolution = star.final_resolution()
                # For cases where Relion resolution is too high, use the input resolution
                nomask_resolution = min(nomask_resolution, 15 * float(self.resolution))
                raw_map_name = find_rawmap_file(self.workdir)
                filtered_raw_map = self.get_lowpassed_map(f'{self.workdir}/{raw_map_name}', nomask_resolution)
                relion_mask_name = relion_mask(filtered_raw_map, relion_mask_dir, self.mapname)

                return relion_mask_name
            else:
                print('Relion fsc and mask directories could not be created.')
        except:
            sys.stderr.write('Relion mask could not be created.')
            return None

    # Glow LUT for color image
    def glowimage(self, im_gray):
        """Applies a glow color map using cv2.applyColorMap()"""

        # Create the LUT:
        lut = np.zeros((256, 1, 3), dtype=np.uint8)
        lut[:, 0, 2] = [0, 1, 1, 2, 2, 3, 4, 6, 8, 11, 13, 15, 18,
                        21, 23, 24, 27, 30, 31, 33, 36, 37, 40, 42, 45, 46,
                        49, 51, 53, 56, 58, 60, 62, 65, 68, 70, 72, 74, 78,
                        80, 82, 84, 86, 89, 91, 93, 96, 98, 100, 102, 104, 106,
                        108, 110, 113, 115, 117, 119, 122, 125, 127, 129, 132, 135, 135,
                        137, 140, 141, 142, 145, 148, 149, 152, 154, 156, 157, 158, 160,
                        162, 164, 166, 168, 170, 171, 173, 174, 176, 178, 179, 180, 182,
                        183, 185, 186, 189, 192, 193, 193, 194, 195, 195, 196, 198, 199,
                        201, 203, 204, 204, 205, 206, 207, 209, 211, 211, 211, 211, 213,
                        215, 216, 216, 216, 216, 218, 219, 219, 219, 220, 222, 223, 223,
                        223, 223, 224, 224, 226, 227, 227, 227, 227, 228, 229, 231, 231,
                        231, 231, 231, 231, 231, 232, 233, 234, 234, 234, 234, 234, 234,
                        235, 237, 238, 238, 238, 238, 238, 238, 238, 238, 239, 240, 242,
                        242, 242, 242, 242, 242, 242, 242, 242, 243, 245, 246, 246, 246,
                        246, 245, 245, 245, 245, 245, 245, 245, 247, 248, 249, 249, 249,
                        249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249,
                        249, 250, 252, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 0]

        lut[:, 0, 1] = [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2,
                        2, 2, 2, 2, 3, 3, 3, 3, 4, 5, 5, 5, 5,
                        6, 6, 6, 7, 7, 8, 9, 9, 9, 9, 10, 10, 11,
                        12, 13, 14, 14, 14, 14, 15, 16, 16, 17, 18, 19, 19,
                        19, 20, 21, 22, 23, 24, 24, 25, 27, 28, 28, 28, 29,
                        31, 32, 32, 33, 35, 36, 36, 37, 39, 40, 40, 41, 42,
                        43, 45, 46, 47, 48, 50, 51, 52, 54, 55, 56, 57, 59,
                        62, 63, 65, 66, 68, 70, 71, 73, 74, 75, 77, 79, 81,
                        83, 85, 87, 89, 92, 93, 96, 98, 99, 100, 103, 105, 107,
                        109, 111, 113, 116, 117, 119, 121, 123, 125, 126, 128, 130, 132,
                        135, 137, 139, 140, 142, 144, 145, 147, 148, 150, 152, 154, 156,
                        158, 160, 161, 162, 164, 166, 168, 171, 172, 172, 174, 176, 177,
                        179, 180, 182, 183, 185, 187, 188, 189, 191, 192, 192, 192, 196,
                        200, 201, 201, 202, 203, 204, 206, 208, 210, 212, 213, 213, 214,
                        215, 217, 218, 220, 221, 222, 223, 224, 225, 226, 226, 227, 228,
                        229, 231, 232, 233, 234, 235, 236, 237, 238, 239, 239, 239, 239,
                        241, 242, 243, 243, 243, 244, 245, 247, 247, 247, 247, 247, 247,
                        248, 249, 250, 251, 251, 251, 252, 252, 252, 252, 252, 252, 252,
                        252, 252, 252, 252, 252, 252, 253, 253, 0]

        lut[:, 0, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 4, 4,
                        4, 4, 4, 4, 3, 3, 3, 3, 4, 6, 6, 6, 6,
                        6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                        6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 7, 9, 10,
                        10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
                        10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
                        9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8,
                        8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 7, 7,
                        7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6,
                        6, 6, 6, 6, 7, 10, 12, 12, 12, 12, 12, 12, 13,
                        15, 17, 18, 18, 19, 20, 22, 23, 23, 24, 26, 27, 27,
                        28, 30, 32, 33, 34, 35, 37, 39, 40, 41, 43, 45, 46,
                        48, 50, 52, 54, 55, 57, 58, 61, 63, 65, 67, 70, 72,
                        73, 76, 79, 80, 83, 86, 88, 89, 92, 95, 96, 99, 102,
                        104, 107, 108, 110, 113, 116, 120, 121, 123, 125, 127, 129, 132,
                        135, 137, 140, 143, 146, 149, 150, 153, 155, 158, 160, 162, 165,
                        168, 171, 173, 175, 178, 180, 183, 186, 188, 191, 192, 195, 198,
                        201, 203, 206, 209, 210, 213, 215, 218, 221, 223, 225, 228, 231,
                        233, 236, 238, 241, 244, 246, 250, 252, 255]

        im_color = cv2.applyColorMap(im_gray, lut)
        return im_color

    def modredhot(self, im_gray):
        """

            Apply modified(use glow LUT first and last value to replace the original rh) red-hot LUT to the gray image
            channel 2- red; channel 1-green; channel 0 - blue
        :param im_gray:
        :return:
        """

        # Create the LUT:
        lut = np.zeros((256, 1, 3), dtype=np.uint8)
        lut[:, 0, 2] = [0, 0, 0, 0, 1, 1, 1, 1, 1, 4, 7, 10, 13,
                        16, 20, 23, 27, 30, 33, 36, 39, 42, 45, 48, 52, 55,
                        58, 61, 65, 68, 71, 74, 78, 81, 84, 87, 90, 93, 96,
                        99, 103, 106, 110, 113, 117, 120, 123, 126, 130, 133, 136, 139,
                        142, 145, 148, 151, 155, 158, 161, 164, 168, 171, 174, 177, 181,
                        184, 187, 190, 193, 196, 200, 203, 207, 210, 213, 216, 220, 223,
                        226, 229, 233, 236, 239, 242, 245, 247, 250, 252, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 0
                        ]

        lut[:, 0, 1] = [138, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 6, 9,
                        12, 16, 19, 22, 25, 29, 32, 35, 38, 42, 45, 48, 51,
                        55, 58, 61, 64, 68, 71, 74, 77, 81, 84, 87, 90, 94,
                        97, 100, 103, 106, 109, 112, 115, 119, 122, 126, 129, 133, 136,
                        139, 142, 145, 148, 151, 154, 158, 161, 164, 167, 171, 174, 177,
                        180, 184, 187, 190, 193, 197, 200, 203, 206, 209, 212, 216, 219,
                        223, 226, 229, 232, 236, 239, 242, 245, 249, 250, 252, 253, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 0]

        lut[:, 0, 0] = [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 4, 6,
                        9, 12, 15, 19, 22, 25, 28, 32, 35, 38, 41, 45, 48,
                        51, 54, 58, 61, 64, 67, 71, 74, 77, 80, 84, 87, 90,
                        93, 97, 100, 103, 106, 110, 113, 116, 119, 122, 125, 128, 131,
                        135, 138, 142, 145, 149, 152, 155, 158, 161, 164, 167, 170, 174,
                        177, 180, 183, 187, 190, 193, 196, 200, 203, 206, 209, 213, 216,
                        219, 222, 225, 228, 232, 235, 239, 242, 245, 248, 252, 252, 253,
                        254, 255, 255, 255, 255, 255, 255, 255, 255]

        # Apply color map using cv2.applyColorMap()
        im_color = cv2.applyColorMap(im_gray, lut)
        return im_color


    @profile_peak_memory()
    def new_projection(self, type=None):
        """
           Get all projections
        """
        start = timeit.default_timer()
        op = Projections(self.map, self.rawmap, self.workdir, self.platform)
        op.orthogonal_projections(self.map, self.workdir, type)
        if self.rawmap:
            op.orthogonal_projections(self.rawmap, self.workdir, type, 'rawmap_')
            # Calculate the glow image green ratio based on z direction glow image
            glow_std_image = f'{self.workdir}/{os.path.basename(self.rawmap.fullname)}_scaled_glow_zstd.jpeg'
            if os.path.isfile(glow_std_image):
                image_checker = ImageChecks(glow_std_image)
                image_checker.image_check()
            # Produce the masked raw map glow image and lowpassed rawmap for checking mask effect
            if self.masked_rawmap:
                op.orthogonal_projections(self.masked_rawmap, self.workdir, 'std', 'maskedrawmap_')
            if self.relion_mask:
                op.orthogonal_projections(self.relion_mask, self.workdir, 'projection', 'relionmask_')
            if os.path.isfile(f'{self.rawmap.fullname}_lowpassed.mrc'):
                op.orthogonal_projections(f'{self.rawmap.fullname}_lowpassed.mrc', self.workdir, 'std', 'std')
            # Above the masked raw map glow image and lowpassed rawmap for checking mask effect

        end = timeit.default_timer()
        print('All projections time is: %s' % (end - start))
        print('------------------------------------')

    def mapincheck(self, mapin, workdirin):

        import inspect
        from mrcfile.mrcfile import MrcFile

        frame = inspect.currentframe()
        func = inspect.getframeinfo(frame.f_back).function
        if mapin is not None:
            if (type(mapin) is str):
                if (os.path.isfile(mapin)):
                    # map = MapParser.readMRC(mapin)
                    map = mrcfile.mmap(mapin, mode='r')
                else:
                    print('Map does not exist.')
                    map = None
            # elif(isinstance(mapin, Map)):
            elif (isinstance(mapin, MrcFile)):
                map = mapin
            else:
                map = None
                print('Function:{} only accept a string of full map name or a TEMPy Map object as input.'.format(func))
        else:
            map = self.map

        if workdirin is not None:
            if (type(workdirin) is str):
                if (os.path.isdir(workdirin)):
                    workdir = workdirin
                else:
                    print('Output directory does not exist.')
                    workdir = None
            else:
                workdir = None
                print('Function:{} only accept a string as the directory parameter.'.format(func))
        else:
            workdir = self.workdir

        return map, workdir

    # @profile
    def surfaces(self):
        """

            Prouding all the surface related images here

        :return:
        """

        vtkpack, chimeraapp = self.surface_envcheck()
        if self.models is not None:
            sufcheck = [False if model.filename.endswith('.pdb') else True for model in self.models]
        else:
            sufcheck = [True]
        # Add if model is cif using chimera for now
        if self.cl is not None and self.met != 'tomo':
            if vtkpack and False in sufcheck:
                self.surfaceview()
            elif chimeraapp:
                self.surfaceview_chimera(chimeraapp)
                self.rawmapsurface_chimera(chimeraapp)
                try:
                    self.modelfitsurface(chimeraapp)
                except:
                    print('No model fit surface view for wwpdb platform.')
            else:
                sys.stderr.write('No proper VTK or Chimera can be used for producing surface view. Please check.\n')
                print('------------------------------------')
        else:
            print('No contour level, no surface view.')
            print('------------------------------------')

    # For mask views and central slice of masks
    @profile_peak_memory()
    def masks(self):
        """


        :return:
        """

        vtkpack, chimeraapp = self.surface_envcheck()
        if self.allmasks:
            # When masks data(not segmentation) are ready, switch this on to produce proper central slice of masks
            self.centralMasks()
            if chimeraapp:
                self.maskviewchimera(chimeraapp)
            elif vtkpack:
                self.maskviews()
            else:
                # print('No proper VTK or Chimera can be used for producing mask view. Please check.', file=sys.stderr)
                sys.stderr.write('No proper VTK or ChimeraX can be used for producing mask view. Please check.\n')
                print('------------------------------------')
        else:
            print('No masks for this entry!')
            print('------------------------------------')


    def maskviewchimera(self, chimeraapp):
        """
            Generate mask views by using chimera method
        :return:
        """

        start = timeit.default_timer()
        errlist = []
        maskresults = [item for item in self.allmasks if os.path.isfile(self.workdir + os.path.basename(item))]
        masksdict = dict()
        finaldict = dict()
        if not maskresults:
            print('There is no masks offered for this map.')
        else:
            # for mask in maskresults:
            for mask in self.allmasks:
                try:
                    masksdict[os.path.basename(mask)] = self.maskviews_chimera(mask, chimeraapp)
                except:
                    err = 'Saving mask {} views error: {}.'.format(mask, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
            if errlist:
                masksdict['err'] = {'mask_view_err': errlist}
            finaldict['masks'] = masksdict
            try:
                with codecs.open(self.workdir + self.mapname + '_mapmaskview.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('Masks view by using ChimeraX method.')
            except:
                sys.stderr.write('Saving masks to json error: {}.\n'.format(sys.exc_info()[1]))

        end = timeit.default_timer()
        print('Maskview time: {}'.format(end-start))
        print('------------------------------------')
        return None

    def maskviews_chimera(self, mask, chimeraapp):
        """
            Generate mask view by using ChimeraX
            Todo: a contour level needed here for the mask

        :return:
        """

        # mapname = self.workdir + self.mapname + '.map'
        errlist = []
        start = timeit.default_timer()
        mapname = self.workdir + self.mapname
        maskname = mask.split('/')[-1]
        reg_maskname = re.search('emd_.*_msk.map', maskname)
        if reg_maskname:
            out_maskname = '{}_1.map'.format(maskname[:-4])
            print('!! Mask name is old !!')
        else:
            out_maskname = maskname
        maskfn = '{}_{}'.format(maskname, self.mapname)
        chimeracmd = maskfn + '_chimera.cxc'
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        mskcl = self.allmasks[mask]

        # if (mskcl and self.cl) is not None:
        met_check = False
        if self.met == 'tomo':
            if mskcl is not None:
                met_check = True
        elif self.met == 'sp' or self.met == 'heli' or self.met == 'subtomo' or self.met == '2dcrys':
            if (mskcl and self.cl) is not None:
                met_check = True
        if met_check and os.path.isfile(self.workdir + str(maskname)):
            # In case there is no mask contour level, here we use 1.0 instead
            contour = "level " + str(mskcl) if mskcl is not None else 1.0
            with open(self.workdir + chimeracmd, 'w') as f:
                if self.met != 'tomo':
                    f.write(
                        'open ' + str(mapname) + ' format ccp4' + '\n'
                        'open ' + self.workdir + str(maskname) + ' format ccp4' + '\n'
                        "volume #1 style surface expandSinglePlane True " + '\n'
                        "volume #2 style surface expandSinglePlane True " + '\n'
                        "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                        "volume #2 color blue step 1 " + contour + '\n'
                        "volume #1 transparency 0.65" + '\n'
                    )
                else:
                    f.write(
                        'open ' + self.workdir + str(maskname) + ' format ccp4' +'\n'
                        "volume #1 style surface expandSinglePlane True " + '\n'
                        "volume #1 color blue step 1 " + contour + '\n'
                    )
                f.write(
                    # 'open ' + str(mask) + ' format ccp4' +'\n'
                    # "volume #1 style surface expandSinglePlane True " + '\n'
                    # "volume #2 style surface expandSinglePlane True " + '\n'
                    # "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                    # "volume #2 color blue step 1 " + contour + '\n'
                    # "volume #1 transparency 0.65" + '\n'
                    "set bgColor light gray" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_" + str(out_maskname) + "_zmaskview.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    "turn x -90" + '\n'
                    "turn y -90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_" + str(out_maskname) + "_xmaskview.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    "view orient" + '\n'
                    "turn x 90" + '\n'
                    "turn z 90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_" + str(out_maskname) + "_ymaskview.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    "close all" + "\n"
                    "exit"
                )
            try:
                if not bindisplay:
                    subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                            cwd=self.workdir, shell=True)
                else:
                    subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir, shell=True)
            except subprocess.CalledProcessError as suberr:
                err = 'Mask view by ChimeraX error: {}'.format(suberr)
                errlist.append(err)
                sys.stderr.write(err + '\n')

            end = timeit.default_timer()
            print('Primary map and mask view time: %s' % (end - start))
            print('------------------------------------')

            self.scale_maskimg()

            onemaskdict = dict()
            for dim in ['x', 'y', 'z']:
                cur_maskview = '{}_{}_{}maskview.jpeg'.format(mapname, out_maskname, dim)
                onemaskdict[dim] = '{}_{}_scaled_{}maskview.jpeg'.format(os.path.basename(mapname), out_maskname, dim) if os.path.isfile(cur_maskview) else None

            return onemaskdict
        else:
            print('REMINDER: Missing contour level (primary map or mask or both) or mask file is not exist.')

    def readmasks(self):
        """

            With the masks and read them into the TEMPy object

        :return: readmaks which is a dict(fullmaskname:
        """

        from va.preparation import PreParation as vaprep

        readfun = vaprep()
        readmasks = {}
        errlist = []
        for key in self.allmasks:
            try:
                # readmasks[key] = readfun.frommrc_totempy(key)
                readmasks[key] = readfun.new_frommrc_totempy(key)
            except:
                err = 'Something is wrong with reading mask: {}, {}'.format(key, sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write('There is something wrong with reading map {}\n'.format(key))

        return readmasks, errlist

    def centralMasks(self):
        """

            Produce the central slice of each masks in x, y, z directions

        :return: directory which contatins all the slices information

        """

        start = timeit.default_timer()
        errlist = []
        allmaskdict = dict()

        readmasks, errfromload = self.readmasks()
        if errfromload:
            errlist.append(errfromload)

        for (key, map) in iteritems(readmasks):
            mapname = os.path.basename(map.fullname)
            map_zsize = map.header.nz
            map_ysize = map.header.ny
            map_xsize = map.header.nx
            xmid = int(float(map_xsize) / 2)
            ymid = int(float(map_ysize) / 2)
            zmid = int(float(map_zsize) / 2)

            # xcentral = map.fullMap[:, :, xmid]
            xcentral = map.data[:, :, xmid]
            xdenom = (xcentral.max() - xcentral.min()) if xcentral.max() != xcentral.min() else 1
            xrescaled = (((xcentral - xcentral.min()) * 255.0) / xdenom).astype('uint8')
            xflipped = np.flipud(xrescaled)
            ximg = Image.fromarray(xflipped)
            try:
                ximg.save(self.workdir + mapname + '_xmaskcentral_slice.jpeg')
            except IOError as ioerr:
                xerr = 'Saving original x central slice of mask err:{}'.format(ioerr)
                errlist.append(xerr)
                sys.stderr.write(xerr + '\n')

            width, height = ximg.size
            xscalename = self.workdir + mapname + '_scaled_xmaskcentral_slice.jpeg'

            try:
                if width > 300 and height > 300:
                    if width >= height:
                        largerscaler = 300. / width
                        newheight = int(ceil(largerscaler * height))
                        imx = Image.fromarray(xflipped).resize((300, newheight), Image.Resampling.LANCZOS)
                        imx.save(xscalename)
                    else:
                        largerscaler = 300. / height
                        newwidth = int(ceil(largerscaler * width))
                        imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.Resampling.LANCZOS)
                        imx.save(xscalename)
                    # imx = Image.fromarray(xflipped).resize((300,300))
                    # imx.save(xscalename)
                else:
                    if width >= height:
                        scaler = 300. / width
                        newheight = int(ceil(scaler * height))
                        imx = Image.fromarray(xflipped).resize((300, newheight), Image.Resampling.LANCZOS)
                        imx.save(xscalename)
                    else:
                        scaler = 300. / height
                        newwidth = int(ceil(scaler * width))
                        imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.Resampling.LANCZOS)
                        imx.save(xscalename)
            except:
                xerr = 'Saving scaled x central slice of mask err:{}'.format(sys.exc_info()[1])
                errlist.append(xerr)
                sys.stderr.write(xerr + '\n')

            # ycentral = map.fullMap[:, ymid, :]
            ycentral = map.data[:, ymid, :]
            ydenom = (ycentral.max() - ycentral.min()) if ycentral.max() != ycentral.min() else 1
            yrescaled = (((ycentral - ycentral.min()) * 255.0) / ydenom).astype('uint8')
            yrotate = np.rot90(yrescaled)
            yimg = Image.fromarray(yrotate)
            try:
                yimg.save(self.workdir + mapname + '_ymaskcentral_slice.jpeg')
            except IOError as ioerr:
                yerr = 'Saving original y central slice of mask err:{}'.format(ioerr)
                errlist.append(yerr)
                sys.stderr.write(yerr + '\n')

            width, height = yimg.size
            yscalename = self.workdir + mapname + '_scaled_ymaskcentral_slice.jpeg'
            try:
                if width > 300 and height > 300:
                    if width >= height:
                        largerscaler = 300. / width
                        newheight = int(ceil(largerscaler * height))
                        imy = Image.fromarray(yrotate).resize((300, newheight), Image.Resampling.LANCZOS)
                        imy.save(yscalename)
                    else:
                        largerscaler = 300. / height
                        newwidth = int(ceil(largerscaler * width))
                        imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.Resampling.LANCZOS)
                        imy.save(yscalename)
                    # imy = Image.fromarray(yrotate).resize((300, 300))
                    # imy.save(yscalename)
                else:
                    if width >= height:
                        scaler = 300. / width
                        newheight = int(ceil(scaler * height))
                        imy = Image.fromarray(yrotate).resize((300, newheight), Image.Resampling.LANCZOS)
                        imy.save(yscalename)
                    else:
                        scaler = 300. / height
                        newwidth = int(ceil(scaler * width))
                        imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.Resampling.LANCZOS)
                        imy.save(yscalename)
            except:
                yerr = 'Saving scaled y central slice of mask err:{}'.format(sys.exc_info()[1])
                errlist.append(yerr)
                sys.stderr.write(yerr + '\n')

            # zcentral = map.fullMap[zmid, :, :]
            zcentral = map.data[zmid, :, :]
            zdenom = (zcentral.max() - zcentral.min()) if zcentral.max() != zcentral.min() else 1
            zrescaled = (((zcentral - zcentral.min()) * 255.0) / zdenom).astype('uint8')
            zflipped = np.flipud(zrescaled)
            zimg = Image.fromarray(zflipped)
            try:
                zimg.save(self.workdir + mapname + '_zmaskcentral_slice.jpeg')
            except IOError as ioerr:
                zerr = 'Saving original z central slice of mask err:{}'.format(ioerr)
                errlist.append(zerr)
                sys.stderr.write(zerr + '\n')

            width, height = zimg.size
            zscalename = self.workdir + mapname + '_scaled_zmaskcentral_slice.jpeg'
            try:
                if width > 300 and height > 300:
                    if width >= height:
                        largerscaler = 300. / width
                        newheight = int(ceil(largerscaler * height))
                        imz = Image.fromarray(zflipped).resize((300, newheight), Image.Resampling.LANCZOS)
                        imz.save(zscalename)
                    else:
                        largerscaler = 300. / height
                        newwidth = int(ceil(largerscaler * width))
                        imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.Resampling.LANCZOS)
                        imz.save(zscalename)
                    # imz = Image.fromarray(zflipped).resize((300, 300))
                    # imz.save(zscalename)
                else:
                    if width >= height:
                        scaler = 300. / width
                        newheight = int(ceil(scaler * height))
                        imz = Image.fromarray(zflipped).resize((300, newheight), Image.Resampling.LANCZOS)
                        imz.save(zscalename)
                    else:
                        scaler = 300. / height
                        newwidth = int(ceil(scaler * width))
                        imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.Resampling.LANCZOS)
                        imz.save(zscalename)
            except:
                zerr = 'Saving original z scaled central slice of mask err:{}'.format(sys.exc_info()[1])
                errlist.append(zerr)
                sys.stderr.write(zerr + '\n')

            cslicejson = dict()
            cslicejson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
            cslicejson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
            cslicejson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

            allmaskdict[mapname] = cslicejson

        if errlist:
            allmaskdict['err'] = {'mask_central_slice_err': errlist}
        finaldict = {'mask_central_slice': allmaskdict}

        try:
            with codecs.open(self.workdir + self.mapname + '_maskcentralslice.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except IOError as ioerr:
            print('Saving masks central slices to json err: {}'.format(ioerr))

        end = timeit.default_timer()
        print('MaksCentralSlice time: %s' % (end - start))
        print('------------------------------------')

        return None

    # Rawmap surface view when two half maps are given
    def rawmapcl(self):
        """

            Calculate a corresponding 'recommended contour level' based on the recommended contour level
            (have tried matching the value scale which get worse result than this one)

        :return: A float which give the contour level
        """

        # numvox = len(self.map.fullMap[self.map.fullMap >= self.cl])
        numvox = len(self.map.data[self.map.data >= self.cl])
        rawmap = self.rawmap
        # rawdata = rawmap.fullMap.flatten()
        rawdata = rawmap.data.flatten()
        flatraw = sorted(rawdata)[::-1]
        rawcl = flatraw[numvox]

        return rawcl

    def findrawmap(self):

        if self.emdid:
            rawmapname = '{}emd_{}_rawmap.map'.format(self.workdir, self.emdid)
        else:
            oddname = os.path.basename(self.hmodd.fullname)
            evenname = os.path.basename(self.hmeven.fullname)
            rawmapname = '{}{}_{}_rawmap.map'.format(self.workdir, oddname, evenname)

        if self.hmodd is not None and self.hmeven is not None:
            if os.path.isfile(rawmapname):
                return rawmapname
            else:

                print('Base on the half maps, rawmap is not produced!!')
                return None
        else:
            return None

    def rawmapsurface_chimera(self, chimeraapp):
        """

            Generate rawmap surfaces if two half maps and rawmap and rawmap contour are there

        :param chimeraapp: binary value to check if ChimeraX is there properly
        :return: None
        """

        # rawmapre = '*_rawmap.map'
        # rawmapname = glob.glob(self.workdir + rawmapre)
        if self.hmodd is not None and self.hmeven is not None:
            rawmapname = self.findrawmap()
        else:
            rawmapname = None

        bindisplay = os.getenv('DISPLAY')

        try:
            rawmapcl = self.rawmapcl()
        except:
            rawmapcl = None
            print('Problem with raw map contour level calculation')

        if (self.hmodd is not None and self.hmeven is not None) and rawmapname and rawmapcl is not None:

            start = timeit.default_timer()
            errlist = []

            mapname = os.path.basename(rawmapname)
            locCHIMERA = chimeraapp
            # rawmap surface view alone
            rawmapchimeracmd = rawmapname + '_chimera.cxc'
            assemble = False
            with open(rawmapchimeracmd, 'w') as f:
                f.write(
                    # Chimera version
                    # 'open ccp4:' + str(mapname) + '\n'
                    # "volume #0 style surface expandSinglePlane True " + '\n'
                    # "volume #0 color #B8860B step 1 " + contour + '\n'
                    # "set projection orthographic" + '\n'
                    # "surftransp 50" + '\n'  # make the surface a little bit see-through
                    # "background solid light gray" + '\n'
                    # "copy file " + str(self.mapname) + "_zsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    # "turn x -90" + '\n'
                    # "center" + '\n'
                    # "copy file " + str(self.mapname) + "_xsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    # "turn z -90" + '\n'
                    # "center" + '\n'
                    # "copy file " + str(self.mapname) + "_ysurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    # "close all" + "\n"
                    # "stop"

                    # ChimeraX version
                    "open " + str(rawmapname) + " format ccp4" + '\n'
                    "volume #1 style surface expandSinglePlane True" + '\n'
                    # "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                    "volume #1 step 1 level " + str(rawmapcl) + '\n'
                    "set bgColor white" + '\n'
                    "lighting full \n"
                    "view cofr True \n"
                    "save " + str(mapname) + "_zsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    "turn x -90" + '\n'
                    "turn y -90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_xsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    "view orient" + '\n'
                    "turn x 90" + '\n'
                    "turn z 90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_ysurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                    "close all" + "\n"
                    "exit" + '\n'
                )
            try:
                if not bindisplay:
                    subprocess.check_call(locCHIMERA + " --offscreen --nogui " + rawmapchimeracmd,
                                            cwd=self.workdir, shell=True)
                else:
                    subprocess.check_call(locCHIMERA + " " + rawmapchimeracmd, cwd=self.workdir, shell=True)

            except subprocess.CalledProcessError as suberr:
                err = 'Raw map surface view by ChimeraX error: {}'.format(suberr)
                errlist.append(err)
                sys.stderr.write(err + '\n')

            print('Raw map surface views were generated by ChimeraX method')
            try:
                self.scale_surfaceview()
            except:
                err = 'Scaling the surface views err: {}'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            rawsurfaceviewjson = dict()

            outmapximage = str(mapname) + '_xsurface.jpeg'
            mapxlist = outmapximage.split('_')
            mapxscaleimage = '_'.join(mapxlist[:-1]) + '_scaled_' + mapxlist[-1]
            rawsurfaceviewjson['x'] = os.path.basename(mapxscaleimage) if os.path.isfile(
                self.workdir + mapxscaleimage) else None

            outmapyimage = str(mapname) + '_ysurface.jpeg'
            mapylist = outmapyimage.split('_')
            mapyscaleimage = '_'.join(mapylist[:-1]) + '_scaled_' + mapylist[-1]
            rawsurfaceviewjson['y'] = os.path.basename(mapyscaleimage) if os.path.isfile(
                self.workdir + mapyscaleimage) else None

            outmapzimage = str(mapname) + '_zsurface.jpeg'
            mapzlist = outmapzimage.split('_')
            mapzscaleimage = '_'.join(mapzlist[:-1]) + '_scaled_' + mapzlist[-1]
            rawsurfaceviewjson['z'] = os.path.basename(mapzscaleimage) if os.path.isfile(
                self.workdir + mapzscaleimage) else None
            if errlist:
                rawsurfaceviewjson['err'] = {'rawmap_surface_err': errlist}

            finaldict = {'rawmap_map_surface': rawsurfaceviewjson}
            rawcldict = {'rawmap_contour_level': {'cl': '{:0.2f}'.format(rawmapcl)}}

            try:
                with codecs.open(self.workdir + mapname + '_rawmapsurfaceview.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except:
                err = 'Saving map surface view json error: {}.'.format(sys.exc_info()[1])
                sys.stderr.write(err + '\n')

            try:
                with codecs.open(self.workdir + mapname + '_rawmapcl.json', 'w', encoding='utf-8') as ff:
                    json.dump(rawcldict, ff)
            except:
                err = 'Saving rawmap contour level json error: {}.'.format(sys.exc_info()[1])
                sys.stderr.write(err + '\n')

            end = timeit.default_timer()
            print('Raw map surface view time: %s' % (end - start))
            print('------------------------------------')

        else:
            print('No raw map or half maps or raw map contour level for raw map surfaces.')

    @profile_peak_memory()
    def new_surfaces(self):
        """
            All surfaces views
        """
        # create viewer
        chimerax = chimerax_envcheck()
        viewer = ChimeraxViews(chimerax, None, self.workdir)

        # Primary map surface view
        primary_input_map = f'{self.workdir}{self.mapname}'
        primary_input_contour = self.cl
        if primary_input_contour is not None and self.met != 'tomo':
            viewer.new_surface_view_chimerax(primary_input_map, primary_input_contour)

        # Raw map surface view
        if self.hmodd is not None and self.hmeven is not None:
            rawmap_name = self.findrawmap()
            rawmap_cl = self.rawmapcl()
            viewer.new_surface_view_chimerax(rawmap_name, rawmap_cl, 'surface', 'raw')

        # Raw map and relion mask surface view
            if self.relion_mask:
                # Raw map and relion mask surface view
                raw_map_predicated_contour = MapProcessor.predict_contour(f'{rawmap_name}')
                viewer.new_surface_view_chimerax(f'{rawmap_name}', raw_map_predicated_contour, 'relionmask', '',
                                                 self.relion_mask, 1.0)

        # Primary map and model
        if self.models:
            for model in self.models:
                viewer.new_surface_view_chimerax(primary_input_map, primary_input_contour, 'surface', '',
                                               None, None, model.filename)

        # Relion mask surface view
        if self.relion_mask:
            viewer.new_surface_view_chimerax(self.relion_mask, 1.0, 'surface', '')

        # Mask and primary map surface view
        for mask_name in self.allmasks:
            # Use all 1.0 for mask contour level till it is given by author in the header
            mask_cl = 1.0
            viewer.new_surface_view_chimerax(primary_input_map, primary_input_contour, 'mask', '',
                                           mask_name, mask_cl)


    # Surface Chimera way
    # def new_surface_view_chimerax(self, input_map, input_contour, type='surface', raw='', mask_map=None,
    #                               mask_map_contour=None, input_mmcif=None):
    #     """
    #     Generate Primary map surface view
    #     """
    #
    #     start = timeit.default_timer()
    #     errlist = []
    #     output_image_dict = None
    #
    #     try:
    #         _, chimerax = self.surface_envcheck()
    #         viewer = ChimeraxViews(chimerax, None, self.workdir)
    #         surface_script_path, surface_assemble_script_path = viewer.generate_map_chimerax_script(input_map,
    #                                                                                                 input_contour,
    #                                                                                                 mask_map=mask_map,
    #                                                                                                 mask_map_contour=mask_map_contour,
    #                                                                                                 input_mmcif=input_mmcif)
    #         viewer.run_chimerax(surface_script_path)
    #         output_assemble_image_dict = None
    #         if surface_assemble_script_path:
    #             viewer.run_chimerax(surface_assemble_script_path)
    #             output_assemble_image_dict = viewer.rescale_view(input_map, input_mmcif, mask_map, type, True)
    #
    #         output_image_dict = viewer.rescale_view(input_map, input_mmcif, mask_map, type)
    #     except Exception as e:
    #         errlist.append(str(e))
    #         print(f'Error: {e}', file=sys.stdout)
    #
    #     if output_image_dict:
    #         try:
    #             if mask_map and input_map:
    #                 main_key = 'map_mask_surface'
    #                 output_json_filename = f'{self.workdir}{self.mapname}_maskview.json'
    #             elif input_mmcif:
    #                 main_key = 'mapmodel_surface'
    #                 output_json_filename = f'{self.workdir}{self.mapname}_mapmodelview.json'
    #                 if output_assemble_image_dict:
    #                     assemble_main_key = 'mapmodel_assemble_surface'
    #             else:
    #                 main_key = 'rawmap_map_surface' if raw else 'map_surface'
    #                 output_json_filename = f'{self.workdir}{self.mapname}_rawmapsurface.json' if raw else f'{self.workdir}{self.mapname}_mapsurface.json'
    #
    #             final_dict = {main_key: output_image_dict}
    #             with codecs.open(output_json_filename, 'w', encoding='utf-8') as f:
    #                 json.dump(final_dict, f)
    #             if output_assemble_image_dict:
    #                 final_dict = {assemble_main_key: output_assemble_image_dict}
    #                 with codecs.open(f'{self.workdir}{self.mapname}_mapmodelassemble.json', 'w',
    #                                  encoding='utf-8') as f:
    #                     json.dump(final_dict, f)
    #         except IOError as ioerr:
    #             errlist.append(str(ioerr))
    #             print(f'IOError: {ioerr}', file=sys.stdout)
    #
    #     end = timeit.default_timer()
    #     if input_map and not mask_map and not input_mmcif and raw == '':
    #         print(f'Primary map surface view time: {end - start}')
    #         print('------------------------------------')
    #     elif input_map and input_mmcif:
    #         print(f'Map with model surface view time: {end - start}')
    #         print('------------------------------------')
    #     elif mask_map and input_map:
    #         print(f'Mask and map surface view time: {end - start}')
    #         print('------------------------------------')
    #     elif raw != '':
    #         print(f'Raw map surface view time: {end - start}')
    #         print('------------------------------------')
    #
    #     if errlist:
    #         print(f'Errors encountered: {errlist}', file=sys.stdout)
    #         print('------------------------------------')

    def surfaceview_chimera(self, chimeraapp):
        """
            Generate surface view by using headless Chimera and pychimera

        """
        import mmap

        start = timeit.default_timer()
        errlist = []
        mmerrlist = []
        bindisplay = os.getenv('DISPLAY')

        mapname = self.workdir + self.mapname
        if not os.path.isfile(mapname) and os.path.isfile(self.mapname):
            mapname = self.mapname

        locCHIMERA = chimeraapp
        contour = "level " + str(self.cl) if self.cl is not None else ''
        # map surface view alone
        mapchimeracmd = self.mapname + '_chimera.cxc'
        assemble = False
        with open(self.workdir + mapchimeracmd, 'w') as f:
            f.write(
                # Chimera version
                # 'open ccp4:' + str(mapname) + '\n'
                # "volume #0 style surface expandSinglePlane True " + '\n'
                # "volume #0 color #B8860B step 1 " + contour + '\n'
                # "set projection orthographic" + '\n'
                # "surftransp 50" + '\n'  # make the surface a little bit see-through
                # "background solid light gray" + '\n'
                # "copy file " + str(self.mapname) + "_zsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                # "turn x -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(self.mapname) + "_xsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                # "turn z -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(self.mapname) + "_ysurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                # "close all" + "\n"
                # "stop"

                # ChimeraX version
                "open " + str(mapname) + " format ccp4" + '\n'
                "volume #1 style surface expandSinglePlane True" + '\n'
                # "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                "volume #1 step 1 level " + str(self.cl) + '\n'
                "set bgColor white" + '\n'
                "lighting full \n"
                "view cofr True \n"
                "save " + str(self.mapname) + "_zsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                "turn x -90" + '\n'
                "turn y -90" + '\n'
                "view cofr True" + '\n'
                "save " + str(self.mapname) + "_xsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                "view orient" + '\n'
                "turn x 90" + '\n'
                "turn z 90" + '\n'
                "view cofr True" + '\n'
                "save " + str(self.mapname) + "_ysurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                "close all" + "\n"
                "exit" + '\n'
            )

        try:
            if not bindisplay:
                subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + mapchimeracmd,
                                        cwd=self.workdir, shell=True)
                end = timeit.default_timer()
                print('Primary map surface view time: %s' % (end - start))
                print('------------------------------------')
            else:
                subprocess.check_call(locCHIMERA + " " + self.workdir + mapchimeracmd, cwd=self.workdir, shell=True)
                end = timeit.default_timer()
                print('Primary map surface view time: %s' % (end - start))
                print('------------------------------------')
        except subprocess.CalledProcessError as suberr:
            end = timeit.default_timer()
            err = 'Primary map surface view by ChimeraX error: {}'.format(suberr)
            print('Primary map surface view time: %s' % (end - start))
            print('------------------------------------')
            errlist.append(err)
            sys.stderr.write(err + '\n')


        # map and models view together
        nstart = timeit.default_timer()
        if self.models:
            for model in self.models:
                # pdbid = model.filename.split('/')[-1].split('.')[0]
                pdbid = os.path.basename(model.filename)
                surfacefn = '{}_{}'.format(pdbid, self.mapname)
                chimeracmd = surfacefn + '_chimera.cxc'
                with open(self.workdir + chimeracmd, 'w') as f:
                    f.write(
                        # Chimera version
                        # 'open ccp4:' + str(mapname) + '\n'
                        # "open cif:" + str(model.filename) + '\n'
                        # "volume #0 style surface expandSinglePlane True " + '\n'
                        # "volume #0 color #B8860B step 1 " + contour + '\n'
                        # "set projection orthographic" + '\n'
                        # "surftransp 50" + '\n'  # make the surface a little bit see-through
                        # "background solid light gray" + '\n'
                        # "copy file " + str(surfacefn) + "_zsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                        # "turn x -90" + '\n'
                        # "center" + '\n'
                        # "copy file " + str(surfacefn) + "_xsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                        # "turn z -90" + '\n'
                        # "center" + '\n'
                        # "copy file " + str(surfacefn) + "_ysurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                        # "close all" + "\n"
                        # "stop"

                        # ChimeraX version
                        'open ' + str(mapname) + " format ccp4" + '\n'
                        "open " + str(model.filename) + " format mmcif" + '\n'
                        "hide selAtoms" + '\n'
                        "show selAtoms ribbons" + '\n'
                        "color #2 #003BFF" + '\n'
                        "volume #1 style surface expandSinglePlane True " + '\n'
                        "volume #1 color #B8860B step 1 " + contour + '\n'
                        "volume #1 transparency 0.65" + '\n'  # make the surface a little bit see-through
                        "set bgColor light gray" + '\n'
                        "view cofr True \n"
                        "save " + str(surfacefn) + "_zsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                        "turn x -90" + '\n'
                        "turn y -90" + '\n'
                        "view cofr True" + '\n'
                        "save " + str(surfacefn) + "_xsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                        "view orient" + '\n'
                        "turn x 90" + '\n'
                        "turn z 90" + '\n'
                        "view cofr True" + '\n'
                        "save " + str(surfacefn) + "_ysurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                        "close all" + "\n"
                        "exit"

                    )
                with open(str(model.filename)) as f:
                    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    # python 3 mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    if s.find(b'point symmetry operation') != -1:
                        assemble = True
                    else:
                        assemble = False
                chimeracmdassemble = surfacefn + '_chimera_assemble.cxc'
                if assemble:
                    modelname = os.path.basename(model.filename)
                    mapname = os.path.basename(mapname)
                    prefix = '{}_{}'.format(modelname, mapname)

                    with open(self.workdir + chimeracmdassemble, 'w') as f:
                        f.write(
                            # ChimeraX version
                            "open " + str(mapname) + " format ccp4" + '\n'
                            "open " + str(model.filename) + " format mmcif" + '\n'
                            "hide selAtoms" + '\n'
                            "show selAtoms ribbons" + '\n'
                            "color #2 #003BFF" + '\n'
                            "volume #1 style surface expandSinglePlane True" + '\n'
                            "volume #1 color #B8860B step 1 " + contour + '\n'
                            "volume #1 transparency 0.65" + '\n'  # make the surface a little bit see-through
                            "sym #2 assembly 1\n"
                            "set bgColor light gray" + '\n'
                            "view cofr True \n"
                            "save " + str(prefix) + "_assemble_zsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(prefix) + "_assemble_xsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(prefix) + "_assemble_ysurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit" + '\n'
                        )


                try:
                    if not bindisplay:
                        subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                              cwd=self.workdir, shell=True)
                        if assemble:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmdassemble,
                                                  cwd=self.workdir, shell=True)
                        nend = timeit.default_timer()
                        print('Primary map and model view time: %s' % (nend - nstart))
                        print('------------------------------------')
                    else:
                        subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir, shell=True)
                        if assemble:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmdassemble,
                                                  cwd=self.workdir, shell=True)
                        nend = timeit.default_timer()
                        print('Primary map and model view time: %s' % (nend - nstart))
                        print('------------------------------------')

                except subprocess.CalledProcessError as suberr:
                    err = 'Saving model {} and map err: {}'.format(str(model.filename), suberr)
                    mmerrlist.append(err)
                    sys.stderr.write(err + '\n')

        print('Surface views were generated by ChimeraX')
        try:
            self.scale_surfaceview()
        except:
            err = 'Scaling the surface views err: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            mmerrlist.append(err)
            sys.stderr.write(err + '\n')

        surfaceviewjson = dict()
        outmapximage = str(self.mapname) + '_xsurface.jpeg'
        mapxlist = outmapximage.split('_')
        mapxscaleimage = '_'.join(mapxlist[:-1]) + '_scaled_' + mapxlist[-1]
        surfaceviewjson['x'] = os.path.basename(mapxscaleimage) if os.path.isfile(self.workdir + mapxscaleimage) else None

        outmapyimage = str(self.mapname) + '_ysurface.jpeg'
        mapylist = outmapyimage.split('_')
        mapyscaleimage = '_'.join(mapylist[:-1]) + '_scaled_' + mapylist[-1]
        surfaceviewjson['y'] = os.path.basename(mapyscaleimage) if os.path.isfile(self.workdir + mapyscaleimage) else None

        outmapzimage = str(self.mapname) + '_zsurface.jpeg'
        mapzlist = outmapzimage.split('_')
        mapzscaleimage = '_'.join(mapzlist[:-1]) + '_scaled_' + mapzlist[-1]
        surfaceviewjson['z'] = os.path.basename(mapzscaleimage) if os.path.isfile(self.workdir + mapzscaleimage) else None
        if errlist:
            surfaceviewjson['err'] = {'map_surface_err': errlist}

        finaldict = {'map_surface': surfaceviewjson}

        try:
            with codecs.open(self.workdir + self.mapname + '_mapsurfaceview.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except:
            err = 'Saving map surface view json error: {}.'.format(sys.exc_info()[1])
            sys.stderr.write(err + '\n')

        jpegs = glob.glob(self.workdir + '/*surface.jpeg')
        modelsurf = dict()
        finalmmdict = dict()
        if self.models:
            # print "self.models:%s" % self.models
            for model in self.models:
                modelname = os.path.basename(model.filename)
                surfacefn = '{}_{}'.format(modelname, self.mapname)
                modelmapsurface = dict()
                for jpeg in jpegs:
                    if modelname in jpeg and 'xsurface' in jpeg:
                        modelmapsurface['x'] = str(surfacefn) + '_scaled_xsurface.jpeg'
                    if modelname in jpeg and 'ysurface' in jpeg:
                        modelmapsurface['y'] = str(surfacefn) + '_scaled_ysurface.jpeg'
                    if modelname in jpeg and 'zsurface' in jpeg:
                        modelmapsurface['z'] = str(surfacefn) + '_scaled_zsurface.jpeg'

                with open(str(model.filename)) as f:
                    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    # python 3 mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    if s.find(b'point symmetry operation') != -1:
                        assemble = True
                    else:
                        assemble = False
                assemblemapsurface = dict()
                if assemble:
                    modelname = os.path.basename(model.filename)
                    surfacefn = '{}_{}'.format(modelname, self.mapname)
                    for jpeg in jpegs:
                        if modelname in jpeg and 'xsurface' in jpeg:
                            assemblemapsurface['x_assemble'] = str(surfacefn) + '_assemble_scaled_xsurface.jpeg'
                        if modelname in jpeg and 'ysurface' in jpeg:
                            assemblemapsurface['y_assemble'] = str(surfacefn) + '_assemble_scaled_ysurface.jpeg'
                        if modelname in jpeg and 'zsurface' in jpeg:
                            assemblemapsurface['z_assemble'] = str(surfacefn) + '_assemble_scaled_zsurface.jpeg'

                mergeddict = dict(modelmapsurface, **assemblemapsurface)
                modelsurf[modelname] = mergeddict
        if mmerrlist:
            modelsurf['err'] = {'mapmodel_surface_err': mmerrlist}
        finalmmdict['mapmodel_surface'] = modelsurf

        try:
            with codecs.open(self.workdir + self.mapname + '_mapmodelsurfaceview.json', 'w',
                                encoding='utf-8') as f:
                json.dump(finalmmdict, f)
        except:
            err = 'Saving model and map surface views json error: {}.'.format(sys.exc_info()[1])
            sys.stderr.write(err + '\n')

        end = timeit.default_timer()
        print('Surfaceview time: %s' % (end - start))
        print('------------------------------------')


    def modelfitsurface(self, chimeraapp):
        """
            Produce surface based on the atom inclusion score
        """
        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*residue_inclusion.json')
        basedir = self.workdir
        mapname = self.mapname
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        errlist = []
        score_dir = os.path.dirname(va.__file__)
        rescolor_file = f'{score_dir}/utils/rescolor.py'

        fulinjson = injson[0] if injson else None
        try:
            if fulinjson:
                with open(fulinjson, 'r') as f:
                    args = json.load(f)
            else:
                args = None
                print('There is no residue inclusion json file.')
        except TypeError:
            err = 'Open residue_inclusion error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None:
                models = args['residue_inclusion']
                try:
                    del models['err']
                except:
                    print('Residue inclusion json result is correct')

                print('There is/are %s model(s).' % len(models))

                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            residues = value[key]['residue']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_fit_chimera.cxc'.format(modelname, mapname)
                            print(chimerafname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(model) + " format mmcif" + '\n')
                        fp.write(f"open {rescolor_file}\n")
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        count = 0
                        number_of_item = len(colors)
                        for (color, residue) in zip(colors, residues):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # res = re.sub("\D", "", restmp)
                            res = re.findall(r'-?\d+', restmp)[0]
                            # res_number, res_type = restmp.split(' ')
                            if count == 0:
                                count += 1
                                fp.write(f'rescolors /{chain}:{res} {color} ')
                            elif count == number_of_item - 1:
                                fp.write(f'/{chain}:{res} {color}\n')
                            else:
                                count += 1
                                fp.write(f'/{chain}:{res} {color} ')
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_zfitsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_xfitsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_yfitsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} fit surface view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        self.scale_surfaceview()
                    except:
                        err = 'Scaling model fit surface view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*surface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.mapname)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xfitsurface' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xfitsurface.jpeg'
                                if modelname in jpeg and 'yfitsurface' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_yfitsurface.jpeg'
                                if modelname in jpeg and 'zfitsurface' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zfitsurface.jpeg'
                            if errlist:
                                modelsurf['err'] = {'model_fit_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['modelfit_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.mapname + '_modelfitsurfaceview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write(
                                'Saving model fit surface view to json error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('Modelfitsurface time: %s' % (end - start))
                print('------------------------------------')


    def scale_surfaceview(self):
        """
            Scale the surface view images size to 300X300

        :return: None
        """

        # import imageio
        import glob

        for imgfile in glob.glob(self.workdir + '*surface.jpeg'):
            if 'scaled' not in imgfile:
                namelist = imgfile.split('/')[-1].split('_')
                nameone = '_'.join(namelist[:-1])
                nametwo = namelist[-1]
                npimg = Image.open(imgfile)
                im = npimg.resize((300, 300))
                im.save(self.workdir + nameone + '_scaled_' + nametwo)

        return None

    def scale_maskimg(self):
        """

        :return: None
        """

        # import imageio
        import glob

        for imgfile in glob.glob(self.workdir + '*maskview.jpeg'):
            if 'scaled' not in imgfile:
                namelist = imgfile.split('/')[-1].split('_')
                nameone = '_'.join(namelist[:-1])
                nametwo = namelist[-1]
                npimg = Image.open(imgfile)
                im = npimg.resize((300, 300))
                im.save(self.workdir + nameone + '_scaled_' + nametwo)

        return None


    def zoomin(self,img, factor, **kwargs):
        """
            Zoom in to the surface view images
        :param img: img object of input
        :return:
        """
        from scipy.ndimage import zoom

        h, w = img.shape[:2]
        zoom_tuple = (factor,) * 2 + (1,) * (img.ndim - 2)
        if factor != 1.:
            # Bounding box of the zoomed-in region within the input array
            zh = int(np.round(h / factor))
            zw = int(np.round(w / factor))
            top = (h - zh) // 2
            left = (w - zw) // 2

            out = zoom(img[top:top + zh, left:left + zw], zoom_tuple, **kwargs)
            trim_top = ((out.shape[0] - h) // 2)
            trim_left = ((out.shape[1] - w) // 2)
            out = out[trim_top:trim_top + h, trim_left:trim_left + w]

        # If factor == 1, just return the input array
        else:
            out = img

        return out


    @staticmethod
    def surface_envcheck():
        """

            Check the running environment for surface view.
            If the machine is headless, remind the user vtk or Chimera have to be build in the headless way.
            If vtk can not imported, try use Chimera.

        :return: tuple of vtkpack and chimeraapp binary value
        """

        display = os.getenv('DISPLAY')
        if display is None:
            print('You may running this program on a headless machine. Please make sure either headless VTK or headless' \
                  'ChimeraX are properly installed accordingly.')

        vtkpack = False
        chimeraapp = False
        try:
            import vtk
            vtkpack = True
        except ImportError:
            sys.stderr.write('VTK is not installed or imported properly. Trying to use ChimeraX to produce surface views.\n')

        try:
            if CHIMERA is not None:
                chimeraapp = CHIMERA
                print(chimeraapp)
            else:
                assert find_executable('ChimeraX') is not None
                chimeraapp = find_executable('ChimeraX')
                print(chimeraapp)
        except AssertionError:
            # print('Chimera executable is not there.', file=sys.stderr)
            sys.stderr.write('ChimeraX executable is not there.\n')

        return vtkpack, chimeraapp

    # Density distribution
    def mapdensity_distribution(self):
        """

            produce the map density distribution

        :return: None
        """
        self.density_distribution(self.map)

        return None

    # Raw map density distribution
    def rawmapdensity_distribution(self):
        """

            Produce raw map density distribution

        :param rawmap: Raw map object
        :return: None
        """

        if self.rawmap is not None:
            self.density_distribution(self.rawmap)
        else:
            print('There is no raw map for density distribution.')
            print('------------------------------------')

        return None

    @profile_peak_memory()
    def density_distribution(self, denmap=None):
        """

            Produce density value distribution information with the density map information.
            x was divided into 128 bins
            y was scaled by logarithmic 10 (for 0 value add 1 to igonre artifacts)

        :param: None
        :return: None

        """

        start = timeit.default_timer()
        bins = 128
        errlist = []
        datadict = {}
        # curmapname = os.path.basename(denmap.filename)
        curmapname = os.path.basename(denmap.fullname)
        if 'rawmap' in curmapname:
            tag = 'rawmap_'
        else:
            tag = ''
        try:
            # mapdata = self.map.getMap()
            mapdata = denmap.data
            flatmap = mapdata.flatten()
            # datamode = self.map.header[3]
            datamode = self.map.header.mode
            uniques, uniquecounts = np.unique(flatmap, return_counts=True)
            uniquelen = len(uniques)
            if datamode == 0:
                bins = uniques
                hist, bin_edges = np.histogram(flatmap, bins=bins)
            elif datamode == 1 or datamode == 6:
                if uniquelen > 1000:
                    inds = np.linspace(0, uniquelen-1, num=128, dtype=np.uint16)
                    bins = np.take(uniques, inds)
                    hist, bin_edges = np.histogram(flatmap, bins=bins)
                else:
                    hist = uniquecounts
                    bin_edges = np.append(uniques, uniques[-1])
            else:
                bins = np.linspace(min(flatmap), max(flatmap), 128)
                hist, bin_edges = np.histogram(flatmap, bins=bins)
            # hist, bin_edges = np.histogram(flatmap, bins=bins)
            hist[hist < 1] = 1
            newhist = np.log10(hist)

            plt.figure(figsize=(10, 3))
            plt.plot(np.round(bin_edges[:-1], 10).tolist(), np.round(newhist, 10).tolist())
            plt.savefig(self.workdir + '/' + curmapname + '_voxel_distribution.png')
            plt.close()

            mode = np.round(bin_edges[:-1][np.argmax(newhist)], 5).tolist()
            datadict = {
                tag + 'density_distribution': {'y': np.round(newhist, 10).tolist(),
                                         'x': np.round(bin_edges[:-1], 10).tolist(),
                                         'mode': mode}}
        except:
            err = 'Density distribution error:{}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {tag + 'density_distribution': {'err': {'density_distribution_error': errlist}}}

        try:
            with codecs.open(self.workdir + curmapname + '_density_distribution.json', 'w',
                             encoding='utf-8') as f:
                json.dump(datadict, f)
        except:
            sys.stderr.write('Saving denisty distribution to json error.')

        end = timeit.default_timer()
        print(tag + 'Density distribution time: %s' % (end - start))
        print('------------------------------------')

        return None

    # Atom and residue includsion
    @staticmethod
    def __floatohex(numlist):
        """

            Produce hex color between red and green

        :param numlist: A list of RGB values
        :return: A list of hex value between R and G with B = 0

        """

        # rgbs = [[int((1 - num) * 255), int(num * 255), 0] for num in numlist]
        # rgbs = [[int((1 - num) * 255)*0.5, 120, int(num * 255)*0.5] for num in numlist]
        numlist = [-1 if i < 0 else i for i in numlist]
        rgbs = [[122, int(num * 255), int(num * 255)] if num >= 0 else [255, 0, 255] for num in numlist]
        resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]

        return resultlist

    # Atom and residue includsion
    @staticmethod
    def __floatohex_aboveone(numlist):
        """

            Produce hex color between red and green

        :param numlist: A list of RGB values
        :return: A list of hex value between R and G with B = 0

        """

        # rgbs = [[int((1 - num) * 255), int(num * 255), 0] for num in numlist]
        # rgbs = [[int((1 - num) * 255)*0.5, 120, int(num * 255)*0.5] for num in numlist]
        numlist = [-1 if i < 0 else i for i in numlist]
        rgbs = [[int(num * 13), 0, int(num * 255)] if num >= 0 else [255, 0, 255] for num in numlist]
        resultlist = []
        resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]

        return resultlist

    def __interPolation(self):
        """

            Usc scipy regulargrid interpolation method feed with all maps info

        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: A interpolation function

        """

        # mapdata = self.map.getMap()
        mapdata = self.map.data
        tmpmapdata = np.swapaxes(mapdata, 0, 2)
        clim, blim, alim = mapdata.shape
        x = range(alim)
        y = range(blim)
        z = range(clim)
        myinter = RegularGridInterpolator((x, y, z), tmpmapdata)

        return myinter

    # version 1 by using TEMPy
    def __interthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.models, list):
            models = self.models
        else:
            models.append(self.models)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        mapsig = map.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]

            atomcount = 0
            chaincount = 1
            chainatoms = 0
            chainaiscore = {}
            chainai = 0.

            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                aiprechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                for atom in model:
                    atomcount += 1
                    # if 'H' not in atom.atom_name:
                    onecoor = [atom.x, atom.y, atom.z]
                    oneindex = self.__getindices(onecoor)[1]
                    if oneindex[0] > map.x_size() - 1 or oneindex[0] < 0 or \
                            oneindex[1] > map.y_size() - 1 or oneindex[1] < 0 or \
                            oneindex[2] > map.z_size() - 1 or oneindex[2] < 0:
                        curinterpolation = map.min()
                        atomoutsidenum += 1
                    else:
                        curinterpolation = myinter(oneindex).tolist()[0]
                    interpolations.append(curinterpolation)
                    atominterbin = 1 if curinterpolation > contour else 0
                    if (rescount == 0) or (atom.res_no == preresid and atom.chain == prechain):
                        sumatominterbin += atominterbin
                        rescount += 1
                        preresid = atom.res_no
                        prechain = atom.chain
                        preres = atom.res

                    else:
                        keystr = prechain + ':' + str(preresid) + preres
                        allkeys.append(keystr)
                        # value = float(sumatominterbin)/rescount
                        value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                        allvalues.append(value)
                        sumatominterbin = atominterbin
                        preresid = atom.res_no
                        prechain = atom.chain
                        rescount = 1

                    # Add the chain based atom inclusion score
                    if (atomcount == 1) or (atom.chain == aiprechain):
                        chainatoms += 1
                        aiprechain = atom.chain
                        chainai += atominterbin
                    else:
                        aivalue = round(float(chainai) / chainatoms, 3)
                        aicolor = self.__floatohex([aivalue])[0]
                        # chainaiscore[prechain] = {'value': aivalue, 'color': aicolor}
                        # (Todo) For chain which have the same chain id non-protein part not included yet especially
                        # ligand bind to the protein ligand has the same chain id as the protein, then how to averge
                        # the ligand and the protein together need to take the numbers into account which also means
                        # need to add another value in the dictonary
                        # Need to properly canculated the average of one chain
                        if aiprechain in chainaiscore.keys():
                            # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                            pass
                        else:
                            chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor, 'numberOfAtoms': chainatoms}

                        chainatoms = 1
                        chaincount += 1
                        chainai = atominterbin
                        aiprechain = atom.chain

                aivalue = round(float(chainai) / chainatoms, 3)
                aicolor = self.__floatohex([aivalue])[0]
                if aiprechain in chainaiscore.keys():
                    # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                    pass
                else:
                    chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor, 'numberOfAtoms': chainatoms}
                keystr = aiprechain + ':' + str(preresid) + preres
                allkeys.append(keystr)
                value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                allvalues.append(value)
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                 atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict, chainaiscore, atomoutsidenum)

        return result

    # version 2 without using TEMPy for model loading which is working but not optimal for using biopython
    def __newinterthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.models, list):
            models = self.models
        else:
            models.append(self.models)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        # mapsig = map.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]

            atomcount = 0
            chaincount = 1
            chainatoms = 0
            chainaiscore = {}
            chainai = 0.

            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                aiprechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                for atom in model.get_atoms():
                    atomcount += 1
                    # if 'H' not in atom.atom_name:
                    # onecoor = [atom.x, atom.y, atom.z]
                    onecoor = atom.coord
                    oneindex = self.__getindices(onecoor)[1]
                    if oneindex[0] > map.header.nx - 1 or oneindex[0] < 0 or \
                            oneindex[1] > map.header.ny - 1 or oneindex[1] < 0 or \
                            oneindex[2] > map.header.nz - 1 or oneindex[2] < 0:
                        curinterpolation = map.min()
                        atomoutsidenum += 1
                    else:
                        curinterpolation = myinter(oneindex).tolist()[0]
                    interpolations.append(curinterpolation)
                    atominterbin = 1 if curinterpolation > contour else 0

                    if (rescount == 0) or (residue.id[1] == preresid and atom.full_id[2] == prechain):
                        sumatominterbin += atominterbin
                        rescount += 1
                        preresid = residue.id[1]
                        prechain = atom.full_id[2]
                        preres = residue.resname
                    else:
                        keystr = prechain + ':' + str(preresid) + preres
                        allkeys.append(keystr)
                        value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                        allvalues.append(value)
                        sumatominterbin = atominterbin
                        preresid = residue.id[1]
                        prechain = atom.full_id[2]
                        rescount = 1

                    # Add the chain based atom inclusion score
                    if (atomcount == 1) or (atom.full_id[2] == aiprechain):
                        chainatoms += 1
                        # aiprechain = atom.chain
                        aiprechain = atom.full_id[2]
                        chainai += atominterbin
                    else:
                        aivalue = round(float(chainai) / chainatoms, 3)
                        aicolor = self.__floatohex([aivalue])[0]
                        # chainaiscore[prechain] = {'value': aivalue, 'color': aicolor}
                        # (Todo) For chain which have the same chain id non-protein part not included yet especially
                        # ligand bind to the protein ligand has the same chain id as the protein, then how to averge
                        # the ligand and the protein together need to take the numbers into account which also means
                        # need to add another value in the dictonary
                        # Need to properly canculated the average of one chain
                        if aiprechain in chainaiscore.keys():
                            # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                            pass
                        else:
                            chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor}

                        chainatoms = 1
                        chaincount += 1
                        chainai = atominterbin
                        # aiprechain = atom.chain
                        aiprechain = atom.full_id[2]

                aivalue = round(float(chainai) / chainatoms, 3)
                aicolor = self.__floatohex([aivalue])[0]
                if aiprechain in chainaiscore.keys():
                    # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                    pass
                else:
                    chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor}
                keystr = aiprechain + ':' + str(preresid) + preres
                allkeys.append(keystr)
                value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                allvalues.append(value)
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                 atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict, chainaiscore, atomoutsidenum)

        return result

    # version 3 for optimal usage of biopython
    def __nnewinterthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.models, list):
            models = self.models
        else:
            models.append(self.models)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        # mapsig = map.std()
        # mapsig = map.data.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]

            atomcount = 0
            chaincount = 1
            chainatoms = 0
            chainaiscore = {}
            chainai = 0.

            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                aiprechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                chainai_atomsno = {}
                for chain in model.get_chains():
                    chainatominterbin = 0
                    chain_atom_count = 0
                    chain_name = chain.id
                    for residue in chain.get_residues():
                        resatominterbin = 0
                        residue_atom_count = 0
                        residue_name = residue.resname
                        residue_no = residue.id[1]
                        for atom in residue.get_atoms():
                            if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                                continue
                            # if 'H' not in atom.name:
                            atomcount += 1
                            residue_atom_count += 1
                            # chain_atom_count += 1
                            onecoor = atom.coord
                            oneindex = self.__getindices(onecoor)[1]
                            # if oneindex[0] > map.x_size() - 1 or oneindex[0] < 0 or \
                            #         oneindex[1] > map.y_size() - 1 or oneindex[1] < 0 or \
                            #         oneindex[2] > map.z_size() - 1 or oneindex[2] < 0:
                            if oneindex[0] > map.header.nx - 1 or oneindex[0] < 0 or \
                                    oneindex[1] > map.header.ny - 1 or oneindex[1] < 0 or \
                                    oneindex[2] > map.header.nz - 1 or oneindex[2] < 0:
                                # curinterpolation = map.min()
                                curinterpolation = map.data.min()
                                atomoutsidenum += 1
                            else:
                                curinterpolation = myinter(oneindex).tolist()[0]
                            interpolations.append(curinterpolation)
                            atominterbin = 1 if curinterpolation > contour else 0
                            resatominterbin += atominterbin
                            if 'H' not in atom.name:
                                chainatominterbin += atominterbin
                                chain_atom_count += 1
                            sumatominterbin += atominterbin
                        if residue_atom_count == 0:
                            continue
                        # residue inclusion section
                        keystr = chain_name + ':' + str(residue_no) + ' ' + residue_name
                        allkeys.append(keystr)
                        value = float('%.4f' % round((float(resatominterbin) / residue_atom_count), 4))
                        allvalues.append(value)

                    # chain inclusion section
                    if chain_name in chainai_atomsno.keys():
                        chainatominterbin += chainai_atomsno[chain_name]['value']
                        chain_atom_count += chainai_atomsno[chain_name]['atomsinchain']
                    # For cases where one water molecule has a sigle but different chain id
                    if chain_atom_count == 0:
                        continue
                    chainai_atomsno[chain_name] = {'value': chainatominterbin, 'atomsinchain': chain_atom_count}

                for chainname, chain_scores in chainai_atomsno.items():
                    chain_ai = float('%.3f' % round((float(chain_scores['value']) / chain_scores['atomsinchain']), 4))
                    aicolor = self.__floatohex([chain_ai])[0]
                    chainaiscore[chainname] = {'value': chain_ai, 'color': aicolor, 'numberOfAtoms': chain_scores['atomsinchain']}
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict, chainaiscore, atomoutsidenum)

        return result


    def map_matrix(self, apixs, angs):
        """

            calculate the matrix to transform Cartesian coordinates to fractional coordinates
            (check the definination to see the matrix formular)

        :param apixs: array of apix lenght
        :param angs: array of anglex in alpha, beta, gamma order
        :return:
        """

        ang = (angs[0]*math.pi/180, angs[1]*math.pi/180, angs[2]*math.pi/180)
        insidesqrt = 1 + 2 * math.cos(ang[0]) * math.cos(ang[1]) * math.cos(ang[2]) - \
                     math.cos(ang[0])**2 - \
                     math.cos(ang[1])**2 - \
                     math.cos(ang[2])**2

        cellvolume = apixs[0]*apixs[1]*apixs[2]*math.sqrt(insidesqrt)

        m11 = 1/apixs[0]
        m12 = -math.cos(ang[2])/(apixs[0]*math.sin(ang[2]))

        m13 = apixs[1] * apixs[2] * (math.cos(ang[0]) * math.cos(ang[2]) - math.cos(ang[1])) / (cellvolume * math.sin(ang[2]))
        m21 = 0
        m22 = 1 / (apixs[1] * math.sin(ang[2]))
        m23 = apixs[0] * apixs[2] * (math.cos(ang[1]) * math.cos(ang[2]) - math.cos(ang[0])) / (cellvolume * math.sin(ang[2]))
        m31 = 0
        m32 = 0
        m33 = apixs[0] * apixs[1] * math.sin(ang[2]) / cellvolume
        prematrix = [[m11, m12, m13], [m21, m22, m23], [m31, m32, m33]]
        matrix = np.asarray(prematrix)

        return matrix


    def matrix_indices(self, apixs, onecoor):
        """

            Method 2: using the fractional coordinate matrix to calculate the indices when the maps are non-orthogonal

        :return:
        """

        # Method 2: by using the fractional coordinate matrix
        # Chosen as the main function for the current implementation

        # Figure out the order of the x, y, z based on crs info in the header
        # crs = list(self.map.header[16:19])
        crs = [self.map.header.mapc, self.map.header.mapr, self.map.header.maps]
        # ordinds save the indices correspoding to x, y ,z
        ordinds = [crs.index(1), crs.index(2), crs.index(3)]
        # angs = self.map.header[13:16]
        angs = [self.map.header.cellb.alpha, self.map.header.cellb.beta, self.map.header.cellb.gamma]
        matrix = self.map_matrix(apixs, angs)
        result = matrix.dot(np.asarray(onecoor))
        # xindex = result[0] - self.map.header[4 + ordinds[0]]
        # yindex = result[1] - self.map.header[4 + ordinds[1]]
        # zindex = result[2] - self.map.header[4 + ordinds[2]]
        xindex = result[0] - self.map.header.nxstart
        yindex = result[1] - self.map.header.nystart
        zindex = result[2] - self.map.header.nzstart

        return (xindex, yindex, zindex)


    def projection_indices(self, onecoor):
        """

            Method 1: using the projection way to calculate the indices when the maps are non-orthogonal

        :return: tumple which contains all three float new indices in (x, y, z) order
        """

        map = self.map
        zdim = map.header[12]
        znintervals = map.header[9]
        z_apix = zdim / znintervals

        ydim = map.header[11]
        ynintervals = map.header[8]
        y_apix = ydim / ynintervals

        xdim = map.header[10]
        xnintervals = map.header[7]
        x_apix = xdim / xnintervals

        theta = (map.header[13] / 90) * (math.pi / 2)
        beta = (map.header[14] / 90) * (math.pi / 2)
        gamma = (map.header[15] / 90) * (math.pi / 2)

        insidesqrt = 1 + 2 * math.cos(theta) * math.cos(beta) * math.cos(gamma) - \
                     math.cos(theta) * math.cos(theta) - \
                     math.cos(beta) * math.cos(beta) - \
                     math.cos(gamma) * math.cos(gamma)

        cellvolume = x_apix * y_apix * z_apix * math.sqrt(insidesqrt)

        cellheightz = cellvolume / (x_apix * y_apix * math.sin(gamma))
        cellheighty = cellvolume / (x_apix * z_apix * math.sin(beta))
        cellheightx = cellvolume / (z_apix * y_apix * math.sin(theta))

        # Figure out the order of the x, y, z based on crs info in the header
        crs = list(map.header[16:19])
        # ordinds save the indices correspoding to x, y ,z
        ordinds = [crs.index(1), crs.index(2), crs.index(3)]

        # Mehtod 1: Calculateing the distances from the atom to different planes(x'y', x'z', y'z') and divided by
        # The unit cell height(calculated by using unit cell volume divided by the plane surface area) to get the
        # indices, then deduct the origin index which give the final results. When calculating the sign of the
        # distance, find a plane parallel to the projection plane and it pass through the atom, the cutoff of this
        # plane and the correspoding axis give the location of the atom projection cutoff at the axis
        # (this should also be able to used to calculate the final indices(not tried)). If this point is outside
        # the normal cell dimension range, then the distance should be negative and vice verse
        relativex = onecoor[0] - map.header[49]
        relativey = onecoor[1] - map.header[50]
        relativez = onecoor[2] - map.header[51]

        # Z index by using the relativez / cellheightz
        zind = relativez / cellheightz
        zindex = zind - map.header[4 + ordinds[2]]

        # X index by calculating the plane first and then calculate the distance from atom to plane
        # Plane x'z'
        # Ax + By + Cz + D = 0 with three data points: (0, 0, 0), (b, 0, 0),
        # (a*cos(alpha), sqrt(a**2 - (celllhz)**2 - (a*cos(alpha)**2), cellhz), x' unit cell length is b, alpha is
        # the angle between x' and z'(which are the cell axes)
        # By using these three points the plane of x'z' can be calculated
        # A=0, B=cellhz, C = -sqrt(a**2 - (cellhz)**2 - (a*cos(alpha))**2), D=0
        A = 0
        B = cellheightz
        C = -math.sqrt(z_apix ** 2 - cellheightz ** 2 - (z_apix * math.cos(beta)) ** 2)
        D = 0

        # distance from atom to x'z' plane:
        #         |Ax + By + Cz + D|
        # d = -----------------------------
        #       sqrt(A**2 + B**2 + C**2)
        dy = math.fabs(B * relativey + C * relativez) / math.sqrt(A ** 2 + B ** 2 + C ** 2)

        # The parallel plan which pass the atom and intersect with the x is:
        # Ax) + B(y + a) + Cz + D = 0
        # a = -(Ax + By + Cz + D)/A
        # xcut = -a
        ycut = -(A * onecoor[0] + onecoor[1] + (C / B) * onecoor[2])
        ycut = -ycut
        if ycut < 0 or ycut > map.header[0 + ordinds[1]] * y_apix * math.sin(gamma):
            dy = -dy

        yind = dy / cellheighty
        yindex = yind - map.header[4 + ordinds[1]]

        # Plane z'y'
        # Ax + By + Cz + D = 0 with three data points: (0, 0, 0), (a*cos(alpha),
        # sqrt(a**2 - (cellhz)**2 - (a*cos(alpha)**2), cellhz),
        # (d*cos(gamma), d*sin(gamma), 0)
        # beta is the angle between x' and z'; gamma is the angle between x' and y'; d is the cell unit length
        # along y'
        # Using these three points a plane can be calculated
        # A=-tg(beta), B = 1, D=0,
        #      a*cos(alpha)*tg(beta) - t
        # C = --------------------------- ,     t = sqrt(a**2 - (cellhz)**2 - (a*cos(alpha))**2)
        #            cellhz
        # A = -math.tan(gamma)
        # B = 1
        # D = 0
        # t = math.sqrt(z_apix**2 - cellheightz**2 - (z_apix*math.cos(beta))**2)
        # C = (z_apix * math.cos(beta)*math.tan(gamma) - t) / cellheightz

        if map.header[15] == 90.:
            singamma = 1.
            cosgamma = 0.
        else:
            singamma = math.sin(gamma)
            cosgamma = math.cos(gamma)

        if map.header[14] == 90.:
            singbeta = 1.
            cosbeta = 0.
        else:
            sinbeta = math.sin(beta)
            cosbeta = math.cos(beta)

        A = -singamma
        B = cosgamma
        D = 0
        t = math.sqrt(z_apix ** 2 - cellheightz ** 2 - (z_apix * cosbeta) ** 2)
        C = (z_apix * cosbeta * singamma - t * cosgamma) / cellheightz

        # distance from atom to z'y' plane:
        #         |Ax + By + Cz + D|
        # d = -----------------------------
        #       sqrt(A**2 + B**2 + C**2)
        dx = math.fabs(A * relativex + B * relativey + C * relativez) / math.sqrt(A ** 2 + B ** 2 + C ** 2)
        xcut = (-(onecoor[0] + (B / A) * onecoor[1] + (C / A) * onecoor[2]))
        xcut = -xcut
        if xcut < 0 or xcut > map.header[0 + ordinds[0]] * x_apix:
            dx = -dx
        xind = dx / cellheightx
        xindex = xind - map.header[4 + ordinds[0]]


        return(xindex, yindex, zindex)


    def __getindices(self, onecoor):
        """

            Find one atom's indices correspoding to its cubic or plane
            the 8 (cubic) or 4 (plane) indices are saved in indices variable

        :param map: Density map instance from TEMPy.MapParser
        :param onecoor: List contains the atom coordinates in (x, y, z) order
        :return: Tuple contains two list of index: first has the 8 or 4 indices in the cubic;
                 second has the float index of the input atom

        """

        # For non-cubic or skewed density maps, they might have different apix on different axises
        map = self.map
        zdim = map.header.cella.z
        znintervals = map.header.mz
        z_apix = zdim / znintervals

        ydim = map.header.cella.y
        ynintervals = map.header.my
        y_apix = ydim / ynintervals

        xdim = map.header.cella.x
        xnintervals = map.header.mx
        x_apix = xdim / xnintervals

        map_zsize = map.header.nz
        map_ysize = map.header.ny
        map_xsize = map.header.nx

        # if map.header[13] == map.header[14] == map.header[15] == 90.:
        if map.header.cellb.alpha == map.header.cellb.beta == map.header.cellb.gamma == 90.:
            # Figure out the order of the x, y, z based on crs info in the header
            # crs = list(map.header[16:19])
            crs = [map.header.mapc, map.header.mapr, map.header.maps]
            # ordinds save the indices correspoding to x, y ,z
            ordinds = [crs.index(1), crs.index(2), crs.index(3)]

            zindex = float(onecoor[2] - map.header.origin.z) / z_apix - map.header.nzstart
            yindex = float(onecoor[1] - map.header.origin.y) / y_apix - map.header.nystart
            xindex = float(onecoor[0] - map.header.origin.x) / x_apix - map.header.nxstart

            zfloor = int(floor(zindex))
            if zfloor >= map_zsize - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(floor(yindex))
            if yfloor >= map_ysize - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(floor(xindex))
            if xfloor >= map_xsize - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1
        else:
            # Method 2: by using the fractional coordinate matrix
            # Chosen as the primary for the current implementation
            apixs = [x_apix, y_apix, z_apix]
            # Method 1: by using the atom projection on planes
            # xindex, yindex, zindex = self.projection_indices(onecoor))
            xindex, yindex, zindex = self.matrix_indices(apixs, onecoor)

            zfloor = int(floor(zindex))
            if zfloor >= map_zsize - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(floor(yindex))
            if yfloor >= map_ysize - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(floor(xindex))
            if xfloor >= map_xsize - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1

        indices = np.array(np.meshgrid(np.arange(xfloor, xceil + 1), np.arange(yfloor, yceil + 1),
                                       np.arange(zfloor, zceil + 1))).T.reshape(-1, 3)
        oneindex = [xindex, yindex, zindex]

        return (indices, oneindex)


    def __getfractions(self, interpolation, model):
        """

            Produce atom inclusion fraction information for full atoms and backbone trace

        :param interpolation: List of interpolation values
        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: Tuple contains full atom inclusion fractions and backbone inclusion fractions

        """

        map = self.map
        bins = np.linspace(map.data.min(), map.data.max(), 129)
        binlist = bins.tolist()
        bisect.insort(binlist, self.cl)
        clindex = binlist.index(self.cl)
        binlist.pop(clindex - 1)
        bins = np.asarray(binlist)

        newinterpolation = []
        for i in range(len(interpolation)):
            # if 'H' not in model[i].atom_name:
            if 'H' not in model[i].fullname:
                newinterpolation.append(interpolation[i])

        # Whole model average atom inlcusion
        entire_average = sum(np.asarray(newinterpolation) > self.cl) / float(len(newinterpolation))

        # Full atom inclusion
        a = []
        templist = np.asarray(newinterpolation)
        for i in bins:
            x = sum(templist > i) / float(len(templist))
            a.append(x)

        traceinter = []
        for i in range(len(interpolation)):
            if (model[i].fullname == 'N' or model[i].fullname == 'C' or model[i].fullname == 'O' or
                    model[i].fullname == 'CA' or model[i].fullname == "C3'" or model[i].fullname == "C4'" or
                    model[i].fullname == "C5'" or model[i].fullname == "O3'" or model[i].fullname == "O5'" or
                    model[i].fullname == 'P' or model[i].fullname == 'OXT'):
                traceinter.append(interpolation[i])

        # Backbone inclusion
        b = []
        temptraceinter = np.asarray(traceinter)
        for j in bins:
            y = sum(temptraceinter > j) / float(len(temptraceinter))
            b.append(y)

        return a, b, entire_average, float(len(newinterpolation))

    @profile_peak_memory()
    def ai_bar(self):

        if not self.onlybar:
            inclusion_instance = Inclusion(self.map, self.cl, self.models, self.workdir)
            inclusion_instance.atom_inclusion()
            self.residue_inclusion_views()
            # old way below
            # self.atom_inclusion()
            # self.residue_inclusion_views()
        self.get_bar('atom_inclusion')

    # @profile
    def atom_inclusion(self):
        """
            Generate atom inclusion and residue atom inclusion information verses different contour level
            Both full atoms and backbone information are included.
            Results wrote to JSON file
        :return: None
        """
        if self.models is None:
            sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated without '
                             'model structure.\n')
            print('------------------------------------')
        elif self.cl is None:
            sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated '
                             'without contour level given.\n')
            print('------------------------------------')
        else:
            start = timeit.default_timer()
            map = self.map

            # modelnames = [ model.filename for model in self.models ]
            # version 1 use tempy
            # combinresult = self.__interthird()
            # version 2 use biopython but not optmised for biopython
            # combinresult = self.__newinterthird()
            # version 3 use biopython need more tests and then delete the other two above
            combinresult = self.__nnewinterthird()
            atomindict = OrderedDict()
            resindict = OrderedDict()
            datadict = OrderedDict()
            resdict = OrderedDict()
            counter = 0
            errlist = []
            reserrlist = []
            allmodels_numberatoms = 0
            allmodels_atom_inclusion = 0.0
            for key, value in combinresult.items():
                try:
                    interpolations, allcontoursdict, chainaiscore, atomoutsidebox = value
                    if isinstance(self.models, list):
                        models = [curmodel for curmodel in self.models if key in curmodel.filename]
                    else:
                        models = list()
                        models.append(self.models)

                    if len(models) == 1:
                        model = models[0]
                    elif len(models) == 0:
                        print('There is no model!')
                        exit()
                    else:
                        print('There are more than one model which should be only one.')
                        exit()

                    allatoms = list(model.get_atoms())
                    result = self.__getfractions(interpolations, allatoms)
                    levels = np.linspace(map.data.min(), map.data.max(), 129)

                    binlist = levels.tolist()
                    bisect.insort(binlist, self.cl)
                    clindex = binlist.index(self.cl)
                    binlist.pop(clindex - 1)
                    levels = np.asarray(binlist)

                    # score_type = 'ai'
                    # new_dict = {'id': self.emdid, 'resolution': float(self.resolution), 'name': key,
                    #             score_type: round(result[2], 3)}
                    # plot_name = '{}_{}_{}_bar.png'.format(self.mapname, key, score_type)
                    # score_dir = os.path.dirname(va.__file__)
                    # relative_towhole, relative_totwo = bar(new_dict, score_type, self.workdir, score_dir, plot_name)
                    # aibar = {'whole': relative_towhole, 'relative': relative_totwo}

                    datadict[str(counter)] = {'name': key, 'level': [round(elem, 6) for elem in levels.tolist()],
                                              'all_atom': [round(elem, 3) for elem in result[0]],
                                              'backbone': [round(elem, 3) for elem in result[1]],
                                              'atomoutside': atomoutsidebox,
                                              'chainaiscore': chainaiscore,
                                              'totalNumberOfAtoms': int(result[3]),
                                              'average_ai_model': round(result[2], 3),
                                              'average_ai_color': self.__floatohex([round(result[2], 6)])[0],
                                              # 'ai_bar': aibar
                                              }
                    allmodels_numberatoms += int(result[3])
                    allmodels_atom_inclusion += result[3]*result[2]

                    data_len = len(levels.tolist())
                    plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[0]], '-g', label='Full atom')
                    plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[1]], '-b', label='Backbone')
                    plt.plot(data_len * [self.cl], np.linspace(0, 1, data_len), '-r', label='Recommended contour level')
                    plt.legend(loc='lower left')
                    plt.savefig(self.workdir + self.mapname + '_inclusion.png')
                    plt.close()
                except:
                    err = 'Atom inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
                if errlist:
                    datadict[str(counter)] = {'err': {'atom_inclusion_err': errlist}}

                contourdict = OrderedDict()
                try:
                    for contour, keysvalues in allcontoursdict.items():
                        allvalues = keysvalues[1]
                        allkeys = keysvalues[0]
                        colours = self.__floatohex(allvalues)
                        contourkey = str(round(float(contour), 6))
                        contourdict[contourkey] = OrderedDict([('color', colours), ('inclusion', allvalues),
                                                               ('residue', allkeys)])

                    contourdict['name'] = key
                    resdict[str(counter)] = contourdict
                except:
                    err = 'Residue inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
                    reserrlist.append(err)
                    sys.stderr.write(err + '\n')
                if reserrlist:
                    resdict[str(counter)] = {'err': {'residue_inclusion_err': reserrlist}}
                counter += 1

            if allmodels_numberatoms != 0:
                average_ai_allmodels = allmodels_atom_inclusion / allmodels_numberatoms
                datadict['average_ai_allmodels'] = round(average_ai_allmodels, 3)
            atomindict['atom_inclusion_by_level'] = datadict
            resindict['residue_inclusion'] = resdict

            try:
                with codecs.open(self.workdir + self.mapname + '_atom_inclusion.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(atomindict, f)
            except:
                sys.stderr.write('Saving to atom inclusion json error: {}.\n'.format(sys.exc_info()[1]))

            try:
                with codecs.open(self.workdir + self.mapname + '_residue_inclusion.json', 'w',
                                 encoding='utf-8') as f1:
                    json.dump(resindict, f1)
            except:
                sys.stderr.write('Saving to residue inclusion json error: {}.\n'.format(sys.exc_info()[1]))



            end = timeit.default_timer()
            print('Inclusion time: %s' % (end - start))
            print('------------------------------------')
        return None

    def residue_inclusion_views(self):
        """
            Produce the residue inclusion views
        """

        data_type = 'residue_inclusion'
        input_json_file = f'{self.workdir}{self.mapname}_{data_type}.json'

        try:
            viewer = ChimeraxViews(input_json=input_json_file, va_dir=self.workdir)
            root_data = viewer.get_root_data(data_type)
            viewer.get_model_views(self.mapname, root_data, data_type)
        except Exception as e:
            print(f'Error occurred: {e}', file=sys.stdout)

    # Volumecontour
    @profile_peak_memory()
    def volumecontour(self):
        """

            Generate Volume versus contour level plot.
            Result wrote to a JSON file.
            View indices as siting on the central of each voxel, no interpolation needed.

        :return: None

        """

        start = timeit.default_timer()
        map = self.map
        # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
        # check functionn frommrc_totempy in preparation.py
        apix = map.voxel_size.tolist()
        mapdata = map.data
        errlist = []
        datadict = dict()
        try:
            bins = np.linspace(mapdata.min(), mapdata.max(), 129)
            hist, bin_edges = np.histogram(mapdata, bins=bins)
            mapsize = map.header.nx * map.header.ny * map.header.nz
            preresult = mapsize - np.cumsum(hist)
            addedpre = np.insert(preresult, 0, mapsize)
            # Todo: for non-orthogonal volume this is not the right formula
            # It needs the formula : abc* sqrt(1 + 2*cos(a)*cos(b)*bos(c) - cos(a)**2 - cos(b)**2 - cos(c)**2)
            if type(apix) is tuple:
                basevolume = ((apix[0]*apix[1]*apix[2]) / (10 ** 3))
            else:
                basevolume = ((apix**3) / (10**3))
            tmpresult = addedpre * basevolume
            if self.cl:
                clvolume = (mapdata >= self.cl).sum()
                estvolume = round(clvolume * basevolume, 2)
            else:
                estvolume = None

            if estvolume:
                datadict = {
                    'volume_estimate': {'volume': np.round(tmpresult, 10).tolist(),
                                        'level': np.round(bins, 10).tolist(),
                                        'estvolume': estvolume,
                                        'estimated_weight': RESIDUE_DENSITY * estvolume
                                        }}
            else:
                datadict = {
                    'volume_estimate': {'volume': np.round(tmpresult, 10).tolist(),
                                        'level': np.round(bins, 10).tolist()}}
        except:
            err = 'Volume estimate calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        if errlist:
            datadict = {'volume_estimate': {'err': {'volume_estimate_error': errlist}}}
        try:
            with codecs.open(self.workdir + self.mapname + '_volume_contour.json', 'w',
                             encoding='utf-8') as f:
                json.dump(datadict, f)
        except:
            sys.stderr.write('Saving volume estimate to json error:{}.\n'.format(sys.exc_info()[1]))

        end = timeit.default_timer()
        print('Volume contour time: %s' % (end - start))
        print('------------------------------------')

        return None





    ################### test

    # def pssum(self,i, dist, indiaxis):
    #     if i != len(indiaxis) - 1:
    #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
    #         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
    #         return psum

    # def pssum(self,indices):
    #     # if i != len(indiaxis) - 1:
    #     # indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
    #     psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
    #     return psum


    def pararaps(self):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """
        import multiprocessing as mp
        import itertools
        threadcount = 2
        pool = mp.Pool(threadcount)

        if self.map.x_size() == self.map.y_size() == self.map.z_size():
            errlist = []
            start = timeit.default_timer()
            map = self.map
            apix = map.apix
            fftmap = map.fourier_transform()
            psmap = fftmap.copy()
            psmean = np.mean(psmap.fullMap)
            psstd = np.std(psmap.fullMap)
            psmap.fullMap = np.abs((psmap.fullMap - psmean) / psstd) ** 2

            midstart = timeit.default_timer() - start
            print(' -- RAPS Fourier-transformation time: %s' % midstart)

            zgrid = np.arange(floor(psmap.z_size() / 2.0) * -1, ceil(psmap.z_size() / 2.0)) / float(floor(psmap.z_size()))
            ygrid = np.arange(floor(psmap.y_size() / 2.0) * -1, ceil(psmap.y_size() / 2.0)) / float(floor(psmap.y_size()))
            xgrid = np.arange(floor(psmap.x_size() / 2.0) * -1, ceil(psmap.x_size() / 2.0)) / float(floor(psmap.x_size()))
            xdis = xgrid ** 2
            ydis = ygrid ** 2
            zdis = zgrid ** 2
            dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

            allaxis = [zgrid, ygrid, xgrid]
            tmpindiaxis = max(allaxis, key=len)
            indiaxist = tmpindiaxis[tmpindiaxis >= 0]
            indiaxis = np.linspace(0, 1 / (2 * apix), len(indiaxist))
            print('dist:')
            print(allaxis)
            print(dist.shape)
            print(indiaxis)
            print(psmap.z_size())
            print('-------')
            print(dist[98,96,96])


            aps = []
            # for i in range(len(indiaxis)):
            #     if i != len(indiaxis) - 1:
            #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
            #         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
            #         aps.append(psum)

            allindices = []
            allpsmap = []
            # for i in range(len(indiaxis)):
            #     if i != len(indiaxis) -1:
            #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
            #
            #         psum = psmap.fullMap[tuple(indices.T)].sum()
            #         allindices.append(indices)
            #         allpsmap.append(psum)
            # print(allindices)
            odd = []
            even =[]
            counter = 0
            rlist = []
            templist = []
            for i in range(len(indiaxis)-1):
                counter += 1
                if i == 0:
                    templist.append(i)
                elif i % 40 == 0:
                    rlist.append(templist)
                    templist = []
                    templist.append(i)
                else:
                    templist.append(i)

            rlist.append(templist)

            def split_list(inp_list, nr):
                """
                Splits evenly a list
                :param inp_list: list
                :param nr: number of parts
                :return: list of "nr" lists
                """
                new_list = []
                nr_el = 1.0 / nr * len(inp_list)
                for i in range(nr):
                    start = int(round(i * nr_el))
                    end = int(round((i + 1) * nr_el))
                    new_list.append(inp_list[start:end])
                return new_list
            inputlist = range(0, len(indiaxis)-1)
            rlist = split_list(inputlist, threadcount)

            # Try with shared object
            import multiprocessing
            import ctypes
            x, y, z = dist.shape

            shared_array_base = multiprocessing.Array(ctypes.c_double, x*y*z)
            # shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
            shared_array = np.frombuffer(shared_array_base.get_obj())
            shared_array = shared_array.reshape(dist.shape)



            shared_array[:] = dist[:]
            # aps = [pool.apply(pcal, args=(i, allindices, allpsmap)) for i in rlist]
            aps = [pool.apply(pssum, args=(i, indiaxis, indiaxist, shared_array)) for i in rlist]
            # aps = aps[:-1]
            # aps = pool.map(self.pssum, [ i for i in allindices])
            newaps = list(itertools.chain.from_iterable(aps))
            # print(len(newaps))

            for i in range(len(indiaxis)-1):
                if i != len(indiaxis) -1:
                    psum = log10(psmap.fullMap[tuple(newaps[i].T)].sum() / len(newaps[i]))
                    allpsmap.append(psum)

            print(allpsmap)

            ##################

            datadict = {'rotationally_averaged_power_spectrum': {'y': np.round(allpsmap, 4).tolist(),
                                                                 'x': np.round(indiaxis[:-1], 4).tolist()}}
            err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            datadict = {'rotationally_averaged_power_spectrum': {'err': {'raps_err': errlist}}}
            sys.stderr.write(err + '\n')

            if bool(datadict):
                try:
                    with codecs.open(self.workdir + self.mapname + '_raps.json', 'w', encoding='utf-8') as f:
                        json.dump(datadict, f)
                except:
                    sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
            else:
                sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

            end = timeit.default_timer()
            print('RAPS time: %s' % (end - start))
            print('------------------------------------')
        else:
            print('No RAPS calculation for non-cubic map.')
            print('------------------------------------')


        return None

    @profile_peak_memory()
    def rapss(self):
        """
            calculate both primary map raps and rawmap raps
        :return: None
        """
        if self.map:
            startraps = timeit.default_timer()
            self.new_raps()
            stopraps = timeit.default_timer()
            print('RAPS: %s' % (stopraps - startraps))
            print('------------------------------------')
        else:
            print('No proper primary map for RAPS calculation.')

        if self.hmeven is not None and self.hmodd is not None:
            startraps = timeit.default_timer()
            # self.fsc(self.hmeven, self.hmodd)
            self.rawmap_raps()
            stop = timeit.default_timer()
            print('Raw map RAPS: %s' % (stop - startraps))
            print('------------------------------------')
        else:
            print('No raw map RAPS: Mising half map(s).')
        plt.close()

    # @profile
    def rawmap_raps(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            self.new_raps(rawmap, dir, label)
        else:
            print('No raw map to calculate RAPS.')

        return None

    #@profile
    def fourier_transform(self, mapdata):


        new_mapdata = fftshift(fftn(mapdata))
        return new_mapdata

    #@profile
    def raps(self, mapin=None, workdir=None, label=''):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """

        map, workdir = self.mapincheck(mapin, workdir)
        mapname = os.path.basename(map.fullname)

        map_zsize = map.header.nz
        map_ysize = map.header.ny
        map_xsize = map.header.nx

        apix_list = map.voxel_size.tolist()
        apixs = (apix_list[0], apix_list[1], apix_list[2])

        if map is not None and workdir is not None:
            # if map.x_size() == map.y_size() == map.z_size():
            if map.header.nx == map.header.ny == map.header.nz:
                errlist = []
                start = timeit.default_timer()
                datadict = dict()
                try:
                    # map = self.map
                    # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
                    # if type(map.apix) is tuple:
                    if type(apixs) is tuple:
                        # apix = map.apix[0]
                        apix = apixs[0]
                    else:
                        # apix = map.apix
                        apix = apixs
                    # fftmap = map.fourier_transform()
                    fftmap = fftshift(fftn(map.data))
                    # psmap = fftmap.copy()
                    # psmean = np.mean(psmap.fullMap)
                    # psstd = np.std(psmap.fullMap)
                    # psmap.fullMap = np.abs((psmap.fullMap - psmean) / psstd) ** 2
                    psmean = np.mean(fftmap)
                    psstd = np.std(fftmap)
                    fftmap = np.abs((fftmap - psmean) / psstd) ** 2

                    midstart = timeit.default_timer() - start
                    print(' -- RAPS Fourier-transformation time: %s' % midstart)

                    # zgrid = np.arange(floor(psmap.z_size() / 2.0) * -1, ceil(psmap.z_size() / 2.0)) / float(floor(psmap.z_size()))
                    # ygrid = np.arange(floor(psmap.y_size() / 2.0) * -1, ceil(psmap.y_size() / 2.0)) / float(floor(psmap.y_size()))
                    # xgrid = np.arange(floor(psmap.x_size() / 2.0) * -1, ceil(psmap.x_size() / 2.0)) / float(floor(psmap.x_size()))
                    zgrid = np.arange(floor(map_zsize / 2.0) * -1, ceil(map_zsize / 2.0)) / float(floor(map_zsize))
                    ygrid = np.arange(floor(map_ysize / 2.0) * -1, ceil(map_ysize / 2.0)) / float(floor(map_ysize))
                    xgrid = np.arange(floor(map_xsize / 2.0) * -1, ceil(map_xsize / 2.0)) / float(floor(map_xsize))
                    # zgrid = np.arange(floor(psmap.z_size()*2 / 2.0) * -1, ceil(psmap.z_size()*2 / 2.0)) / float(floor(psmap.z_size()))
                    # ygrid = np.arange(floor(psmap.y_size()*2 / 2.0) * -1, ceil(psmap.y_size()*2 / 2.0)) / float(floor(psmap.y_size()))
                    # xgrid = np.arange(floor(psmap.x_size()*2 / 2.0) * -1, ceil(psmap.x_size()*2 / 2.0)) / float(floor(psmap.x_size()))
                    xdis = xgrid ** 2
                    ydis = ygrid ** 2
                    zdis = zgrid ** 2
                    dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

                    allaxis = [zgrid, ygrid, xgrid]
                    tmpindiaxis = max(allaxis, key=len)
                    indiaxist = tmpindiaxis[tmpindiaxis >= 0]
                    # indiaxist = np.arange(0, np.amax(tmpindiaxis),0.0104 )
                    # indiaxist = np.linspace(0, np.amax(tmpindiaxis), 200 )
                    indiaxis = np.linspace(0, 1 / (2 * apix), len(indiaxist))

                    aps = []
                    for i in range(len(indiaxis)):
                        if i == 0:
                            indices = np.argwhere(dist == indiaxist[i])
                            # psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                            psum = log10(fftmap[tuple(indices.T)].sum() / len(indices))
                            aps.append(psum)
                        if i != len(indiaxis) - 1:
                            indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
                            # psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                            psum = log10(fftmap[tuple(indices.T)].sum() / len(indices))
                            aps.append(psum)
                        else:
                            pass
                            # indices = np.argwhere(dist == indiaxist[i])
                            # psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                            # aps.append(psum)
                    print(aps)
                    if aps[0] < 0:
                        aps[0] = aps[1]
                    datadict = {label + 'rotationally_averaged_power_spectrum':  {'y': np.round(aps, 10).tolist(),
                                                                         'x': np.round(indiaxis, 10).tolist()}}
                    plt.figure(figsize=(10, 3))
                    plt.plot(np.round(indiaxis, 4).tolist(), np.round(aps, 4).tolist(), )
                    plt.savefig(workdir + self.mapname + '_raps.png')
                    plt.close()

                except:
                    err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

                if errlist:
                    datadict = {'rotationally_averaged_power_spectrum': {'err': {'raps_err': errlist}}}

                if bool(datadict):
                    try:
                        with codecs.open(workdir + mapname + '_raps.json', 'w', encoding='utf-8') as f:
                            json.dump(datadict, f)
                    except:
                        sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
                else:
                    sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

                end = timeit.default_timer()
                print('RAPS time for %s: %s' % (mapname, end - start))
                print('------------------------------------')
            else:
                print('No RAPS calculation for non-cubic map.')
                print('------------------------------------')

                return None
        else:
            print('No RAPS without proper map input and the output directory information.')


    # Below Here is the test new raps function area

    def apply_3d_symmetry(self, inds, origin):
        O = origin
        operators = [[np.array([-1, 1, 1]), [O[0] * 2, 0, 0]],
                     [np.array([1, 1, -1]), [0, 0, O[2] * 2]],
                     # [np.array([1, -1, 1]), [0, O[1] * 2, 0]],
                     # [np.array([-1, -1, 1]), [O[0] * 2, O[1] * 2, 0]],
                     [np.array([-1, 1, -1]), [O[0] * 2, 0, O[2] * 2]],]
                     # [np.array([1, -1, -1]), [0, O[1] * 2, O[2] * 2]],
                     # [np.array([-1, -1, -1]), [O[0] * 2, O[1] * 2, O[2] * 2]]]
        ind = np.array(inds)
        res = np.array(inds)
        # w1 = np.where((ind[:, 1] == O[1]) | (ind[:, 0] == O[0]) | (ind[:, 2] == O[2]), True, False)
        # w1 = ind[w1, :]
        # w2 = np.where((ind[:, 1] != O[1]) | (ind[:, 0] != O[0]) | (ind[:, 2] != O[2]), True, False)
        # w2 = ind[w2, :]
        for op in operators[:]:
            # tmp = w2 * op[0] + np.array(op[1])
            tmp = ind * op[0] + np.array(op[1])
            res = np.concatenate((res, tmp))
        # on_axis_res = np.concatenate((w1 * np.array([-1, -1, -1]) + np.array([O[0] * 2, O[1] * 2, O[2] * 2]), w1))
        # res = np.concatenate((res, on_axis_res))
        return np.unique(res, axis=0)

    def generate_shell(self, n1, n2, shape):
        d1 = n1
        d2 = n2
        # O1 = [shape[0]//2, shape[1]//2, shape[2]//2]
        # even number for grid
        # based on fft
        if min(shape) % 2 == 0:
            O1 = [shape[0] / 2, shape[1] / 2, shape[2] / 2]
        else:
            O1 = [(shape[0] - 1) / 2, (shape[1] - 1) / 2, (shape[2] - 1) / 2]
        indices = []
        # make sure
        x_max = int(d2) + int(O1[0]) + 1 if int(d2) + int(O1[0]) < shape[0] else int(d2) + int(O1[0])
        y_max = int(d2) + int(O1[1]) + 1 if int(d2) + int(O1[1]) < shape[1] else int(d2) + int(O1[1])
        for x in range(round(O1[0] + 0.1), x_max):
            for y in range(round(O1[1] + 0.1), y_max):
                xy_dist = math.sqrt((x - O1[0]) ** 2 + (y - O1[1]) ** 2)
                if xy_dist <= d2:
                    if xy_dist == 0:
                        z_min = int(O1[2] + d1)
                        z_max = int(O1[2] + d2)
                    elif xy_dist < d1:
                        z_min = math.sqrt(d1 ** 2 - xy_dist ** 2) + O1[2]
                        z_min = int(z_min)
                        z_max = math.sqrt(d2 ** 2 - xy_dist ** 2) + O1[2]
                    elif d1 <= xy_dist <= d2:
                        z_min = O1[2]
                        z_max = math.sqrt(d2 ** 2 - xy_dist ** 2) + O1[2]
                    else:
                        z_min = O1[2]
                        z_max = O1[2]
                    if int(z_min) < O1[2]:
                        z_min = round(O1[2] + 0.1)
                    z_max = int(z_max) + 1 if int(z_max) < shape[2] else int(z_max)
                    for z in range(int(z_min), z_max):
                        # print(x, y, z)
                        d = math.sqrt(xy_dist ** 2 + ((z - O1[2]) ** 2))
                        if d1 < d <= d2:
                            indices.append([x, y, z])
        all_ind = self.apply_3d_symmetry(indices, O1).astype(int)
        return all_ind

    # @profile
    def new_raps(self, mapin=None, workdir=None, label=''):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """

        map, workdir = self.mapincheck(mapin, workdir)
        mapname = os.path.basename(map.fullname)
        apix_list = map.voxel_size.tolist()
        apixs = (apix_list[0], apix_list[1], apix_list[2])

        if map is not None and workdir is not None:
            # if map.x_size() == map.y_size() == map.z_size():
            if map.header.nx == map.header.ny == map.header.nz:
                errlist = []
                start = timeit.default_timer()
                datadict = dict()
                try:
                    # map = self.map
                    # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
                    # if type(map.apix) is tuple:
                    if type(apixs) is tuple:
                        apix = apixs[0]
                    else:
                        apix = apixs
                    fftmap = fftshift(fftn(map.data))
                    psmean = np.mean(fftmap)
                    psstd = np.std(fftmap)
                    fftmap = np.abs((fftmap - psmean) / psstd) ** 2

                    midstart = timeit.default_timer() - start
                    print(' -- RAPS Fourier-transformation time: %s' % midstart)

                    ## applying new indices function
                    map_shape = fftmap.shape
                    aps = []
                    if map_shape[0] % 2 == 0:
                        org = [map_shape[0] / 2, map_shape[1] / 2, map_shape[2] / 2]
                    else:
                        org = [(map_shape[0] - 1) / 2, (map_shape[1] - 1) / 2, (map_shape[2] - 1) / 2]
                    indiaxis = np.linspace(0, int(org[0]), int(org[0]) + 1) / (map_shape[0] * apix)

                    shell_range = int(max(map_shape) - max(org))
                    for i in range(0, shell_range):
                        indices = self.generate_shell(i, i+1, map_shape)
                        psum = log10(fftmap[tuple(indices.T)].sum() / len(indices))
                        aps.append(psum)
                    if aps[0] < 0:
                        aps[0] = aps[1]
                    if map_shape[0] % 2 == 0:
                        aps.insert(0, aps[0])

                    datadict = {label + 'rotationally_averaged_power_spectrum':  {'y': np.round(aps, 10).tolist(),
                                                                         'x': np.round(indiaxis, 10).tolist()}}
                    if not label:
                        plt.plot(np.round(indiaxis, 4).tolist(), np.round(aps, 4).tolist(), label='RAPS')
                    else:
                        plt.plot(np.round(indiaxis, 4).tolist(), np.round(aps, 4).tolist(), label='Raw map RAPS')
                    plt.legend()
                    plt.savefig(workdir + self.mapname + '_raps.png')

                except:
                    err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

                if errlist:
                    datadict = {'rotationally_averaged_power_spectrum': {'err': {'raps_err': errlist}}}

                if bool(datadict):
                    try:
                        with codecs.open(workdir + mapname + '_raps.json', 'w', encoding='utf-8') as f:
                            json.dump(datadict, f)
                    except:
                        sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
                else:
                    sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

                end = timeit.default_timer()
                print('RAPS time for %s: %s' % (mapname, end - start))
                print('------------------------------------')
            else:
                print('No RAPS calculation for non-cubic map.')
                print('------------------------------------')

                return None
        else:
            print('No RAPS without proper map input and the output directory information.')

    # Above Here is the test new raps function area


    # New curve intersection functions
    def _rect_inter_inner(self, x1, x2):
        n1 = x1.shape[0] - 1
        n2 = x2.shape[0] - 1
        X1 = np.c_[x1[:-1], x1[1:]]
        X2 = np.c_[x2[:-1], x2[1:]]
        S1 = np.tile(X1.min(axis=1), (n2, 1)).T
        S2 = np.tile(X2.max(axis=1), (n1, 1))
        S3 = np.tile(X1.max(axis=1), (n2, 1)).T
        S4 = np.tile(X2.min(axis=1), (n1, 1))

        return S1, S2, S3, S4

    def _rectangle_intersection(self, x1, y1, x2, y2):
        S1, S2, S3, S4 = self._rect_inter_inner(x1, x2)
        S5, S6, S7, S8 = self._rect_inter_inner(y1, y2)

        C1 = np.less_equal(S1, S2)
        C2 = np.greater_equal(S3, S4)
        C3 = np.less_equal(S5, S6)
        C4 = np.greater_equal(S7, S8)

        ii, jj = np.nonzero(C1 & C2 & C3 & C4)

        return ii, jj

    def curves_intersection(self, x1, y1, x2, y2):
        """
        Get the interscetion of two curves
        return: list of of tuple contains [(x1, y1), (x2, y2), ...] (no duplicated points)
        """
        x1 = np.asarray(x1)
        x2 = np.asarray(x2)
        y1 = np.asarray(y1)
        y2 = np.asarray(y2)

        ii, jj = self._rectangle_intersection(x1, y1, x2, y2)
        if 0 in ii:
            zero_ind = np.where(ii == 0)
            ii = np.delete(ii, zero_ind)
            jj = np.delete(jj, zero_ind)
        if 1 in ii:
            one_ind = np.where(ii == 1)
            ii = np.delete(ii, one_ind)
            jj = np.delete(jj, one_ind)
        n = len(ii)

        dxy1 = np.diff(np.c_[x1, y1], axis=0)
        dxy2 = np.diff(np.c_[x2, y2], axis=0)

        T = np.zeros((4, n))
        AA = np.zeros((4, 4, n))
        AA[0:2, 2, :] = -1
        AA[2:4, 3, :] = -1
        AA[0::2, 0, :] = dxy1[ii, :].T
        AA[1::2, 1, :] = dxy2[jj, :].T

        BB = np.zeros((4, n))
        BB[0, :] = -x1[ii].ravel()
        BB[1, :] = -x2[jj].ravel()
        BB[2, :] = -y1[ii].ravel()
        BB[3, :] = -y2[jj].ravel()

        for i in range(n):
            try:
                T[:, i] = np.linalg.solve(AA[:, :, i], BB[:, i])
            except:
                T[:, i] = np.Inf

        in_range = (T[0, :] >= 0) & (T[1, :] >= 0) & (
                T[0, :] <= 1) & (T[1, :] <= 1)

        xy0 = T[2:, in_range]
        xy0 = xy0.T
        newlist = []
        print(xy0)
        for i in xy0:
            a = tuple(i)
            newlist.append(a)
        res = list(set(newlist))
        res.sort(key=newlist.index)
        nlist = []
        for b in res:
            nlist.append(list(b))
        lres = np.array(nlist)
        print(np.array(nlist))
        print(np.array(nlist)[:, 0])
        print(np.array(nlist)[:, 1])
        return lres[:, 0], lres[:, 1]

    # End of new curve intersection functions

    def __interpolated_intercept(self, x, y1, y2):
        """

            Find the intercept of two curves, given by the same x data

        """

        def intercept(point1, point2, point3, point4):
            """

                Find the intersection between two lines
                the first line is defined by the line between point1 and point2
                the second line is defined by the line between point3 and point4
                each point is an (x,y) tuple.

                So, for example, you can find the intersection between
                intercept((0,0), (1,1), (0,1), (1,0)) = (0.5, 0.5)

                :return: Intercept, in (x,y) format

            """

            def line(p1, p2):
                A = (p1[1] - p2[1])
                B = (p2[0] - p1[0])
                C = (p1[0] * p2[1] - p2[0] * p1[1])

                return A, B, -C

            def intersection(L1, L2):
                D = L1[0] * L2[1] - L1[1] * L2[0]
                Dx = L1[2] * L2[1] - L1[1] * L2[2]
                Dy = L1[0] * L2[2] - L1[2] * L2[0]

                x = Dx / D
                y = Dy / D

                return x, y

            L1 = line([point1[0], point1[1]], [point2[0], point2[1]])
            L2 = line([point3[0], point3[1]], [point4[0], point4[1]])

            R = intersection(L1, L2)

            return R

        idx = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)
        # Remove the first point usually (0, 1) to avoid all curves starting from (0, 1) which pick as one intersection
        if idx.size != 0:
            if idx[0][0] == 0:
                idx = np.delete(idx, 0, 0)
            xc, yc = intercept((x[idx], y1[idx]), ((x[idx + 1], y1[idx + 1])), ((x[idx], y2[idx])),
                               ((x[idx + 1], y2[idx + 1])))
            return xc, yc
        else:
            nullarr = np.empty(shape=(0, 0))
            return nullarr, nullarr


    def mmfsc(self):
        """

            Calculate Model-map FSC based on simulated density map from model

        :return:
        """

        if self.platform == 'emdb':
            start = timeit.default_timer()
            modelsmaps = self.modelsmaps
            ## Todo: Consider putting this err information into the final fsc json file
            modelmapsdict = {}
            oldfiles = []
            if self.met != 'tomo' and self.met != 'crys' and (modelsmaps is not None):
                for modelmap in modelsmaps:
                    # read model map
                    modelname = os.path.basename(modelmap).split('_')[0]
                    # objmodelmap = self.frommrc_totempy(modelmap)
                    objmodelmap = mrcfile.mmap(modelmap, mode='r')
                    # self.fsc(self.map, objmodelmap, label='{}_mm'.format(modelname))
                    self.new_fsc(self.map, objmodelmap, label='{}_mm'.format(modelname))
                    oldname = '{}{}_{}_mmfsc.json'.format(self.workdir, self.mapname, modelname)
                    newname = '{}{}'.format(self.workdir, self.mapname + '_' + modelname + '_mmfsc.json')
                    if os.path.isfile(oldname):
                        oldfiles.append(oldname)
                        os.rename(oldname, newname)
                    else:
                        print('{} does not exist, please check.'.format(oldname))
                    modelmapsdict[modelname] = newname
                self.mergemmfsc(modelmapsdict)
                self.deloldmmfsc(oldfiles)
                end = timeit.default_timer()

                print('mmfsc time: %s' % (end - start))
                print('------------------------------------')

            else:
                print('Model-map FSC only calculated for single particle data where there is a fitted model '
                      '(Please use -m sp and -f) or no model map is calculated us -i t/f to switch if on or off.')

        return None

    def deloldmmfsc(self, oldfiles):
        """

            delete separate mmfsc files to avoid merged into the final json

        :param oldfiles:
        :return: None
        """

        if oldfiles:
            for file in oldfiles:
                os.remove(file)
            print('Separate mmfsc files were deleted.')
        else:
            print('No mmfsc exist, no mmfsc file can be deleted')


    def mergemmfsc(self, mmfscdict):
        """

            Merge all *_mmfsc.json files of different models

        :return:
        """

        nfiles = len(list(mmfscdict))
        fulldata = {}
        for i, modelname in zip(range(0, nfiles), list(mmfscdict)):
            file = mmfscdict[modelname]
            if os.path.getsize(file):
                with open(file, 'r') as f:
                    if f is not None:
                        content = json.load(f)
                        if 'err' not in content.keys():
                            fulldata[str(i)] = list(content.values())[0]
                            fulldata[str(i)]['name'] = modelname
                        else:
                            curerr = content.values()[0]['err']
                            fulldata[str(i)]['err'] = curerr


        output = '{}{}_mmfsc.json'.format(self.workdir, self.mapname, )
        finaldata = {}
        finaldata['mmfsc'] = fulldata
        with open(output, 'w') as out:
            json.dump(finaldata, out)

        return None

    @staticmethod
    def compute_surface_area_two(mrc_file, contour_level):
        """
        Compute the surface area of a 3D cryo-EM density map at a given contour level.
        Returns:
            float: Surface area in arbitrary units, or None if failed.
        """
        try:
            with mrcfile.open(mrc_file, permissive=True) as mrc:
                volume = mrc.data.astype(np.float32)
                voxel_size = mrc.voxel_size['x']

            verts, faces, _, _ = measure.marching_cubes(volume, level=contour_level)

            def triangle_area(v1, v2, v3):
                return 0.5 * np.linalg.norm(np.cross(v2 - v1, v3 - v1))

            surface_area = sum(triangle_area(verts[f[0]], verts[f[1]], verts[f[2]]) for f in faces)
            surface_area *= (voxel_size ** 2)
            return surface_area

        except MemoryError:
            print("Error: Not enough memory to compute surface area.")
            sys.exit(1)
        except Exception as e:
            print(f"Error during surface area computation: {e}")
            return None

    def compute_surface_ratios_two(self, map_one, map_two):
        """
        Compute the surface ratios of the primary map and raw map before masking.

        :param map_one: Name of the primary map file
        :param map_two: Name of the raw map file
        :return: Surface ratio before masking (maptwo / mapone)
        """

        primary_map = mrcfile.open(map_one)
        primary_data = primary_map.data
        predicated_contour_primary_map = calc_level_dev(primary_data)[0]
        primary_map_surface = self.compute_surface_area_two(map_one, predicated_contour_primary_map)

        raw_map = mrcfile.open(f'{map_two}')
        raw_data = raw_map.data
        predicated_contour_raw_map = calc_level_dev(raw_data)[0]
        raw_map_surface = self.compute_surface_area_two(f'{map_two}', predicated_contour_raw_map)

        surface_ratio_before_masking = keep_three_significant_digits(raw_map_surface / primary_map_surface)
        return surface_ratio_before_masking, primary_map_surface, raw_map_surface

    @profile_peak_memory()
    @execution_time('surface ratio')
    def surface_ratios(self):
        """
            Calculate surface ratios
        """
        try:
            if self.hmodd and self.hmeven:
                primary_map = self.map.fullname
                raw_map = self.rawmap.fullname
                surface_ratio_before_masking,_,_ = self.compute_surface_ratios_two(primary_map, raw_map)

                lowpassed_rawmap = f'{raw_map}_lowpassed.mrc'
                surface_ratio_lowpassed, primary_map_surface, lowpassed_rawmap_surface = self.compute_surface_ratios_two(primary_map, lowpassed_rawmap)
                surface_ratio_lowpassed_toraw, raw_map_surface, _ = self.compute_surface_ratios_two(raw_map, lowpassed_rawmap)

                relion_mask_name = f'{self.workdir}{self.mapname}_relion/mask/{self.mapname}_mask.mrc'
                masked_raw_map = MapProcessor.mask_map(raw_map, relion_mask_name)
                surface_ratio_after_masking,_,masked_raw_map_surface = self.compute_surface_ratios_two(primary_map, masked_raw_map)

                output_dict = {'surface_ratio': {'before_masking': surface_ratio_before_masking,
                                                 'lowpassed': surface_ratio_lowpassed,
                                                 'lowpassed_toraw': surface_ratio_lowpassed_toraw,
                                                 'after_masking': surface_ratio_after_masking
                                                 },
                               'surfaces': {'masked_raw_map': masked_raw_map_surface,
                                            'lowpassed_raw_map': lowpassed_rawmap_surface}
                               }
                out_json(output_dict, f'{self.workdir}{self.mapname}_surface_ratio.json')
            else:
                print('Missing half maps!!!')
        except Exception as e:
            print(f'Surface ratio calculation error: {e}')



    @profile_peak_memory()
    def fsc_relion(self):
        """
        Using Relion to calculate fsc
        """

        # Get author provided FSC here
        if self.fscfile:
            xlist = []
            ylist = []
            errlist = []
            try:
                filefsc = self.workdir + self.fscfile
                tree = ET.parse(filefsc)
                root = tree.getroot()
                for child in root:
                    x = float(child.find('x').text)
                    y = float(child.find('y').text)
                    xlist.append(x)
                    ylist.append(y)
            except:
                err = 'Read FSC from XML error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')
        else:
            print('Inside Relion FSC: no given FSC information.')
            xlist = None
            ylist = None

        try:
            star_file = relion_fsc_calculation(self.hmodd.fullname, self.hmeven.fullname, self.workdir, self.mapname)
            # temporary line for get process all intersections
            # star_file = f'{self.workdir}/emd_{self.emdid}.map_relion/fsc/fsc.star'
            # star_file = '/Users/zhe/Downloads/tests/VA/nfs/msd/work2/emdb/development/staging/em/81/8117/va/emd_8117.map_relion/fsc/fsc.star'
            #star_file = '/Users/zhe/Downloads/tests/VA/nfs/msd/work2/emdb/development/staging/em/37/6/37676/va/emd_37676.map_relion/fsc/fsc.star'
            #star_file = '/Users/zhe/Downloads/tests/VA/nfs/msd/work2/emdb/development/staging/em/42/5/42532/va/emd_42532.map_relion/fsc/fsc.star'
            star = GetStars(star_file)
            initial_fsc_block = star.data_fsc_block()
            data_fsc_block = star.data_extra(initial_fsc_block)
            data_curves = star.all_curves(data_fsc_block)
            zones = star.feature_zone(data_curves)
            if xlist and ylist:
                star.plot_fsc(data_curves, (xlist, ylist))
            else:
                star.plot_fsc(data_curves)
            data_intersections = star.all_intersection(data_fsc_block)

            fsc_dict = {**data_curves, **data_intersections, **zones}
            out_dict = {}
            out_dict['relion_fsc'] = fsc_dict

            if self.platform == 'emdb':
                check_file = f'{self.check_dir}/check_fsc.json'
                va_zones_file = f'{self.check_dir}/va_zones.json'
                checker = FSCChecks(fsc_dict)
                checker.fsc_checks(check_file)
                out_json(zones, va_zones_file)
            out_fsc_json = f'{self.workdir}{self.mapname}_fsc_relion.json'
            out_json(out_dict, out_fsc_json)
        except Exception as e:
            print(e)

    @profile_peak_memory()
    def fscs(self):
        """
            FSC calculation and read provided FSC if exist
        :return: None
        """

        fscxmlre = '*_fsc.xml'
        fscxmlarr = glob.glob(self.workdir + fscxmlre)
        if fscxmlarr or self.fscfile:
            startfsc = timeit.default_timer()
            self.readfsc()
            stop = timeit.default_timer()
            print('Load FSC: %s' % (stop - startfsc))
            print('------------------------------------')
        else:
            print('No given FSC data to be loaded.')

        if self.hmeven is not None and self.hmodd is not None:
            startfsc = timeit.default_timer()
            # self.fsc(self.hmeven, self.hmodd)
            self.new_fsc(self.hmeven, self.hmodd)
            end = timeit.default_timer()
            print('FSC own: %s' % (end - startfsc))
            print('------------------------------------')
            self.fsc_relion()
            stop = timeit.default_timer()
            print('FSC: %s' % (stop - end))
            print('------------------------------------')
        else:
            print('Mising half map(s).')


    def readfsc(self, asym=1.0):
        """

        :return:
        """
        import xml.etree.ElementTree as ET

        errlist = []
        finaldict = dict()

        if self.hmodd and self.hmeven:
            if self.fscfile is not None:
                xlist = []
                ylist = []
                map_zsize = self.hmeven.header.nz
                map_ysize = self.hmeven.header.ny
                map_xsize = self.hmeven.header.nx
                try:
                    filefsc = self.workdir + self.fscfile
                    tree = ET.parse(filefsc)
                    root = tree.getroot()
                    for child in root:
                        x = float(child.find('x').text)
                        y = float(child.find('y').text)
                        xlist.append(x)
                        ylist.append(y)
                except:
                    err = 'Read FSC from XML error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

                try:
                    # Grid here to generate for tracing the indices of grids with in the shells.
                    zgrid = np.arange(floor(map_zsize / 2.0) * -1, ceil(map_zsize / 2.0)) / float(
                        floor(map_zsize))
                    ygrid = np.arange(floor(map_ysize / 2.0) * -1, ceil(map_ysize / 2.0)) / float(
                        floor(map_ysize))
                    xgrid = np.arange(floor(map_xsize / 2.0) * -1, ceil(map_xsize / 2.0)) / float(
                        floor(map_xsize))
                    xdis = xgrid ** 2
                    ydis = ygrid ** 2
                    zdis = zgrid ** 2
                    # dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

                    allaxis = np.array([zgrid, ygrid, xgrid])
                    tmpindiaxis = max(allaxis, key=len)
                    indiaxist = tmpindiaxis[tmpindiaxis >= 0]
                    lindi = len(indiaxist)
                    # indiaxis = np.linspace(0, 1 / (2 * cpmap.apix), lindi)

                    # Looping through all shells
                    threesig = []
                    halfbit = []
                    onebit = []
                    # for i in range(len(indiaxis)):
                    for i in range(len(xlist)):
                        # if i < len(indiaxis) - 1:
                            # indices = np.argwhere((dist >= indiaxist[i]) & (dist < indiaxist[i + 1]))

                        volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                        nvoxring = volumediff / (1 ** 3)
                        effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                        if effnvox < 1.0: effnvox = 1.0
                        sqreffnvox = np.sqrt(effnvox)

                        # 3-sigma curve
                        if i != 0:
                            sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                        else:
                            sigvalue = 1
                        threesig.append(sigvalue)

                        # Half bit curve
                        if i != 0:
                            bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                        else:
                            bitvalue = 1
                        halfbit.append(bitvalue)

                        if i != 0:
                            onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                        else:
                            onebitvalue = 1
                        onebit.append(onebitvalue)

                    if ylist[0] <= 0:
                        ylist[0] = 1

                    a = np.asarray(xlist)
                    b = np.asarray(ylist)
                    c = np.asarray(threesig)
                    d = np.asarray(halfbit)
                    e = np.asarray(onebit)
                    f = np.full((len(xlist)), 0.5)
                    g = np.full((len(xlist)), 0.333)
                    h = np.full((len(xlist)), 0.143)

                    if len(c) < len(b):
                        b = b[:len(c)]
                    else:
                        c = c[:len(b)]

                    if len(d) < len(b):
                        b = b[:len(d)]
                    else:
                        d = d[:len(b)]


                    if len(e) < len(b):
                        b = b[:len(e)]
                    else:
                        e = e[:len(b)]


                    if len(f) < len(b):
                        b = b[:len(f)]
                    else:
                        f = f[:len(b)]


                    if len(g) < len(b):
                        b = b[:len(g)]
                    else:
                        g = g[:len(b)]

                    if len(h) < len(b):
                        b = b[:len(h)]
                    else:
                        h = h[:len(b)]

                    xthreesig, ythreesig = self.__interpolated_intercept(a, b, c)
                    xhalfbit, yhalfbit = self.__interpolated_intercept(a, b, d)
                    xonebit, yonebit = self.__interpolated_intercept(a, b, e)
                    xhalf, yhalf = self.__interpolated_intercept(a, b, f)
                    xonethree, yonethree = self.__interpolated_intercept(a, b, g)
                    xgold, ygold = self.__interpolated_intercept(a, b, h)

                    if xthreesig.size == 0 and ythreesig.size == 0:
                        txthreesig = None
                        tythreesig = None
                    else:
                        txthreesig = np.round(xthreesig[0][0], 4)
                        tythreesig = np.round(ythreesig[0][0], 4)

                    if xhalfbit.size == 0 and yhalfbit.size == 0:
                        txhalfbit = None
                        tyhalfbit = None
                    else:
                        if np.isnan(xhalfbit[0][0]):
                            txhalfbit = None
                            tyhalfbit = None
                            print('!!! The loaded fsc has no intersection with the half bit curve !!!')
                        else:
                            txhalfbit = np.round(xhalfbit[0][0], 4)
                            tyhalfbit = np.round(yhalfbit[0][0], 4)

                    if xonebit.size == 0 and yonebit.size == 0:
                        txonebit = None
                        tyonebit = None
                    else:
                        txonebit = np.round(xonebit[0][0], 4)
                        tyonebit = np.round(yonebit[0][0], 4)

                    if xhalf.size == 0 and yhalf.size == 0:
                        txhalf = None
                        tyhalf = None
                    else:
                        txhalf = np.round(xhalf[0][0], 4)
                        tyhalf = np.round(yhalf[0][0], 4)

                    if xonethree.size == 0 and yonethree.size == 0:
                        txonethree = None
                        tyonethree = None
                    else:
                        txonethree = np.round(xonethree[0][0], 4)
                        tyonethree = np.round(yonethree[0][0], 4)

                    if xgold.size == 0 and ygold.size == 0:
                        txgold = None
                        tygold = None
                    else:
                        txgold = np.round(xgold[0][0], 4)
                        tygold = np.round(ygold[0][0], 4)

                    xlen = len(xlist)

                    datadict = {
                        'curves': {'fscy': np.round(np.real(ylist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist()[:xlen],
                                   'halfbit': np.round(halfbit, 4).tolist()[:xlen],
                                   'onebit': np.round(onebit, 4).tolist()[:xlen], '0.5': f.tolist()[:xlen], '0.333': g.tolist()[:xlen],
                                   '0.143': h.tolist()[:xlen],
                                   # one of the following can be removed after remediation
                                   'level': np.round(np.real(xlist), 4).tolist(),
                                   'fscx': np.round(np.real(xlist), 4).tolist()},
                        'intersections': {'threesig': {'x': txthreesig, 'y': tythreesig},
                                          'halfbit': {'x': txhalfbit, 'y': tyhalfbit},
                                          'onebit': {'x': txonebit, 'y': tyonebit},
                                          '0.5': {'x': txhalf, 'y': tyhalf},
                                          '0.333': {'x': txonethree, 'y': tyonethree},
                                          '0.143': {'x': txgold, 'y': tygold}}}

                    finaldict['load_fsc'] = datadict

                    plt.plot(xlist, ylist, label='Provided FSC')
                    #plt.plot(indiaxis, threesig, label='3 sigma')
                    #plt.plot(indiaxis, halfbit, label='1/2 bit')
                    #plt.plot(indiaxis, onebit, label='1 bit')
                    plt.plot(xlist[:-1], len(xlist[:-1])*[0.5], linestyle=':', label='_nolegend_')
                    #plt.plot(indiaxis, g, label='0.333', linestyle='--')
                    plt.plot(xlist[:-1], len(xlist[:-1])*[0.143], linestyle='-.', label='_nolegend_')
                    plt.legend()
                    # plt.savefig(self.workdir + self.mapname + '_fsc.png')
                    # plt.close()
                except:
                    err = 'FSC reading error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

                if errlist:
                    finaldict['load_fsc'] = {'err': {'load_fsc_err': errlist}}

                try:
                    with codecs.open(self.workdir + self.mapname + '_loadfsc.json', 'w', encoding='utf-8') as f:
                        json.dump(finaldict, f)

                    return None
                except:
                    sys.stderr.write('Saving loaded FSC to json error:{}.\n'.format(sys.exc_info()[1]))
            else:
                print('No fsc.xml file can be read for FSC information.')
        else:
            if self.fscfile is not None:
                xlist = []
                ylist = []
                try:
                    filefsc = self.workdir + self.fscfile
                    tree = ET.parse(filefsc)
                    root = tree.getroot()
                    for child in root:
                        x = float(child.find('x').text)
                        y = float(child.find('y').text)
                        xlist.append(x)
                        ylist.append(y)

                    ax = np.asarray(xlist)
                    ay = np.asarray(ylist)
                    golden_line = np.full((len(xlist)), 0.143)
                    half_line = np.full((len(xlist)), 0.5)
                    xhalf, yhalf = self.__interpolated_intercept(ax, ay, half_line)
                    xgold, ygold = self.__interpolated_intercept(ax, ay, golden_line)
                    datadict = {
                        'curves': {'fscy': ylist,
                                   '0.143': golden_line.tolist(),
                                   '0.5': half_line.tolist(),
                                   'level': xlist,
                                   'fscx': xlist},
                        'intersections': {
                                          '0.5': {'x':np.round(xhalf[0][0], 4), 'y':np.round(yhalf[0][0], 4)},
                                          '0.143': {'x':np.round(xgold[0][0], 4), 'y':np.round(ygold[0][0], 4)}}}

                    finaldict['load_fsc'] = datadict

                    plt.plot(xlist, ylist, label='Provided FSC')
                    plt.plot(xlist[:-1], len(xlist[:-1])*[0.5], linestyle=':', label='_nolegend_')
                    plt.plot(xlist[:-1], len(xlist[:-1])*[0.143], linestyle='-.', label='_nolegend_')
                    plt.legend()
                    plt.savefig(self.workdir + self.mapname + '_fsc.png')

                except:
                    err = 'Read FSC from XML error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

                if errlist:
                    finaldict['load_fsc'] = {'err': {'load_fsc_err': errlist}}

                try:
                    with codecs.open(self.workdir + self.mapname + '_loadfsc.json', 'w', encoding='utf-8') as f:
                        json.dump(finaldict, f)

                    return None
                except:
                    sys.stderr.write('Saving composited map provided FSC to json error:{}.\n'.format(sys.exc_info()[1]))





    # @profile
    def fsc(self, mapodd, mapeven, asym=1.0, label=''):
        """

            Calculate FSC based on the two input half maps
            Results wrote to JSON file including resolution at 0.143, 0.333, 0.5 and noise
            level at 0.5-bit, 1-bit, 3-sigma. A corresponding plot is also save as PNG file.

        :param mapodd: TEMPy map instance
        :param mapeven: TEMPy map instance
        :return: None

        """

        start = timeit.default_timer()
        errlist = []
        datadict = dict()
        finaldict = dict()
        try:
            assert mapodd.data.shape == mapeven.data.shape, 'The two half maps do not have same size.'
            assert mapodd.voxel_size == mapeven.voxel_size, 'The two half maps do not have same apix.'
            oddnan = np.isnan(mapodd.data).any()
            evennan = np.isnan(mapeven.data).any()
            nancheck = oddnan | evennan
            assert not nancheck, 'There is NaN value in half map.'

            map_zsize = mapodd.header.nz
            map_ysize = mapodd.header.ny
            map_xsize = mapodd.header.nx

            apixs = tuple(mapodd.voxel_size.tolist())

            mapodd_data = fftshift(fftn(mapodd.data))
            mapeven_data = fftshift(fftn(mapeven.data))

            start = timeit.default_timer() - start
            print(' -- FSC Fourier-transformation time: %s' % start)

            # Grid here to generate for tracing the indices of grids with in the shells.
            zgrid = np.arange(floor(map_zsize / 2.0) * -1, ceil(map_zsize / 2.0)) / float(
                floor(map_zsize))
            ygrid = np.arange(floor(map_ysize / 2.0) * -1, ceil(map_ysize / 2.0)) / float(
                floor(map_ysize))
            xgrid = np.arange(floor(map_xsize / 2.0) * -1, ceil(map_xsize / 2.0)) / float(
                floor(map_xsize))
            xdis = xgrid ** 2
            ydis = ygrid ** 2
            zdis = zgrid ** 2
            dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

            allaxis = np.array([zgrid, ygrid, xgrid])
            tmpindiaxis = max(allaxis, key=len)
            indiaxist = tmpindiaxis[tmpindiaxis >= 0]
            lindi = len(indiaxist)
            if type(apixs) is tuple:
                tapix = apixs[0]
            else:
                tapix = apixs
            indiaxis = np.linspace(0, 1 / (2 * tapix), lindi)

            # Looping through all shells
            corrlist = []
            threesig = []
            halfbit = []
            onebit = []
            for i in range(len(indiaxis)):
                if i == 0:
                    indices = np.argwhere(dist == indiaxis[i])
                    oddring = mapodd_data[tuple(indices.T)]
                    evenring = mapeven_data[tuple(indices.T)]

                elif i != len(indiaxis) - 1:
                    indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
                    oddring = mapodd_data[tuple(indices.T)]
                    evenring = mapeven_data[tuple(indices.T)]
                else:
                    pass
                corr = (oddring * np.conj(evenring)).sum()
                corr_deno = np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum())
                if corr_deno == 0.:
                    norcorr = 0.
                else:
                    norcorr = np.real(corr / corr_deno)
                corrlist.append(norcorr)

                volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                nvoxring = volumediff / (1 ** 3)
                effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                if effnvox < 1.0: effnvox = 1.0
                sqreffnvox = np.sqrt(effnvox)


                # 3-sigma curve
                if i != 0:
                    sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                else:
                    sigvalue = 1
                threesig.append(sigvalue)

                # Half bit curve
                if i != 0:
                    bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                else:
                    bitvalue = 1
                halfbit.append(bitvalue)

                if i != 0:
                    onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                else:
                    onebitvalue = 1
                onebit.append(onebitvalue)
            print(corrlist)

            if corrlist[0] <= 0:
                corrlist[0] = 1
            a = np.asarray(indiaxis)
            b = np.asarray(corrlist)
            c = np.asarray(threesig)
            d = np.asarray(halfbit)
            e = np.asarray(onebit)
            f = np.full((len(indiaxis)), 0.5)
            g = np.full((len(indiaxis)), 0.333)
            h = np.full((len(indiaxis)), 0.143)
            # use [:1] to ignore all the curves start from 0,1
            xthreesig, ythreesig = self.__interpolated_intercept(a, b, c)
            xhalfbit, yhalfbit = self.__interpolated_intercept(a, b, d)
            xonebit, yonebit = self.__interpolated_intercept(a, b, e)
            xhalf, yhalf = self.__interpolated_intercept(a, b, f)

            # Check if mm in label then, see which intersecion is the most closest to the given resolution(Todo)
            if 'mm' in label:
                if xhalf.size != 0:
                    newxhalf = abs(xhalf - 1 / float(self.resolution))
                    indmin = np.argmin(newxhalf)
                    xhalf = np.array([xhalf[indmin]])
                    yhalf = np.array([yhalf[indmin]])

            xonethree, yonethree = self.__interpolated_intercept(a, b, g)
            xgold, ygold = self.__interpolated_intercept(a, b, h)

            # Assign intersection value as None when there is no intersection
            if xthreesig.size == 0 and ythreesig.size == 0:
                print('No intersection between FSC and 3-sigma curves. Here use the last point.')
                xthreesig, ythreesig = None, None
            else:
                xthreesig = np.round(xthreesig[0][0], 4)
                ythreesig = np.round(ythreesig[0][0], 4)

            if xhalfbit.size == 0 and yhalfbit.size == 0:
                print('No intersection between FSC and 1/2-bit curves. Here use the last point.')
                xhalfbit, yhalfbit = None, None
            else:
                xhalfbit = np.round(xhalfbit[0][0], 4)
                yhalfbit = np.round(yhalfbit[0][0], 4)

            if xonebit.size == 0 and yonebit.size == 0:
                print('No intersection between FSC and 1-bit curves. Here use the last point.')
                xonebit, yonebit = None, None
            else:
                xonebit = np.round(xonebit[0][0], 4)
                yonebit = np.round(yonebit[0][0], 4)

            if xonethree.size == 0 and yonethree.size == 0:
                print('No intersection between FSC and 0.333 curves. Here use the last point')
                xonethree, yonethree = None, None
            else:
                xonethree = np.round(xonethree[0][0], 4)
                yonethree = np.round(yonethree[0][0], 4)

            if xhalf.size == 0 and yhalf.size == 0:
                print('!!! No intersection between FSC and 0.5 curves. Here use the last point')
                xhalf, yhalf = None, None
            else:
                xhalf = np.round(xhalf[0][0], 4)
                yhalf = np.round(yhalf[0][0], 4)
            if xgold.size == 0 and ygold.size == 0:
                print('!!! No intersection between FSC and 0.143 curves. Here use the last point')
                xgold, ygold = None, None
            else:
                xgold = np.round(xgold[0][0], 4)
                ygold = np.round(ygold[0][0], 4)


            datadict = {
                'curves': {'fsc': np.round(np.real(corrlist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist(),
                           'halfbit': np.round(halfbit, 4).tolist(),
                           'onebit': np.round(onebit, 4).tolist(), '0.5': f.tolist(), '0.333': g.tolist(),
                           '0.143': h.tolist(),
                           'level': np.round(indiaxis, 4).tolist()},
                'intersections': {'threesig': {'x': xthreesig, 'y': ythreesig},
                                  'halfbit': {'x': xhalfbit, 'y': yhalfbit},
                                  'onebit': {'x': xonebit, 'y': yonebit},
                                  '0.5': {'x': xhalf, 'y': yhalf},
                                  '0.333': {'x': xonethree, 'y': yonethree},
                                  '0.143': {'x': xgold, 'y': ygold}}}
            finaldict = dict()
            finaldict[label + 'fsc'] = datadict

            plt.plot(indiaxis, corrlist, label=label + 'FSC')
            # plt.plot(indiaxis, threesig, label='3 sigma')
            plt.plot(indiaxis, halfbit, label='1/2 bit')
            # plt.plot(indiaxis, onebit, label='1 bit')
            plt.plot(indiaxis, f, label='0.5', linestyle=':')
            # plt.plot(indiaxis, g, label='0.333', linestyle='--')
            plt.plot(indiaxis, h, label='0.143', linestyle='-.')
            plt.legend()
            if label:
                plt.savefig(self.workdir + self.mapname + '_' + label + '_fsc.png')
            else:
                plt.savefig(self.workdir + self.mapname + '_fsc.png')
            plt.close()

        except:
            err = 'FSC calculation error: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {'err': {label + 'fsc_error': errlist}}
            finaldict[label + 'fsc'] = datadict
        else:
            print('No error in FSC calculation.')

        if bool(datadict) and bool(finaldict):
            try:
                with codecs.open(self.workdir + self.mapname + '_' + label + 'fsc.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('FSC produced by two half maps.')
            except:
                sys.stderr.write('Writing FSC data to json file error: {}.'.format(sys.exc_info()[1]))
        else:
            sys.stderr.write('FSC calculation get none ')

        return None


    @profile_peak_memory()
    def new_fsc(self, mapodd, mapeven, asym=1.0, label=''):
        """

            Calculate FSC based on the two input half maps
            Results wrote to JSON file including resolution at 0.143, 0.333, 0.5 and noise
            level at 0.5-bit, 1-bit, 3-sigma. A corresponding plot is also save as PNG file.

        :param mapodd: TEMPy map instance
        :param mapeven: TEMPy map instance
        :return: None

        """

        start = timeit.default_timer()
        errlist = []
        datadict = dict()
        finaldict = dict()
        # evenname = os.path.basename(mapeven.fullname)
        # oddname = os.path.basename(mapodd.fullname)
        try:
            assert mapodd.data.shape == mapeven.data.shape, 'The two half maps do not have same size.'
            assert mapodd.voxel_size == mapeven.voxel_size, 'The two half maps do not have same apix.'
            oddnan = np.isnan(mapodd.data).any()
            evennan = np.isnan(mapeven.data).any()
            nancheck = oddnan | evennan
            assert not nancheck, 'There is NaN value in half map.'
            # Assume all dimension are the same size

            apixs = tuple(mapodd.voxel_size.tolist())

            mapodd_data = fftshift(fftn(mapodd.data))
            mapodd.close()
            mapeven_data = fftshift(fftn(mapeven.data))
            mapeven.close()

            start = timeit.default_timer() - start
            print(' -- FSC Fourier-transformation time: %s' % start)

            if type(apixs) is tuple:
                tapix = apixs[0]
            else:
                tapix = apixs

            # Looping through all shells
            corrlist = []
            threesig = []
            halfbit = []
            onebit = []

            ## applying new indices function
            map_shape = mapodd_data.shape
            if min(map_shape) % 2 == 0:
                org = [map_shape[0] / 2, map_shape[1] / 2, map_shape[2] / 2]
                indiaxis = np.linspace(0, int(min(org)), int(min(org)) + 1) / (min(map_shape) * tapix)
            else:
                org = [(map_shape[0] - 1) / 2, (map_shape[1] - 1) / 2, (map_shape[2] - 1) / 2]
                indiaxis = np.linspace(0, int(min(org)), int(min(org)) + 1) / (min(map_shape) * tapix)
                indiaxis = np.append(indiaxis, 1/(2 * tapix))
            # indiaxis = np.linspace(0, int(org[0]), int(org[0]) + 1) / (map_shape[0] * tapix)
            shell_range = int(min(map_shape) - min(org))
            for i in range(0, shell_range):
                indices = self.generate_shell(i, i + 1, map_shape)
                oddring = mapodd_data[tuple(indices.T)]
                evenring = mapeven_data[tuple(indices.T)]
                corr = (oddring * np.conj(evenring)).sum()
                corr_deno = np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum())
                if corr_deno == 0.:
                    norcorr = 0.
                else:
                    norcorr = np.real(corr / corr_deno)
                corrlist.append(norcorr)

                volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                nvoxring = volumediff / (1 ** 3)
                effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                if effnvox < 1.0: effnvox = 1.0
                sqreffnvox = np.sqrt(effnvox)

                sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                threesig.append(sigvalue)
                bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                halfbit.append(bitvalue)
                onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                onebit.append(onebitvalue)

            corrlist.insert(0, 1)
            threesig.insert(0, 1)
            halfbit.insert(0, 1)
            onebit.insert(0, 1)
            del mapodd_data
            del mapeven_data

            # If any of the first 5 values is negative, make it to 1
            for i in range(0, 5):
                if corrlist[i] <= 0:
                    corrlist[i] = 1

            a = np.asarray(indiaxis)
            b = np.asarray(corrlist)
            c = np.asarray(threesig)
            d = np.asarray(halfbit)
            e = np.asarray(onebit)
            f = np.full((len(indiaxis)), 0.5)
            g = np.full((len(indiaxis)), 0.333)
            h = np.full((len(indiaxis)), 0.143)
            # use [:1] to ignore all the curves start from 0,1
            xthreesig, ythreesig = self.__interpolated_intercept(a, b, c)
            xhalfbit, yhalfbit = self.__interpolated_intercept(a, b, d)
            xonebit, yonebit = self.__interpolated_intercept(a, b, e)
            xhalf, yhalf = self.__interpolated_intercept(a, b, f)

            # Check if mm in label then, see which intersecion is the most closest to the given resolution(Todo)
            if 'mm' in label:
                if xhalf.size != 0:
                    newxhalf = abs(xhalf - 1 / float(self.resolution))
                    indmin = np.argmin(newxhalf)
                    xhalf = np.array([xhalf[indmin]])
                    yhalf = np.array([yhalf[indmin]])

            xonethree, yonethree = self.__interpolated_intercept(a, b, g)
            xgold, ygold = self.__interpolated_intercept(a, b, h)

            # Assign intersection value as None when there is no intersection
            if xthreesig.size == 0 and ythreesig.size == 0:
                print('No intersection between FSC and 3-sigma curves. Here use the last point.')
                xthreesig, ythreesig = None, None
            else:
                xthreesig = np.round(xthreesig[0][0], 4)
                ythreesig = np.round(ythreesig[0][0], 4)

            if xhalfbit.size == 0 and yhalfbit.size == 0:
                print('No intersection between FSC and 1/2-bit curves. Here use the last point.')
                xhalfbit, yhalfbit = None, None
            else:
                xhalfbit = np.round(xhalfbit[0][0], 4)
                yhalfbit = np.round(yhalfbit[0][0], 4)

            if xonebit.size == 0 and yonebit.size == 0:
                print('No intersection between FSC and 1-bit curves. Here use the last point.')
                xonebit, yonebit = None, None
            else:
                xonebit = np.round(xonebit[0][0], 4)
                yonebit = np.round(yonebit[0][0], 4)

            if xonethree.size == 0 and yonethree.size == 0:
                print('No intersection between FSC and 0.333 curves. Here use the last point')
                xonethree, yonethree = None, None
            else:
                xonethree = np.round(xonethree[0][0], 4)
                yonethree = np.round(yonethree[0][0], 4)

            if xhalf.size == 0 and yhalf.size == 0:
                print('!!! No intersection between FSC and 0.5 curves. Here use the last point')
                xhalf, yhalf = None, None
            else:
                xhalf = np.round(xhalf[0][0], 4)
                yhalf = np.round(yhalf[0][0], 4)
            if xgold.size == 0 and ygold.size == 0:
                print('!!! No intersection between FSC and 0.143 curves. Here use the last point')
                xgold, ygold = None, None
            else:
                xgold = np.round(xgold[0][0], 4)
                ygold = np.round(ygold[0][0], 4)


            datadict = {
                'curves': {'fsc': np.round(np.real(corrlist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist(),
                           'halfbit': np.round(halfbit, 4).tolist(),
                           'onebit': np.round(onebit, 4).tolist(), '0.5': f.tolist(), '0.333': g.tolist(),
                           '0.143': h.tolist(),
                           'level': np.round(indiaxis, 4).tolist()},
                'intersections': {'threesig': {'x': xthreesig, 'y': ythreesig},
                                  'halfbit': {'x': xhalfbit, 'y': yhalfbit},
                                  'onebit': {'x': xonebit, 'y': yonebit},
                                  '0.5': {'x': xhalf, 'y': yhalf},
                                  '0.333': {'x': xonethree, 'y': yonethree},
                                  '0.143': {'x': xgold, 'y': ygold}}}
            finaldict = dict()
            finaldict[label + 'fsc'] = datadict

            plt.plot(indiaxis, corrlist, label=label + 'FSC')
            # plt.plot(indiaxis, threesig, label='3 sigma')
            plt.plot(indiaxis, halfbit, label='1/2 bit')
            # plt.plot(indiaxis, onebit, label='1 bit')
            plt.plot(indiaxis, f, label='0.5', linestyle=':')
            # plt.plot(indiaxis, g, label='0.333', linestyle='--')
            plt.plot(indiaxis, h, label='0.143', linestyle='-.')
            if self.resolution is not None:
                plt.plot([1/float(self.resolution)] * 100, np.linspace(0, 1, 100), color='red')
            plt.legend()
            if label:
                plt.savefig(self.workdir + self.mapname + '_' + label + '_fsc.png')
            else:
                plt.savefig(self.workdir + self.mapname + '_fsc.png')
            plt.close()

        except:
            err = 'FSC calculation error: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {'err': {label + 'fsc_error': errlist}}
            finaldict[label + 'fsc'] = datadict
        else:
            print('No error in FSC calculation.')

        if bool(datadict) and bool(finaldict):
            try:
                with codecs.open(self.workdir + self.mapname + '_' + label + 'fsc.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('FSC produced by two half maps.')
                # with codecs.open(self.workdir + oddname + '_' + evenname + '_' + label + 'fsc.json', 'w', encoding='utf-8') as nf:
                #     json.dump(finaldict, nf)
                # print('2nd fsc saved')
            except:
                sys.stderr.write('Writing FSC data to json file error: {}.'.format(sys.exc_info()[1]))
        else:
            sys.stderr.write('FSC calculation get none ')

        return None

    @staticmethod
    def mempred(resultfile, inputfilesize):
        """

            Produce memory prediction results using linear regression
            based on the data from previous entries.


        :param resultfile: Previous memory usage information in CSV file
        :param inputfilesize: The input density map size
        :return: 0 or y_pred (the predicted memory usage)
        """
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error, r2_score
        from sklearn.model_selection import train_test_split
        from sklearn.model_selection import cross_val_score, cross_val_predict

        data = pd.read_csv(resultfile, header=0)
        data = data.dropna()
        if data.empty:
            print('No useful data in the dataframe.')
            return None
        else:
            newdata = data.iloc[:, 1:]
            sortdata = newdata.sort_values(newdata.columns[0])
            merdata = sortdata.groupby(sortdata.columns[0], as_index=False).mean()
            x = merdata['maprealsize']
            y = merdata['mem']
            if x.shape[0] <= 1:
                print('Sample is too little to split.')
                return None
            X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
            if X_train.empty or X_test.empty or y_train.empty or y_test.empty or len(x.index) < 30:
                print('Sparse data for memory prediction, result may not accurate.')
                return None
            else:
                lrmodel = LinearRegression(fit_intercept=False)
                # Perform CV
                scores = cross_val_score(lrmodel, x.values.reshape(-1, 1), y, cv=6)
                predictions = cross_val_predict(lrmodel, x.values.reshape(-1, 1), y, cv=6)

                lrmodel.fit(X_train.values.reshape(-1, 1), y_train)
                lrpredict = lrmodel.predict(X_test.values.reshape(-1, 1))
                print('6-Fold CV scores:%s' % scores)
                print('CV accuracy: %s' % (r2_score(y, predictions)))
                # print 'Score:%s' % (lrmodel.score(X_test.values.reshape(-1,1), y_test))
                print('Linear model coefficients: %s' % (lrmodel.coef_))
                print('MSE: %s' % (mean_squared_error(y_test, lrpredict)))
                print('Variance score(test accuracy): %s' % (r2_score(y_test, lrpredict)))
                y_pred = lrmodel.predict([[inputfilesize]])

                return y_pred

    @staticmethod
    def savepeakmemory(filename, maxmem):
        """

            Data collected and to be used for prediction for memory usage
            Memory saved as a comma separate CSV file.


        :param filename: String for file which used to collect data
        :param maxmem: Float number which gives peak memory usage of the finished job
        :return: None

        """

        columnname = 'mem'
        # dir = MAP_SERVER_PATH if self.emdid is not None else os.path.dirname(os.path.dirname(self.workdir))
        # filename = dir + 'input.csv'
        memresultfile = filename
        df = pd.read_csv(filename, header=0, sep=',', skipinitialspace=True)
        df[columnname][len(df.index) - 1] = maxmem
        df.to_csv(memresultfile, sep=',', index=False)

        return None


    # @profile
    def symmetry(self):
        """
            Produing symmetry information of the map by using Proshade
            This function using the binary proshade program  not the python api

        :return:  None
        """

        if self.platform == 'emdb':
            start = timeit.default_timer()
            errlist = []
            finaldict = {}
            symmetryRes = False
            resfactor = 1.0
            if self.met is not None and self.resolution is not None:
                if self.met != 'tomo' and self.met != 'heli':
                    proshade = False
                    if PROSHADEPATH:
                        proshadepath = PROSHADEPATH
                        proshade = True

                    else:
                        try:
                            assert find_executable('proshade') is not None
                            proshadepath = find_executable('proshade')
                            proshade = True
                        except AssertionError:
                            sys.stderr.write('proshade executable is not there, please install proshade.\n')
                            sys.stderr.write('Symmetry information will not be produced.\n')

                    if proshade:
                        try:
                            fullmappath = '{}{}'.format(self.workdir, self.mapname)
                            if 'ccpem' not in PROSHADEPATH:
                                # cmd = list((PROSHADEPATH + ' -S -f ' + self.map.filename + ' -s ' + str(float(self.resolution) * resfactor)).split(' '))
                                cmd = list((PROSHADEPATH + ' -S -f ' + self.map.fullname + ' -s ' + str(float(self.resolution) * resfactor)).split(' '))
                                print(cmd)
                            else:
                                shareindex = [idx for idx, s in enumerate(PROSHADEPATH.split('/')) if 'ccpem-' in s][0] + 1
                                beforeshare = '/'.join(PROSHADEPATH.split('/')[:shareindex])
                                rvpath = '{}/share'.format(beforeshare)
                                # cmd = list((PROSHADEPATH + ' -S -f ' + self.map.filename + ' -s ' + str(float(self.resolution)*1.5) + ' --rvpath ' + rvpath).split(' '))
                                cmd = list((PROSHADEPATH + ' -S -f ' + self.map.fullname + ' -s ' + str(float(self.resolution) * 1.0) + ' --rvpath ' + rvpath).split(' '))
                            print('Symmetry command: {}'.format(' '.join(cmd)))

                            # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            # code = process.wait()
                            # output = process.stdout.read()

                            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.workdir)
                            output = process.communicate('n\n')[0]
                            errproshade = '!!! ProSHADE ERROR !!!'

                            # For python3 migration to python3 with decode problem of string to bytes
                            if sys.version_info[0] >= 3:
                                for item in output.decode('utf-8').split('\n'):
                                    # item = cline.decode('utf-8').strip()
                                    print(item)
                                    if errproshade in item:
                                        errline = item.strip()
                                        errlist.append(errline)
                                        assert errproshade not in output.decode('utf-8'), errline
                            else:
                                for item in output.split('\n'):
                                    print(item)
                                    if errproshade in item:
                                        errline = item.strip()
                                        errlist.append(errline)
                                        assert errproshade not in output.decode('utf-8'), errline

                            proshadefolder = self.workdir + 'proshade_report'
                            sym_tables = '{}/*.table'.format(proshadefolder)
                            nfileinproshade = len([f for f in glob.glob(sym_tables)])
                            # nfileinproshade = len([f for f in os.listdir(proshadefolder) if os.path.isfile(os.path.join(proshadefolder, f))])
                            if nfileinproshade >= 3:
                                symmetryRes = True
                            # splstr = 'RESULTS'
                            # outputspl = output.split('Detected Cyclic symmetry', 1)
                            # outputspl = re.split('RESULTS', output.decode())
                            # if splstr in output.decode():
                            #     print(outputspl[1])
                            # else:
                            #     print(outputspl[0])

                            # self.moveproshadeResult()
                            end = timeit.default_timer()
                            print('Symmetry time: %s' % (end - start))
                            print('------------------------------------')
                        except:
                            err = 'Symmetry calculation error: {}.'.format(sys.exc_info()[1])
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                            print('------------------------------------')

                        if errlist:
                            finaldict['symmetry'] = {'err': {'symmetry_err': errlist}}
                        else:
                            finaldict['symmetry'] = {'symmetry_info': symmetryRes}

                        try:
                            with codecs.open(self.workdir + self.mapname + '_symmetry.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finaldict, f)
                        except IOError as ioerr:
                            sys.stderr.write('Saving symmetry information to json err: {}.\n'.format(ioerr))



                    else:
                        sys.stderr.write('Proshade is not installed. There will be no symmetry information.\n')
                        print('------------------------------------')

                else:
                    sys.stderr.write('This is a {} entry, symmetry will not be calculated.\n'.format(self.met))
                    print('------------------------------------')

            else:
                sys.stderr.write('EM method and resolution needed to calculated symmetry information!\n')
                print('------------------------------------')

        return None

    # Q-score related started from here
    def ochimeracheck(self):
        """

            Check where is old Chimera not for ChimeraX

        :return: the path of old Chimera or None with no Chimera
        """

        ochimeraapp = None
        try:
            if OCHIMERA is not None:
                ochimeraapp = OCHIMERA
                print('Chimera: {}'.format(ochimeraapp))
            else:
                assert find_executable('chimera') is not None
                ochimeraapp = find_executable('chimera')
                print('Chimera: {}'.format(ochimeraapp))

        except AssertionError:
            sys.stderr.write('ChimeraX executable is not there.\n')

        return ochimeraapp

    def checkqscore(self, ochimeraapp):

        """

            Check if Qscore is properly installed

        :return: Qscore file full path or None
        """

        qscoreapp = None
        if ochimeraapp:
            # check if ochimeraapp is a symbolic link
            if os.path.islink(ochimeraapp):
                realchimeraapp = os.path.realpath(path)
            else:
                realchimeraapp = ochimeraapp

            if 'Content' in realchimeraapp:
                vorcontent = ochimeraapp.split('Content')[0]
                mapq = vorcontent + 'Contents/Resources/share/mapq/mapq_cmd.py'
                qscoreapp = mapq if os.path.isfile(mapq) else None
            elif 'bin' in realchimeraapp:
                vorcontent = ochimeraapp.split('bin')[0]
                mapq = vorcontent + 'share/mapq/mapq_cmd.py'
                qscoreapp = mapq if os.path.isfile(mapq) else None
            else:
                print('Chimera is not given in a proper executable or symbolic link format.')
        else:
            print('Chimera was not found.')

        return qscoreapp

    def atom_numbers(self, model_filename):
        """
            Get the number of atoms in the model
        :param model_filename: string of full model name with path
        :return: integer of number of atoms
        """

        parser = MMCIFParser()
        structure = parser.get_structure('t', model_filename)
        atoms = structure.get_atoms()

        return sum(1 for _ in atoms)

    @profile_peak_memory()
    def qscore_bar(self):

        if not self.onlybar:
            # testing q score module now
            qscore = Qscore(self.workdir, self.mapname, self.models, self.resolution)
            qscore.class_qscore()
            # Old way
            # self.qscore()
        self.get_bar(score_type='qscore')

    # @profile
    def qscore(self):
        """

            Calculate Q-score

        :return:
        """

        errlist = []
        qscoreapp = None
        ochimeraapp = None
        mapname = None
        models = None
        # use a fix value for now, may consider as a argument for later
        numofcores = int(os.cpu_count() / 2)

        if self.resolution is None or float(self.resolution) >= 1.25:
            try:
                ochimeraapp = self.ochimeracheck()
                qscoreapp = self.checkqscore(ochimeraapp)
                mapname = self.map.fullname
                if self.models is not None:
                    models = ' '.join(['cif=' + model.filename for model in self.models])
                    atom_number_all = []
                    for model in self.models:
                        # for models with extra data blocks
                        moderated_cif = '{}_moderated.cif'.format(os.path.basename(model.filename))
                        if os.path.isfile(self.workdir + moderated_cif):
                            atom_number_all.append(self.atom_numbers(self.workdir + moderated_cif))
                        else:
                            atom_number_all.append(self.atom_numbers(model.filename))

                    if numofcores > min(atom_number_all):
                        numofcores = min(atom_number_all)
                else:
                    print('No fitted model.')

            except:
                err = 'Q-score preparation error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            # models = ' '.join(['myfirst.cif', 'mysecond.cif'])       # fake test point for multiple cif files
            if qscoreapp and self.models:
                # old Qscore
                # qscorecmd = '{} --nogui --nostatus {} {} {}'.format(ochimeraapp, mapname, models, qscoreapp)
                vorcontents = ochimeraapp.split('Contents')[0] if 'Contents' in ochimeraapp else ochimeraapp.split('bin')[0]
                qscorecmd = '{} {} {} map={} {} np={} res={} sigma=0.4'.format(sys.executable, qscoreapp, vorcontents,
                                                                 mapname, models, numofcores, self.resolution)
                print(qscorecmd)
                lqscorecmd = qscorecmd.split(' ')
                try:
                    process = subprocess.Popen(lqscorecmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               cwd=self.workdir)
                    output = process.communicate('n\n')[0]
                    errqscore = 'error'
                    if sys.version_info[0] >= 3:
                        for item in output.decode('utf-8').split('\n'):
                            # item = cline.decode('utf-8').strip()
                            print(item)
                            if errqscore in item.lower():
                                errline = item.strip()
                                errlist.append(errline)
                                assert errqscore not in output.decode('utf-8'), errline

                    else:
                        for item in output.split('\n'):
                            print(item)
                            if errqscore in item.lower():
                                errline = item.strip()
                                errlist.append(errline)
                                assert errqscore not in output.decode('utf-8'), errline
                    self.postqscore()

                except:
                    err = 'Q-score calculation error: {}'.format(sys.exc_info()[1])
                    print(traceback.format_exc())
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

            else:
                print('Chimera is not detected or no fitted model for this entry. Qscore will not be calculated.')

        return None


    def postqscore(self):

        # self.renameqfiles()
        try:
            self.newread_qscore()
            vtkpack, chimeraapp = self.surface_envcheck()
            self.qscoreview(chimeraapp)
        except:
            err = 'Q-score results processing failed: {}'.format(sys.exc_info()[1])
            print(traceback.format_exc())
            sys.stderr.write(err + '\n')

        return None

    def renameqfiles(self):
        """
            Rename Q-score output files if in-case, they use *_Alt_A/B.cif to produce the result

        :return:
        """
        altfiles = glob.glob('{}/*.*_Alt_*__Q__emd_*.pdb'.format(self.workdir))
        if altfiles:
            for altfile in altfiles:
                altdir = os.path.dirname(altfile)
                altpdb = os.path.basename(altfile)
                newpdb = re.sub('.cif_Alt_.', '', altpdb)
                alttxt = '{}_All.txt'.format(altpdb[:-4])
                newtxt = '{}_All.txt'.format(newpdb[:-4])
                os.rename('{}/{}'.format(altdir, altpdb), '{}/{}'.format(altdir, newpdb))
                os.rename('{}/{}'.format(altdir, alttxt), '{}/{}'.format(altdir, newtxt))
        else:
            print('No alternative coordinates exist.')

        return None

    def newread_qscore(self):
        """

            Load the Q-score cif file match to Qscore 1.8.2 (temparary)
            Output json file with Q-score information derived from cif file

        :return: None
        """

        mapname = self.mapname
        qfiles = []
        qscoreerrlist = []
        modelnum = 0
        qscoredict = OrderedDict()
        finaldict = OrderedDict()
        allmodels_numberofatoms = 0
        allmodels_qscores = 0.
        for model in self.models:
            orgmodel = os.path.basename(model.filename)
            curmodel = orgmodel
            qfile = '{}{}__Q__{}.cif'.format(self.workdir, curmodel, mapname)
            if os.path.isfile(qfile):
                p = MMCIFParser()
                p._mmcif_dict = MMCIF2Dict(qfile)
                coords = zip(p._mmcif_dict['_atom_site.Cartn_x'], p._mmcif_dict['_atom_site.Cartn_y'], p._mmcif_dict['_atom_site.Cartn_z'])
                qscores = p._mmcif_dict['_atom_site.Q-score']
                coords_qscores_dict = OrderedDict()
                for coord, qscore in zip(coords, qscores):
                    float_coord = tuple(map(float, coord))
                    # org_coord_key = tuple(map(lambda x: math.floor(x * 10 ** 2) / 10 ** 2, float_coord))
                    org_coord_key = tuple(map(lambda x: math.floor(x), float_coord))
                    coords_qscores_dict[org_coord_key] = float(qscore) if qscore != '?' else 0.
                pqscorecif = p.get_structure(qfile, qfile)
                for atom in pqscorecif.get_atoms():
                    # coord_key = tuple(map(float, map(str, atom.coord)))
                    coord_key = tuple(map(float, tuple(map(str, atom.coord))))
                    # new_coord_key = tuple(map(lambda x: math.floor(x * 10 ** 2) / 10 ** 2, coord_key))
                    new_coord_key = tuple(map(lambda x: math.floor(x), coord_key))
                    setattr(atom, 'qscore', coords_qscores_dict[new_coord_key])
                qscorecif = pqscorecif if len(pqscorecif.get_list()) == 1 else pqscorecif[0]
                qfiles.append(qscorecif)
                try:
                    cifdict = self.newcif_toqdict(qscorecif, orgmodel)
                    allmodels_numberofatoms += cifdict['data']['numberofatoms']
                    allmodels_qscores += cifdict['data']['numberofatoms']*cifdict['data']['averageqscore']
                    qscoredict[str(modelnum)] = cifdict
                    modelnum += 1
                except:
                    err = 'Qscore calculation error (Model: {}): {}.'.format(model.filename, sys.exc_info()[1])
                    qscoreerrlist.append(err)
                    sys.stderr.write(err + '\n')
            else:
                raise ValueError
        if allmodels_numberofatoms != 0:
            allmodels_average_qscore = allmodels_qscores / allmodels_numberofatoms
            # qscoredict.update({'allmodels_average_qscore': round(allmodels_average_qscore, 3)})
            qscoredict['allmodels_average_qscore'] = round(allmodels_average_qscore, 3)
        if qscoredict:
            finaldict['qscore'] = qscoredict
            try:
                with codecs.open(self.workdir + self.mapname + '_qscore.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except:
                sys.stderr.write('Saving to Qscore json error: {}.\n'.format(sys.exc_info()[1]))
        else:
            print('Qscore was not collected, please check!')


        return None

    def newcif_toqdict(self, qscorecif, orgmodel):
        """

            Given cif biopython object and convert to a dictory which contains all data for JSON

        :return: DICT contains Q-score data from mmcif (biopython object)
        """


        residues = []
        colors = []
        model_colors = []
        qscores = []
        chain_qscore = {}
        # qscore_list = [atom.qscore for atom in qscorecif.get_atoms() if atom.qscore > 1.0]
        qscore_list = [atom.qscore for atom in qscorecif.get_atoms() ]
        min_qscore = None
        max_qscore = None
        protein_qscores = []
        for atom in qscorecif.get_atoms():
            if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                continue
            protein_qscores.append(atom.qscore)
        average_qscore = round(sum(protein_qscores) / len(protein_qscores), 3)
        if qscore_list:
            min_qscore = min(qscore_list)
            max_qscore = max(qscore_list)
        for chain in qscorecif.get_chains():
            curchain_name = chain.id
            curchain_qscore = []
            for atom in chain.get_atoms():
                if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                    continue
                curchain_qscore.append(atom.qscore)
            if not curchain_qscore:
                continue
            averagecurchain_qscore = round(sum(curchain_qscore) / len(curchain_qscore), 3)
            atoms_inchain = 0
            qscore_inchain = 0.
            for residue in chain:
                curres_name = residue.resname
                if curres_name == 'HOH':
                    continue
                curres_id = residue.id[1]
                atoms_inresidue = 0
                qscore_inresidue = 0.
                for atom in residue:
                    if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                        continue
                    atoms_inchain += 1
                    atoms_inresidue += 1
                    curatom_qscore = atom.qscore
                    qscore_inchain += curatom_qscore
                    qscore_inresidue += curatom_qscore
                if atoms_inresidue != 0.:
                    curres_qscore = round(qscore_inresidue / atoms_inresidue, 3)
                else:
                    curres_qscore = 0.
                if curres_qscore > 1.0:
                    if min_qscore == max_qscore:
                        curres_color = '#000000'
                    else:
                        scaled_qscore = (curres_qscore - min_qscore) / (max_qscore - min_qscore)
                        curres_color = self.__floatohex_aboveone([scaled_qscore])[0]
                else:
                    curres_color = self.__floatohex([curres_qscore])[0]

                icode = residue.id[2]
                if icode != ' ':
                    curres_string = '{}:{}{} {}'.format(curchain_name, curres_id, icode, curres_name)
                else:
                    curres_string = '{}:{} {}'.format(curchain_name, curres_id, curres_name)
                residues.append(curres_string)
                colors.append(curres_color)
                qscores.append(curres_qscore)

        min_qscore = min(qscores)
        max_qscore = max(qscores)
        for res_qscore in qscores:
            if min_qscore == max_qscore:
                curres_model_color = '#000000'
            else:
                scaled_qscore = (res_qscore - min_qscore) / (max_qscore - min_qscore)
                platelet = [(255, 0, 0), (255, 255, 255), (0, 0, 255)]
                curres_model_color = float_to_hex(scaled_qscore, platelet)
            model_colors.append(curres_model_color)

            averageqscore_incolor = self.__floatohex([averagecurchain_qscore])[0]
            chain_qscore[curchain_name] = {'value': averagecurchain_qscore, 'color': averageqscore_incolor}

        levels = np.linspace(-1, 1, 100)
        qarray = np.array(qscores)
        hist, bin_edges = np.histogram(qarray, bins=levels)
        plt.plot(bin_edges[1:], hist/qarray.size)

        protein_qarray = np.array(protein_qscores)
        phist, p_bin_edges = np.histogram(protein_qarray, bins=levels)
        plt.plot(p_bin_edges[1:], phist/protein_qarray.size)
        plt.xlabel('Q-score')
        plt.ylabel('Fraction')
        plt.legend(('Residue: ' + '(' + str(qarray.size) + ')', 'Atom: ' + '(' + str(protein_qarray.size) + ')'), loc='upper left', shadow=True)
        if self.mapname and self.resolution:
            plt.title('Map: ' + self.mapname + ' at: ' + str(self.resolution) + 'Å')
        else:
            plt.title('Map Q-score ')
        plt.savefig(self.workdir + self.mapname + '_qscore.png')
        plt.close()
        q_residue_fractions = list(np.around(hist/qarray.size, 3))
        q_protein_fractions = list(np.around(phist/protein_qarray.size, 3))
        qfractions = {'qLevels': list(np.around(levels[1:], 3)), 'qResidueFractions': q_residue_fractions,
                      'qAtomFractions': q_protein_fractions}

        # score_type = 'qscore'
        # new_dict = {'id': self.emdid, 'resolution': float(self.resolution), 'name': orgmodel, score_type: average_qscore}
        # plot_name = '{}_{}_{}_bar.png'.format(self.mapname, orgmodel, score_type)
        # score_dir = os.path.dirname(va.__file__)
        # relative_towhole, relative_totwo = bar(new_dict, score_type, self.workdir, score_dir, plot_name)
        # qbar = {'whole': relative_towhole, 'relative': relative_totwo}

        tdict = OrderedDict([
            ('averageqscore', average_qscore),
            ('averageqscore_color', self.__floatohex([average_qscore])[0]),
            # ('qscore_bar', qbar),
            ('numberofatoms', len(protein_qscores)),
            ('color', colors),
            ('model_color', model_colors),
            ('inclusion', qscores),
            ('qscore', qscores),
            ('residue', residues),
            ('chainqscore', chain_qscore),
            ('qFractionDistribution', qfractions)
        ])


        resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])

        return resultdict


    def readqscore(self):
        """

            Load the Q-score pdb file(temparary)

        :return:
        """

        mapname = self.mapname[:-4]
        qfiles = []
        qscoreerrlist = []
        result = {}
        modelnum = 0
        qscoredict = OrderedDict()
        finaldict = OrderedDict()
        for model in self.models:
            orgmodel = os.path.basename(model.filename)
            curmodel = orgmodel[:-4]
            qfile = '{}{}__Q__{}.pdb'.format(self.workdir, curmodel, mapname)
            if os.path.isfile(qfile):
                p = orgPDBParser()
                pqscorepdb = p.get_structure('myqfile', qfile)
                qscorepdb = pqscorepdb if len(pqscorepdb.get_list()) == 1 else pqscorepdb[0]
                qfiles.append(qscorepdb)
                try:
                    # qscoredict[str(modelnum)] = self.pdbtoqdict(qscorepdb, orgmodel)
                    qscoredict[str(modelnum)] = self.newpdbtoqdict(qscorepdb, orgmodel)
                    modelnum += 1
                except:
                    err = 'Qscore calculation error (Model: {}): {}.'.format(model.filename, sys.exc_info()[1])
                    qscoreerrlist.append(err)
                    sys.stderr.write(err + '\n')
            else:
                raise ValueError

        if qscoredict:
            finaldict['qscore'] = qscoredict
            try:
                with codecs.open(self.workdir + self.mapname + '_qscore.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except:
                sys.stderr.write('Saving to Qscore json error: {}.\n'.format(sys.exc_info()[1]))
        else:
            print('Qscore was not collected, please check!')


        return None

    def newpdbtoqdict(self, qscorepdb, orgmodel):
        """

            Given pdb biopython object and convert to a dict which contains all data for JSON

        :return: DICT contains all data
        """

        residues = []
        colors = []
        qscores = []
        chain_qscore = {}
        qscore_list = [atom.bfactor for atom in qscorepdb.get_atoms() if atom.bfactor > 1.0]
        protein_qscores = []
        for atom in qscorepdb.get_atoms():
            if atom.name.startswith('H') or atom.get_parent().resname == 'HOH' or atom.bfactor >= 1.0:
                continue
            protein_qscores.append(atom.bfactor)
        average_qscore = round(sum(protein_qscores) / len(protein_qscores), 3)
        if qscore_list:
            min_qscore = min(qscore_list)
            max_qscore = max(qscore_list)
        for chain in qscorepdb.get_chains():
            curchain_name = chain.id
            curchain_qscore = []
            for atom in chain.get_atoms():
                if atom.name.startswith('H') or atom.get_parent().resname == 'HOH' or atom.bfactor >= 1.0:
                    continue
                curchain_qscore.append(atom.bfactor)
            averagecurchain_qscore = round(sum(curchain_qscore) / len(curchain_qscore), 3)
            atoms_inchain = 0
            qscore_inchain = 0.
            for residue in chain:
                curres_name = residue.resname
                if curres_name == 'HOH':
                    continue
                curres_id = residue.id[1]
                atoms_inresidue = 0
                qscore_inresidue = 0.
                for atom in residue:
                    if atom.name.startswith('H') or atom.get_parent().resname == 'HOH' or atom.bfactor >= 1.0:
                        continue
                    atoms_inchain += 1
                    atoms_inresidue += 1
                    curatom_qscore = atom.bfactor
                    qscore_inchain += curatom_qscore
                    qscore_inresidue += curatom_qscore
                curres_qscore = round(qscore_inresidue / atoms_inresidue, 3)
                if curres_qscore > 1.0:
                    if min_qscore == max_qscore:
                        curres_color = '#000000'
                    else:
                        scaled_qscore = (curres_qscore - min_qscore) / (max_qscore - min_qscore)
                        curres_color = self.__floatohex_aboveone([scaled_qscore])[0]
                else:
                    curres_color = self.__floatohex([curres_qscore])[0]

                icode = residue.id[2]
                if icode:
                    curres_string = '{}:{}{}{}'.format(curchain_name, curres_id, icode, curres_name)
                else:
                    curres_string = '{}:{}{}'.format(curchain_name, curres_id, curres_name)
                residues.append(curres_string)
                colors.append(curres_color)
                qscores.append(curres_qscore)
            averageqscore_incolor = self.__floatohex([averagecurchain_qscore])[0]
            chain_qscore[curchain_name] = {'value': averagecurchain_qscore, 'color': averageqscore_incolor}

        tdict = OrderedDict([
            ('averageqscore', average_qscore), ('color', colors),
            ('inclusion', qscores),
            ('residue', residues),
            ('chainqscore', chain_qscore)

        ])

        resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])

        return resultdict

    def pdbtoqdict(self, qscorepdb, orgmodel):
        """

            Given pdb biopython object and convert to a dict which contains all data for JSON

        :return: DICT contains all data
        """

        allkeys = []
        allvalues = []
        preresid = 0
        prechain = ''
        aiprechain = ''
        preres = ''
        rescount = 1
        atomcount = 0
        chainatomcount = 0
        resocc = 0.
        allatoms = 0
        allocc = 0.
        chainocc = 0.
        chaincount = 1
        chainatoms = 0
        chainqscore = {}
        for atom in qscorepdb:
            if not atom.atom_name.startswith('H'):
                allatoms += 1
                allocc += atom.temp_fac
                atomcount += 1
                chainatomcount += 1
                if (atomcount == 1) or (atom.res_no == preresid and atom.chain == prechain):
                    preresid = atom.res_no
                    prechain = atom.chain
                    preres = atom.res
                    resocc += atom.temp_fac
                else:
                    atomcount -= 1
                    keystr = prechain + ':' + str(preresid) + preres
                    allkeys.append(keystr)
                    resoccvalue = resocc / atomcount
                    allvalues.append(resoccvalue)
                    preresid = atom.res_no
                    prechain = atom.chain
                    preres = atom.res
                    atomcount = 1
                    rescount += 1
                    resocc = atom.temp_fac
                if (chainatomcount == 1) or (atom.chain == aiprechain):
                    chainatoms += 1
                    aiprechain = atom.chain
                    chainocc += atom.temp_fac
                else:
                    qvalue = round(chainocc / chainatoms, 3)
                    qcolor = self.__floatohex([qvalue])[0]
                    # chainqscore[aiprechain] = {'value': qvalue, 'color': qcolor}
                    if aiprechain in chainqscore.keys():
                        # chainqscore[prechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                        pass
                    else:
                        chainqscore[aiprechain] = {'value': qvalue, 'color': qcolor}
                    chainatoms = 1
                    chainocc = atom.temp_fac
                    aiprechain = atom.chain
                    chaincount += 1

        qvalue = round(chainocc / chainatoms, 3)
        qcolor = self.__floatohex([qvalue])[0]
        if aiprechain in chainqscore.keys():
            # chainqscore[prechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
            pass
        else:
            chainqscore[aiprechain] = {'value': qvalue, 'color': qcolor}
        lastvalue = resocc / atomcount
        keystr = prechain + ':' + str(preresid) + preres
        allkeys.append(keystr)
        allvalues.append(lastvalue)
        colours = self.__floatohex([i for i in allvalues])
        averageocc = allocc / allatoms

        tdict = OrderedDict([
            ('averageocc', round(averageocc, 6)), ('color', colours),
            ('inclusion', [round(elem, 6) for elem in allvalues]),
            ('residue', allkeys),
            ('chainqscore', chainqscore)

        ])

        resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])

        return resultdict

    def qscoreview(self, chimeraapp):
        """

            X, Y, Z images which model was colored by Q-score

        :return:
        """

        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*_qscore.json')
        basedir = self.workdir
        mapname = self.mapname
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        score_dir = os.path.dirname(va.__file__)
        rescolor_file = f'{score_dir}/utils/rescolor.py'
        errlist = []

        fulinjson = injson[0] if injson else None
        try:
            if fulinjson:
                with open(fulinjson, 'r') as f:
                    args = json.load(f)
            else:
                args = None
                print('There is no Qscore json file.')
        except TypeError:
            err = 'Open Qscore JSON error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None:
                models = args['qscore']
                try:
                    del models['err']
                except:
                    print('Qscore json result is correct')

                print('There is/are %s model(s).' % len(models))
                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    if type(value) is float:
                        continue
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            model_colors = value[key]['model_color']
                            residues = value[key]['residue']
                            qscores = value[key]['inclusion']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_qscore_chimera.cxc'.format(modelname, mapname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                            chimera_model_cmd = '{}_{}_qscore_model_chimera.cxc'.format(modelname, mapname)
                            # pdbmodelname = '{}{}__Q__{}.pdb'.format(basedir, modelname[:-4], mapname[:-4])
                            pdbmodelname = '{}{}__Q__{}.cif'.format(basedir, modelname, mapname)

                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(pdbmodelname) + " format mmcif" + '\n')
                        fp.write(f"open {rescolor_file}\n")
                        # fp.write("open " + str(pdbmodelname) + " format pdb" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        count = 0
                        number_of_item = len(colors)
                        for (color, residue, qscore) in zip(colors, residues, qscores):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # 1st way of getting res_id
                            # res_id = re.sub("\D", "", restmp)
                            # 2nd way of getting res
                            res_id = re.findall(r'-?\d+', restmp)[0]
                            if count == 0:
                                count += 1
                                fp.write(f'rescolors /{chain}:{res_id} {color} ')
                            elif count == number_of_item - 1:
                                fp.write(f'/{chain}:{res_id} {color}\n')
                            else:
                                count += 1
                                fp.write(f'/{chain}:{res_id} {color} ')

                            # fp.write(
                            #     'color /' + chain + ':' + res_id + ' ' + color + '\n'
                            # )
                            if qscore > 1.0:
                                fp.write(
                                    'show /' + chain + ':' + res_id + ' atoms' + '\n'
                                    'style /' + chain + ':' + res_id + ' stick' + '\n'
                                )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_zqscoresurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_xqscoresurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_yqscoresurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )

                    with open(self.workdir + chimera_model_cmd, 'w') as fp:
                        fp.write("open " + str(pdbmodelname) + " format mmcif" + '\n')
                        fp.write(f"open {rescolor_file}\n")
                        # fp.write("open " + str(pdbmodelname) + " format pdb" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        count = 0
                        number_of_item = len(colors)
                        for (color, residue, qscore) in zip(model_colors, residues, qscores):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # 1st way of getting res_id
                            # res_id = re.sub("\D", "", restmp)
                            # 2nd way of getting res
                            res_id = re.findall(r'-?\d+', restmp)[0]
                            if count == 0:
                                count += 1
                                fp.write(f'rescolors /{chain}:{res_id} {color} ')
                            elif count == number_of_item - 1:
                                fp.write(f'/{chain}:{res_id} {color}\n')
                            else:
                                count += 1
                                fp.write(f'/{chain}:{res_id} {color} ')

                            # fp.write(
                            #     'color /' + chain + ':' + res_id + ' ' + color + '\n'
                            # )
                            if qscore > 1.0:
                                fp.write(
                                    'show /' + chain + ':' + res_id + ' atoms' + '\n'
                                                                                 'style /' + chain + ':' + res_id + ' stick' + '\n'
                                )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_model_zqscoresurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_model_xqscoresurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_model_yqscoresurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models based on Qscore were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models based on Qscore were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} Qscore view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimera_model_cmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models based on Qscore were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimera_model_cmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models based on Qscore were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} Qscore view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        self.scale_surfaceview()
                    except:
                        err = 'Scaling model Qscore view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*surface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        # print "self.models:%s" % self.models
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.mapname)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xqscore' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xqscoresurface.jpeg'
                                if modelname in jpeg and 'yqscore' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_yqscoresurface.jpeg'
                                if modelname in jpeg and 'zqscore' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zqscoresurface.jpeg'
                            if errlist:
                                modelmapsurface['err'] = {'model_fit_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['qscore_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.mapname + '_qscoreview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write(
                                'Saving Qscore view to JSON error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('Qscore surface time: %s' % (end - start))
                print('------------------------------------')

    def moveproshadeResult(self):

        import shutil

        cwd = os.getcwd()
        srcdir = '{}/proshade_report'.format(cwd)
        desdir = self.workdir
        desprodir = '{}/proshade_report'.format(desdir)
        if os.path.isdir(desprodir):
            shutil.rmtree(desprodir)
        if os.path.isdir(srcdir):
            dest = shutil.move(srcdir, desdir)
        else:
            dest = None
            print('No proshade result to be moved.')

        return dest

    def symmetrytojson(self, output):
        """

            Convert the output of proshade symmetry calculation to json which can be used further

        :param output:
        :return:
        """

        pass

    def strudel(self):
        """

        :return:
        """
        if self.platform == 'emdb' and self.met != 'tomo':
            errlist = []
            final_range = None
            res_ranges = [[2.0, 2.3], [2.3, 2.5], [2.5, 2.8], [2.8, 3.0], [3.0, 3.2], [3.2, 3.5], [3.5, 4.0]]
            try:
                for idx, crange in enumerate(res_ranges):
                    if crange[0] < float(self.resolution) <= crange[1]:
                        final_range = crange
                        break
                else:
                    print('Map did not fall into any available resolution range.')
                    print('------------------------------------')
            except:
                err = 'Strudel motif lib resolution range check error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            strudelapp = None
            # use a fix value for now, may consider as a argument for later
            try:
                # strudelapp = self.checkstrudelscore(ochimeraapp)
                mapname = self.map.fullname
                if self.models is not None:
                    models = ' '.join([model.filename for model in self.models])
                else:
                    print('No fitted model for Strudel calculation.')
                    print('------------------------------------')

            except:
                err = 'Strudel preparation error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            lib_root = None
            if LIB_STRUDEL_ROOT is not None:
                lib_root = LIB_STRUDEL_ROOT
            elif LIB_STRUDEL_ROOT is None and self.strudellib is not None:
                lib_root = self.strudellib
            else:
                lib_root = None

            # if strudelapp and self.models:
            if final_range and self.models:
                for model in self.models:
                    full_model = '{}{}'.format(self.workdir, os.path.basename(model.filename))
                    full_map = '{}{}'.format(self.workdir, self.mapname)
                    lib_path = '{}/motifs_{}-{}'.format(lib_root, final_range[0], final_range[1])
                    out_path = '{}_strudel'.format(full_model)

                    rerr = run_strudel(full_model, full_map, lib_path, out_path, self.queue, self.platform)
                    if rerr:
                        err = 'Strudel calculation error: {}'.format(rerr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                        print('------------------------------------')

            else:
                print('No model or resolution is not covered in the motif library (<4.0Å) ')
                print('------------------------------------')

        return None


    @profile_peak_memory()
    def real_mmcc(self):
        """
            Calculation real space cross-correlation between primary map and model-map (Refmac)

        :return:
        """

        if self.modelsmaps and self.platform == 'emdb':
            start = timeit.default_timer()
            rmmccc = {}
            mmcc_dict = {}
            errlist = []
            for modelmap in self.modelsmaps:
                print(modelmap)
                modelmap_name = os.path.basename(modelmap)
                try:
                    mmap = mrcfile.mmap(modelmap, mode='r')
                    mmapdata = mmap.data
                    mmcc = run_realmmcc(self.map.data, mmapdata)[1]
                    mmcc_dict[modelmap_name] = mmcc
                except:
                    err = 'Map and model {} real space CC calculation error: {}.'.format(modelmap_name, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

            if errlist:
                rmmccc['err'] = {'rmmccc_err': errlist}
            else:
                print('No error in rmmccc calculation.')

            rmmccc['rmmccc'] = mmcc_dict
            if rmmccc:
                with codecs.open(self.workdir + self.mapname + '_rmmccscore.json', 'w', encoding='utf-8') as f:
                    json.dump(rmmccc, f)
            else:
                print('No model map CC is calculated, check the error information.')

            end = timeit.default_timer()
            print('Real space model and map Cross-Correlation Coefficient time: %s' % (end - start))
            print('------------------------------------')

        else:
            print('No model map for model and map real space cross-correlation calculation.')
            print('------------------------------------')

        return None

    @profile_peak_memory()
    def smoc_bar(self):
        """
        smoc calcualtion and bar
        """

        if not self.onlybar:
            self.smoc()
        self.get_bar(score_type='smoc')

    # use latest TEMPy 2.0 for smoc calculation
    def smoc(self):
        """
            run smoc
        :return:
        """
        if self.platform == 'emdb' and self.met != 'tomo':
            start = timeit.default_timer()
            errlist = []
            result_dict = {}
            try:
                if self.models:
                    count = 0
                    final_dict = {}
                    out_path = '{}/smoc'.format(self.workdir)
                    for model in self.models:
                        full_model = '{}{}'.format(self.workdir, os.path.basename(model.filename))
                        full_map = '{}{}'.format(self.workdir, self.mapname)
                        res = self.resolution

                        rdict, rerr = run_smoc(full_model, full_map, res, out_path)
                        if rdict:

                            final_dict[str(count)] = rdict
                            count += 1

                        end = timeit.default_timer()
                        print('SMOC time: %s' % (end - start))
                        print('------------------------------------')
                        if rerr:
                            err = 'SMOC calculation error: {}'.format(rerr)
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                            print('------------------------------------')

                    if final_dict:
                        result_dict['smoc'] = final_dict

                    if errlist:
                        result_dict['err'] = errlist

                    if result_dict:
                        try:
                            with codecs.open(self.workdir + self.mapname + '_smoc.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(result_dict, f)

                            with codecs.open(out_path + '/' + self.mapname + '_smoc.json', 'w', encoding='utf-8') as ff:
                                json.dump(result_dict, ff)
                            self.smoc_surface()
                        except:
                            sys.stderr.write('Saving to SMOC json error: {}.\n'.format(sys.exc_info()[1]))
                    else:
                        print('SMOC was not collected, please check!')

                else:
                    print('No model or something wrong with model loading.')
                    print('------------------------------------')
            except:
                err = 'SMOC calculation error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')


        else:
            print('Check the entry, there is no SMOC for this entry.')

        return None

    def get_bar(self, score_type):


        score_list = ['ccc', 'CCC', 'atom_inclusion_by_level', 'smoc', 'qscore']
        file_name = None
        if score_type == 'smoc':
            file_name = '{}/{}_{}.json'.format(self.workdir, self.mapname, score_type)
        elif score_type == 'ccc':
            file_name = '{}/{}_res{}.json'.format(self.workdir, self.mapname, score_type)
        elif score_type == 'qscore':
            file_name = '{}/{}_{}.json'.format(self.workdir, self.mapname, score_type)
        elif score_type == 'atom_inclusion':
            file_name = '{}/{}_{}.json'.format(self.workdir, self.mapname, score_type)

        if file_name and os.path.isfile(file_name):
            with open(file_name, 'r') as json_file:
                cur_json = json.load(json_file)
            if any(item in cur_json for item in score_list):
                if score_type == 'atom_inclusion':
                    score_data = cur_json[f'{score_type}_by_level']
                elif score_type == 'ccc':
                    if 'ccc' in cur_json.keys():
                        score_data = cur_json['ccc']
                    elif 'CCC' in cur_json.keys():
                        score_data = cur_json['CCC']
                    else:
                        score_data = None
                else:
                    score_data = cur_json[score_type]
                if score_type == 'atom_inclusion':
                    if 'average_ai_allmodels' in score_data.keys():
                        model_numbers = len(score_data) - 1
                    else:
                        model_numbers = len(score_data)
                else:
                    model_numbers = len(score_data)
                    if 'allmodels_average_qscore' in score_data.keys():
                        model_numbers -= 1
                final_dict = {}
                data = {}
                for i in range(0, model_numbers):
                    try:
                        cur_score_data = score_data[str(i)]
                    except KeyError:
                        print(f'Key: {i}: {list(score_data.keys())[i]} skipped.')
                        continue
                    model_name = cur_score_data['name']
                    if score_type == 'ccc':
                        new_dict = {'id': self.emdid, 'resolution': float(self.resolution) if self.resolution else None, 'name': model_name,
                                    score_type: round(cur_score_data['data']['averagecc'], 3)}
                    elif score_type == 'atom_inclusion':
                        new_dict = {'id': self.emdid, 'resolution': float(self.resolution) if self.resolution else None, 'name': model_name,
                                    'ai': round(cur_score_data['average_ai_model'], 3)}
                    else:
                        new_dict = {'id': self.emdid, 'resolution': float(self.resolution) if self.resolution else None, 'name': model_name,
                                    score_type: round(cur_score_data['data'][f'average{score_type}'], 3)}
                    plot_name = '{}_{}_{}_bar.png'.format(self.mapname, model_name, score_type)
                    score_dir = os.path.dirname(va.__file__)
                    if score_type == 'atom_inclusion':
                        (relative_towhole,relative_towhole_counts, whole_res_low, whole_res_high), (relative_totwo, relative_totwo_counts, relative_res_low, relative_re_high), resbin = bar(new_dict, 'ai', self.workdir, score_dir, plot_name, self.update_resolution_bin_file)
                    else:
                        (relative_towhole,relative_towhole_counts, whole_res_low, whole_res_high), (relative_totwo, relative_totwo_counts, relative_res_low, relative_re_high), resbin = bar(new_dict, score_type, self.workdir, score_dir, plot_name, self.update_resolution_bin_file)
                    score_bar = {'whole': relative_towhole, 'whole_counts':relative_towhole_counts,'whole_res_low': whole_res_low, 'whole_res_high': whole_res_high, 'relative': relative_totwo, 'relative_counts': relative_totwo_counts, 'relative_res_low': relative_res_low, 'relative_res_high': relative_re_high}
                    version_str = va.version.__em_statistics_version__.split('.')[0]
                    formatted_date = format_version_date(version_str)
                    em_statistic_version = f'{va.version.__em_statistics_version__} (Using data in the EMDB archive up until {formatted_date})'
                    if score_type == 'atom_inclusion':
                        # atom inclusion need to swtich to this later
                        #data[str(i)] = {'name': model_name, 'data': {'ai_bar': score_bar, 'bin_size': resbin}}
                        data[str(i)] = {'name': model_name, 'ai_bar': score_bar, 'bin_size': resbin, 'em_statistic_version': em_statistic_version}
                    else:
                        data[str(i)] = {'name': model_name, 'data': {f'{score_type}_bar': score_bar, 'bin_size': resbin, 'em_statistic_version': em_statistic_version}}
                if score_type == 'atom_inclusion':
                    final_dict['atom_inclusion_by_level'] = data
                else:
                    final_dict[score_type] = data

                if score_type == 'atom_inclusion':
                    bar_json = '{}/{}_aibar.json'.format(self.workdir, self.mapname)
                else:
                    bar_json = '{}/{}_{}bar.json'.format(self.workdir, self.mapname, score_type)
                if final_dict:
                    try:
                        with codecs.open(bar_json, 'w', encoding='utf-8') as f:
                            json.dump(final_dict, f)

                    except:
                        sys.stderr.write('Saving to score json error: {}.\n'.format(sys.exc_info()[1]))
                else:
                    print('Score was not collected, please check!')
            else:
                print(f'{score_type} JSON exist but corresponding score does not exist. Check the error.')
        else:
            print(f'{score_type} JSON results does not exist.')

    def smoc_view(self, chimeraapp):
        """

            X, Y, Z images which model was colored by SMOC

        :return:
        """

        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*_smoc.json')
        basedir = self.workdir
        mapname = self.mapname
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        score_dir = os.path.dirname(va.__file__)
        rescolor_file = f'{score_dir}/utils/rescolor.py'
        errlist = []

        fulinjson = injson[0] if injson else None
        try:
            if fulinjson:
                with open(fulinjson, 'r') as f:
                    args = json.load(f)
            else:
                args = None
                print('There is no SMOC json file.')
        except TypeError:
            err = 'Open SMOC JSON error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None:
                models = args['smoc']
                try:
                    del models['err']
                except:
                    print('SMOC json result is correct')

                print('There is/are %s model(s).' % len(models))
                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    if type(value) is float:
                        continue
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            residues = value[key]['residue']
                            smocs = value[key]['smoc_scores']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_smoc_chimera.cxc'.format(modelname, mapname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                            # pdbmodelname = '{}{}__Q__{}.pdb'.format(basedir, modelname[:-4], mapname[:-4])
                            pdbmodelname = '{}{}'.format(basedir, modelname)

                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(pdbmodelname) + " format mmcif" + '\n')
                        fp.write(f"open {rescolor_file}\n")
                        # fp.write("open " + str(pdbmodelname) + " format pdb" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        count = 0
                        number_of_item = len(colors)
                        for (color, residue, smocscore) in zip(colors, residues, smocs):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # 1st way of getting res_id
                            # res_id = re.sub("\D", "", restmp)
                            # 2nd way of getting res
                            res_id = re.findall(r'-?\d+', restmp)[0]
                            if count == 0:
                                count += 1
                                fp.write(f'rescolors /{chain}:{res_id} {color} ')
                            elif count == number_of_item - 1:
                                fp.write(f'/{chain}:{res_id} {color}\n')
                            else:
                                count += 1
                                fp.write(f'/{chain}:{res_id} {color} ')

                            # fp.write(
                            #     'color /' + chain + ':' + res_id + ' ' + color + '\n'
                            # )
                            if smocscore > 1.0:
                                fp.write(
                                    'show /' + chain + ':' + res_id + ' atoms' + '\n'
                                    'style /' + chain + ':' + res_id + ' stick' + '\n'
                                )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_zsmocsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_xsmocsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_ysmocsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models based on SMOC were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models based on SMOC were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} SMOC view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        self.scale_surfaceview()
                    except:
                        err = 'Scaling model SMOC view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*smocsurface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        # print "self.models:%s" % self.models
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.mapname)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xsmoc' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xsmocsurface.jpeg'
                                if modelname in jpeg and 'ysmoc' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_ysmocsurface.jpeg'
                                if modelname in jpeg and 'zsmoc' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zsmocsurface.jpeg'
                            if errlist:
                                modelmapsurface['err'] = {'model_fit_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['smocscore_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.mapname + '_smocview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write(
                                'Saving SMOC view to JSON error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('SMOC surface time: %s' % (end - start))
                print('------------------------------------')

    def smoc_surface(self):

        # self.renameqfiles()
        try:
            vtkpack, chimeraapp = self.surface_envcheck()
            self.smoc_view(chimeraapp)
        except:
            err = 'SMOC surface view failed: {}'.format(sys.exc_info()[1])
            print(traceback.format_exc())
            sys.stderr.write(err + '\n')

    @profile_peak_memory()
    def ccc_bar(self):


        if not self.onlybar:
            self.phenix_resccc()
        self.get_bar(score_type='ccc')

    def phenix_resccc(self):
        """
            Run Phenix residue-wise CCC calculation + collect stdout summary
        :return:
        """
        if self.platform == 'emdb' and self.met != 'tomo':
            start = timeit.default_timer()
            errlist = []
            result_dict = {}
            if self.models:
                nummodels = 0
                allresults = {}
                for model in self.models:
                    try:
                        full_model = '{}{}'.format(self.workdir, os.path.basename(model.filename))
                        full_map = '{}{}'.format(self.workdir, self.mapname)
                        out_path = '{}_phenix'.format(full_model)

                        rerr, cc_metrics, _stdout = run_phenixcc(full_model, full_map, self.resolution, out_path)

                        end = timeit.default_timer()
                        print('Phenix CCC time: %s' % (end - start))
                        cclog = '{}/cc_per_residue.log'.format(out_path)
                        print(cclog, rerr)
                        print('------------------------------------')
                    except:
                        err = 'Phenix CCC calculation error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        # Your existing per-residue path remains the same
                        df = read_cc(cclog, rerr)
                        ccdict = ccdf_todict(df)

                        # allresults[nummodels] keeps both residue-wise curve and stdout summary
                        allresults[str(nummodels)] = {
                            'name': os.path.basename(model.filename),
                            'data': {**ccdict, 'summary': cc_metrics} # existing residue-wise dict
                        }

                        # (Optional) Save a compact JSON next to the log for quick inspection
                        try:
                            with open(os.path.join(out_path, "cc_summary.json"), "w", encoding="utf-8") as fh:
                                json.dump(cc_metrics, fh, indent=2)
                        except Exception as e:
                            sys.stderr.write(f'Could not write cc_summary.json: {e}\n')

                    except:
                        err = 'Save Phenix CCC data error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    nummodels += 1

                if allresults:
                    result_dict['ccc'] = allresults

                if errlist:
                    result_dict['err'] = errlist

                if len(result_dict) == 1 and 'ccc' in result_dict:
                    try:
                        with codecs.open(self.workdir + self.mapname + '_resccc.json', 'w', encoding='utf-8') as f:
                            json.dump(result_dict, f)
                    except:
                        sys.stderr.write('Saving to CCC json error: {}.\n'.format(sys.exc_info()[1]))

                    try:
                        self.cc_surface()
                    except:
                        sys.stderr.write('CCC surface error: {}.\n'.format(sys.exc_info()[1]))
                else:
                    print('CCC was not collected, please check the error!')

            else:
                print('No model or resolution is not covered in the motif library (<4.0Å) ')
                print('------------------------------------')

        return None

    def ccscoreview(self, chimeraapp):
        """

            X, Y, Z images which model was colored by residue-wise CCC

        :return:
        """

        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*_resccc.json')
        basedir = self.workdir
        mapname = self.mapname
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        score_dir = os.path.dirname(va.__file__)
        rescolor_file = f'{score_dir}/utils/rescolor.py'
        errlist = []

        fulinjson = injson[0] if injson else None
        try:
            if fulinjson:
                with open(fulinjson, 'r') as f:
                    args = json.load(f)
            else:
                args = None
                print('There is no CCC json file.')
        except TypeError:
            err = 'Open CCC JSON error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None and 'ccc' in args.keys():
                models = args['ccc']
                try:
                    del models['err']
                except:
                    print('CCC json result is correct')

                print('There is/are %s model(s).' % len(models))
                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    if type(value) is float:
                        continue
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            residues = value[key]['residue']
                            smocs = value[key]['ccscore']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_ccc_chimera.cxc'.format(modelname, mapname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                            # pdbmodelname = '{}{}__Q__{}.pdb'.format(basedir, modelname[:-4], mapname[:-4])
                            pdbmodelname = '{}{}'.format(basedir, modelname)

                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(pdbmodelname) + " format mmcif" + '\n')
                        fp.write(f"open {rescolor_file}\n")
                        # fp.write("open " + str(pdbmodelname) + " format pdb" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        count = 0
                        number_of_item = len(colors)
                        for (color, residue, smocscore) in zip(colors, residues, smocs):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # 1st way of getting res_id
                            # res_id = re.sub("\D", "", restmp)
                            # 2nd way of getting res
                            res_id = re.findall(r'-?\d+', restmp)[0]
                            if count == 0:
                                count += 1
                                fp.write(f'rescolors /{chain}:{res_id} {color} ')
                            elif count == number_of_item - 1:
                                fp.write(f'/{chain}:{res_id} {color}\n')
                            else:
                                count += 1
                                fp.write(f'/{chain}:{res_id} {color} ')

                            # fp.write(
                            #     'color /' + chain + ':' + res_id + ' ' + color + '\n'
                            # )

                            if smocscore > 1.0:
                                fp.write(
                                    'show /' + chain + ':' + res_id + ' atoms' + '\n'
                                    'style /' + chain + ':' + res_id + ' stick' + '\n'
                                )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_zcccsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_xcccsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_ycccsurface.jpeg" + " supersample 1 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models based on CCC were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models based on CCC were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} CCC view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        self.scale_surfaceview()
                    except:
                        err = 'Scaling model CCC view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*cccsurface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        # print "self.models:%s" % self.models
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.mapname)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xccc' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xcccsurface.jpeg'
                                if modelname in jpeg and 'yccc' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_ycccsurface.jpeg'
                                if modelname in jpeg and 'zccc' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zcccsurface.jpeg'
                            if errlist:
                                modelmapsurface['err'] = {'ccc_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['cccscore_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.mapname + '_cccview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write(
                                'Saving CCC view to JSON error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('CCC surface time: %s' % (end - start))
                print('------------------------------------')

    def cc_surface(self):
        try:
            vtkpack, chimeraapp = self.surface_envcheck()
            self.ccscoreview(chimeraapp)
        except:
            err = 'CCC surface view failed: {}'.format(sys.exc_info()[1])
            print(traceback.format_exc())
            sys.stderr.write(err + '\n')

    @profile_peak_memory()
    def phenix_mmfsc(self):
        """
            Run Phenix map-model FSC calculation
        :return:
        """

        if self.platform == 'emdb' and self.met != 'tomo' and self.met != 'crys' :
            start = timeit.default_timer()
            errlist = []
            result_dict = {}
            raw_result_dict = {}
            # if strudelapp and self.models:
            if self.models:
                nummodels = 0
                allresults = {}
                raw_allresults = {}
                for model in self.models:
                    try:
                        full_model = '{}{}'.format(self.workdir, os.path.basename(model.filename))
                        full_map = '{}{}'.format(self.workdir, self.mapname)
                        out_path = '{}_phenix'.format(full_model)
                        rerr = run_phenixmmfsc(full_model, full_map, out_path)
                        tmmfsclog = '{}/fsc_model.unmasked.mtriage.log'.format(out_path)
                        mmfsclog = '{}/fsc_model.unmasked.mtriage_{}.log'.format(out_path, self.mapname)
                        change_filename(tmmfsclog, mmfsclog)
                        raw_mmfsclog = None
                        raw_rerr = None
                        if self.hmodd and self.hmeven:
                            raw_full_map = self.rawmap.fullname
                            raw_mapname = os.path.basename(raw_full_map)
                            raw_rerr = run_phenixmmfsc(full_model, raw_full_map, out_path)
                            raw_mmfsclog = '{}/fsc_model.unmasked.mtriage_{}.log'.format(out_path, raw_mapname)
                            change_filename(tmmfsclog, raw_mmfsclog)
                        end = timeit.default_timer()
                        print('Phenix mmFSC time: %s' % (end - start))
                        print('------------------------------------')
                    except:
                        err = 'Phenix mmFSC calculation error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                    nyquist = 1 / (2 * self.map.voxel_size.tolist()[0])
                    try:
                        df = read_mmfsc(mmfsclog, rerr)
                        mmfscdict = mmfscdf_todict(df, nyquist)

                        allresults[str(nummodels)] = {'name': os.path.basename(model.filename),
                                                      'data': mmfscdict}

                        if self.hmodd and self.hmeven:
                            raw_df = read_mmfsc(raw_mmfsclog, raw_rerr)
                            raw_mmfscdict = mmfscdf_todict(raw_df, nyquist)

                            raw_allresults[str(nummodels)] = {'name': os.path.basename(model.filename),
                                                              'data': raw_mmfscdict}

                    except:
                        err = 'Save Phenix mmFSC data error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                    nummodels += 1

                if allresults:
                    result_dict['mmfsc'] = allresults
                if raw_allresults:
                    raw_result_dict['raw_mmfsc'] = raw_allresults

                if errlist:
                    result_dict['err'] = errlist

                if len(result_dict) == 1 and 'mmfsc' in result_dict:
                    try:
                        with codecs.open(self.workdir + self.mapname + '_mmfsc.json', 'w',
                                         encoding='utf-8') as f:
                            json.dump(result_dict, f)
                    except:
                        sys.stderr.write('Saving to mmFSC json error: {}.\n'.format(sys.exc_info()[1]))

                else:
                    print('mmFSC was not collected, please check the error!')

                if len(raw_result_dict) == 1 and 'raw_mmfsc' in raw_result_dict:
                    try:
                        with codecs.open(self.workdir + self.mapname + '_raw_mmfsc.json', 'w',
                                         encoding='utf-8') as f:
                            json.dump(raw_result_dict, f)
                    except:
                        sys.stderr.write('Saving to raw mmFSC json error: {}.\n'.format(sys.exc_info()[1]))

                else:
                    print('Raw map mmFSC was not collected, please check the error!')

            else:
                print('No model!!')
                print('------------------------------------')

        return None

    @profile_peak_memory()
    def locres_resmap(self):
        """
            Calculate local resolution by using Resmap
        :return:
        """
        if self.platform == 'emdb' and self.met != 'tomo':
            start = timeit.default_timer()
            errlist = []
            result_dict = {}
            # if strudelapp and self.models:
            if self.hmeven and self.hmodd:
                even = self.hmeven.fullname
                odd = self.hmodd.fullname
                full_map = '{}{}'.format(self.workdir, self.mapname)
                out_path = '{}_relion'.format(full_map)
                print(out_path)
                allresults = {}
                try:

                    # rerr = run_resmap(odd, even, out_path, RESMAP)
                    rerr = run_locres(odd, even, out_path, RESMAP)
                    end = timeit.default_timer()
                    print('Relion local resolution time: %s' % (end - start))
                    print('------------------------------------')
                except:
                    err = 'Local resolution calculation error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
                # check = resmap_filecheck(odd, self.workdir)
                check = locres_filecheck(odd, even, out_path)
                if check:
                    try:
                        resmap_chimerax_file = resmap_chimerax(odd, self.workdir)
                        if os.path.isfile(resmap_chimerax_file):
                            vtkpack, chimeraapp = self.surface_envcheck()
                            bindisplay = os.getenv('DISPLAY')
                            run_resmap_chimerax(bindisplay, chimeraapp, resmap_chimerax_file)
                            # resmap = '{}_ori_resmap.map'.format(odd[:-4])
                            # output_json = '{}{}_resmap.json'.format(self.workdir, self.mapname)
                            # save_imagestojson(resmap, output_json)
                    except:
                        err = 'ResMap views error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                else:
                    print('Chimerax file does not exist. Check!!')

                if errlist:
                    result_dict['err'] = errlist
                else:
                    try:
                        resmap = '{}_ori_resmap.map'.format(odd[:-4])
                        output_json = '{}{}_resmap.json'.format(self.workdir, self.mapname)
                        save_imagestojson(resmap, output_json)
                    except:
                        sys.stderr.write('Saving to resmap json error: {}.\n'.format(sys.exc_info()[1]))
                end = timeit.default_timer()
                print('Whole ResMap local resolution time: %s' % (end - start))
                print('------------------------------------')
            else:
                print('No half maps ResMap local resolution will not be calculated. ')
                print('------------------------------------')

        return None


    def locres_histo(self):
        """
            Produce local resolution histogram information
        """

        result_dict = {}
        errlist = []
        start = timeit.default_timer()
        if self.platform == 'emdb' and self.met != 'tomo' and self.hmodd and self.hmeven:
            local_res = localres_histogram(self.hmodd.fullname, self.mapname, float(self.resolution))
        else:
            local_res = None

        if local_res:
            result_dict['local_res_histogram'] = local_res
            try:
                with codecs.open(self.workdir + self.mapname + '_localres_histo.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(result_dict, f)
            except Exception as e:
                jsonerr = 'Saving local resolution histogram to json error: {}'.format(e)
                errlist.append(jsonerr)
                sys.stderr.write(jsonerr + '\n')
        else:
            print('No local resolution histogram for this entry, check half maps.')
        end = timeit.default_timer()
        print(f'Local resolution histogram time: {end - start}')
        print('------------------------------------')

    # Phase randimization
    def phrand(self):

        phaserandomization(self.mapname, self.hmodd.fullname, self.hmeven.fullname, self.workdir)


    @profile_peak_memory()
    def cl_prediction(self):
        """
            To predicate contour level for both primary map and raw map output as json file
        """

        if self.met != 'tomo':
            try:
                start = timeit.default_timer()
                pred_primary = {}
                pred_raw = {}
                if self.map.fullname:
                    m = mrcfile.open(self.map.fullname)
                    d = m.data
                    voxel_volume = np.prod(m.voxel_size.tolist())
                    # non-cubic map use padding 0 to make it cubic
                    if not all(dim == d.shape[0] for dim in d.shape):
                        dim_shape = max(d.shape)
                        target_shape = (dim_shape, dim_shape, dim_shape)
                        d = pad_array(m.data, target_shape)
                    norm_pred = calc_level_dev(d)[0]
                    cur_volume = keep_three_significant_digits(np.sum(d >= norm_pred) * voxel_volume)
                    # primary_surface = self.compute_surface_area_two(self.map.fullname, norm_pred)
                    primary_weight = (cur_volume / 1000.) * RESIDUE_DENSITY
                    primary_sigma = norm_pred / m.data.std()
                    primary_disconnected_percentage = compute_connected_metrics(self.map.fullname, norm_pred)['disconnected_percentage']
                    pred_primary['primary'] = {'value': keep_three_significant_digits(float(norm_pred)),
                                               'sigma': keep_three_significant_digits(primary_sigma),
                                               'disconnected_percentage': keep_three_significant_digits(primary_disconnected_percentage),
                                               'volume': cur_volume,
                                               # 'surface': keep_three_significant_digits(primary_surface),
                                               'weight': keep_three_significant_digits(primary_weight)}

                if self.rawmap:
                    m = mrcfile.open(self.rawmap.fullname)
                    d = m.data
                    norm_pred = calc_level_dev(d)[0]
                    voxel_volume = np.prod(m.voxel_size.tolist())
                    cur_volume = keep_three_significant_digits(np.sum(d >= norm_pred) * voxel_volume)
                    # raw_surface = self.compute_surface_area_two(self.rawmap.fullname, norm_pred)
                    raw_weight = (cur_volume / 1000.) * RESIDUE_DENSITY
                    raw_sigma = norm_pred / m.data.std()
                    raw_disconnected_percentage = compute_connected_metrics(self.rawmap.fullname, norm_pred)['disconnected_percentage']
                    pred_raw['raw'] = {'value': keep_three_significant_digits(float(norm_pred)),
                                       'sigma': keep_three_significant_digits(raw_sigma),
                                       'disconnected_percentage': keep_three_significant_digits(raw_disconnected_percentage),
                                       'volume': cur_volume,
                                       # 'surface': keep_three_significant_digits(raw_surface),
                                       'weight': keep_three_significant_digits(raw_weight)
                                       }

                    lowpassed_rawmap = f'{self.rawmap.fullname}_lowpassed.mrc'
                    if os.path.isfile(lowpassed_rawmap):
                        lm = mrcfile.open(lowpassed_rawmap)
                        ld = lm.data
                        norm_pred = calc_level_dev(ld)[0]
                        voxel_volume = np.prod(lm.voxel_size.tolist())
                        cur_volume = keep_three_significant_digits(np.sum(ld >= norm_pred) * voxel_volume)
                        lp_sigma = norm_pred / lm.data.std()
                        lp_disconnected_percentage = compute_connected_metrics(lowpassed_rawmap, norm_pred)['disconnected_percentage']
                        pred_raw['lowpassed'] = {'value': keep_three_significant_digits(norm_pred),
                                                'sigma': keep_three_significant_digits(lp_sigma),
                                                'disconnected_percentage': keep_three_significant_digits(lp_disconnected_percentage),
                                                'volume': cur_volume
                                                }


                    if self.hmodd:
                        hm = mrcfile.open(self.hmodd.fullname)
                        hd = hm.data
                        norm_pred = calc_level_dev(hd)[0]
                        voxel_volume = np.prod(hm.voxel_size.tolist())
                        cur_volume = keep_three_significant_digits(np.sum(hd >= norm_pred) * voxel_volume)
                        # odd_surface = self.compute_surface_area_two(self.hmodd.fullname, norm_pred)
                        odd_sigma = norm_pred / hm.data.std()
                        odd_disconnected_percentage = compute_connected_metrics(self.hmodd.fullname, norm_pred)['disconnected_percentage']
                        pred_raw['half_odd'] = {'value': keep_three_significant_digits(norm_pred),
                                                'sigma': keep_three_significant_digits(odd_sigma),
                                                'disconnected_percentage': keep_three_significant_digits(odd_disconnected_percentage),
                                                'volume': cur_volume
                                                # 'surface': keep_three_significant_digits(odd_surface)
                                                }

                    if self.hmeven:
                        hm = mrcfile.open(self.hmeven.fullname)
                        hd = hm.data
                        norm_pred = calc_level_dev(hd)[0]
                        voxel_volume = np.prod(hm.voxel_size.tolist())
                        cur_volume = keep_three_significant_digits(np.sum(hd >= norm_pred) * voxel_volume)
                        # even_surface = self.compute_surface_area_two(self.hmeven.fullname, norm_pred)
                        even_sigma = norm_pred / hm.data.std()
                        even_disconnected_percentage = compute_connected_metrics(self.hmeven.fullname, norm_pred)['disconnected_percentage']
                        pred_raw['half_even'] = {'value': keep_three_significant_digits(norm_pred),
                                                 'sigma': keep_three_significant_digits(even_sigma),
                                                 'disconnected_percentage': keep_three_significant_digits(even_disconnected_percentage),
                                                 'volume': cur_volume
                                                 # 'surface': keep_three_significant_digits(even_surface)
                                                 }

                result_dict = {}
                if pred_primary or pred_raw:
                    result_dict['predicated_contour_level'] = {**pred_primary, **pred_raw} if pred_primary and pred_raw \
                                                                                            else pred_primary or pred_raw
                else:
                    print('Predicated contour level does not exist for either primary or raw map.')

                if result_dict:
                    file_name = f'{self.workdir}{self.mapname}_predicated_contour_level.json'
                    out_json(result_dict, file_name)
                end = timeit.default_timer()
                print('Predicated contour level time: %s' % (end - start))
                print('------------------------------------')
            except Exception as e:
                print(f'The predicated contour level failed: {e}.')
        else:
            print('No predicated contour level for tomo entries.')

    def mask_volume(self):
        """
            Calculate the volume of the mask
        """

        mask_map = f'{self.workdir}/{self.mapname}_relion/mask/{self.mapname}_mask.mrc'
        if os.path.isfile(mask_map):
            ## output mask volume here
            mask_volume = MapProcessor.get_map_volume(mask_map)
            output_file = f'{self.workdir}{self.mapname}_maskvolume.json'
            out_dict = {'mask_volume': {'mask_name': f'{self.mapname}_mask.mrc', 'volume': mask_volume }}
            out_json(out_dict, output_file)

    def locres_residue(self):
        """
            Generate local resolution coloured model views
        """

        start = timeit.default_timer()
        models = self.models
        raw_map = self.findrawmap()
        # raw_map = f'{self.va_dir}/{map_name[:-4] + "_rawmap.map"}'
        mask_map = f'{self.workdir}/{self.mapname}_relion/mask/{self.mapname}_mask.mrc'
        if os.path.isfile(mask_map) and models and raw_map:
            ## output mask volume here
            mask_volume = MapProcessor.get_map_volume(mask_map)
            output_file = f'{self.workdir}{self.mapname}_maskvolume.json'
            out_dict = {'mask_volume': {'mask_name': f'{self.mapname}_mask.mrc', 'volume': mask_volume }}
            out_json(out_dict, output_file)
            ##

            map_processor = MapProcessor()
            binarized_mask_map = map_processor.binarized_mask(mask_map, self.mapname)
            masked_raw_map = map_processor.mask_map(raw_map, mask_map)
            # masked_raw_map = f'{self.workdir}{self.mapname[:-4] + "_rawmap.map"}_{self.mapname}_mask.mrc_masked.map'
            radius = 3
            try:
                loca_res_map = f'{self.workdir}{self.mapname}_relion/{os.path.basename(self.hmodd.fullname)}_{os.path.basename(self.hmeven.fullname)}_locres.mrc'
                map = mrcfile.open(loca_res_map) if masked_raw_map else None
                map_processor = MapProcessor()
                value_range = map_processor.map_minmax(masked_raw_map, loca_res_map)
                output = local_resolution_json(map, models, radius, value_range)
                final_dict = {}
                data_type = 'residue_local_resolution'
                if output:
                    final_dict[data_type] = output
                    _, chimerax = self.surface_envcheck()
                    output_file = f'{self.workdir}{self.mapname}_{data_type}.json'
                    out_json(final_dict, output_file)
                    model_local_resolution_views(output_file, self.mapname, data_type, chimerax)
            except Exception as e:
                print(f'Residue local resolution calculation or results saving failed: {e}.')

        else:
            print('No raw map found.')

        end = timeit.default_timer()
        print('Residue local resolution time: %s' % (end - start))
        print('------------------------------------')

    def model_map_ration(self):
        """
            Calculated the percentage that the map was modelled into the map
        """
        start = timeit.default_timer()
        try:
            map_processor = MapProcessor(self.map)
            map_processor.model_ratio(self.map, self.models[0], 1.5)
        except Exception as e:
            print(f'Model map ration error: {e}.')

        end = timeit.default_timer()
        print('Model map ratio time: %s' % (end - start))
        print('------------------------------------')

    def locres_map(self):
        """
            Generate local resolution coloured map views
        """
        raw_map = self.findrawmap()
        map = mrcfile.open(raw_map) if raw_map else None
        start = timeit.default_timer()
        if map:
            try:
                data_type = 'map_local_resolution'
                _, chimerax = self.surface_envcheck()
                output_file = f'{self.workdir}{self.mapname}_residue_local_resolution.json'
                if os.path.isfile(output_file):
                    map_local_resolution_views(self.mapname, data_type, chimerax, self.workdir, output_file)
                else:
                    map_local_resolution_views(self.mapname, data_type, chimerax, self.workdir)
            except Exception as e:
                print(f'Local resolution calculation or results saving failed: {e}.')

        else:
            print('No raw map found.')

        end = timeit.default_timer()
        print('Local resolution views time: %s' % (end - start))
        print('------------------------------------')

    @profile_peak_memory()
    def emringer(self):
        """
            Emringer score
        :return: None
        """

        if self.platform == 'emdb' and self.met != 'tomo':
            start = timeit.default_timer()
            errlist = []
            # if strudelapp and self.models:
            if self.models:
                for model in self.models:
                    full_model = '{}{}'.format(self.workdir, os.path.basename(model.filename))
                    full_map = '{}{}'.format(self.workdir, self.mapname)
                    out_path = '{}_emringer'.format(full_model)

                    rerr = run_emringer(full_model, full_map, out_path)
                    end = timeit.default_timer()
                    print('EMRinger time: %s' % (end - start))
                    print('------------------------------------')
                    if rerr:
                        err = 'Strudel calculation error: {}'.format(rerr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                        print('------------------------------------')

            else:
                print('No model or resolution is not covered in the motif library (<4.0Å) ')
                print('------------------------------------')

        return None


    def threedfsc(self):
        """

            Emringer score

        :return:
        """

        if self.platform == 'emdb' and self.met != 'tomo':
            if self.threedfscdir is not None:
                start = timeit.default_timer()
                errlist = []
                if self.hmodd is not None and self.hmeven is not None:
                    out_path = '{}_3dfsc'.format(self.map.fullname)
                    vxsizes = self.map.voxel_size
                    if vxsizes.x == vxsizes.y == vxsizes.z and self.hmodd.voxel_size == self.hmeven.voxel_size:
                        rerr = run_threedfsc(self.hmodd.fullname, self.hmeven.fullname, self.map.fullname,
                                             vxsizes.x, out_path, self.threedfscdir)
                        end = timeit.default_timer()
                        print('3DFSC time: %s' % (end - start))
                        if rerr:
                            err = '3DFSC calculation error: {}'.format(rerr)
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                            print('------------------------------------')
                        else:
                            print('------------------------------------')

                    else:
                        print('3DFSC input map need to be cubic and two half maps need to have same voxel size.')
                        print('------------------------------------')

                else:
                    print('No half map information for 3DFSC calculation.')
                    print('------------------------------------')
            else:
                print('No threedfsc information provided, use --threeddir/-threedd <full file path>.')

        return None
