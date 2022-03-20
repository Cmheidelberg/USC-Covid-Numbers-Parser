
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

