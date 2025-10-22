"""

preparation.py

preparation class is used to initialize the input and working
environment for validation analysis.

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


import os
import sys
import psutil
import re
import codecs
import timeit
import json
import glob
import argparse
import logging
import mrcfile
import numpy as np
import xml.etree.ElementTree as ET
import copy
import gemmi
from PIL import Image
from Bio.PDB import MMCIFParser
from Bio.PDB.mmcifio import MMCIFIO
from Bio.PDB.PDBIO import Select
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
# from emda.core import iotools
# from emda import emda_methods
from va.validationanalysis import ValidationAnalysis
from va.version import __version__
from va.utils.misc import out_json, create_symbolic_link, keep_three_significant_digits
from va.utils.MapProcessor import MapProcessor
from memory_profiler import profile

try:
    from PATHS import MAP_SERVER_PATH
    from PATHS import THREEDFSC_ROOT
    from PATHS import LIB_STRUDEL_ROOT
except ImportError:
    MAP_SERVER_PATH = None
    THREEDFSC_ROOT = None
    LIB_STRUDEL_ROOT = None


class NotDisordered(Select):
    """Select non-disordered atoms from a Biopython structure.

    This selector keeps only atoms that are either not disordered
    or explicitly marked with alternative location ``"A"``.
    """

    def accept_atom(self, atom):
        """Return whether the atom should be accepted.

        Args:
            atom (Bio.PDB.Atom.Atom): Atom instance from the Biopython library.

        Returns:
            bool: ``True`` if the atom is not disordered or has altloc "A".
        """
        if (not atom.is_disordered()) or atom.get_altloc() == "A":
            atom.set_altloc(" ")
            return True
        else:
            return False

class PreParation:

    def __init__(self):
        """
        Initializes the PreParation object for validation analysis.

        This constructor sets up input parameters, working directories, and environment variables
        based on command-line arguments, JSON input, or default values. It loads map and model
        information, sets up paths for output, and prepares attributes for further analysis.

        Args:
            self: Instance of the PreParation class.

        Raises:
            FileNotFoundError: If required files are missing.
            KeyError: If expected keys are missing in input data.
            Exception: For any other errors during initialization.

        Attributes:
            args: Parsed command-line arguments.
            emdid: EMDB identifier.
            json: Path to input JSON file.
            mapname: Name of the map file.
            subdir: Subdirectory for the entry.
            vadir: Working directory for validation analysis.
            model: List of model file names.
            contourlevel: Recommended contour level.
            evenmap: Even half-map file name.
            oddmap: Odd half-map file name.
            resolution: Map resolution.
            method: Experimental method type.
            masks: Dictionary of mask files and scaling factors.
            modelmap: Flag for model map generation.
            mofit_libpath: Path to Strudel library.
            threedfscdir: Path to 3DFSC results.
            onlybar: Flag for bar plot merging.
            run: List of analysis steps to run.
            run_exclude: List of analysis steps to exclude.
            fscfile: Path to FSC XML file.
            platform: Data platform type.
            queue: Job queue name.
            update_resolution_bin_file: Path to resolution bin update file.
            full_modelpath: Full path to Strudel model (if applicable).
            full_mappath: Full path to Strudel map (if applicable).
            strdout: Output directory for Strudel results (if applicable).
        """

        self.args = self.read_para()
        self.emdid = self.args.emdid
        self.json = self.args.j
        methoddict = {'tomography': 'tomo', 'twodcrystal': 'crys', 'singleparticle': 'sp',
                      'subtomogramaveraging': 'subtomo', 'helical': 'heli', 'crystallography': 'crys',
                      'single particle': 'sp', 'subtomogram averaging': 'subtomo'}
        if self.emdid:
            self.mapname = 'emd_{}.map'.format(self.emdid)
            self.subdir = self.folders(self.emdid)
            self.vadir = '{}{}/va/'.format(MAP_SERVER_PATH, self.subdir)
            filepath = '{}{}/va/{}'.format(MAP_SERVER_PATH, self.subdir, self.mapname)
            try:
                emcif_file = os.path.join(self.vadir, f'emd-{self.emdid}.cif')
                inputdict_cif = self.parse_emdb_cif(emcif_file) if os.path.isfile(emcif_file) else None
                inputdict = inputdict_cif or self.read_header()

                if os.path.isfile(filepath):
                    if inputdict_cif:
                        # Load information from EM CIF
                        pdb_id = inputdict_cif.get('PDB')
                        self.model = [pdb_id.lower() + '.cif'] if pdb_id else None
                        self.contourlevel = inputdict_cif.get('primary_contour')
                        self.evenmap = inputdict_cif.get('even')
                        self.oddmap = inputdict_cif.get('odd')
                        self.resolution = inputdict_cif.get('resolution')
                        self.method = methoddict.get(inputdict_cif.get('method', '').replace(" ", ""))
                        if 'mask' in inputdict_cif:
                            mask_path = inputdict_cif['mask']
                            self.masks = {mask_path: 1.0}
                        else:
                            self.masks = {}

                    else:
                        # Load information from header file
                        self.model = inputdict.get('fitmodels')
                        self.contourlevel = inputdict.get('reccl')
                        halfmaps = inputdict.get('halfmaps', [])
                        self.evenmap, self.oddmap = (halfmaps[0], halfmaps[1]) if len(halfmaps) == 2 else (None, None)
                        self.pid = inputdict.get('fitpid')
                        self.method = inputdict.get('method', '').lower()
                        self.resolution = inputdict.get('resolution')
                        self.masks = inputdict.get('masks') or self.collectmasks()

                # Set additional attributes
                self.modelmap = self.args.modelmap
                self.mofit_libpath = LIB_STRUDEL_ROOT
                self.threedfscdir = THREEDFSC_ROOT
                self.onlybar = self.args.onlybar

            except FileNotFoundError as e:
                logging.error(f"File not found: {e}")
            except KeyError as e:
                logging.error(f"Missing key in input data: {e}")
            except Exception as e:
                logging.error(f"An error occurred: {e}")


            self.run = self.args.run
            self.run_exclude = self.args.run_exclude
            if any(x in ['rmmcc', 'mmfsc'] for x in self.run):
                self.modelmap = True
            self.fscfile = self.findfscxml()
            self.platform = 'emdb'
            if self.args.p in ['emdb', 'wwpdb']:
                self.platform = self.args.p
            else:
                print('Please use "emdb" or "wwpdb" as platform argument.')
            self.queue = self.args.jobqueue
            self.update_resolution_bin_file = self.args.update_resolution_bin_file

        elif self.json:
            (self.mapname, self.vadir, self.model, self.contourlevel, self.evenmap, self.oddmap, \
             self.fscfile, self.method, self.resolution, self.masks, self.run, self.run_exclude, self.platform, \
             self.modelmap, self.onlybar, self.update_resolution_bin_file, self.threedfscdir, \
             self.mofit_libpath) = self.read_json(self.json)
            self.method = methoddict[self.method.lower()] if self.method is not None else None

        else:

            if self.args.positions is None:
                self.mapname = self.args.m
                self.model = self.args.f
                self.pid = self.args.pid
                self.emdid = self.args.emdid
                self.evenmap = self.args.hmeven
                self.oddmap = self.args.hmodd
                self.contourlevel = self.read_contour()
                self.run = self.args.run
                self.run_exclude = self.args.run_exclude
                self.vadir = self.args.d + '/'
                self.method = methoddict[self.args.met.lower()] if self.args.met is not None else None
                self.resolution = self.args.s
                self.platform = 'emdb'
                if self.args.p in ['emdb', 'wwpdb']:
                    self.platform = self.args.p
                else:
                    print('Please use "emdb" or "wwpdb" as platform argument.')

                if self.args.ms is not None:
                    self.masks = {self.vadir + i: float(j) for i, j in zip(self.args.ms, self.args.mscl)}
                else:
                    self.masks = {}
                self.fscfile = self.findfscxml()
                self.modelmap = True if self.args.modelmap else False
                self.onlybar = True if self.args.onlybar else False
                self.threedfscdir = self.args.threeddir if self.args.threeddir else None
                self.mofit_libpath = self.args.strdlib if self.args.strdlib else None
                self.update_resolution_bin_file = self.args.update_resolution_bin_file if self.args.update_resolution_bin_file else None
            else:
                if self.args.positions == 'strudel':
                    self.full_modelpath = self.args.strdmodel
                    self.full_mappath = self.args.strdmap
                    self.mofit_libpath = self.args.strdlib
                    self.strdout = self.args.strdout
                    self.vadir = self.args.strdout

    def findfscxml(self):
        """Finds the `fsc.xml` file in the working directory if it exists.

        Returns:
            str or None: The filename of the `fsc.xml` file if found and only one exists,
            otherwise `None`. Prints a message if no file or multiple files are found.
        """

        fscxmlre = '*_fsc.xml'
        fscxmlarr = glob.glob(self.vadir + fscxmlre)
        if not fscxmlarr:
            print('No fsc.xml file can be read for FSC information.')
            return None
        elif len(fscxmlarr) > 1:
            print('There are more than one FSC files in the folder. Please make sure only one exist.')
            return None
        else:
            filefsc = os.path.basename(fscxmlarr[0])
            return filefsc

    def read_json(self, injson):
        """Loads input arguments from a JSON file and returns a tuple of parameters for the pipeline.

        Args:
            injson (str): Path to the input JSON file.

        Returns:
            tuple: Contains the following elements:
                - map (str): Map file name.
                - workdir (str): Working directory path.
                - models (list or None): List of model names or None.
                - cl (float or None): Contour level value or None.
                - evenmap (str or None): Even map file name or None.
                - oddmap (str or None): Odd map file name or None.
                - fscfile (str or None): FSC file name or None.
                - method (str or None): Method type or None.
                - resolution (float or None): Resolution value or None.
                - masks (dict): Dictionary of mask file paths and contours.
                - runs (str or list): Runs to execute.
                - run_exclude (str or list or None): Runs to exclude or None.
                - platform (str): Platform type ('emdb' or 'wwpdb').
                - modelmap (bool): Whether to perform model map calculations.
                - onlybar (bool): Whether to merge only bar images.
                - update_resolution_bin_file (str or None): Path to resolution bin file or None.
                - threedfscdir (str or None): 3DFSC directory path or None.
                - mofit_libpath (str or None): Strudel library path or None.

        Raises:
            AssertionError: If required fields are missing in the input JSON.

        Prints:
            Informational messages if certain fields are missing or not specified.
        """

        if injson:
            with open(injson, 'r') as f:
                args = json.load(f)
            argsdata = args['inputs']
            map = argsdata['map']
            assert map is not None, "There must be a map needed in the input JSON file."
            assert argsdata['workdir'] is not None, "Working directory must be provided in the input JSON file."
            workdir = str(argsdata['workdir'] + '/')
            if 'contour_level' in argsdata and argsdata['contour_level'] is not None:
                cl = argsdata['contour_level']
            else:
                print('There is no contour level.')
                cl = None

            if 'evenmap' in argsdata and argsdata['evenmap'] is not None:
                evenmap = argsdata['evenmap']
            else:
                print('There is no evnemap.')
                evenmap = None

            if 'oddmap' in argsdata and argsdata['oddmap'] is not None:
                oddmap = argsdata['oddmap']
            else:
                print('There is no oddmap.')
                oddmap = None

            if 'fscfile' in argsdata and argsdata['fscfile'] is not None:
                fscfile = argsdata['fscfile']
            else:
                print('There is no fsc file.')
                fscfile = None

            if 'method' in argsdata and argsdata['method'] is not None:
                method = argsdata['method']
            else:
                print('There is no method information.')
                method = None

            if 'resolution' in argsdata and argsdata['resolution'] is not None:
                resolution = argsdata['resolution']
            else:
                print('There is no resolution information.')
                resolution = None

            if 'runs' in argsdata and argsdata['runs'] is not None:
                runs = argsdata['runs']
            else:
                runs = 'all'

            if 'run_exclude' in argsdata and argsdata['run_exclude'] is not None:
                run_exclude = argsdata['run_exclude']
            else:
                run_exclude = None

            if 'models' in argsdata and argsdata['models'] is not None:
                models = [argsdata['models'][item]['name'] for item in argsdata['models'] if item is not None]
            else:
                models = None

            if 'masks' in argsdata and argsdata['masks'] is not None:
                masks = {workdir + argsdata['masks'][item]['name']: argsdata['masks'][item]['contour']
                          for item in argsdata['masks']}
            else:
                masks = {}

            if 'platform' in argsdata and argsdata['platform'] in ['emdb', 'wwpdb']:
                platform = str(argsdata['platform'])
            else:
                print('There is no platform information.')
                platform = 'emdb'

            if 'modelmap' in argsdata and argsdata['modelmap'] == 1:
                modelmap = True
            else:
                modelmap = False
                print('Model map and related calculations will not be done. Please specify modelmap in input json.')

            if 'onlybar' in argsdata and argsdata['onlybar'] == 1:
                onlybar = True
            else:
                onlybar = False

            if 'update_resolution_bin_file' in argsdata and argsdata['update_resolution_bin_file'] is not None:
                update_resolution_bin_file = argsdata['update_resolution_bin_file']
            else:
                update_resolution_bin_file = None

            if '3dfscdir' in argsdata and argsdata['3dfscdir'] is not None:
                threedfscdir = argsdata['3dfscdir']
            else:
                print('There is no 3dfsc directory information.')
                threedfscdir = None

            if 'strudellib' in argsdata and argsdata['strudellib'] is not None:
                mofit_libpath = argsdata['strudellib']
            else:
                print('There is no 3dfsc directory information.')
                mofit_libpath = None

            return (map, workdir, models, cl, evenmap, oddmap, fscfile,
                    method, resolution, masks, runs, run_exclude, platform, modelmap,
                    onlybar, update_resolution_bin_file, threedfscdir, mofit_libpath)
        else:
            print('Input JSON needed.')

    def runs(self):
        """Checks and processes the parameters for the `-run` argument.

        Returns:
            list: A list of enabled run modes based on the input arguments.

        Notes:
            - If `self.run` is a string, it is converted to lowercase.
            - If `self.run` is a list, all elements are converted to lowercase.
            - If the first run argument is 'validation', returns a predefined list of modes.
            - Otherwise, returns the intersection of available modes and requested runs, excluding any in `self.run_exclude`.
        """

        # If only one argument, it will be string type and should be converted to lower letters directly
        # For more than one arguments, it will be list type
        if isinstance(self.run, str):
            runs = self.run.lower()
        else:
            runs = [x.lower() for x in self.run]
        if runs[0] == 'validation':
            return ['projection', 'central', 'surface', 'volume', 'density', 'raps', 'largestvariance', 'mask',
                    'inclusion', 'fsc', 'qscore']
                    # 'smoc', 'resccc', 'locres']
        else:
            resdict = {'all': False, 'projection': False, 'central': False, 'surface': False, 'density': False,
                       'volume': False, 'fsc': False, 'raps': False, 'mapmodel': False, 'inclusion': False,
                       'largestvariance': False, 'mask': False, 'symmetry': False, 'rmmcc': False, 'smoc': False,
                       'resccc': False, 'emringer': False, 'strudel': False, '3dfsc': False, 'locres': False,
                       'phrand': False, 'predictcontour': False}
            for key in resdict.keys():
                if key in runs:
                    resdict[key] = True
            # If -run has arguments but do not fit with any above, set to all to True
            if True not in resdict.values():
                resdict['all'] = False

            runlist = []

            # not for OneDep for now: mmfsc, symmetry, qscore, some projectioins
            if self.mapname is not None:
                runlist.extend(['projection', 'central', 'surface', 'volume', 'density', 'raps', 'largestvariance',
                                'mask', 'fsc', 'mmfsc', 'rmmcc', 'symmetry', 'qscore', 'strudel', 'emringer', '3dfsc',
                                'smoc', 'resccc', 'locres', 'phrand', 'predictcontour',
                                ])

            if self.masks is None:
                runlist.remove('mask')

            if self.model is not None and self.contourlevel is not None:
                runlist.extend(['inclusion'])
            else:
                sys.stderr.write('REMINDER: Contour level or model needed for atom and residue inclusion.\n')

            if runs[0] == 'all' or runs == 'all':
                finallist = runlist
            else:
                finallist = list(set(runlist) & set(runs))

            if self.run_exclude is not None:
                finallist = [item for item in finallist if item not in self.run_exclude]

            return finallist

    @staticmethod
    def folders(emdid):
        """Generate a subdirectory path for an EMDB entry based on its ID.

        Args:
            emdid (str): The EMDB entry ID.

        Returns:
            str or None: The subdirectory path for the entry if the ID is valid, otherwise None.

        Example:
            folders("123456") -> "12/34/123456"
        """

        breakdigits = 2
        emdbidmin = 4
        if len(emdid) >= emdbidmin and isinstance(emdid, str):
            topsubpath = emdid[:breakdigits]
            middlesubpath = emdid[breakdigits:-breakdigits]
            subpath = os.path.join(topsubpath, middlesubpath, emdid)

            return subpath
        else:
            return None

    @staticmethod
    def parse_emdb_cif(file_path):
        """Parse an EMDB mmCIF file and extract key metadata.

        Args:
            file_path (str): Path to the EMDB mmCIF file.

        Returns:
            dict: Dictionary containing resolution, reconstruction method, map file names and contours,
                and database cross-references (e.g., PDB accession).

        Raises:
            Exception: If the file cannot be parsed or required fields are missing.

        Example:
            result = PreParation.parse_emdb_cif('/path/to/emd-xxxx.cif')
        """

        doc = gemmi.cif.read_file(file_path)
        block = doc.sole_block()

        # Extract resolution and reconstruction method
        reconstruction_method = block.find_value('_em_experiment.reconstruction_method').replace("'", "").lower() or None
        resolution = block.find_value('_em_3d_reconstruction.resolution')
        resolution = float(resolution) if resolution and resolution != '?' else None
        if resolution is None and reconstruction_method != 'tomography':
            resolution_loop = block.find_loop('_em_3d_reconstruction.resolution')
            resolution = next(x for x in resolution_loop if x != '?')

        # Initialize map containers
        map_data = {'primary': {}, 'mask': {}, 'odd': {}, 'even': {}}

        # Extract map-related loops
        contour_loop = block.find_loop('_em_map.contour_level')
        file_loop = block.find_loop('_em_map.file')
        map_type_loop = block.find_loop('_em_map.type')

        # If loops are present
        if contour_loop and file_loop and map_type_loop:
            contour_levels = [None if row == '?' else row for row in contour_loop]
            map_files = [row for row in file_loop]
            map_types = [row.replace("'", "") for row in map_type_loop]
        else:
            # Check if individual items exist instead
            try:
                contour_level = float(block.find_value('_em_map.contour_level'))
                map_file = block.find_value('_em_map.file')[:-3]
                map_type = block.find_value('_em_map.type').replace("'", "")  # sanitize string

                contour_levels = [contour_level]
                map_files = [map_file]
                map_types = [map_type]
            except Exception as e:
                # fallback or log error
                contour_levels, map_files, map_types = [], [], []

        # Parse combined map data
        for map_file, contour, map_type in zip(map_files, contour_levels, map_types):
            map_key = map_file[:-3] if map_file.endswith('.gz') else map_file
            try:
                contour = float(contour) if contour is not None else None
            except:
                continue  # skip if contour is not valid

            if map_type == 'primary map':
                map_data['primary'] = {'primary': map_key, 'primary_contour': contour}
            if map_type == 'half map' and 'half_map_1' in map_file:
                map_data['odd'] = {'odd': map_key, 'odd_contour': contour}
            if map_type == 'half map' and 'half_map_2' in map_file:
                map_data['even'] = {'even': map_key, 'even_contour': contour}
            if 'msk' in map_file:
                map_data['mask'] = {'mask': map_file, 'mask_contour': contour}

        # Extract database cross-references
        db_ids = block.find_loop('_database_2.database_id')
        db_codes = block.find_loop('_database_2.database_code')
        db_accessions = block.find_loop('_database_2.pdbx_database_accession')

        db_info = {}
        if db_ids and db_codes and db_accessions:
            for db, code, accession in zip(db_ids, db_codes, db_accessions):
                db_name = db
                db_code = code
                accession_code = accession if accession else None

                db_info[db_name] = db_code
                if db_name == 'PDB' and accession_code:
                    db_info['accession'] = accession_code

        # Final merge and return
        result = {
            'resolution': resolution,
            'method': reconstruction_method,
            **map_data['primary'],
            **map_data['mask'],
            **map_data['odd'],
            **map_data['even'],
            **db_info
        }

        return result

    def read_header(self):
        """Parses the EMDB XML header file and extracts metadata for validation analysis.

        Args:
            self: Instance of the class containing required attributes (`emdid`, `subdir`, `vadir`).

        Returns:
            dict: Dictionary containing extracted metadata, including:
                - fitmodels (list or None): List of fitted model file names or None for tomography.
                - fitpid (list): List of fitted model IDs.
                - reccl (float or None): Recommended contour level.
                - halfmaps (list): List of half map file paths.
                - method (str): Experimental method type (e.g., 'tomo', 'sp').
                - resolution (str or None): Map resolution.
                - masks (dict or None): Dictionary of mask file paths and scaling factors.

        Raises:
            OSError: If the header file does not exist.
        """

        headerfile = '{}{}/va/emd-{}.xml'.format(MAP_SERVER_PATH, self.subdir, self.emdid)
        headerdict = {}
        if os.path.isfile(headerfile):
            tree = ET.parse(headerfile)
            root = tree.getroot()

            # Model
            fitmodel = []
            fitpid = []
            for model in tree.findall('./crossreferences/pdb_list/pdb_reference/pdb_id'):
                fitmodel.append(model.text.lower() + '.cif')
                fitpid.append(model.text.lower())

            # contour
            contour_list = []
            for contour in tree.findall('./map/contour_list/contour/level'):
                contour_list.append(contour.text.lower())
            reccl = None
            if contour_list:
                #reccl = "{0:.3f}".format(float(contour_list[0]))
                reccl = float(contour_list[0])

            # Half maps
            halfmapsfolder = '{}{}/va/*_half_map_*.map'.format(MAP_SERVER_PATH, self.subdir)
            all_files = glob.glob(halfmapsfolder)
            halfmaps = [f for f in all_files if re.match(r'.*emd_\d+_half_map_[12]\.map$', f)]

            # check when there is fitted models for tomography data, do not count the fitted model
            # for calculating atom inclusion, residue inclusion or map model view
            structure_determination_list = root.find('structure_determination_list')
            structure_determination = structure_determination_list.find('structure_determination') if structure_determination_list else None
            cur_method = structure_determination.find('method') if structure_determination else None
            method = cur_method.text if not cur_method else None
            headerdict['fitmodels'] = None if method == 'tomography' else fitmodel

            # Resolution
            all_processings = {
                'singleParticle': 'singleparticle',
                'subtomogramAveraging': 'subtomogram_averaging',
                'tomography': 'tomography',
                'electronCrystallography': 'crystallography',
                'helical': 'helical'
            }
            processing = all_processings[method] if method else None
            cur_processing = '{}_processing'.format(processing) if processing else None
            tres = structure_determination.find('./{}/final_reconstruction/resolution'.format(cur_processing))
            resolution = tres.text if tres is not None else None

            # Masks
            masks = {}
            for model in tree.findall('./interpretation/segmentation_list/segmentation/file'):
                # masks.append(self.dir + child.find('file').text)
                # Here as there is no mask value from the header, I use 1.0 for all masks
                masks[self.vadir + model.text.lower()] = 1.0

            methoddict = {'tomography': 'tomo', 'electronCrystallography': '2dcrys', 'singleParticle': 'sp',
                          'subtomogramAveraging': 'subtomo', 'helical': 'heli'}

            headerdict['fitmodels'] = fitmodel if fitmodel else None
            headerdict['fitpid'] = fitpid
            headerdict['reccl'] = reccl
            headerdict['halfmaps'] = halfmaps
            headerdict['method'] = methoddict[method]
            headerdict['resolution'] = resolution
            headerdict['masks'] = masks if masks else None


            return headerdict

        else:
            print('Header file: %s does not exit.' % headerfile)
            raise OSError('Header file does not exist.')

    @staticmethod
    def str2bool(arg_input):
        """Converts an input value to a boolean type for use in argument parsing.

        Args:
            arg_input (Any): The input value to convert. Can be a bool or a string.

        Returns:
            bool: The converted boolean value.

        Raises:
            argparse.ArgumentTypeError: If the input cannot be interpreted as a boolean.
        """

        if isinstance(arg_input, bool):
            return arg_input
        if arg_input.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif arg_input.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected')

    @staticmethod
    def read_para():
        """Parses command-line arguments for the validation analysis pipeline.

        Returns:
            argparse.Namespace: Parsed arguments containing input file paths, options, and analysis parameters.

        Raises:
            AssertionError: If no arguments are provided to the command.

        Command-line Arguments:
            -m: Density map file.
            -d: Directory of all input files.
            -f: Structure model file names (space separated).
            -pid: PDB ID for use with "-f".
            -hmeven: Half map.
            -hmodd: The other half map.
            -cl: Recommended contour level.
            -run: Run customized validation analysis (default: 'all').
            -re, --run-exclude: Exclude specific validation analysis steps.
            -met: EM method (choices: tomography, twodcrystal, crystallography, singleparticle, sub...).
            -s: Resolution of the map.
            -ms: All masks.
            -mscl: Contour levels for the masks.
            -p: Platform ('emdb' or 'wwpdb', default: 'emdb').
            -i, --modelmap: Whether to produce model map.
            --b, -onlybar: Only produce bar images.
            --strdlib: Strudel library path.
            --threeddir, -threedd: 3DFSC root directory.
            -q, --jobqueue: Job queue (default: 'production').
            -u, --update_resolution_bin_file: Path to CSV for Q-score resolution bin update.
            -emdid: EMDB ID for running without other parameters.
            -j: JSON file with all arguments.
            strudel: Subparser for Strudel calculation.
            resmap: Subparser for ResMap local resolution calculation.

        Exits:
            If no required arguments are provided, prints usage and exits the program.
        """

        assert len(sys.argv) > 1, ('There has to be arguments for the command.\n \
               Usage: mainva.py [-h] -m [M] -d [D] [-f [F]] [-pid [PID]] [-hm [HM]] [-cl [CL]]\n \
               or:    mainva.py -emdid <EMDID>\n \
               or:    mainva.py -j <input.json>')
        methodchoices = ['tomography', 'twodcrystal', 'crystallography', 'singleparticle', 'single particle',
                         'subtomogramaveraging', 'subtomogram averaging', 'helical']

        parser = argparse.ArgumentParser(description='Input density map(name) for Validation Analysis')
        #parser = mainparser.add_mutually_exclusive_group(required = True)
        parser.add_argument('--version', '-V', action='version', version='va: {version}'.format(version=__version__),
                            help='Version')
        parser.add_argument('-f', nargs='*',
                            help='Structure model file names. Multiple model names can be used with space separated.')
        parser.add_argument('-pid', nargs='?', help='PDB ID which needed while "-f" in use.')
        parser.add_argument('-hmeven', nargs='?', help='Half map.')
        parser.add_argument('-hmodd', nargs='?', help='The other half map.')
        parser.add_argument('-cl', nargs='?', help='The recommended contour level .')
        parser.add_argument('-run', nargs='*', help='Run customized validation analysis.', default='all')
        parser.add_argument( '-re', '--run-exclude', nargs='*', help='Run customized validation analysis.', default=None)
        parser.add_argument('-met', nargs='?', help='EM method: tomography-tomo, twoDCrystal-2dcrys, singleParticle-sp, '
                                                    'subtomogramAveraging-subtomo, helical-heli', choices=methodchoices)
        parser.add_argument('-s', nargs='?', help='Resolution of the map.')
        parser.add_argument('-ms', nargs='*', help='All masks')
        parser.add_argument('-mscl', nargs='*', help='Contour level corresponding to the masks.')
        parser.add_argument('-p', nargs='?', type=str, help='Platform to run the data either wwpdb or emdb', default='emdb')
        parser.add_argument('-i', '--modelmap', type=PreParation.str2bool,
                            help='If specified then model map will be produce or vice versa', default=False)
        parser.add_argument('--b', '-onlybar', dest='onlybar', type=PreParation.str2bool,
                            help='If specified then only produce bar instead of running actual metric', default=False)
        parser.add_argument('--strdlib', nargs='?', help='Strudel library path')
        parser.add_argument('--threeddir', '-threedd', nargs='?', type=str, help='3DFSC root directory')
        parser.add_argument('-q', '--jobqueue', nargs='?', help='Partitions chosen to run jobs on codon', default='production')
        # parser.add_argument('-u', '--update_resolution_bin',  dest='update_resolution_bin', type=PreParation.str2bool, default=False, help='Update resolution bin for Q-score (default: False)')
        parser.add_argument(
            '-u', '--update_resolution_bin_file',
            dest='update_resolution_bin_file',
            type=str,
            default=None,
            help='Full path to a CSV file for updating resolution bin for Q-score'
        )
        requiredname = parser.add_argument_group('required arguments')
        requiredname2 = parser.add_argument_group('alternative required arguments')
        requiredname3 = parser.add_argument_group('alternative required arguments')
        # requiredname_strudel = parser.add_argument_group('Strudel calculation arguments')
        requiredname.add_argument('-m', nargs='?', help='Density map file')
        requiredname.add_argument('-d', nargs='?', help='Directory of all input files')
        # requiredname_strudel.add_argument('strudel', nargs='?', help='Strudel calculation')
        requiredname2.add_argument('-emdid', nargs='?', help='EMD ID with which can run without other parameters.')
        requiredname3.add_argument('-j', nargs='?', help='JSON file which has all arguments.')
        # requiredname_strudel.add_argument('--strdmodel', nargs='?', help='Strudel model path')
        # requiredname_strudel.add_argument('--strdmap', nargs='?', help='Strudel map path')
        # requiredname_strudel.add_argument('--strdlib', nargs='?', help='Strudel library path')

        subparser = parser.add_subparsers(dest='positions')
        pstrudel = subparser.add_parser('strudel', description='Calculation of Strudel')
        pstrudel.add_argument('-p', '--strdmodel', nargs='?', help='Strudel model path')
        pstrudel.add_argument('-m', '--strdmap', nargs='?', help='Strudel map path')
        pstrudel.add_argument('-l', '--strdlib', nargs='?', help='Strudel library path')
        pstrudel.add_argument('-d', '--strdout', nargs='?', help='Strudel output path')


        presmap = subparser.add_parser('resmap', description='Calculation of local resolution with ResMap')
        presmap.add_argument('-o', '--oddmap', nargs='?', help='Full path to oddmap')
        presmap.add_argument('-e', '--evemap', nargs='?', help='Full path to evenmap')
        presmap.add_argument('-s', '--resmap', nargs='?', help='Full path to ResMap.py')

        args = parser.parse_args()

        checkpar = (isinstance(args.m, type(None)) and isinstance(args.f, type(None)) and
                    isinstance(args.pid, type(None)) and isinstance(args.hmeven, type(None)) and
                    isinstance(args.cl, type(None)) and isinstance(args.hmodd, type(None)) and
                    isinstance(args.emdid, type(None)) and isinstance(args.run, type(None)) and
                    isinstance(args.re, type(None)) and isinstance(args.j, type(None)) and
                    isinstance(args.ms, type(None)) and isinstance(args.mscl, type(None)) and
                    isinstance(args.p, type(None)) and isinstance(args.modelmap, type(None)))

        if checkpar:
            print('There has to be arguments for the command. \n \
                  usage: mainva.py [-h] [-m [M]] [-d [D]] [-f [F]] [-pid [PID]] [-hm [HM]] [-cl [CL]]'
                  '[-i/--modelmap] [-run [all]/[central...]]\n \
                  or   : mainva.py [-emdid [EMDID]] [-run [-run [all]/[central...]]] \n \
                  or   : mainva.py [-j] <input.json>\n \
                  or   : mainva.py strudel [-p/--strdmodel] <fullmodelpath> [-m/strdmap] <fullmappath>\n \
                                            [-l/--strdlib] <Strudel library path> [-d/--strdout] <Strudel output path>')
            sys.exit()
        return args

    def collectmasks(self):
        """Collects valid mask files from the working directory and returns a dictionary mapping mask file names to contour levels.

        This function searches for files in `self.vadir` matching the mask pattern (`*_mask*.map` or `*_msk*.map`),
        excludes files containing 'binarized' or 'masked', and verifies that each file is a valid MRC file.
        All found masks are assigned a contour level of 1.0.

        Returns:
            dict: A dictionary where keys are mask file names and values are contour levels (float, always 1.0).
        """

        mask_pattern = re.compile(r'(.*?)_(mask|msk)(.*?)\.map')

        # Helper function to validate MRC file
        def is_valid_mrc(file_path):
            try:
                mrcfile.mmap(file_path)
                return True
            except ValueError:
                return False

        # Collect masks using a single comprehension
        search_mask = [
            file for file in os.listdir(self.vadir)
            if mask_pattern.match(file)
               and 'binarized' not in file
               and 'masked' not in file
               and is_valid_mrc(os.path.join(self.vadir, file))
        ]

        if search_mask:
            print(
                '!!! Be careful: masks were only taken from the folder instead of the header. '
                'Header missing the corresponding information. All masks assume proper contour 1.0.'
            )
            return {mask: 1.0 for mask in search_mask}

        return {}

    def read_contour(self):
        """Returns the contour level for the map.

        If the contour level is provided via command-line arguments, it returns that value as a float.
        Otherwise, returns None. If not provided, a future implementation may estimate a reasonable contour level.

        Returns:
            float or None: The contour level if specified, otherwise None.
        """

        if self.args.cl:
            return float(self.args.cl)
        else:
            # Todo: Add a estimated contour level function here
            return None

    # @profile
    def write_map(self, outmap_name, mapdata, nstarts, org_header):
        """Saves a map to disk with corrected axes and header information.

        Args:
            outmap_name (str): Output file name for the map.
            mapdata (np.ndarray): Map data array to be saved.
            nstarts (tuple): Starting indices (nxstart, nystart, nzstart) for the map axes.
            org_header (mrcfile.header.Header): Original MRC header to copy metadata from.

        Returns:
            None
        """

        # with mrcfile.new(outmap_name, overwrite=True) as mout:
        mout = mrcfile.new(outmap_name, overwrite=True)
        mout.set_data(mapdata)
        mout.update_header_from_data()
        mout.header.cella = org_header.cella
        mout.header.cellb = org_header.cellb

        mout.header.nxstart, mout.header.nystart, mout.header.nzstart = nstarts

        mout.header.mapc = 1
        mout.header.mapr = 2
        mout.header.maps = 3

        mout.header.mx = org_header.mx
        mout.header.my = org_header.my
        mout.header.mz = org_header.mz

        mout.header.origin.x = org_header.origin.x
        mout.header.origin.y = org_header.origin.y
        mout.header.origin.z = org_header.origin.z
        mout.header.label = org_header.label
        mout.flush()
        mout.close()

    # @profile
    def new_frommrc_totempy(self, fullmapname):
        """Load a map into mrcfile object, correcting axis order if necessary.

        Args:
            fullmapname (str): Path to the primary MRC map file.

        Returns:
            mrcfile.mmap: A memory-mapped MRC map object with corrected axes.
        """

        reload_map = None
        mrcmap = mrcfile.mmap(fullmapname, mode='r+')
        mrcheader = mrcmap.header
        datatype = mrcmap.data.dtype
        # mapdata = mrcmap.data.astype('float')
        mapdata = mrcmap.data
        crs = (mrcheader.mapc, mrcheader.mapr, mrcheader.maps)
        nstarts = (mrcheader.nxstart, mrcheader.nystart, mrcheader.nzstart)
        reversecrs = crs[::-1]
        stdcrs = (3, 2, 1)
        diffcrs = tuple(x-y for x, y in zip(reversecrs, stdcrs))
        if diffcrs != (0, 0, 0):

            aa = copy.deepcopy(mrcmap.header.mx)
            bb = copy.deepcopy(mrcmap.header.my)
            cc = copy.deepcopy(mrcmap.header.mz)

            crsindices = (crs.index(1), crs.index(2), crs.index(3))
            new_order = [2 - crsindices[2 - i] for i in (0, 1, 2)]
            mapdata = mapdata.transpose(new_order)
            nstarts = [mrcmap.header.nxstart, mrcmap.header.nystart, mrcmap.header.nzstart]

            x = copy.deepcopy(nstarts[crsindices[0]])
            y = copy.deepcopy(nstarts[crsindices[1]])
            z = copy.deepcopy(nstarts[crsindices[2]])

            # mrcmap.set_data(mapdata)
            # mrcmap.update_header_from_data()
            # mrcmap.header.mapc = 1
            # mrcmap.header.mapr = 2
            # mrcmap.header.maps = 3
            #
            # mrcmap.header.nxstart = x
            # mrcmap.header.nystart = y
            # mrcmap.header.nzstart = z
            #
            # mrcmap.header.mx = aa
            # mrcmap.header.my = bb
            # mrcmap.header.mz = cc

            output_map = fullmapname[:-4] + '_nonpermuted.map'
            self.write_map(output_map, mapdata, (x, y, z), mrcheader)
            mrcmap.close()
            reload_map = mrcfile.mmap(output_map, mode='r+')
            reload_map.fullname = fullmapname

        mrcmap.fullname = fullmapname
        return reload_map if reload_map else mrcmap

    # @profile
    def read_map(self):
        """Reads a map file and returns the map object, its size, and its dimension.

        This function attempts to read the map file based on the EMDB ID or the provided working directory and map name.
        It calculates the mean and standard deviation of the map data, checks for NaN values, and returns relevant map information.
        If the map file or folder does not exist, or if the map is corrupted, the function prints an error and exits.

        Returns:
            tuple:
                - inputmap (mrcfile.mmap): The loaded map object.
                - mapsize (int): Size of the map file in bytes.
                - mapdimension (int): Product of map dimensions (nx \* nx \* nx).

        Raises:
            AssertionError: If NaN values are found in the map data.
            SystemExit: If the map file or folder does not exist, or if the map is corrupted.
        """

        start = timeit.default_timer()

        try:
            if self.emdid:
                fullmapname = '{}{}/va/{}'.format(MAP_SERVER_PATH, self.subdir, self.mapname)
                mapsize = os.stat(fullmapname).st_size
                # inputmap = self.frommrc_totempy(fullmapname)
                inputmap = self.new_frommrc_totempy(fullmapname)
                # self.primarymapmean = inputmap.mean()
                # self.primarymapstd = inputmap.std()
                # nancheck = np.isnan(inputmap.fullMap).any()
                self.primarymapmean = inputmap.data.mean()
                self.primarymapstd = inputmap.data.std()
                nancheck = np.isnan(inputmap.data).any()
                assert not nancheck, 'There is NaN value in the map, please check.'
                # mapdimension = inputmap.map_size()
                mapdimension = inputmap.header.nx * inputmap.header.nx * inputmap.header.nx
                end = timeit.default_timer()

                print('Read map time: %s' % (end - start))
                print('------------------------------------')

                return inputmap, mapsize, mapdimension
            elif os.path.exists(self.vadir) and self.mapname is not None:
                #print "selfmap:%s" % (self.mapname)
                fullmapname = self.vadir + self.mapname
                if not os.path.isfile(fullmapname):
                    fullmapname = self.mapname
                mapsize = os.stat(fullmapname).st_size
                # Swith off using the TEMPy to read map and using the mrcfile loaded information for reading map
                # inputmap = MapParser.readMRC(fullmapname)
                inputmap = self.new_frommrc_totempy(fullmapname)
                # self.primarymapmean = inputmap.mean()
                # self.primarymapstd = inputmap.std()
                # nancheck = np.isnan(inputmap.fullMap).any()
                self.primarymapmean = inputmap.data.mean()
                self.primarymapstd = inputmap.data.std()
                nancheck = np.isnan(inputmap.data).any()
                nan_values = np.argwhere(np.isnan(inputmap.data))
                assert not nancheck, 'There is NaN value ({}) in the map, please check.'.format(nan_values)
                # mapdimension = inputmap.map_size()
                mapdimension = inputmap.header.nx * inputmap.header.nx * inputmap.header.nx

                end = timeit.default_timer()
                print('Read map time: %s' % (end - start))
                print('------------------------------------')

                return inputmap, mapsize, mapdimension
            else:
                print('------------------------------------')
                print('Folder: %s does not exist.' % self.vadir)
                exit()
        except:
            print('Map does not exist or corrupted.')
            sys.stderr.write('Error: {} \n'.format(sys.exc_info()[1]))
            print('------------------------------------')
            exit()

    def remove_lines_after_match(self, input_file, output_file, match_text):
        """Removes all lines from `input_file` after the second occurrence of a line starting with `match_text`
        and writes the remaining lines to `output_file`.

        Args:
            input_file (str): Path to the input file to process.
            output_file (str): Path to the output file to write the result.
            match_text (str): Text to match at the start of lines.

        Returns:
            bool: True if the second match was found and lines were written, False otherwise.

        Raises:
            FileNotFoundError: If the input file does not exist.
            Exception: For any other errors during file processing.
        """

        try:
            with open(input_file, 'r') as infile:
                found_second_match = False
                match_count = 0
                content_before_second_match = []

                for line in infile:
                    if line.startswith(match_text):
                        match_count += 1
                        if match_count >= 2:
                            found_second_match = True
                            break
                    content_before_second_match.append(line)

            if found_second_match:
                with open(output_file, 'w') as outfile:
                    outfile.writelines(content_before_second_match)
                return True
            else:
                print('Second match not found in the file.')
                return False

        except FileNotFoundError:
            print(f'Error: Input file "{input_file}" not found.')
            return False
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return False

    def hasdisorder_atom(self, structure):
        """Checks if any residue in the given structure is disordered.

        Args:
            structure (Bio.PDB.Structure.Structure): A Biopython structure object.

        Returns:
            bool: True if at least one residue is disordered, False otherwise.
        """

        ress = structure.get_residues()
        disorder_flag = False
        for res in ress:
            if res.is_disordered() == 1:
                disorder_flag = True
                return disorder_flag
        return disorder_flag

    def get_auth_comp_id_map(self, input_cif):
        """Extracts a mapping from \(_chain\_id_, _resseq_\) to _auth\_comp\_id_ from an mmCIF file.

        Args:
            input_cif (str): Path to the input mmCIF file.

        Returns:
            dict: Dictionary mapping \((chain\_id, resseq)\) tuples to _auth\_comp\_id_ strings.
        """

        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif)
        mmcif_dict = parser._mmcif_dict
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']
        auth_comp_ids = mmcif_dict['_atom_site.auth_comp_id']

        auth_comp_id_map = {}
        for chain, resseq, auth_comp_id in zip(chains, resseqs, auth_comp_ids):
            key = (chain, int(resseq))
            auth_comp_id_map[key] = auth_comp_id

        return auth_comp_id_map

    def get_formal_charge_map(self, input_cif):
        """Extracts the pdbx\_formal\_charge mapping from an mmCIF file.

        Args:
            input_cif (str): Path to the input mmCIF file.

        Returns:
            dict: A dictionary mapping (chain\_id, resseq) tuples to pdbx\_formal\_charge values.
        """

        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif)
        mmcif_dict = parser._mmcif_dict
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']
        formal_charges = mmcif_dict['_atom_site.pdbx_formal_charge']

        formal_charge_map = {}
        for chain, resseq, formal_charge in zip(chains, resseqs, formal_charges):
            key = (chain, int(resseq))
            formal_charge_map[key] = formal_charge

        return formal_charge_map

    def save_updated_model(self, input_cif_file_one, input_cif_file):
        """Saves the first model from an mmCIF file to a new mmCIF file,
        updating it with `auth_comp_id` and `pdbx_formal_charge` fields.

        Args:
            input_cif_file_one (str): Path to the reference mmCIF file used to extract
                                      `auth_comp_id` and `pdbx_formal_charge` mappings.
            input_cif_file (str): Path to the mmCIF file whose first model will be updated and saved.

        Returns:
            None
        """

        # Create the auth_comp_id_map
        auth_comp_id_map = self.get_auth_comp_id_map(input_cif_file_one)
        formal_charge_map = self.get_formal_charge_map(input_cif_file_one)

        # Extract the first model
        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif_file)
        mmcif_dict = parser._mmcif_dict
        first_model = structure[0]

        # Prepare to add auth_comp_id
        if '_atom_site.auth_comp_id' not in mmcif_dict:
            mmcif_dict['_atom_site.auth_comp_id'] = []
        if '_atom_site.pdbx_formal_charge' not in mmcif_dict:
            mmcif_dict['_atom_site.pdbx_formal_charge'] = []

        # Get the existing residue information
        residues = mmcif_dict['_atom_site.label_comp_id']
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']

        # Add auth_comp_id based on the map
        for res, chain, resseq in zip(residues, chains, resseqs):
            auth_comp_id = auth_comp_id_map.get((chain, int(resseq)), res)
            formal_charge = formal_charge_map.get((chain, int(resseq)), '?')
            mmcif_dict['_atom_site.auth_comp_id'].append(auth_comp_id)
            mmcif_dict['_atom_site.pdbx_formal_charge'].append(formal_charge)

        # Write the modified dictionary to a new mmCIF file
        io = MMCIFIO()
        io.set_dict(mmcif_dict)
        io.save(input_cif_file)

    def _structure_tomodel(self, pid, curmodelname):
        """Converts a structure file (mmCIF) to a model object for Biopython.

        Handles multiple data blocks, removes extra lines after the second 'data_' occurrence,
        processes multiple models by keeping only the first, and filters out disordered atoms.

        Args:
            pid (str): Identifier for the structure or PDB ID.
            curmodelname (str): Path to the model file (mmCIF format).

        Returns:
            Structure: A Biopython model instance for further calculations.

        Raises:
            OSError: If file operations (rename, open) fail.
            Exception: For parsing errors or unexpected file content.
        """

        p = MMCIFParser()
        io = MMCIFIO()
        orgfilename = curmodelname
        # structure = p.get_structure(pid, curmodelname)

        # multiple data block
        # cur_model = open(curmodelname)
        match_text = 'data_'
        out_moderate_cif = curmodelname + '_moderated.cif'
        match = self.remove_lines_after_match(curmodelname, out_moderate_cif, match_text)
        if match:
            structure = p.get_structure(pid, out_moderate_cif)
            curmodelname = out_moderate_cif
        else:
            structure = p.get_structure(pid, curmodelname)

        if len(structure.get_list()) > 1:
            orgmodel = curmodelname + '_org.cif'
            os.rename(curmodelname, orgmodel)
            fstructure = structure[0]
            io.set_structure(fstructure)
            io.save(curmodelname)
            self.save_updated_model(orgmodel, curmodelname)
            usedframe = p.get_structure('first', curmodelname)
            print('!!!There are multiple models in the cif file. Here we only use the first for calculation.')
        else:
            usedframe = structure

        # io.set_structure(usedframe)
        if self.hasdisorder_atom(usedframe):
            curmodelname = curmodelname + '_Alt_A.cif'
            io.set_structure(usedframe)
            print('There are alternative atom in the model here we only use A for calculations and saved as {}'
                  .format(curmodelname))
            io.save(curmodelname, select=NotDisordered())
            newstructure = p.get_structure(pid, curmodelname)
        else:
            # curmodelname = curmodelname[:-4] + '_resaved.cif'
            # io.save(curmodelname)
            newstructure = usedframe




        # newstructure = p.get_structure(pid, curmodelname)
        setattr(newstructure, "filename", orgfilename)
        # tmodel = mmCIFParser._biommCIF_strcuture_to_TEMpy(curmodelname, newstructure, hetatm=True)
        tmodel = newstructure
        # tmodel.filename = orgfilename

        return tmodel

    def change_cifname(self):
        """Rename CIF files ending with ``*_org.cif`` back to their original names.

        If there is a file matching the pattern ``*_org.cif`` in the ``va`` folder,
        it is renamed by removing the ``_org`` part of the filename.

        Returns:
            None
        """
        for file in os.listdir(self.vadir):
            if file.endswith('_org.cif'):
                print('{} to {}'.format(file, file[:-8]))
                os.rename(self.vadir + '/' + file, self.vadir + '/' + file[:-8])

    # @profile
    def read_model(self):
        """Reads structure models specified by the '-f' argument.

        This function locates and loads one or more model files (mmCIF format) for validation analysis.
        It handles both local and server-based file paths, processes multiple models, and returns model objects,
        their identifiers, and file sizes. If no model is provided or an error occurs, returns None for all outputs.

        Returns:
            tuple:
                inputmodel (list or None): List of loaded model objects, or None if loading failed.
                pids (list or None): List of model identifiers (PDB IDs), or None if loading failed.
                modelsize (list or None): List of model file sizes in bytes, or None if loading failed.
        """

        start = timeit.default_timer()
        if self.model is not None:
            modelname = self.model
            # Todo: 1)modelname could be multiple models here using just the first model
            #       2)after 'else', the path should be a path on server or a folder I ust to store all files
            #         right now just use the same value as before 'else'
            ## commented area can be deleted after fully test (below)
            # if self.emdid:
            #     # Real path is comment out for the reason that the folder on server is not ready yet
            #     # Here use the local folder VAINPUT_DIR for testing purpose
            #     #fullmodelname = MAP_SERVER_PATH + modelname[0] if self.emdid is None else MAP_SERVER_PATH + modelname[0]
            #     fullmodelname = [ VAINPUT_DIR + curmodel if self.emdid is None else MAP_SERVER_PATH + self.subdir + '/va/' + curmodel for curmodel in modelname ]
            # else:
            #     fullmodelname = [ VAINPUT_DIR + curmodel if self.emdid is None else VAINPUT_DIR + curmodel for curmodel in modelname ]
            # fullmodelname = [ self.dir + curmodel if self.emdid is None else MAP_SERVER_PATH + self.subdir + '/va/' + curmodel for curmodel in modelname ]
            fullmodelname = []
            if self.emdid is None:
                for curmodel in modelname:
                    if not os.path.isfile(self.vadir + curmodel) and os.path.isfile(curmodel):
                        fullmodelname.append(curmodel)
                    elif os.path.isfile(self.vadir + curmodel):
                        fullmodelname.append(self.vadir + curmodel)
                    else:
                        print('Something wrong with the input model name or path: {}.'.format(self.vadir + curmodel))
            else:
                fullmodelname = [MAP_SERVER_PATH + self.subdir + '/va/' + curmodel for curmodel in modelname]

            try:
                modelsize = [os.stat(curmodelname).st_size for curmodelname in fullmodelname]
                #pid = self.pid
                pids = [os.path.basename(model)[:-4] for model in fullmodelname]
                # inputmodel = [mmCIFParser.read_mmCIF_file(pid, curmodelname, hetatm=True) for pid, curmodelname in zip(pids, fullmodelname)]
                inputmodel = []
                p = MMCIFParser()
                io = MMCIFIO()
                for pid, curmodelname in zip(pids, fullmodelname):
                    # structure = p.get_structure(pid, curmodelname)
                    # print(structure)
                    # structure[0] here when cif has multiple models, only use the first one for calculation
                    tmodel = self._structure_tomodel(pid, curmodelname)
                    # if len(structure.get_list()) > 1:
                    #     io.set_structure(structure[0])
                    #     orgmodel = curmodelname[:-4] + '_org' + '.cif'
                    #     # self.model = [os.path.basename(firstmodel) if (os.path.basename(curmodelname) == m) else m for m in self.model]
                    #     os.rename(curmodelname, orgmodel)
                    #     print('!!!There are multiple models in the cif file. Here we only use the first for calculation.')
                    #     if self.hasdisorder_atom(structure[0]):
                    #         usedmodel = curmodelname[:-4] + '_Alt_A.cif'
                    #         io.save(usedmodel, select=NotDisordered())
                    #     else:
                    #         io.save(curmodelname)
                    #     newstructure = p.get_structure(pid, curmodelname)
                    #     tmodel = mmCIFParser._biommCIF_strcuture_to_TEMpy(curmodelname, newstructure, hetatm=True)
                    #     tmodel.filename = '/Users/zhe/Downloads/alltempmaps/D_6039242/moriginalfile.cif'
                    #     # tmodel = mmCIFParser._biommCIF_strcuture_to_TEMpy(curmodelname, structure[0], hetatm=True)
                    # else:
                    #     print('fine here')
                    #     io.set_structure(structure)
                    #     if self.hasdisorder_atom(structure):
                    #         curmodelname = curmodelname[:-4] + '_Alt_A.cif'
                    #         io.save(curmodelname, select=NotDisordered())
                    #     else:
                    #         io.save(curmodelname)
                    #     newstructure = p.get_structure(pid, curmodelname)
                    #     tmodel = mmCIFParser._biommCIF_strcuture_to_TEMpy(curmodelname, newstructure, hetatm=True)
                    #     tmodel.filename = '/Users/zhe/Downloads/alltempmaps/D_6039242/moriginalfile.cif'
                    #     print(tmodel)
                    #     print(dir(tmodel))
                    #     exit(0)
                        # tmodel = mmCIFParser._biommCIF_strcuture_to_TEMpy(curmodelname, structure, hetatm=True)

                    # tmodel = mmCIFParser.read_mmCIF_file(pid, curmodelname, hetatm=True)
                    inputmodel.append(tmodel)

                    # Split each model mmcif file to a chain mmcif file
                    # if self.modelmap:
                    #     tempdict = self.cifchains(fullmodelname)
                    #     chaindict = self.updatechains(tempdict)
                    #     tchaindict = self.chainmaps(chaindict)

                end = timeit.default_timer()
                print('Read model time: %s' % (end - start))
                print('------------------------------------')

                return inputmodel, pids, modelsize
            except:
                print('!!! File: %s does not exist or corrupted: %s!!!' % (fullmodelname, sys.exc_info()[1]))
                print('------------------------------------')
                inputmodel = None
                pid = None
                modelsize = None

                return inputmodel, pid, modelsize
        else:
            print('No model is given.')
            inputmodel = None
            pid = None
            modelsize = None

            return inputmodel, pid, modelsize

    def cifchains(self, fullmodelname):
        """Splits an mmCIF model file into individual chain-specific mmCIF files.

        This method parses the input mmCIF file, extracts each chain, and saves it as a separate mmCIF file.
        It returns a dictionary mapping the original file to a dictionary of chain IDs and their corresponding file paths.

        Args:
            fullmodelname (str): Path to the full mmCIF model file.

        Returns:
            dict: A dictionary mapping the original model file to a dictionary
            of chain IDs and their corresponding file paths

        Raises:
            FileNotFoundError: If the provided mmCIF file does not exist.
        """

        parser = MMCIFParser()
        chaindict = {}
        onechaindict = {}
        modelname = os.path.basename(fullmodelname)
        structure = parser.get_structure(modelname, fullmodelname)
        singlechainfiles = []
        io = MMCIFIO()
        for chain in structure.get_chains():
            io.set_structure(chain)
            name = '{}{}_chain_{}.cif'.format(self.vadir, modelname, chain.id)
            print(name)
            singlechainfiles.append(name)
            io.save(name)
            onechaindict[chain.id] = name
        chaindict[fullmodelname] = onechaindict
        print(chaindict)
        print('Each chain cif files saved')

        return chaindict

    def updatechains(selfs, chaindict):
        """Updates chain-specific mmCIF files with symmetry information from the original model.

        This method ensures that each chain file contains the required symmetry information needed by
        Refmac to produce model maps. It reloads the original model and individual chain files, copies
        the symmetry data to each chain file, and then saves the updated chain files.

        Args:
            chaindict (dict): A dictionary mapping the original model file to a dictionary of chain IDs
                and their corresponding file paths

        Returns:
            dict: The updated `chaindict` with the same structure as the input, where each chain file now
                contains the symmetry information.

        Raises:
            FileNotFoundError: If any of the model or chain files do not exist.
        """

        model = list(chaindict)[0]
        chains = list(chaindict[model].values())
        model_dict = MMCIF2Dict(model)
        io = MMCIFIO()
        for chain in chains:
            chain_dict = MMCIF2Dict(chain)
            if '_symmetry.space_group_name_H-M' in model_dict.keys():
                chain_dict['_symmetry.space_group_name_H-M'] = model_dict['_symmetry.space_group_name_H-M']
            else:
                chain_dict['_symmetry.space_group_name_H-M'] = 'P 1'
            io.set_dict(chain_dict)
            io.save(chain)

        return chaindict

    def chainmaps(self, chaindict):
        """Generate simulated density maps for individual chains based on their mmCIF models.

        This method takes a dictionary of chain-specific mmCIF files, simulates a density map for each chain,
        and writes the resulting maps in MRC format. It uses EMDA methods for map generation and attempts
        a fallback method (GEMMI) if the primary method fails.

        Args:
            chaindict (dict): A dictionary from the `cifchains` function

        Returns:
            tuple:
                finaldict (dict): Mapping each chain ID to a dictionary

                errlist (list): List of error messages for chains where map simulation failed.
        Raises:
            FileNotFoundError: If the map file or any chain file cannot be found.
            ValueError: If map simulation fails due to invalid resolution or dimensions.
        """

        unit_cell, arr, origin = iotools.read_map(self.vadir + self.mapname)
        dim = list(arr.shape)

        finaldict = {}
        errlist = []
        key = list(chaindict)[0]
        value = list(chaindict[key].values())
        chains = list(chaindict[key])
        modelmaps = []
        for chain, chainfile in zip(chains, value):
            print(chainfile)
            chainfilename = os.path.basename(chainfile)
            modelmapname = '{}{}_chainmap.map'.format(self.vadir, chainfilename)
            try:
                modelmap = emda_methods.model2map(chainfile, dim, float(self.resolution),
                                                  unit_cell, maporigin=origin, outputpath=self.vadir)
                emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                modelmaps.append(modelmapname)
            except:
                err = 'Simulating model({}) map error:{}.'.format(chainfilename, sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            if errlist:
                try:
                    modelmap = emda_methods.model2map_gm(chainfile, float(self.resolution), dim,
                                                         unit_cell, maporigin=origin, outputpath=self.vadir)
                    emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                    modelmaps.append(modelmapname)
                    print('Model is simulated by using GEMMI in Servalcat.')
                except:
                    err = 'Simulating model({}) map error:{}.'.format(chainfilename, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
            finaldict[chain] = {chainfilename: os.path.basename(modelmapname)}

        return finaldict, errlist

    def modelstomaps(self):
        """Converts all models into corresponding density maps and writes them to disk.

        This method generates model maps (in MRC format) for all provided models using EMDA methods.
        If the primary simulation method fails, it falls back to GEMMI (Servalcat). Optionally, it can also
        produce chain-specific maps (currently commented out for performance reasons). The results are stored
        both as files and as metadata in a JSON file.

        Only applicable for single-particle entries (`method != 'tomo'` and `method != 'crys'`) with a valid
        resolution value. If these conditions are not met, no maps will be generated.

        Returns:
            tuple:
                modelmaps (list): A list of generated model map file paths.
                errlist (list): A list of error messages for models or chains where map simulation failed.

        Raises:
            FileNotFoundError: If the input map file or model files do not exist.
            ValueError: If resolution or dimensions are invalid for map simulation.
        """

        if not self.model or not self.modelmap:
            print('If there is no model given or no modelmap in json or command line, '
                  'model map or model-map FSC will not be produced.')
        else:
            # get map cell and dimension info,
            # 1) using mrcfile to only read the header to get the information
            # but need to take correct order of crs corresponding to the cell grid size ...
            # start = timeit.default_timer()
            # primarymapheader = mrcfile.open(self.dir + self.mapname, mode=u'r', permissive=False, header_only=True)
            # end = timeit.default_timer()
            # print(primarymapheader.print_header())
            # print('mrcfile use:{}s to read the map data'.format(end - start))

            # 2) currently direcctly use emda to avoid self formating the dimension and so on
            # but it may take more time to load a large map than using mrcfile just for header info but durable for now
            # only do it for single particle as electron crystallography does not need model map FSC calculation
            if self.method != 'tomo' and self.method != 'crys' and self.resolution:
                unit_cell, arr, origin = iotools.read_map(self.vadir + self.mapname)
                dim = list(arr.shape)

                modelmaps = []
                errlist = []
                finaldict = {}
                realfinaldict = {}
                counter = 0
                # for each model produce a model map
                for model in self.model:
                    modelmapname = '{}{}_modelmap.map'.format(self.vadir, model)
                    curmodelname = '{}{}'.format(self.vadir, model)
                    try:
                        modelmap = emda_methods.model2map(self.vadir + model, dim, float(self.resolution), unit_cell,
                                                          maporigin=origin, outputpath=self.vadir)
                        emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                        modelmaps.append(modelmapname)
                    except:
                        err = 'Simulating model({}) map error:{}.'.format(model, sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    if errlist:
                        try:
                            modelmap = emda_methods.model2map_gm(self.vadir + model, float(self.resolution), dim, unit_cell,
                                                                 maporigin=origin, outputpath=self.vadir)
                            emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                            modelmaps.append(modelmapname)
                            print('Model is simulated by using GEMMI in Servalcat.')
                        except:
                            err = 'Simulating model({}) map error:{}.'.format(model, sys.exc_info()[1])
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                    # Chain maps
                    chainerr = []
                    try:
                        tempdict = self.cifchains(curmodelname)
                        chaindict = self.updatechains(tempdict)
                        # Switch off the following 3 lines as some huge models take very long time to produce
                        # a lot chain model maps. When mmfsc is entirely ready activate it and a extra arguments for
                        # chainmap button is needed (make sure people really want the chain maps) (todo)

                        # tchaindict, chainerr = self.chainmaps(chaindict)
                        # finaldict[str(counter)] = {'name': model, 'mmap': os.path.basename(modelmapname),
                        #                            'chain_maps': tchaindict}
                    except:
                        err = 'Simulating chain map of model({}) error:{}.'.format(model, sys.exc_info()[1])
                        if chainerr:
                            errlist.extend(chainerr)
                            sys.stderr.write('Error in simulating chain map: ' + str(chainerr) + '\n')
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                    counter = counter + 1

                realfinaldict['modelmap'] = finaldict
                if errlist:
                    realfinaldict['modelmap']['err'] = {'mmap_err': errlist}

                try:
                    with codecs.open(self.vadir + self.mapname + '_modelmaps.json', 'w',
                                     encoding='utf-8') as f:
                        json.dump(realfinaldict, f)
                except:
                    sys.stderr.write('Saving model/chain-map info to json error: {}.\n'.format(sys.exc_info()[1]))

                return modelmaps, errlist
            else:
                print("No model map is produced as this is either not a single particle entry or nothing specified "
                      "for method -m (please use: -m sp) or resolution not specified -s (please use: -s <value>).")

        return None, None

    # @profile
    def new_combinemap(self, odd_file, even_file, rawmapfullname):
        """Generates a combined raw map from two half-maps and scales it to match the primary map statistics.

        This method takes two half-maps (odd and even), normalizes them, combines them into a single map,
        and applies scaling so that the resulting raw map matches the mean and standard deviation of the
        primary map. The combined map is written to disk as an MRC file and returned as an `mrcfile` object.

        Args:
            odd_file (str or mrcfile.mmap): Path to the odd half-map file or an `mrcfile` object.
            even_file (str or mrcfile.mmap): Path to the even half-map file or an `mrcfile` object.
            rawmapfullname (str): Full path for saving the combined raw map.

        Returns:
            mrcfile.mmap: A memory-mapped `mrcfile` object representing the combined raw map.

        Raises:
            FileNotFoundError: If either half-map file does not exist (when given as file paths).
            ValueError: If the input maps contain invalid values (NaN, Inf) that cannot be corrected.
            RuntimeError: If writing the combined raw map fails.
        """

        import gc

        def load_map_data(file):
            if isinstance(file, str):
                with mrcfile.mmap(file, mode='r+') as m:
                    data = m.data
                    header = m.header
            else:
                data = file.data
                header = file.header

            mode = header.mode.item()  # Ensure mode is a single value
            if mode in {0, 1, 3, 6}:
                return np.memmap.astype(data, 'float32'), header
            else:
                return data.copy(), header

        def sanitize_extreme_data(arr, scale_threshold=1e+30):
            """
            In-place version of sanitize_extreme_data to avoid memory duplication.
            """
            if np.isnan(arr).any():
                return arr, "Array contains NaN values."
            if np.isinf(arr).any():
                return arr, "Array contains inf or -inf values."

            arr_sum = np.sum(arr)
            arr_std = np.std(arr)

            if np.isnan(arr_sum) or np.isnan(arr_std):
                arr /= scale_threshold  # in-place division
                return arr, f"Array scaled in-place by {scale_threshold} due to numeric instability."

            return arr, "Array is clean and numerically stable."

        oddmap, header = load_map_data(odd_file)
        evenmap, _ = load_map_data(even_file)
        oddmap, odd_status = sanitize_extreme_data(oddmap)
        evenmap, even_status = sanitize_extreme_data(evenmap)
        print(f'Odd map status: {odd_status}')
        print(f'Even map status: {even_status}')

        np.divide((oddmap - oddmap.mean()), oddmap.std(), out=oddmap)
        np.multiply(oddmap, evenmap.std(), out=oddmap)
        np.add(oddmap, (evenmap - evenmap.mean()), out=oddmap)
        np.divide(oddmap, evenmap.std(), out=oddmap)
        np.subtract(oddmap, oddmap.mean(), out=oddmap)
        np.divide(oddmap, oddmap.std(), out=oddmap)
        np.multiply(oddmap, self.primarymapstd, out=oddmap)
        np.add(oddmap, self.primarymapmean, out=oddmap)

        nstarts = [header.nxstart, header.nystart, header.nzstart]
        org_header = header
        self.write_map(rawmapfullname, oddmap, nstarts, org_header)
        rawmap = mrcfile.mmap(rawmapfullname, mode='r+')
        rawmap.fullname = rawmapfullname

        del evenmap
        del oddmap
        gc.collect()

        return rawmap

    # @profile
    def read_halfmaps(self):
        """Reads two half-maps and generates a combined raw map for FSC calculation.

        This method loads two half-maps (odd and even), either from the EMDB server or from the local
        directory, combines them into a raw map using `new_combinemap`, and calculates their combined size.
        If any map is missing or invalid, it returns `None` for all maps and size 0.

        Returns:
            tuple:
                halfeven (mrcfile.mmap or None): The even half-map as an `mrcfile` object, or `None` if not available.
                halfodd (mrcfile.mmap or None): The odd half-map as an `mrcfile` object, or `None` if not available.
                rawmap (mrcfile.mmap or None): The combined raw map generated from the two half-maps, or `None` if not created.
                twomapsize (float): Total voxel count of the two half-maps, or `0.0` if maps are missing.

        Raises:
            IOError: If only one half-map is provided instead of two.
            ValueError: If map processing fails due to invalid content or format.
            FileNotFoundError: If expected half-map files do not exist.
        """

        halfeven = None
        halfodd = None
        rawmap = None
        twomapsize = 0.
        if self.emdid:
            mapone = MAP_SERVER_PATH + self.subdir + '/va/' + 'emd_' + self.emdid + '_half_map_1.map'
            maptwo = MAP_SERVER_PATH + self.subdir + '/va/' + 'emd_' + self.emdid + '_half_map_2.map'
            rawmapname = '{}{}/va/emd_{}_rawmap.map'.format(MAP_SERVER_PATH, self.subdir, self.emdid)
            if os.path.isfile(mapone) and os.path.isfile(maptwo):
                try:
                    # halfodd = self.frommrc_totempy(mapone)
                    # halfeven = self.frommrc_totempy(maptwo)
                    halfodd = self.new_frommrc_totempy(mapone)
                    halfeven = self.new_frommrc_totempy(maptwo)
                    # rawmap = self.new_combinemap(mapone, maptwo, rawmapname)
                    rawmap = self.new_combinemap(halfodd, halfeven, rawmapname)
                    # low_pass = 15. if float(self.resolution) < 8. else float(self.resolution) * 2.0
                    # filtered_rawmap_name = f'{rawmapname}_lowpassed.mrc'
                    # try:
                    #     rawmap_mrc = f'{rawmapname[:-3]}mrc'
                    #     create_symbolic_link(rawmapname, rawmap_mrc)
                    #     MapProcessor.low_pass_filter_relion(rawmap_mrc,low_pass, filtered_rawmap_name)
                    # except:
                    #     MapProcessor.low_pass_filter_map(rawmap, low_pass, filtered_rawmap_name)
                    # if not MapProcessor.check_map_starts(filtered_rawmap_name, rawmapname):
                    #     print('Relion mask does not have the same nstarts as the original map.')
                    #     MapProcessor.update_map_starts(rawmapname, filtered_rawmap_name)
                    # print(f'Filtered raw map is {filtered_rawmap_name}.')
                    odd_mapsize = halfodd.header.nx * halfodd.header.ny * halfodd.header.nz
                    even_mapsize = halfeven.header.nx * halfeven.header.ny * halfeven.header.nz
                    # twomapsize = halfodd.map_size() + halfeven.map_size()
                    twomapsize = odd_mapsize + even_mapsize
                    print('Raw map {} has been generated.'.format(rawmapname))
                except (IOError, ValueError) as e:
                    print('!!! Half-maps were given but something was wrong: {}'.format(e))
            else:
                halfeven = None
                halfodd = None
                rawmap = None
                twomapsize = 0.
                print('No half maps for this entry.')
        else:
            if self.evenmap is not None and self.oddmap is not None:
                mapone = self.vadir + self.oddmap
                maptwo = self.vadir + self.evenmap
                try:
                    rawmapname = '{}{}_{}_rawmap.map'.format(self.vadir, self.oddmap, self.evenmap)
                    halfodd = self.new_frommrc_totempy(mapone)
                    halfeven = self.new_frommrc_totempy(maptwo)
                    # rawmap = self.new_combinemap(mapone, maptwo, rawmapname)
                    rawmap = self.new_combinemap(halfodd, halfeven, rawmapname)
                    # low_pass = 15. if float(self.resolution) < 8. else float(self.resolution) * 2.0
                    # filtered_rawmap_name = f'{rawmapname}_lowpassed.mrc'
                    # try:
                    #     rawmap_mrc = f'{rawmapname[:-3]}mrc'
                    #     create_symbolic_link(rawmapname, rawmap_mrc)
                    #     lowpassed_rawmap = MapProcessor.low_pass_filter_relion(rawmap_mrc, low_pass, filtered_rawmap_name)
                    # except:
                    #     lowpassed_rawmap = MapProcessor.low_pass_filter_map(rawmap, low_pass, filtered_rawmap_name)
                    # if not MapProcessor.check_map_starts(filtered_rawmap_name, rawmapname):
                    #     print('Relion mask does not have the same nstarts as the original map.')
                    #     MapProcessor.update_map_starts(rawmapname, filtered_rawmap_name)
                    # print(f'Filtered raw map is {filtered_rawmap_name}.')
                    odd_mapsize = halfodd.header.nx * halfodd.header.ny * halfodd.header.nz
                    even_mapsize = halfeven.header.nx * halfeven.header.ny * halfeven.header.nz
                    # twomapsize = halfodd.map_size() + halfeven.map_size()
                    twomapsize = odd_mapsize + even_mapsize
                    print('Raw map {} has been generated.'.format(rawmapname))
                except (IOError, ValueError) as maperr:
                    print('!!! Half-maps were given but something was wrong: {}'.format(maperr))
            elif self.evenmap is None and self.oddmap is None:
                print('REMINDER: Both half maps are needed for FSC calculation!')
                halfeven = None
                halfodd = None
                rawmap = None
                twomapsize = 0.
            else:
                raise IOError('Another half map is needed for FSC calculation.')

        return halfeven, halfodd, rawmap, twomapsize

    def merge_json_objects(self, obj1, obj2):
        """Recursively merges two JSON-like Python dictionaries into a single dictionary.

        This method combines keys and values from two dictionaries. If a key exists in both dictionaries:
        - If both values are dictionaries, they are merged recursively.
        - If one value is a dictionary and the other is not, the dictionary value takes precedence.
        - If both values are non-dictionaries, the value from the first dictionary (`obj1`) is used.

        Args:
            obj1 (dict): The first JSON-like dictionary.
            obj2 (dict): The second JSON-like dictionary.

        Returns:
            dict: A new dictionary containing the merged keys and values from both input dictionaries.

        Examples:
            >>> obj1 = {"a": 1, "b": {"x": 10}}
            >>> obj2 = {"b": {"y": 20}, "c": 3}
            >>> merge_json_objects(obj1, obj2)
            {'a': 1, 'b': {'x': 10, 'y': 20}, 'c': 3}
        """

        merged_obj = {}
        for key in set(obj1.keys()) | set(obj2.keys()):
            if key in obj1 and key in obj2 and isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                merged_obj[key] = self.merge_json_objects(obj1[key], obj2[key])
            elif key in obj1 and key in obj2:
                if isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                    merged_obj[key] = {**obj1[key], **obj2[key]}
                elif isinstance(obj1[key], dict) and not isinstance(obj2[key], dict):
                    merged_obj[key] = obj1[key]
                elif not isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                    merged_obj[key] = obj2[key]
                else:
                    merged_obj[key] = obj1[key]
            elif key in obj1:
                merged_obj[key] = obj1[key]
            elif key in obj2:
                merged_obj[key] = obj2[key]

        return merged_obj

    def merge_json_files(self, files):
        """Merges multiple JSON files into a single dictionary.

        This method reads a list of JSON files, loads their contents, and merges them recursively
        using `merge_json_objects`. If a file is empty, an error message is written to `stderr`.

        Args:
            files (list): A list of file paths (str) to JSON files that need to be merged.

        Returns:
            dict: A dictionary containing the merged content of all JSON files.

        Raises:
            FileNotFoundError: If any of the specified files do not exist.
            json.JSONDecodeError: If a file is not a valid JSON.
            PermissionError: If the file cannot be opened due to insufficient permissions.

        Examples:
            >>> files = ["data1.json", "data2.json"]
            >>> merge_json_files(files)
            {'a': 1, 'b': {'x': 10, 'y': 20}, 'c': 3}
        """
        merged_data = {}

        for file in files:
            if os.path.getsize(file) > 0:
                with open(file, 'r') as f:
                    data = json.load(f)
                    merged_data = self.merge_json_objects(merged_data, data)
            else:
                sys.stderr.write('The {} is empty!\n'.format(file))

        return merged_data

    def merge_jsons(self):
        """Merges all generated JSON files in the working directory into a single consolidated JSON file.

        This method searches for all JSON files in `self.vadir`, excluding any already merged files
        (e.g., `*_all.json`). It merges their contents recursively using `merge_json_files` and writes
        the combined result to a new JSON file named either `emd_<EMDB_ID>_all.json` (if `self.emdid` is set)
        or `<mapname>_all.json` otherwise. Additionally, if `self.emdid` is present, it merges any JSON
        files in the `checks/` subdirectory and writes a consolidated checks JSON file.

        Returns:
            None

        Side Effects:
            - Writes the merged JSON file(s) to disk in `self.vadir` (and optionally `checks/` subdirectory).
            - Reads all JSON files in the working directory, excluding previously merged files.
            - Uses `merge_json_files` internally to combine file contents recursively.

        Notes:
            - Existing `_all.json` files are ignored to prevent duplication.
            - The structure of the output JSON is `{EMDB_ID or mapname: merged_data}`.
            - If `self.emdid` is set, a separate checks JSON file is also created with a similar structure.

        Raises:
            FileNotFoundError: If any of the JSON files to be merged do not exist.
            json.JSONDecodeError: If any of the files contain invalid JSON.
            PermissionError: If the output file cannot be written due to insufficient permissions.
        """

        filename = os.path.basename(self.mapname) if self.emdid is None else self.emdid
        if self.emdid:
            checks_json_files = glob.glob(f'{self.vadir}/checks/*.json')
            checks_json_files = [cfile for cfile in checks_json_files if 'all_checks.json' not in cfile]
            checks_output_file = f'{self.vadir}/checks/{filename}_all_checks.json'
            checks_data = self.merge_json_files(checks_json_files)
            # output to checks folder
            checks_full_data = {str(self.emdid): checks_data}
            out_json(checks_full_data, checks_output_file)
            # output into va folder for easy access
            checks_va_output_file = f'{self.vadir}/{self.mapname}_all_checks.json'
            checks_va_data = {'checks': checks_data}
            out_json(checks_va_data, checks_va_output_file)

        # workdir = '{}{}/va/'.format(MAP_SERVER_PATH, self.subdir())
        jsonfiles = glob.glob(self.vadir + '*.json')
        jsonfiles = [jfile for jfile in jsonfiles if 'all.json' not in jfile]

        fuldata = self.merge_json_files(jsonfiles)


        finaldata = dict()
        if self.emdid is not None:
            finaldata[self.emdid] = fuldata
            output = '{}emd_{}_all.json'.format(self.vadir, self.emdid)
        else:
            finaldata[filename] = fuldata
            output = '{}{}_all.json'.format(self.vadir, filename)
        with open(output, 'w') as out:
            json.dump(finaldata, out)

        return None

    def merge_bars(self):
        """Merges all bar plot PNG files in the working directory into a single vertical image.

        This method searches for all PNG files ending with `_bar.png` in `self.vadir`, excluding any
        previously merged file (`*_allbars.png`). It stacks all bar images vertically into one combined
        image and saves it as `<mapname>_allbars.png` in the same directory.

        Returns:
            None

        Side Effects:
            - Reads multiple PNG files from `self.vadir`.
            - Creates a new PNG file `<mapname>_allbars.png` in `self.vadir`.
            - Prints messages to stdout if no bar files are found or an error occurs.

        Raises:
            IOError: If any of the PNG files cannot be read or the combined image cannot be saved.
            Exception: Any other unexpected error during image processing.
        """

        try:
            barfiles = glob.glob(self.vadir + '*_bar.png')
            barfiles = [jfile for jfile in barfiles if 'allbars.png' not in jfile]

            images = [Image.open(img_path) for img_path in barfiles]
            total_width = images[0].width
            total_height = sum(img.height for img in images)

            new_image = Image.new("RGB", (total_width, total_height))

            y_offset = 0
            for img in images:
                new_image.paste(img, (0, y_offset))
                y_offset += img.height

            output_path = '{}/{}_allbars.png'.format(self.vadir, os.path.basename(self.mapname))
            new_image.save(output_path)
        except Exception as e:
            print('No bar to be merged')
            print('The error is {}'.format(e))

        return None

    def write_recl(self):
        """Writes the recommended contour level (recl) and normalized sigma to a JSON file.

        This method creates a JSON file containing the `recl` value and its sigma (normalized by
        the primary map standard deviation) if `self.contourlevel` is set. The JSON file is saved
        as `<mapname>_recl.json` in `self.vadir`.

        Returns:
            None

        Side Effects:
            - Writes a JSON file `<mapname>_recl.json` to `self.vadir`.
            - Uses `keep_three_significant_digits` to format the sigma value.

        Raises:
            IOError: If the file cannot be written due to permission issues or invalid path.
        """

        if self.contourlevel is not None:
            dictrecl = dict()
            dictrecl['recl'] = self.contourlevel
            dictrecl['sigma'] = keep_three_significant_digits(self.contourlevel / self.primarymapstd)
            lastdict = dict()
            lastdict['recommended_contour_level'] = dictrecl
            filename = self.mapname
            output = '{}{}_recl.json'.format(self.vadir, os.path.basename(filename))
            with open(output, 'w') as out:
                json.dump(lastdict, out)

        return None

    def write_version(self):
        """Writes the current software version to a JSON file.

        This method creates a JSON file containing the version string (`__version__`) and saves it
        as `<mapname>_version.json` in `self.vadir`.

        Returns:
            None

        Side Effects:
            - Writes a JSON file `<mapname>_version.json` to `self.vadir`.

        Raises:
            IOError: If the file cannot be written due to permission issues or invalid path.
        """

        versiondict = dict()
        versiondict['version'] = __version__
        filename = self.mapname
        output = '{}{}_version.json'.format(self.vadir, os.path.basename(filename))
        with open(output, 'w') as out:
            json.dump(versiondict, out)

        return None

    def finiliszejsons(self):
        """Finalizes all JSON and bar outputs by writing contour level, version information, and merging files.

        This method sequentially performs the following actions:
        1. Writes the recommended contour level JSON (`write_recl`).
        2. Writes the software version JSON (`write_version`).
        3. Merges all bar PNG files into a single image (`merge_bars`).
        4. Merges all generated JSON files into a consolidated JSON (`merge_jsons`).

        It also prints the elapsed time for merging JSONs.

        Returns:
            None

        Side Effects:
            - Creates or overwrites JSON files for contour level and version.
            - Merges bar images into a single PNG file.
            - Merges multiple JSON files into a single consolidated JSON.
            - Prints timing and status messages to stdout.

        Raises:
            IOError: If any of the file writing or merging operations fail.
        """

        start = timeit.default_timer()
        self.write_recl()
        self.write_version()
        self.merge_bars()
        self.merge_jsons()
        stop = timeit.default_timer()
        print('Merge JSONs: %s' % (stop - start))
        print('------------------------------------')

        return None

    #@staticmethod
    def memmsg(self, mapsize):
        """Provides a memory usage reminder based on predicted memory requirements.

        This method checks for a memory prediction file (`input.csv`) in the appropriate directory
        and calculates the expected memory usage for processing a map of size `mapsize`. It prints
        the predicted memory requirement and asserts if it exceeds the available system memory.

        Args:
            mapsize (int or float): Size of the map in bytes (or other consistent units) used for memory prediction.

        Returns:
            int or None: Predicted memory usage in megabytes, or `None` if no prediction is available.

        Side Effects:
            - Prints memory prediction messages to stdout.
            - Raises an `AssertionError` if predicted memory exceeds available system memory.

        Raises:
            AssertionError: If the predicted memory exceeds the total available system memory.
            FileNotFoundError: If the memory prediction file (`input.csv`) does not exist.
        """
        # When there is no emdid given, we use one level above the given "dir" to save the memory prediction file
        # input.csv. If emdid is given, we use the. self.dir is like /abc/cde/ so it needs to used os.path.dirname()
        # twice.

        if self.emdid:
            vout = MAP_SERVER_PATH
        else:
            vout = os.path.dirname(os.path.dirname(self.vadir)) + '/'
        if os.path.isfile(vout + 'input.csv') and os.path.getsize(vout + 'input.csv') > 0:
            mempred = ValidationAnalysis.mempred(vout + 'input.csv', 2 * mapsize)
            if mempred == 0 or mempred is None:
                print('No memory prediction.')
                return None
            else:
                print('The memory you may need is %s M' % mempred)
                assert mempred < psutil.virtual_memory().total / 1024 / 1024, \
                    'The memory needed to run may exceed the total memory you have on the machine.'
                return mempred
        else:
            print('No memory data available for prediction yet')
            return None



