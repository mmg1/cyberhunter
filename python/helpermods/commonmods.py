#!/usr/bin/env python3

'''
 NAME: commonmods.py | version: 0.2
 CYBERHUNTER Version: 0.1
 AUTHOR: Diego Perez (@darkquasar) - 2019
 DESCRIPTION: Collection of helper modules to facilitate specific tasks in CYBERHUNTER like: downloading the tools required for artefact acquisition, copying a file using raw disk access, etc.
 
 Updates: 
    v0.2: Added tools download function.
    
 ToDo:
    1. ----.

'''
import logging
import os
import re
import shutil
import subprocess
import sys
import wget
import yaml
import zipfile
from pathlib import Path

# Setup logging
logger = logging.getLogger('COMMONMODS')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

class common:
  def __init__(self):
  
    # Initializing variables
    logger.info('Initializing {}'.format(__name__))
    config_file_path = Path.cwd() / "cyberhunt-config.yml"
    self.CYBERHUNTER_config = self.load_CYBERHUNTER_config(config_file_path)

  def get_cyberhunt_tools(self):

    CYBERHUNTER_base_dir = Path.cwd()

    # Download Tools
    # tools = self.extract_key_dict("tools", self.CYBERHUNTER_config).__next__()
    tools_dict = self.CYBERHUNTER_config['tools']
    
    for kitem, vitem in tools_dict.items():
      # tool: ex. "RawCopy", "AppCompatCacheParser", etc.
      for ktool, vtool in tools_dict[kitem].items():
        target_path = Path.cwd() / tools_dict[kitem][ktool]['ExtractDir']
        logger.info('Downloading [{}] from {} to {}'.format(ktool, tools_dict[kitem][ktool]['SourceUrl'], str(target_path)))
        self.create_dir(target_path)
        try:
          wget.download(tools_dict[kitem][ktool]['SourceUrl'], str(target_path))
        except ValueError:
          continue
          
        # Now let's unzip the tools if they should be unzipped
        extracted_tool_name = Path(tools_dict[kitem][ktool]['SourceUrl'])
        extracted_tool_path = target_path / extracted_tool_name.name
        if "zip" in extracted_tool_name.suffix:
          self.unzip(extracted_tool_path, target_path, extract_all=True)

  def create_dir(self, target_dir, return_handle=False, erase_contents=False):
      # This function will create a new folder at the specified location
      # relative to CYBERHUNTER's base dir. If the folder already exists, it will do nothing, 
      # unless "erase_contents" is set to True. In both cases it will return a string 
      # with the absolute path to the folder.

      # Get CYBERHUNTER framework base dir which should be at the same level as commonmods.py
      CYBERHUNTER_base_dir = Path.cwd()
      target_dir = Path(target_dir)
      target_dir = CYBERHUNTER_base_dir / target_dir

      if not Path.exists(target_dir):
        logger.info('Directory [' + str(target_dir) + '] does not exist, creating it...')
        os.makedirs(target_dir)
        
        if return_handle == False:
          return
        else:
          return target_dir

      else: 
        logger.info('Directory [' + str(target_dir) + '] already exists')

        if erase_contents == True: 
          logger.info('Erasing contents of Directory [' + str(target_dir) + ']')
          for fileobj in target_dir.iterdir():
            try:
                if os.path.isfile(fileobj):
                    os.unlink(fileobj)
                # Uncomment in the future adding an option to erase the directory as well
                #elif os.path.isdir(fileobj): 
                # shutil.rmtree(fileobj)
            except Exception as e:
                print(e)
        
        if return_handle == False:
          return
        else:
          return target_dir

  def list_files(self, path):
    # Helper function to return list of files inside a directory
    # If the parameter passed as "path" is a path to a file, return the file path itself back
    # to the calling function, otherwise, if the path is a directory, return the list of all files
    # (only the files)
    
    # Converting the path string to pathlib.Path() object
    path = Path(path)

    if Path.is_file(path):
      return path
    else:
      return [f for f in path.iterdir() if f.is_file]

  def copy_raw_file(self, src, dst):

    # Get a handle to the RawCopy app
    app_rawcopy = self.get_bin_path("RawCopy")
    logger.info('Loading RawCopy at {}'.format(app_rawcopy))

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
      logger.info('Copying file {} to {}'.format(src, dst))
      subprocess.run([str(app_rawcopy), '/FileNamePath:{}'.format(src), '/OutputPath:{}'.format(dst)], startupinfo=startupinfo)
    except:
      logger.info('Could not copy file {}'.format(src))

  def extract_key_dict(self, key, dictionary):
      # This helper function iterates over the "n" depth structure of a dict 
      # in search for a Key specified in the "key" parameter, then
      # returns all values associated with that Key.

      if hasattr(dictionary, 'items'):
          for k, v in dictionary.items():
              if k == key:
                  yield v
              if isinstance(v, dict):
                  for result in self.extract_key_dict(key, v):
                      yield result
              elif isinstance(v, list):
                  for d in v:
                      for result in self.extract_key_dict(key, d):
                          yield result

  def get_bin_path(self, app):
    # This function will return the absolute path to the tool specified in the "app" parameter
    # as a Pathlib.Path() object

    # Get CYBERHUNTER framework base dir which should be at the same level as commonmods.py
    CYBERHUNTER_base_dir = Path.cwd()

    cfg = self.CYBERHUNTER_config
    
    # Loading CYBERHUNTER.yml will return a list of 3 elements, the first one [0] represents
    # the folder where the tool will be extracted relative to CYBERHUNTER's base directory, 
    # the second one [1] represents the name of the executable and finally the 
    # third one [2] represents the download URL.
    # The names give to the executables are extracted from [1]

    binary_path = self.extract_key_dict(app, cfg).__next__()

    bin_path = Path() / CYBERHUNTER_base_dir / binary_path[0] / binary_path[1]

    return bin_path

  def load_cyberhunter_config(self, config_path):
    # This function will load cyberhunt-config.yml
    logger.info('Loading CYBERHUNTER Config at {}'.format(config_path))

    with open(config_path, 'r') as conf:
      try:
        return yaml.load(conf)
      except yaml.YAMLError as e:
        print(e)

  def unzip(self, src, dst, extract_all=False, name_filter=None, type_filter=None):
    # Helper function to unzip files. It accepts two filters:
    # 1. name_filter: it will only extract a file matching this name pattern
    # 2. type_filter: it will only extract a file that matches a particular type (like PE)

    # TODO: improve this function by collecting all file names at the beginning
    # so as to not have to iterate over each file for a simple string match
    
    # Open the ZIP file
    logger.info('Accessing Zip file {}'.format(src))
    with zipfile.ZipFile(src, 'r') as zipf:
      if extract_all == True:
        logger.info('Extracting files to {}'.format(dst))
        zipf.extractall(dst)

      if name_filter != None:
        files_list = [f.filename for f in zipf.infolist()]

        for filen in files_list:
          if re.match(name_filter, filen):
            logger.info('Extracting file {}'.format(filen))
            zipf.extract(filen, dst)
            break
          else:
            file_in_zip = False
        
        if file_in_zip == False:
          logger.info('No file found inside [{}] matching pattern {}'.format(src, name_filter))

      else:  
        for zfile in zipf.infolist():
          if type_filter != None:
            with zipf.open(zfile.filename) as fileitem: 
              if type_filter == "registry_hive":
                # NT Registry Hive Magic Number:
                # 72 65 67 66 => regf
                NT_MAGIC_DAT = b'\x72\x65\x67\x66'
                if NT_MAGIC_DAT == fileitem.read(4):
                  zipf.extract(zfile, dst)


