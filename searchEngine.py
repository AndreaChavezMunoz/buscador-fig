import pandas as pd
from buscadorDeTiendas import buscadorDeTiendas
import streamlit as st
from googlesearch import search
from urllib.parse import urlparse
import pickle


def searchEngine(productoToSearch):
    print('Buscando...')
    urls = searchURLs(productoToSearch)
    print('urls encontrados')
    info = searchPrices(urls)
    print('Info encontrada')
    return info


buscador = buscadorDeTiendas()     

# Takes: list of dictionaries with product, link and domain
# Retruns: List of dictionary with all product information
def searchPrices(productosToSearch):

    # Webscrape each product
    product_info=[]
    for info in productosToSearch:
        buscador.newProduct(info)
        buscador.findPrices()
        info = buscador.getItem()
        print(info)
        product_info.append(info)


    return product_info


# Takes: product to search online (str)
# Return: list of dictionaries with product searched, link and domain
def searchURLs(productToSearch):

    allProducts = []
    
    # Find links with product
    links_found= search(productToSearch, tld='com', lang='es', num=5, start=0, stop=5, pause=1.5, country='Peru')
    
    # Find unique domains
    unique_domains = set()
    all_links = []
    for url in links_found:
        all_links.append(url)
        uri = urlparse(url)
        dom = uri.netloc or uri.path
        unique_domains.add(dom if not dom.startswith('www.') else dom[4:])

    # Select urls in unique domain 
    for domain in unique_domains:
        for url in all_links:
            if domain in url: # Get first link for each domain
                allProducts.append({'Producto':productToSearch,'Link': url,'Dominio':domain})
                break

    return allProducts




