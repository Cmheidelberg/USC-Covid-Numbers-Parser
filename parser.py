from hashlib import new
from bs4 import BeautifulSoup
from cv2 import line
from constants import *


def parse_html_file(path):
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
        print("Could not find the html file ")
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
        curr_split = i.contents[0].split()
        removed_junk = []
        if len(curr_split) >= 3:
            for j in curr_split:
                
                # Remove || deliminator between some fields 
                if j != "||":
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
        newline (str, optional): Newline for csv. Defaults to "\n".

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
            csv_str += "null" + delim
            csv_str += "null" + delim
            csv_str += "null" + delim
            csv_str += "null" + delim
            csv_str += "null" + delim
        
        if len(i) >= 2:
            csv_str += i[1] + delim
        else:
            csv_str += "null" + delim
            csv_str += "null" + delim
            csv_str += "null" + delim
            csv_str += "null" + delim

        if len(i) >= 5:
            has_weekdays = str_contains_only_day_of_week_characters(i[2])
            has_first_time = str_is_acceptable_time(i[3])
            has_second_time = str_is_acceptable_time(i[4])
            if has_weekdays and has_first_time and has_second_time:
                csv_str += i[2] + delim
                csv_str += i[3] + delim
                csv_str += i[4] + delim
            else:
                csv_str += "null" + delim
                csv_str += "null" + delim
                csv_str += "null" + delim
        
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
        newline (str): new line for csv. Defaults to "\n".
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


if __name__ == "__main__":
    parsed_html = parse_html_file(PAGE_NAME)

    if parsed_html == None: # TODO check if page is empty
        print("Parsed HTML file is empty. Quitting")
        exit()

    strongs = parsed_html.find_all('strong')
    splits = parse_page_strong_text(strongs)
    unvalidated_csv = create_csv(splits)
    valid_csv = validate_csv(unvalidated_csv,quiet_mode=QUIET_MODE)
    with open(OUTPUT_FILE_NAME,"w") as csv_writer:
        csv_writer.write(valid_csv)



    