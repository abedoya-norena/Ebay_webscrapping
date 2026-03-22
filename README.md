# eBay Scraper (ebay-dl.py)

Description: This repository contains a python scripts that scrapes eBay search results (specifics below) and converts them into JSON or CSV files depending on specification (default is JSON).

The script takes as input any search term (if space use '') as input and retrives desired pages of listings (default is ten, more specifcs below). This script also uses Playwright to load the webpage (so JavaScript is executed), and BeautifulSoup to parse the HTML. (Additionally, I used [undetected-playwright][https://github.com/QIN2DIM/undetected-playwright?tab=readme-ov-file#sync])

For each item, the script extracts:

- name: the title of the item  
- price: the price in cents (stored as an integer)  
- status: the condition of the item (e.g., New, Pre-owned, Refurbished) 
- shipping: the shipping cost in cents (0 if free)  
- free_returns: whether the item has free returns (True/False)  
- items_sold: number of items sold (integer or None if not listed)  

If any field is missing, its value is set to `None`.

**Please note that for the "status", eBay allows people to put all sorts of information under that box, so in an attempt to get only clean data, I restricted it to only show "new, pre-owned, refurbished, open box, parts, good, excellent, very good" (this can be easily editable see ebay-dl.py)**

## How to Run


The script requires a search term and optionally allows you to specify the number of pages to scrape.

Basic usage:

```
python3 ebay-dl.py SEARCHTERM
```

If your search term contains spaces, use quotation marks:

```
python3 ebay-dl.py "drill press"
```

To specify the number of pages:

```
python3 ebay-dl.py shoes --num_pages=3
```


## CSV Output

By default, the script outputs a JSON file.

To save the results as a CSV file instead, use:

```
python3 ebay-dl.py "drill press" --csv
```

## Example Runs

Below are example commands used to generate the files in this repository:

```
python3 ebay-dl.py GPU
python3 ebay-dl.py CPU
python3 ebay-dl.py Hammer

python3 ebay-dl.py CPU --csv
python3 ebay-dl.py GPU --csv
python3 ebay-dl.py Hammer --csv
```



## Course Project

## Course Project

[Project 02: Web Scraping Assignment](https://github.com/mikeizbicki/cmc-csci040/tree/2026spring/project_02_webscraping)