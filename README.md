# USC COVID NUMBERS PARSER

### Base Data Parser
This project is designed to parse the html from  the USC covid data page and convert it in a more usable csv. The generated csv is then validated and any erronious rows are removed to guarantee the output file is consistant. Any columns for each row that cannot be parsed will be entered as `null` to prevent uneven rows. Rows with null values could be post processed later if needed. 

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


> :warning: **Note**: Because of the inconsistant way the covid data is entered onto the site, older data might not be correctly parsed in the current state of the parser. This parser was designed on the 2022 january/febuary datasets. 

### Additional features

Since it is hard to do meaningful analysis on this data alone additional features have been added to enrich the output data. There is also an option to append building address to the end of the csv. This adds another two columns to each row of the csv with the full buiding name and street address. Since this process is automatic it is not perfect, any buildings who's address cannot be resolved will be entered as `null`.

Example of csv with appended location data
```
class_name,code,weekday,start_time,end_time,location,full_building_name,building_address
ACCT-410,14006,MW,10:00,11:50,JFF241,Jill and Frank Fertitta Hall,610 Childs Way
ACCT-416,14105,MW,14:00,15:50,ACC310,Accounting,Leventhal School of 3660 Trousdale Pkwy.
...
```

| Column name         | description                                                      |
| ------------------- | ---------------------------------------------------------------- | 
| full_building_name  | Full name of building as presented on the USC building directory | 
| building_address    | Building address as presented on the USC building directory      |

## Directory structure

- `/html`: the data in the html folder should be downloaded from the usc covid data page. You can download these pages by hitting `ctrl + s` while viewing the page. When you download it place it into the `/html` directory. 

- `/src`: This is the code folder. Do not edit it unless you want to modify the code

- `/data`: any internal data used by the program. By default any data the program needs should be included when you clone the repository.