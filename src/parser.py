from cgitb import html
from turtle import ht
from bs4 import BeautifulSoup
from constants import *
from utils import *
import os
from datetime import datetime

def parse_cases_html_file(path):
    """Parse the given html file using BeautifulSoup. Return BeautifulSoup object if parsable, None otherwise. 

    Args:
        path (str): Path location to html file

    Returns:
        [BeautifulSoup]: beutiful soup object
    """
    try:
        with open(path, encoding="utf8") as f:
            soup = BeautifulSoup(f, "html.parser")
            return soup
    except FileNotFoundError:
        print(f"Could not find the html file: {path}")
        return None


def parse_page_strong_text(strongs):
    """Parse the page into a list of lines that contain covid exposures by class

    Args:
        strongs (list): List of lines with <strong> elements from the soup class. List should be of str type though.

    Returns:
        [list]: List of valid covid exposure classes with all accompaning data. (ie: ['BUAD-304','14725','MW','18:00','19:50','JFFLL101'])
    """
    splits = []
    for i in strongs:
        white_space_split = i.contents[0].split()
        removed_junk = []
        if len(white_space_split) >= 3:
            removed_junk.append(white_space_split[0])
            removed_junk.append(white_space_split[1])

            metadata_split = ' '.join(white_space_split[2:])
            metadata_split = metadata_split.split("||")
            for j in metadata_split:
                j = j.strip()
                if len(j) <= 0 or j == "" or j==None:
                    removed_junk.append("null")
                else:
                    removed_junk.append(j)
            
            #Remove things that dont start with class number
            if len(removed_junk[0].split("-")) == 2:
                splits.append(removed_junk)
    return splits


def str_contains_only_day_of_week_characters(input_string):
    """Check if the string given contains only characters used in the day of week section (ie: "MWF")

    Args:
        input_string (str): String from cell expecting days of week location

    Returns:
        [bool]: True if only contains days of week chars. False otherwise
    """
    days_of_week_chars = ["m","t","w","h","f","s"]
    for c in input_string:
        if c.lower() not in days_of_week_chars:
            return False
            
    return True

def str_is_acceptable_time(input_string):
    """Check if the given string is parsable as a time (format = numbers : numbers)

    Args:
        input_string ([type]): True if parsable as time false otherwise
    """
    split = input_string.split(":")
    if len(split) != 2:
        return False
    
    if split[0].isnumeric() and split[1].isnumeric():
        return True
    
    return False
        

def create_csv(splits, delim=",",newline="\n"):
    """Create a csv file from the splits of every parsed line. Attempt to make each line have the same number of 
    elements filling unknown cells with null. Also provides another level of rudimentary validation before appending 
    a line to the putput

    Args:
        splits (list): list of strings for every parsed line
        delim (str, optional): Delimiter for csv. Defaults to ",".
        newline (str, optional): Newline for csv. Defaults to "\\n".

    Returns:
        [str]: csv string. Each row is an exposure event with class. Note: output needs to be validated with the
        validate_csv function after due to the inconsistant nature of USC's recording.
    """
    csv_header = f"class_name{delim}code{delim}weekday{delim}start_time{delim}end_time{delim}location{newline}"
    csv_str = csv_header
    for i in splits:
        if len(i) >= 1:
            csv_str += i[0] + delim
        else:
            csv_str += 5*("null" + delim)
        
        if len(i) >= 2:
            csv_str += i[1] + delim
        else:
            csv_str += 4*("null" + delim)

        if len(i) >= 5:
            has_weekdays = str_contains_only_day_of_week_characters(i[2])
            has_first_time = str_is_acceptable_time(i[3])
            has_second_time = str_is_acceptable_time(i[4])
            if has_weekdays and has_first_time and has_second_time:
                csv_str += i[2] + delim
                csv_str += i[3] + delim
                csv_str += i[4] + delim
            else:
                csv_str += 3*("null" + delim)
        
        if not str_is_acceptable_time(i[-1]):
            csv_str += i[-1] + newline
        else:
            csv_str += "null" + newline
    return csv_str


def validate_csv(csv_str, delim=',',newline="\n",quiet_mode=False):
    """Reads in csv with possibly invalid rows and returns a csv with invalid rows removed. Prints out invalid lines as they come.

    Args:
        csv_str (str): csv string
        delim (str): Delimiter for csv. Defaults to ','.
        newline (str): new line for csv. Defaults to "\\n".
        quiet_mode (bool): Dissable printing invalid lines
    """

    valid_first_line = f"class_name{delim}code{delim}weekday{delim}start_time{delim}end_time{delim}location"
    listify = csv_str.split(newline) 

    if listify[0] != valid_first_line:
        print(f"Given: {listify[0]}")
        print(f"Expected: {valid_first_line}")
        print("Error: first line of csv must be valid header. Aborting.")
        exit(0)

    outp = listify[0] + newline
    for i in range(1,len(listify)-1):
        line_valid = True
        split = listify[i].split(delim)
        if len(split) != 6:
            line_valid = False
            if not quiet_mode:
                bad_csv_print(split,"invalid length",i)
        
        elif len(split[0].split("-")) != 2:
            line_valid = False
            if not quiet_mode:
                bad_csv_print(split, "Invalid class field",i)

        elif not split[1].isnumeric():
            line_valid = False
            if not quiet_mode:
                bad_csv_print(split, "Class ID not numeric",i)
        
        elif not str_contains_only_day_of_week_characters(split[2]) and not split[2].lower() == "null":
            line_valid = False
            if not quiet_mode:
                bad_csv_print(split, "Day of week field invalid",i)

        elif not str_is_acceptable_time(split[3]) and not split[3].lower() == "null":
            line_valid = False
            if not quiet_mode:
                bad_csv_print(split, "Start time invalid",i)

        elif not str_is_acceptable_time(split[4]) and not split[4].lower() == "null":
            line_valid = False
            if not quiet_mode:
                bad_csv_print(split, "End time invalid",i)

        if line_valid:
            l = listify[i]
            els = l.split(delim)
            outp += els[0] + delim +els[1] + delim + els[2] + delim + els[3] + delim + els[4] + delim + els[5] + newline;

    return outp
    

