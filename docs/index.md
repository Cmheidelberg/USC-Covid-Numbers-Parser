# USC COVID NUMBERS PARSER

# Installation

The code can be cloned from GitHub at: `https://github.com/Cmheidelberg/USC-Covid-Numbers-Parser`.

There are some dependancies which can be installed using `pip`:

1. [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) is used for html parsing. It can be installed using: `pip install beautifulsoup4`

2. [geojson](https://pypi.org/project/geojson/) is used for reading and creating geojson files. These files are able to be imported into software such as CARTO for data visualization.


# Directory structure

#### Directory structure tree:
```
USC-Covid-Data-Parser 
├── data       
├── docs       
├── html       
└── src
```

#### Descriptions:

- `/data`: any internal data used by the program. By default any data the program needs should be included when you clone the repository.

- `/docs`: this folder houses markdown files responsible for this documentation. Unless you are modifying the documentation dont edit anything in this directory 

- `/html`: the data in the html folder should be downloaded from the usc covid data page. You can download these pages by hitting `ctrl + s` while viewing the page. When you download it place it into the `/html` directory. 

- `/src`: This is the code folder. Do not edit it unless you want to modify the code

