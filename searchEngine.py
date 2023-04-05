import pandas as pd
import streamlit as st
from googlesearch import search
from urllib.parse import urlparse
from config import user_agent_list

from buscadorDeTiendas import buscadorDeTiendas


class SearchEngine:
    """
    A class to search for product information online.

    Attributes:
    -----------
    buscador: buscadorDeTiendas object
        An object of the buscadorDeTiendas class to scrape product information.
    """

    def __init__(self):
        """Initialize SearchEngine object."""
        self.buscador = buscadorDeTiendas()
        self.user_agent = user_agent_list.sample().values[0]

    def search_URLs(self, product_to_search):
        """
        Search for links with the specified product.

        Parameters:
        -----------
        product_to_search: str
            The product to search online.

        Returns:
        --------
        list of dictionaries
            List of dictionaries with product searched, link, and domain.
        """
        for n in range(3):
            # Select a random user agent from user_agent_list
            print('User agent:', self.user_agent)

            all_products = []
            try:
                # Find links with product
                links_found = search(product_to_search, tld='com', lang='es', num=5, start=0, stop=5, pause=5, country='Peru', user_agent=self.user_agent)

                # Find unique domains
                unique_domains = set()
                all_links = []
                for url in links_found:
                    print('url ',url)
                    all_links.append(url)
                    uri = urlparse(url)
                    dom = uri.netloc or uri.path
                    unique_domains.add(dom if not dom.startswith('www.') else dom[4:])

            except Exception as e:
                print(e)
                self.user_agent = user_agent_list.sample().values[0]
                continue

            else:
                # Select urls in unique domain
                for domain in unique_domains:
                    for url in all_links:
                        if domain in url:  # Get first link for each domain
                            all_products.append({'Producto': product_to_search, 'Link': url, 'Dominio': domain})
                            break

                return all_products

            return None 


    def search_prices(self, products_to_search):
        """
        Webscrape each product to find the prices.

        Parameters:
        -----------
        products_to_search: list of dictionaries
            List of dictionaries with product, link, and domain for the same product.

        Returns:
        --------
        list of dictionaries
            List of dictionaries with all product information.
        """
        product_info = []
        for info in products_to_search:
            self.buscador.newProduct(info)
            try:  # Find prices in website. If there is an error ignore it and go to next one
                self.buscador.findPrices()
            except:
                print(f'Error encontrando producto {info}')
                continue

            info = self.buscador.getItem()
            print(info)
            product_info.append(info)

        # Add quantity and traza, unidad
        return product_info

    def search_engine(self, product_to_search, quantity, traza):
        """
        Search for product information online and return a DataFrame with the results.

        Parameters:
        -----------
        product_to_search: str
            The product to search for online.
        quantity: str
            The quantity of the product.
        traza: str
            The trace of the product.

        Returns:
        --------
        DataFrame
            DataFrame with all product information.
        """
        print('Buscando producto:', product_to_search)
        urls = self.search_URLs(product_to_search)
        print('urls encontrados:', urls)
        if urls is not None:
            info = self.search_prices(urls)
            
            # add quantity and traza
            df_info= pd.DataFrame(info)
            df_info['Cantidad']=quantity
            df_info['Producto Solicitado']= traza
            return df_info
        else:
            return pd.DataFrame()


