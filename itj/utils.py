import os, sys
from termcolor import cprint
from pddlstream.utils import Saver

###########################################

class VerboseToFile(Saver):
    def __init__(self, log_to_file=True, log_file_path=None):
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path
    def save(self):
        if not self.log_to_file:
            return
        self.stdout = sys.stdout
        self.log = open(self.log_file_path, "w")
        sys.stdout = self.log
    def restore(self):
        if not self.log_to_file:
            return
        sys.stdout = self.stdout
        self.log.close()
        cprint('Log file saved to {}'.format(self.log_file_path), 'green')