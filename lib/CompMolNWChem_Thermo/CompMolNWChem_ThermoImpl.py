# -*- coding: utf-8 -*-
#BEGIN_HEADER

import logging
import os
import sys
import subprocess as _subprocess
import csv
import inchi_to_submission as its
import extract_properties_mulliken_charges_mol2 as mul
import compound_parsing as com
import pandas as pd
import compound_parsing as parse
import export as ex
import re
import zipfile
import uuid
import copy
import shutil
import argparse

os.system('pip install snakemake')

from pybel import *
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
from csv import DictReader
#from mulitprocessing import cpu_count
from os.path import *
from pkg_resources import resource_filename
from cme import *
from snakemake import snakemake
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.CompoundSetUtilsClient import CompoundSetUtils

#from CompMolNWChem import CompoundSetUtil

#END_HEADER


class CompMolNWChem_Thermo:
    '''
    Module Name:
    CompMolNWChem_Thermo

    Module Description:
    A KBase module: CompMolNWChem_Thermo
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/nkkchem/CompMolNWChem_Thermo.git"
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    def _generate_output_file_list(self, result_directory):
        """
        _generate_output_file_list: zip result files and generate file_links for report
        """

        #log('start packing result files')
        output_files = list()

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
        result_file = os.path.join(output_directory, 'Thermo_Result.zip')
        plot_file = os.path.join(output_directory, 'Thermo_Plot.zip')

        with zipfile.ZipFile(result_file, 'w',
                             zipfile.ZIP_DEFLATED,
                             allowZip64=True) as zip_file:
            for root, dirs, files in os.walk(result_directory):
                for file in files:
                    if not (file.endswith('.zip') or
                            file.endswith('.png') or
                            file.endswith('.DS_Store')):
                        zip_file.write(os.path.join(root, file), 
                                       os.path.join(os.path.basename(root), file))

        output_files.append({'path': result_file,
                             'name': os.path.basename(result_file),
                             'label': os.path.basename(result_file),
                             'description': 'File(s) generated by CompMolNWChem_Thermo App'})

        with zipfile.ZipFile(plot_file, 'w',
                             zipfile.ZIP_DEFLATED,
                             allowZip64=True) as zip_file:
            for root, dirs, files in os.walk(result_directory):
                for file in files:
                    if file.endswith('.png'):
                        zip_file.write(os.path.join(root, file), 
                                       os.path.join(os.path.basename(root), file))

        output_files.append({'path': plot_file,
                             'name': os.path.basename(plot_file),
                             'label': os.path.basename(plot_file),
                             'description': 'Plot(s) generated by CompMolNWChem_Thermo App'})

        return output_files

    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _save_to_ws_and_report(self, ws_id, source, compoundset, message=None):
        """Save compound set to the workspace and make report"""
        info = self.dfu.save_objects(
            {'id': ws_id,
             "objects": [{
                 "type": "KBaseBiochem.CompoundSet",
                 "data": compoundset,
                 "name": compoundset['name']
             }]})[0]
        compoundset_ref = "%s/%s/%s" % (info[6], info[0], info[4])
        if not message:
            message = 'Imported %s as %s' % (source, info[1])
        report_params = {
            'objects_created': [{'ref': compoundset_ref,
                                 'description': 'Compound Set'}],
            'message': message,
            'workspace_name': info[7],
            'report_object_name': 'compound_set_creation_report'
        }

        # Construct the output to send back
        report_client = KBaseReport(self.callback_url)
        report_info = report_client.create_extended_report(report_params)
        output = {'report_name': report_info['name'],
                  'report_ref': report_info['ref'],
                  'compoundset_ref': compoundset_ref}
        return output

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.dfu = DataFileUtil(self.callback_url)
        self.comp = CompoundSetUtils(self.callback_url)
        self.scratch = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #self.scratch = config['scratch']

        #END_CONSTRUCTOR
        pass


    def run_CompMolNWChem_Thermo(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_CompMolNWChem_Thermo

        # Initial Tests to Check for Proper Inputs

        for name in ['Input_File','calculation_type','workspace_name']:
            if name not in params:
                raise ValueError('Parameter "' + name + '"is required but missing')
        if not isinstance(params['Input_File'], str):
            raise ValueError('Input_File must be a string')

        
        # Load the tsv file into a compound set using DataFileUtil methods
        
        scratch_file_path = self.dfu.download_staging_file({'staging_file_subdir_path':params['Input_File']}
                                       ).get('copy_file_path')

        #print('Scratch File Path: ',scratch_file_path)

        mol2_file_dir = None        
        ext = os.path.splitext(scratch_file_path)[1]
        file_name = os.path.basename(scratch_file_path)
        if ext == '.sdf':
            compounds = parse.read_sdf(scratch_file_path,
                                       mol2_file_dir=mol2_file_dir,
                                       callback_url=self.callback_url)
        elif ext == '.tsv':
            compounds = parse.read_tsv(scratch_file_path,
                                       mol2_file_dir=mol2_file_dir,
                                       callback_url=self.callback_url)
        #elif ext == '.csv':
        #    compounds = parse.read_csv(scratch_file_path,
        #                               mol2_file_dir=mol2_file_dir,
        #                               callback_url=self.callback_url)
        #else:
        #    raise ValueError('Invalid input file type. Expects .tsv or .sdf')
       
        # SNAKEMAKE PIPELINE START, READ FILES IN AND CHECK EXISTING REACTIONS

        from snakemake import snakemake

        modelseedID_to_deltaG = {}
        calculated = []

        # fill with modelseed ID and correspodning delta_G of metabolites
        # This is the dictionary of all Modelseed cpds with their delta_G values

        with open('modelSeed_ID_delta_G_calculated.csv', 'r') as dfile:
            lines = dfile.readlines()
            for line in lines:
                key = line.split(',')[0]
                G   = line.split(',')[1]
                modelseedID_to_deltaG[key] = float(G)
                calculated.append(key)

        modelseedID_to_deltaG['cpd00001'] +=  2.38
        modelseedID_to_deltaG['cpd00067']  = -268.61


        # map metabolites to the reactions with stoichmetry 

        reactionlist = scratch_file_path

        with open(reactionlist,'r') as f:
            reactions = f.readlines()[0].rstrip().replace(' ', '')
            reactants = reactions.split('<=>')[0].split('+')
            products  = reactions.split('<=>')[1].split('+')

            G_reactants = 0
            left = []
            stoich_left = []
            for reactant in reactants:
                stoich_left.append(int((re.findall('(\(\d+\))cpd', reactant)[0]).replace('(','').replace(')', '')))
                reactant = re.search(re.findall('[a-zA-Z]{3}\d{5}', reactant)[0], reactant).group(0)
                left.append(reactant.strip())

            G_products = 0
            right = []
            stoich_right = []
            for product in products:
                stoich_right.append(int((re.findall('(\(\d+\))cpd', product)[0]).replace('(','').replace(')', '')))
                product = re.search(re.findall('[a-zA-Z]{3}\d{5}', product)[0], product).group(0)
                right.append(product.strip())

            print(stoich_right, right)
            print(stoich_left, left)

        #id_to_smiles = {}
        #data = open('/kb/module/modelseed_test.csv','r')

        #for lines in data.readlines():
        #    id = lines.split(',')[0]
        #    smiles = lines.split(',')[1].rstrip()
        #    id_to_smiles[id] = smiles

        #data.close()

        #with open(reactionlist,'r') as f:
        #    reactions = f.readlines()[0].rstrip()
        #    reactant = reactions.split('=')[0].split('+')
        #    product = reactions.split('=')[1].split('+')
        #    metabolites = []
            for each in reactants:
                each = each.strip()
                metabolites.append(each)
            for each in products:
                each = each.strip()
                metabolites.append(each)

            for molecule in metabolites:
                
                moldir = molecule
                if not os.path.exists(moldir):
                    os.mkdir(moldir)
    
                initial_structure_dir = moldir + '/initial_structure'
                if not os.path.exists(initial_structure_dir):
                    os.mkdir(initial_structure_dir)

                md_structure_dir = moldir + '/md'
                if not os.path.exists(md_structure_dir):
                    os.mkdir(md_structure_dir)

                dft_structure_dir = moldir + '/dft'
                if not os.path.exists(dft_structure_dir):
                    os.mkdir(dft_structure_dir)

                inchifile_str = initial_structure_dir + '/' + moldir + '.smiles'
                with open(inchifile_str,'w+') as f:
                    f.write(id_to_smiles[moldir])
        
        os.system('snakemake -p --cores 3 --snakefile snakemake-scripts/final_pipeline.snakemake -w 12000')

        # Build KBase Output. Should output entire /simulation directory and build a CompoundSet with Mol2 Files

        #result_directory = '/kb/module/snakemake-scripts'
        result_directory = '/kb/module/'


        ## Create Extended Report
        
        output_files = self._generate_output_file_list(result_directory)
        #output_files = 
        
        report_params = {
            'message':'',
            'workspace_id': params['workspace_id'],
            'objects_created': [],
            'file_links':output_files,
            'report_object_name': 'kb_deseq2_report_' + str(uuid.uuid4())}

        report = KBaseReport(self.callback_url)
        
        report_info = report.create_extended_report(report_params)

        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }

        return [output]

        #END run_CompMolNWChem_Thermo
        
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]