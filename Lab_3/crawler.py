import requests
from bs4 import BeautifulSoup
import json
import re

base_url = "https://999.md/ro/list/transport/motorcycles"

def find_next_page_url(current_url,page,soup):
    pg=str(page)
    nextp="?page=" + pg
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if re.search(re.escape(nextp), href):  
            current_url = re.sub(r'\?page=\d+', nextp, current_url) 
            return current_url
    return None

def web_crawler(start_url:str, page:int,links:[], final_page=None):
    if start_url==None:
        return links
    response = requests.get(start_url)
    if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")        
    if page!=final_page:
            if soup:
                product_id_pattern = r'/ro/(\d+)'
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if re.match(product_id_pattern, href):
                        if 'https://999.md'+href in links:
                            pass
                        else:
                            links.append('https://999.md'+href)
            page+=1
            start_url=find_next_page_url(start_url,page,soup)
    else:
        return links
    return web_crawler(start_url,page,links,final_page)

def pas_pr(product_links:[],items,result:[]):
    i=0 
    for href in product_links:
        pattern = r'<span[^>]*>(.*?)</span>'
        i+=1
        spr=[]
        matches=[]
        res=[]
        if i==items:
            return result
        else:
            response = requests.get(href)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                if soup:
                    span_elements=soup.find_all('span')
                    for span in span_elements:
                        sp=str(span)
                        spr.append(sp)
            for sp in spr:
                matches.append(re.findall(pattern,sp))
            for match in matches:
                if match==['+373']:
                    break
                elif match ==['Acasă']:
                    pass
                elif re.match(r'(.*?)<i id="js-total-ads"></i>',str(match)):
                    pass
                elif re.match(r'(.*?)<a href',str(match)):
                    pass
                else:
                    res.append(str(match).replace("['",'').replace("']",'').replace('  ',''))
            #result=" ".join(res)  
            result.append(res)          

    
    
if __name__ == "__main__":
    prod_ln=[]
    start_page=2
    start_p=str(start_page)
    start_url = base_url+"?page="+start_p
    links_prod=[]
    all_links = web_crawler(start_url, start_page,links_prod,3)
    product_links=all_links
    prod_ln=pas_pr(product_links,4,prod_ln)
    with open("unique_product_links.json", "w") as json_file:
        json.dump(all_links, json_file, indent=4)
    with open("unique_product_descr.json", "w", encoding="utf-8") as json_file:
        json.dump(prod_ln, json_file, indent=4)