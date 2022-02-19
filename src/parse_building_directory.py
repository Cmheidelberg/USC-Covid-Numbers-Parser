from bs4 import BeautifulSoup
from constants import *
from geopy.geocoders import Nominatim
import numpy as np


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
    csv = "building_code,building_name,building_address,lat,lon\n"
    
    geo_success = 0
    geo_failed = 0
    geo_total = 0

    for t in tables:
        building_code = t.find('th').contents[0].strip().upper()
        
        td_split = t.find('td').contents[0].split(",")
        building_name = td_split[0].strip()
        building_location = ''.join(td_split[1:]).strip()

        
        geolocator = Nominatim(user_agent="my_user_agent")
        geo_location = geolocator.geocode(building_location + ", Los Angeles, CA")
        
        # Try for places out of LA
        if geo_location is None: 
            geo_location = geolocator.geocode(building_location)

        if geo_location is not None and len(geo_location) > 0:
            geo_success += 1
            print(f"SUCCESS: " + building_location + ", Los Angeles, CA")
            lat = str(geo_location.latitude)
            lon = str(geo_location.longitude)
        else:
            geo_failed += 1
            print(f"ERROR:   " + building_location + ", Los Angeles, CA")
            lat = "null"
            lon = "null"
        geo_total += 1

        csv += f"{building_code},{building_name},{building_location},{lat},{lon}\n"
    
    print(f"Geo Location success rate of "\
        "{100*np.round((geo_success/geo_total),2)}% (Successful: {geo_success}, Failed: {geo_failed})")
    # Note: Buildings with commas in location have commas removed here (ie:  "P.O. Box 398, Catalina Island,
    # 90704" becomes "P.O. Box 398 Catalina Island 90704")
    with open(BUILDING_CODE_MAP_PATH,"w") as f:
        f.write(csv)
