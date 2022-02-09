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


# ===================================================================================================

if __name__ == "__main__":
    # https://classes.usc.edu/building-directory/
    parsed_html = parse_page_direcory_html_file(CLASS_DIR_PAGE_PATH)

    if parsed_html == None: # TODO check if page is empty
        print("Parse building dir HTML file is empty. Quitting")
        exit()

    tables = parsed_html.find_all('tr')
    csv = "building_code,building_name,building_address\n"
    for t in tables:
        building_code = t.find('th').contents[0].strip().upper()
        
        td_split = t.find('td').contents[0].split(",")
        building_name = td_split[0].strip()
        building_location = ''.join(td_split[1:]).strip()

        csv += building_code + "," + building_name + "," + building_location + "\n"
    
    # Note: Buildings with commas in location have commas removed here (ie:  "P.O. Box 398, Catalina Island, 90704" becomes "P.O. Box 398 Catalina Island 90704")
    with open(BUILDING_CODE_MAP_PATH,"w") as f:
        f.write(csv)
