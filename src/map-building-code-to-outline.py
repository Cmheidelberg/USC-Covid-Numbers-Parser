from difflib import SequenceMatcher
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

def validate_building_geojson(building_outline ,quiet_mode=False):
    # TODO: validate geojson files
    print("THE GEOJSON VALIDATOR IS NOT DONE. PLASE FINISH")
    return True

def create_output_geojson(building_outline,building_map_csv,delim=',', newline="\n", weight_location_on_name=True):
    """Create a geojson from only the buildings mapped in the csv

    Args:
        building_outline (geojson): geojson with all the building outlines and additonal metadata
        building_map_csv (str): csv of building map 
        delim (str, optional): csv delimiter. Defaults to ','.
        newline (str, optional): csv newline. Defaults to "\n".
    """
    output = {"type": "FeatureCollection", "features": []}
    buildings = building_outline["features"]
    header = building_map_csv.split(newline)[0]
    lines = building_map_csv.split(newline)[1:]
    ignored = 0
    blacklist_size = 0
    start_size = len(lines)

    blacklist = {}
    for l in lines:
        three = l.split(delim)[0]
        blacklist[three] = []

    # Loop for each building in the input csv
    for i,line in enumerate(lines):
       
        # blacklist a building in the csv from matching with a building in the json (a closer building exists)
        # key: csv[0](3 letter code) value: geojson feature name
        cols = line.split(delim)

        # DEBUG
        # if cols[0] != "RRB":
        #     continue

        if len(cols) > 2:
            csv_building_name = cols[1]
        else:
            continue

        print(f"Checking: {csv_building_name} ({i}/{start_size})")
        print(f"Remaining: {len(lines)-i}, Blacklist_Size: {blacklist_size}")

        # make sure the line of the csv is valid
        if len(line) > 0 and line.isspace() == False and cols[3].lower() != "null" and cols[4].lower() != "null":
            curr_lat = float(cols[3])
            curr_lon = float(cols[4])

            min_dist = 100
            closest_feature = "null"
            
            # Loop over all features in the input geojson
            for feature in buildings:
                fprop = feature.get("properties")
                
                if fprop is None or fprop == "":
                    print(f"WARNING: feature lacks properties field. Skipping feature: {feature}")
                    continue

                fbuilding = fprop.get("building")
                fname = fprop.get("name")

                # Cannot weight building on name if it has no name
                if weight_location_on_name and (fname is None or fname == "None"):
                    continue

                # if current csv element has been blacklisted from choosing certain features to be it
                if blacklist.get(cols[0]):
                    if fname in blacklist[cols[0]]:
                        #print(f"{fname} in blacklist for {csv_building_name}. Skipping")
                        continue

                # if the feature code is labled as a building
                if fbuilding and fname != "None" and (fprop["amenity"] == None or fprop["amenity"] == "None"): # and fprop["building"].lower() == "university":                    
                    coords = list(geojson.utils.coords(feature))
                    local_min_dist = get_radial_distance(float(coords[0][1]), float(coords[0][0]), curr_lat, curr_lon)
                    dists = []
                    for c in coords:
                        
                        curr_dist = get_radial_distance(float(c[1]), float(c[0]), curr_lat, curr_lon)
                        
                        # Add a multiplyer to the curr distance based on how similar the building names are 
                        if weight_location_on_name:
                            if fname is not None and csv_building_name is not None and fname != "None":
                                string_cmp = 2*compare_strings(csv_building_name, fname)
                            else:
                                string_cmp = 0


                            # If strings have no relation distance = inf
                            if string_cmp > 0:
                                dists.append(curr_dist * 1/string_cmp)
                            else:
                                curr_dist = 10000
                            
                            # Debug
                            # if fname != "None":
                            #     print(f"\"{fname}\": {curr_dist}")

                        if curr_dist < min_dist:
                            local_min_dist = curr_dist
                    
                    if local_min_dist < min_dist:
                        min_dist = local_min_dist
                        closest_feature = feature

            # if there was a closests feature found for that building add it to the output geojson
            if str(closest_feature).lower() != "null" and min_dist < 0.008:
                
                new_feature = closest_feature
                new_feature["min_dist"] = min_dist
                prop = new_feature["properties"]
                prop_name = prop["name"]
                #print(f"ACCEPTED: {cols[1]} || {prop_name}" )

                # Find if new feature is already in outputs
                old_prop = {}
                for of in output["features"]:
                    of = of["properties"]
                    #print(f"\n\n{of}\n\n")
                    #print(f"\n\n{prop}\n\n")
                    if of["name"] == prop["name"]:
                        old_prop = of
                        break
                
                addme = True
                if old_prop:
                    if min_dist < old_prop["min_dist"]:
                        ocode = old_prop["building_code"]
                        oname = old_prop["building_name"]
                        oaddress = old_prop["building_address"]
                        olat = old_prop["lat"]
                        olong = old_prop["lon"]
                        lines.append(f"{ocode},{oname},{oaddress},{olat},{olong}\n")
                        blacklist[ocode].append(old_prop["name"])
                        blacklist_size += 1
                        #print("new one closer")

                    else:
                        lines.append(line)
                        blacklist[cols[0]].append(old_prop["name"])
                        blacklist_size += 1
                        #print("old one closer")
                        addme = False
                
                if addme:
                    prop["min_dist"] = min_dist
                    for num,c in enumerate(cols):
                        prop[header.split(delim)[num]] = c
                    output["features"].append(new_feature)
            else:
                #print(f"IGNORING - closest feature: {cols[0]}")
                ignored += 1
            
    print(f"IGNORED: {ignored}")
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



    