from difflib import SequenceMatcher
from tkinter import N

from cv2 import compare
from utils import *
from constants import *
import geojson

def compare_strings(first, second):
    """Compare two strings and return a number between 0 and 1 representing how similar they are.
    1=perfect match 
    0=no match 

    Args:
        first (str): first string
        second (str): second string

    Returns:
        float: float representing how similar the two strings are
    """
       
    return SequenceMatcher(None, first, second).ratio()

def get_csv_building_names(input, newline="\n", delim=","):
    """Given an input building_code_map csv file return a list of every building name in that list

    Args:
        input (str): input csv
        newline (str, optional): csv file newline character. Defaults to "\n".
        delim (str, optional): csv file delimiter. Defaults to ",".

    Returns:
        list: list of every building name
    """
    rows = input.split(newline)[1:]
    names = []
    for r in rows:
        cols = r.split(delim)
        if cols is not None and len(cols) > 1:
            names.append(cols[1])
    
    return names

def get_geojson_building_names(input):
    """Take in a geojson object and return a list of each building name found within the geojson

    Args:
        input (geojson,json,dict): input geojson file 

    Returns:
        list: list of each building name
    """
    features = input["features"]
    names = []
    for ele in features:
        try:
            properties = ele["properties"]
            if properties["building"] is not None and properties["building"].lower() == "university":
                n = properties["name"]
                if n is not None and n.lower() != "none":
                    # Remove commas 
                    n = n.split(",")
                    n = "".join(n)
                    
                    # add building name to array
                    names.append(n)
        except Exception as e:
            print(f"Error (ignoring): {e}")
    names.sort()
    return names

def create_similarity_csv(geojson_names, csv_names):
    output = ","
    # create header
    for i in geojson_names:
        output += i + ","
    output = output[:-1] 
    output += "\n"

    for i in csv_names:
        output += i + ","
        for j in geojson_names:
            # output += f"{i} || {j} = {compare_strings(i,j)},"
            cmp = compare_strings(i,j)
            output += f"{cmp},"


        output = output[:-1] 
        output += "\n"

    with open(PROJECT_ROOT_PATH / "debug-str-tester.csv","w") as csv_writer:
        csv_writer.write(output)

if __name__ == "__main__":

    # Ask user which file they want to open
    data_pages = [f for f in listdir(DATA_FOLDER_PATH) if isfile(pjoin(DATA_FOLDER_PATH,f))]
    data_paths = [pjoin(DATA_FOLDER_PATH,f) for f in listdir(DATA_FOLDER_PATH) if isfile(pjoin(DATA_FOLDER_PATH,f))]

    data_pages = [f"{f} (created: {get_created_string(DATA_FOLDER_PATH,f)})" for f in data_pages ]
    
    # choose building outlines geojson
    choice = simple_menu_print(f"Select a building outlines geojson from the /{DATA_FOLDER_NAME} directory:",data_pages)
    building_outlines = data_paths[choice-1]

    # chose building map csv
    choice = simple_menu_print(f"Select a building code map from the /{DATA_FOLDER_NAME} directory:",data_pages)
    building_code_map = data_paths[choice-1]

    # open the selected files
    try:
        print("Opening outlines file...")
        with open(building_outlines,"r") as outlines_reader:
            building_outlines_geojson = geojson.load(outlines_reader)
    except Exception as e:
        print("Something went wrong opening the builiding code map file:")
        print(e)
        print("Quitting")
        sys.exit()

    try:
        print("Opening building code map...")
        with open(building_code_map,"r") as csv_reader:
            building_map_csv = csv_reader.read()
    except Exception as e:
        print("Something went wrong opening the builiding code map file:")
        print(e)
        print("Quitting")
        sys.exit()

    geojson_names = get_geojson_building_names(building_outlines_geojson)
    csv_names = get_csv_building_names(building_map_csv)
    create_similarity_csv(geojson_names, csv_names)