def bad_csv_print(list_split, error_message, line_number=None):
    """Print bad csv line error

    Args:
        list_split (str): list of the currently erronious line
        error_message (str): message explaining the reson for this lines removal
        line_number (int, optional): line number of the removed element. Defaults to None.
    """
    if line_number is not None:
        print(f"Bad element on line {line_number}: {list_split}. ({error_message}). Removing from csv.")
    else:
        print(f"Bad line in csv: {list_split}. ({error_message}). Removing from csv.")


def add_building_code_name_and_location(target_csv, building_map_csv,delim=",",newline="\n"):
    """Appends a `building_name` and `building_location` field to the end od the target_csv and attemts to match building
    codes from the building_map_csv to each building

    Args:
        target_csv (str): string representation of csv. Any format will do as long as the `location` field is the last one
        building_map_csv (str): string representation of building map csv: `building_code,building_name,_building_location`
        delim (str, optional): Delimiter for csv file. Defaults to ",".
        newline (str, optional): newline indicator for csv file. Defaults to "\\n".
    """
    class_map_dict = {}
    building_csv_line = building_map_csv.split(newline)
    building_csv_line = building_csv_line[1:] # ignore first line (header)

    for i in building_csv_line:
        elements = i.split(delim)
        if len(elements) == 3:
            class_map_dict[elements[0]] = {"Name": elements[1], "Location": elements[2]}

    target_csv_line = target_csv.split(newline)

    # Append new columns to header
    output_csv = target_csv_line[0][0:]
    output_csv += delim + "full_building_name"
    output_csv += delim + "building_address"
    output_csv += newline

    target_csv_line = target_csv_line[1:] # ignore header
    for i in target_csv_line:
        elements = i.split(delim)
        building_code = elements[-1]
        if len(building_code) >= 3 and building_code.lower() != "office" and building_code.lower() != "null":
            building_code = building_code[0:3].upper()
        
        output_csv += i[0:] #Existing elements minus newline
        if building_code in class_map_dict:
            output_csv += delim + class_map_dict.get(building_code).get("Name")
            output_csv += delim + class_map_dict.get(building_code).get("Location")
            output_csv += newline
        else:
            output_csv += 2*(delim + "null")
            output_csv += newline

    return output_csv
# ========================================================================================================

if __name__ == "__main__":
    # https://sites.google.com/usc.edu/covidnotifications-ay22/home
    
    menu_title = "Select a file to parse from html"
    html_pages = [f for f in os.listdir(HTML_FOLER_PATH) if os.path.isfile(os.path.join(HTML_FOLER_PATH,f))]
    html_pages_path = [os.path.join(HTML_FOLER_PATH,f) for f in os.listdir(HTML_FOLER_PATH) if os.path.isfile(os.path.join(HTML_FOLER_PATH,f))]
    html_pages = [f"{f} (created: {datetime.utcfromtimestamp(os.stat(os.path.join(HTML_FOLER_PATH,f))[7]).strftime('%m-%d-%Y [UTC]')})" for f in html_pages ]
    choice = simple_menu_print("Select a file to parse from the /html directory:",html_pages)
    selected = html_pages_path[choice-1]
    #print(f"\n Selected page: {selected}")

    print("Parsing html to csv: ",end="",flush=True)
    parsed_html = parse_cases_html_file(selected)

    if parsed_html == None: # TODO check if page is empty
        print("Parsed HTML file is empty. Quitting")
        exit()

    strongs = parsed_html.find_all('strong')
    splits = parse_page_strong_text(strongs)
    unvalidated_csv = create_csv(splits)
    print("Done")

    print("Validating csv...")
    valid_csv = validate_csv(unvalidated_csv,quiet_mode=QUIET_MODE)
    print("Done")

    print("\nShould this program try to append building code information to the end of the csv?: [y/n]")
    choice=input().lower()
    if choice == "y" or choice == "yes":
        try:
            class_dir_map = ""
            # read in the building code map csv file
            print(f"Appending building information: (Using: {BUILDING_CODE_MAP_PATH})")
            with open(BUILDING_CODE_MAP_PATH,"r") as csv_reader:
                class_dir_map = csv_reader.read()

            mapped_csv = add_building_code_name_and_location(valid_csv,class_dir_map)
        except Exception as e:
            print(f"Something went wrong: {e}")

            print("\nSave unmapped building code csv? [y/n]")
            choice = input()
            if choice == "y" or choice == "yes":
                mapped_csv = valid_csv
            else:
                exit(0)
    else:
        mapped_csv = valid_csv

    print("\nWhat would you like to name the output?")
    file_name = input()

    # Append .csv to the end if needed
    tmp = file_name.split('.')
    if len(tmp) == 1:
        file_name = file_name + ".csv"

    out_file_full_path = PROJECT_ROOT_PATH / file_name
    # Write the final csv file
    print(f"Creating output csv file: (At: {out_file_full_path})")
    with open(out_file_full_path,"w") as csv_writer:
        csv_writer.write(mapped_csv)




    