from bs4 import BeautifulSoup
from constants import *

def parse_page_direcory_html_file(path):
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

# ===================================================================================================

if __name__ == "__main__":
    # https://classes.usc.edu/building-directory/
    parsed_html = parse_page_direcory_html_file(CLASS_DIR_PAGE_PATH)

    if parsed_html == None: # TODO check if page is empty
        print("Parse building dir HTML file is empty. Quitting")
        exit()

    tables = parsed_html.find_all('tr')
    csv = "building_code,building_name,_building_location\n"
    for t in tables:
        building_code = t.find('th').contents[0].strip().upper()
        
        td_split = t.find('td').contents[0].split(",")
        building_name = td_split[0].strip()
        building_location = ''.join(td_split[1:]).strip()

        csv += building_code + "," + building_name + "," + building_location + "\n"
    
    # Note: Buildings with commas in location have commas removed here (ie:  "P.O. Box 398, Catalina Island, 90704" becomes "P.O. Box 398 Catalina Island 90704")
    with open(BUILDING_CODE_MAP_PATH,"w") as f:
        f.write(csv)

    
    #splits = parse_page_strong_text(strongs)