import os
from datetime import datetime
from constants import *

def simple_menu_print(menu_title, options_list, help_text=""):
    """Print a menu to the terminal. Validates user input and return the selection number. 
    Help text can be passed to print text describing each choice in the menu

    Args:
        menu_title (str): Title/question of the menu
        options_list (list): string list of each choice
        help_text (str, optional): Description of the menu/each choice. Defaults to "".

    Returns:
        int: number of choice [0 - len(options_list)-1]
    """
    has_help_text = len(help_text) > 0
    while(True):
        print(menu_title)

        i = 0
        for i in range(len(options_list)):
            print(f"{i+1}. {options_list[i]}")
        
        if(has_help_text):
            print(f"{i+2}. Help")

        inp = input()
        if(inp.isnumeric()):
            inp = int(inp)
            if(has_help_text and inp == len(options_list)+1):
                print(help_text + "\n")
            elif(inp > 0 and inp <= len(options_list)):
                return inp
            else:
                print("Invalid selection\n")
        else:
            print("Input must be a number\n")

def get_created_string(path,f):
    """Return formatted datetime of when the given file was created (month day year)"""
    return datetime.utcfromtimestamp(os.stat(os.path.join(path,f))[7]).strftime('%m-%d-%Y [UTC]')

def pjoin(path1, path2):
    """Return os.path.join of path1 and path2"""
    return os.path.join(path1,path2)

def isfile(path):
    """Return if the given path is a file (true/false)"""
    return os.path.isfile(path)

def listdir(path):
    """Return a list of all the files/directories under a given path"""
    return os.listdir(path)