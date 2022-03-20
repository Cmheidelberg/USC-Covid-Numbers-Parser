from constants import *
from utils import *
import geojson
import numpy as np

def validate_building_code_map_file(building_map_csv,delim=',', newline="\n" ,quiet_mode=False):
    """Validates the selected building code map to ensure it is valid  before trying to map buildings to shapes

    Args:
        path (str): path to building code map file. This is the output file from parse_building_directory.py
    """
    lines = building_map_csv.split(newline)[1:]
    for num,line in enumerate(lines):
        if len(line) > 0 and line.isspace() == False:
            cols = line.split(delim)
            if len(cols) < 4:
                if not quiet_mode:
                    bad_csv_print(cols,"invalid length",num)
                    return False
            
            # check building code is valid
            if len(cols[0]) != 3:
                if not quiet_mode:
                    bad_csv_print(cols,f"invalid building code: \"{cols[0]}\"",num) 
                return False
            
            # check lat is castable to float
            if cols[3].lower() != "null": 
                try:
                    float(cols[3])
                except ValueError:
                    if not quiet_mode:
                        bad_csv_print(cols,f"invalid latitude value: \"{cols[3]}\"",num) 
                    return False

            # check lon is castable to float 
            if cols[4].lower() != "null":
                try:
                    float(cols[4])
                except ValueError:
                    if not quiet_mode:
                        bad_csv_print(cols,f"invalid longitude value: \"{cols[4]}\"",num) 
                    return False
    return True
            
def validate_building_geojson(building_outline,delim=',', newline="\n" ,quiet_mode=False):
    # TODO: validate geojson files
    print("THE GEOJSON VALIDATOR IS NOT DONE. PLASE FINISH")
    return True

def create_output_geojson(building_outline,building_map_csv,delim=',', newline="\n"):
    """Creates a geojson from only the buildings mapped in the csv

    Args:
        building_outline (_type_): _description_
        building_map_csv (_type_): _description_
        delim (str, optional): _description_. Defaults to ','.
        newline (str, optional): _description_. Defaults to "\n".
    """
    output = {"type": "FeatureCollection", "features": []}
    buildings = building_outline["features"]
    header = building_map_csv.split(newline)[0]
    lines = building_map_csv.split(newline)[1:]
    for line in lines:
        cols = line.split(delim)

        # make sure the line of the csv is valid
        if len(line) > 0 and line.isspace() == False and cols[3].lower() != "null" and cols[4].lower() != "null":
            curr_lat = float(cols[3])
            curr_lon = float(cols[4])

            min_dist = 100
            closest_feature = "null"
            if cols[0].lower() == "GFS":
                print(f"GFS: {curr_lat},{curr_lon}")
            for feature in buildings:
                if feature["properties"]["CODE"] is not None and feature["properties"]["CODE"].lower() == "building":
                    coords = list(geojson.utils.coords(feature))
                    local_min_dist = get_radial_distance(float(coords[0][1]), float(coords[0][0]), curr_lat, curr_lon)
                    for c in coords:
                        
                        curr_dist = get_radial_distance(float(c[1]), float(c[0]), curr_lat, curr_lon)
                        if curr_dist < min_dist:
                            local_min_dist = curr_dist
                    
                    if local_min_dist < min_dist and local_min_dist < 0.005:
                        min_dist = local_min_dist
                        closest_feature = feature

            if str(closest_feature).lower() != "null":
                new_feature = closest_feature
                prop = new_feature["properties"]
                for num,c in enumerate(cols):
                    prop[header.split(delim)[num]] = c
                output["features"].append(new_feature)
            
            
    return output

def get_radial_distance(a_lat, a_lon, b_lat, b_lon):
    """retuen the radial distance between two points

    Args:
        a_lat (float): first lat
        a_lon (float): first lon
        b_lat (float): second lat
        b_lon (float): second lon
    """
    # print(f"alat: {a_lat} | alon: {a_lon}")
    # print(f"blat: {b_lat} | blon: {b_lon}")
    lat_diff = np.absolute(a_lat - b_lat)
    lon_diff = np.absolute(a_lon - b_lon)
    radial_dist = np.sqrt(lat_diff**2 + lon_diff**2)
    return radial_dist
# ---------------------------------------------------------------------------------------------------------------------

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

    # Validate the read files 
    print("Validating files...")

    if not validate_building_code_map_file(building_map_csv,quiet_mode = not VERBOSE):
        print("Error: Invalid building map csv file. Aborting!")
        sys.exit()


    output = create_output_geojson(building_outlines_geojson, building_map_csv)
        
    output = geojson.dumps(output)
    print("\nWhat would you like to name the output?")
    file_name = input()

    # Append .geojson to the end if needed
    tmp = file_name.split('.')
    if len(tmp) == 1:
        file_name = file_name + ".geojson"

    out_file_full_path = PROJECT_ROOT_PATH / file_name
    # Write the final csv file
    print(f"Creating output geojson file: (At: {out_file_full_path})")
    with open(out_file_full_path,"w") as csv_writer:
        csv_writer.write(output)



    