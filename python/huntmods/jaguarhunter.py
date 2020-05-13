'''
 MODULE NAME: jaguarhunter.py | Version: 0.1
 CYBERHUNTER Version: 0.1
 AUTHOR: Diego Perez (@darkquasar) - 2018
 DESCRIPTION: This module will load hunting templates and execute them against an ElasticSearch database via Apache Spark. It should be called from within CYBERHUNTER-jupyter
'''

import pyspark
import multiparser as mp

# All parsermods have a class called "mod" and define
# any initialization parameters inside.
# Parsermods can have any number of functions inside the "mod" class.
class mod:
  def __init__(self, xmlparsetype, logtype, filepath, output, **kwargs):
  
    # Initializing variables
    self.xmlparsetype = xmlparsetype
    self.logtype = logtype
    self.filepath = filepath
    self.output = output

  # All parsermods must contain an "execute" function that will: 
  # a. initialize the output pipe via de MultiParser "init_output" func.
  # b. return a generator back to CYBERHUNTER.py so that records can be iterated through.
  def execute(self):
    # Instantiating the MultiParser for plain parsing (no modules)
    self.fileparser = mp.MultiParser(self.xmlparsetype, self.logtype, self.filepath)
    results = self.fileparser.parser()
    self.fileparser.init_output(self.output, self.logtype)
    
    return results