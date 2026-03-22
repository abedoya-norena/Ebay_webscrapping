import argparse
from playwright.sync_api import sync_playwright
from undetected_playwright import Tarnished
from bs4 import BeautifulSoup
import json
import csv 

#as stated in the readme, ebay lets you put anything as the items condition so a lot of people put a lot of trash data 
#well trash for us, so i filtered it to the information below.
#EDIT TO DESIRED     
def parse_status(text):
    lower = text.lower()

    if "new" in lower:
        return text
    elif "pre-owned" in lower:
        return text
    elif "refurbished" in lower:
        return text
    elif "open box" in lower:
        return text
    elif "parts" in lower:
        return text
    elif "good" in lower or "excellent" in lower or "very good" in lower:
        return text

    return None

#cleaning to cents (PRICE)
def parse_price(text):
    text = text.replace('$', '').replace(',', '').strip()

    # handle ranges like "54.99 to 79.99"
    text = text.split('to')[0].strip()

    numbers = ''
    for char in text:
        if char.isdigit() or char == '.':
            numbers += char

    if numbers != '':
        return int(float(numbers) * 100)

    return None

#making sure it is talking about sold items 
def parse_itemssold(text):
    numbers = ''
    for char in text:
    
        if char in '1234567890':
            numbers += char
    if "sold" in text:
        return int(numbers)
    else:
        return None 
#changed this above for consistancy ^ 

#making sure it is talking about shipping cost and cleaning number
def parse_shipping(text):
    text = text.lower()

    if "free" in text:
        return 0

    numbers = ''
    for char in text:
        if char.isdigit() or char == '.':
            numbers += char

    if numbers != '':
        return int(float(numbers) * 100)

    return None

#make sure its the correct text 
def parse_free_returns(text):
    if "free returns" in text.lower():
        return True
    return None


#this is the undetectable playwright 
def download_html_and_run_javascript(url):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)

        context = browser.new_context()
        Tarnished.apply_stealth(context)   

        page = context.new_page()
        page.goto(url)

        page.wait_for_timeout(5000)

        html = page.content()
        browser.close()
    return html



#get command line arguments 
parser = argparse.ArgumentParser(description='Download information from ebay and convert to JSON.')
parser.add_argument('search_term',)
parser.add_argument('--num_pages', default=10)
parser.add_argument('--csv', action='store_true')
args = parser.parse_args()
print('args.search_term=', args.search_term)
#list of all items found in all ebay webpages
items = []

#loop over ebay webpages
for page_number in range(1, int(args.num_pages)+1):
    
    #Build the Url 
    url = 'https://www.ebay.com/sch/i.html?_nkw='+args.search_term + '&_sacat=0&_from=R40&_pgn='
    url += str(page_number) 
    

    #download the html 
    html = download_html_and_run_javascript(url)


    #process the html

    soup = BeautifulSoup(html, 'html.parser')

    #loop over the items in the page 
    tags_items = soup.select('.su-card-container__content')
    for tag_item in tags_items:

        #extract the name
        name = None
        tags_name = tag_item.select('.s-card__title')
        for tag in tags_name: 
            name = tag.text.replace("Opens in a new window or tab", "").strip()
        if not name:
            continue
        if name.strip() == "Shop on eBay":
            continue

    #shipping (this tag grabs a ton of info so i used helper func similar to items sold)
        shipping = None
        tags_attributes = tag_item.select('.su-styled-text.secondary.large')
        for tag in tags_attributes:
            text = tag.text
            if "delivery" in text.lower() or "shipping" in text.lower():
                shipping = parse_shipping(text)

            #items sold 
        items_sold = None
        tags_itemssold = tag_item.select('.su-styled-text.primary.bold.large')
        for tag in tags_itemssold:
            items_sold = parse_itemssold(tag.text)
        # free returns (same idea as shipping)
        freereturns = False
        tags_attributes = tag_item.select('.su-styled-text.secondary.large')
        for tag in tags_attributes:
            text = tag.text
            if parse_free_returns(text):
                    freereturns = True
        #price             
        price = None
        tags_price = tag_item.select('.s-card__price')

        for tag in tags_price:
            price = parse_price(tag.text)
        
        #status 
        status = None
        tags_status = tag_item.select('.su-styled-text.secondary.default')

        for tag in tags_status:
            text = tag.text.strip()

            result = parse_status(text)
            if result:
                status = result
                break
        item = {
            'name': name,
            'price': price,
            'status': status,
            'shipping': shipping,
            'free_returns': freereturns,
            'items_sold': items_sold,
        }

        items.append(item) 

    print('len(tag_item)=', len(tags_items))
    print('len(items)=', len(items))

    #for item in items: 
        #print('item=', item)

#If specified write file as CSV, otherwise write as JSON
if args.csv:
    filename = args.search_term + '.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'name', 'price', 'status', 'shipping', 'free_returns', 'items_sold'
        ])
        writer.writeheader()
        writer.writerows(items)

else:
    filename = args.search_term + '.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2)
    