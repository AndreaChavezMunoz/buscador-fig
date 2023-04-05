import pandas as pd
from buscadorDeTiendas import buscadorDeTiendas
import streamlit as st
from googlesearch import search
from urllib.parse import urlparse
#import pickle
#from config import user_agent
import csv, random

file = open('UserAgents.csv', "r")
user_agent_list = list(csv.reader(file, delimiter=","))
file.close()

def searchEngine(productoToSearch,quantity,traza):
    print('Buscando producto:', productoToSearch)
    urls = searchURLs(productoToSearch)
    print('urls encontrados:', urls)
    info = searchPrices(urls)

    # add quantity and traza
    df_info= pd.DataFrame(info)
    df_info['Cantidad']=quantity
    df_info['Producto Solicitado']= traza
    return df_info


buscador = buscadorDeTiendas()     

# Takes: list of dictionaries with product, link and domain for the same product
# Retruns: List of dictionary with all product information
def searchPrices(productosToSearch):

    # Webscrape each product
    product_info=[]
    for info in productosToSearch:
        buscador.newProduct(info)
        try: # Find prices in website. If there is an error ignore it and go to next one
            buscador.findPrices()
        except:
            print(f'Error encontrando producto {info}')
            
        info = buscador.getItem()
        print(info)
        product_info.append(info)

    # Add quantity and traza, unidad

    return product_info


# Takes: product to search online (str)
# Return: list of dictionaries with product searched, link and domain
def searchURLs(productToSearch):
    
    while True:
        user_agent = random.choice(user_agent_list)[0]
        print('User agent: ', user_agent)
        allProducts = []
        
        try:
            # Find links with product
            links_found= search(productToSearch, tld='com', lang='es', num=5, start=0, stop=5, pause=5, country='Peru', user_agent=user_agent)
            
            # Find unique domains
            unique_domains = set()
            all_links = []
            for url in links_found:
                all_links.append(url)
                uri = urlparse(url)
                dom = uri.netloc or uri.path
                unique_domains.add(dom if not dom.startswith('www.') else dom[4:])

        except:
            pass

        else:
            # Select urls in unique domain 
            for domain in unique_domains:
                for url in all_links:
                    if domain in url: # Get first link for each domain
                        allProducts.append({'Producto':productToSearch,'Link': url,'Dominio':domain})
                        break

            return allProducts
