from constants import PROJECT_ROOT_PATH


with open(PROJECT_ROOT_PATH / "output.csv","r") as outlines_reader:
    my_csv = outlines_reader.read()

building_names = {}

rows = my_csv.split("\n")[1:]

for r in rows:
    cols = r.split(",")
    if len(cols) > 4 and cols[5][0:3].lower() != "nul":
        three_letter_id = cols[5][0:3]
        if building_names.get(three_letter_id) == None:
            building_names[three_letter_id] = 1
        else:
            building_names[three_letter_id] = building_names[three_letter_id] + 1

output_csv = ""
for a in building_names:
    output_csv += f"{a},{building_names[a]}\n"

with open(PROJECT_ROOT_PATH / "summed_covid_data.csv","w") as writer:
    writer.write(output_csv)