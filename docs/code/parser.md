# Summary

This project is designed to parse the raw html from the USC COVID data page and convert it in a more usable csv. The generated csv is then validated and any erronious rows are removed to guarantee the output file is consistant. For each row in the csv, any columns that cannot be parsed will be entered as `null` to prevent uneven rows. Rows with null values could be post-processed later if needed. 

# Setup

The html parser reads in the raw html page from the USC COVID data site. Since the page requires users to be logged into the USC Shibboleth SSO (which additonally requires a confirmation from DUO Push) users are required to manually download the covid data page html. To do this simply navigate to the USC COVID data page and hit `ctrl + s` on the keyboard. Once downloaded the user will need to move it into the `/html` directory.  

!!! warning
    Because of the inconsistant way the covid data is entered onto the site, older data might not be correctly parsed in the current state of the parser. This parser was designed on the 2022 January/Febuary datasets.

# Invocation

To run parser.py from the base project directory simply type: `python src/parser.py`. 

All directory references made within the file use relative paths, so it will not matter what directory the user calls this script from. 

# Output 

An example of an output csv is as follows:

```
class_name,code,weekday,start_time,end_time,location
AHIS-460,12016,H,14:00,16:40,CPA260
AMST-101,10310,TH,09:30,10:50,MHP101
AMST-101,10315,M,13:00,13:50,GFS108
...
```

The first line is always the header containing the name of each colomn. Below is a description of each colomn: 

| Column name | description                                     |
| ----------- | ----------------------------------------------- | 
| class_name  | Class name + code separated by hyphen           | 
| code        | Internal USC class code. Contains only numbers. |
| weekday     | Characters for day of week. Subset of "MTWTHF"  |
| start_time  | Starting time (24 hr). Format is hour:min       |
| end_time    | Ending time (24 hr). Format is hour:min         |
| location    | (building) location name                        |
