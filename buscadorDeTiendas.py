# This file contains info to webscrape websites
from config import *
import requests
from bs4 import BeautifulSoup
import re 
import time
import pandas as pd

class buscadorDeTiendas:

    def __init__(self):
        print("Busador creado.")
        # User input
        self.product = pd.NA  # Original search input
        self.domain = pd.NA # Store domain
        self.url = pd.NA  # Full link of product
        # Found items
        self.name = pd.NA  # Name found on website
        self.price = pd.NA  # Price in website
        self.brand = pd.NA


    # Updates item being search
    # Takes: item(pandas series or dictionary)
    def newProduct(self, item,n):
        self.product = item['Producto']
        self.domain = item['Dominio']
        self.url = item['Link']
        self.n = n
        self.name = pd.NA  
        self.price = pd.NA  
        self.brand = pd.NA


    # Returns info 
    def getItem(self):
        producto = {'Producto':self.product,
        'Dominio':self.domain,
        'Nombre':self.name,
        'Precio': self.price,
        'Marca': self.brand,
        'Link': self.url,
        'Cantidad':self.n
        }
        return producto

       
    # Takes: domain (str) and url (str)
    # Updates: Nombre y precio 
    def findPrices(self):

        # If it is a known domain
        if self.domain in accepted_domains.keys(): 
            print('Domain found:',self.domain)
            print(self.url)

            # # Get html
            # self.driver.get(self.url)
            # soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            r=requests.get(self.url,headers=headers)
            time.sleep(1)
            soup = BeautifulSoup(r.text,"html.parser")

            # Get information
            if self.domain == 'plazavea.com.pe':
                self.plazaVea(soup)

            elif self.domain =='sodimac.com.pe':
                self.sodimac(soup)

            elif self.domain == 'promart.pe':
                self.promart(soup)
            
            elif self.domain == 'sodimac.falabella.com.pe':
                self.sodimac_falabella(soup)

            elif self.domain =='shopstar.pe':
                self.shopstar(soup)

            elif self.domain =='akl.com.pe':
                self.akl(soup)
            
            elif self.domain =='promelsa.com.pe':
                self.promelsa(soup)

            elif self.domain=='listado.mercadolibre.com.pe':
                self.mercado_libre(soup)
            
            elif self.domain=='cahema.pe':
                self.cahema(soup)

        # Unknown domain
        else:
            print('New domain:',self.domain)
            self.name= pd.NA #datan
            self.price = pd.NA #datan

    
        

    # TIENDAS 
    # Each of the following functions has been tailored to their websites
    def plazaVea(self,htmlSoup):
        # Assuming 1 element page
        nombre=htmlSoup.find('h1',{'class':"ProductCard__name"}).find('div').text
        precio = htmlSoup.find('input',{'id':'___rc-p-dv-id'})['value']
        precio = float(precio.replace(',','.'))
        marca = htmlSoup.find('span',{'class':'ProductCard__brand'}).find('a').text
        marca = marca.lower()
        
        self.name = nombre
        self.price = precio
        self.brand = marca
        
    def sodimac(self,htmlSoup):
        # If its actually falabella
        bool_falabella=htmlSoup.find('meta',{'name':'apple-mobile-web-app-title'})
        if not bool_falabella:
            print('actually sodimac')
            t=self.url.split('/')
            # Assuming 1 element page
            if t[4] == 'product':
                nombre=htmlSoup.find('h1',{'class':'jsx-4095377833 product-title'})
                nombre = nombre.text
                marca = htmlSoup.find('div',{'class':'jsx-4095377833 product-brand'}).text
                try:
                    precio = htmlSoup.find('div',{'class':'jsx-2167963490 primary'}).text
                    precio = precio.replace('S/','')
                    precio=precio.replace(',','')
                    precio = float(precio.replace('c/u',''))
                except:
                    precio = 'Agotado'
            
            # Multiple object page
            else:
                # Encontrar todos los productos
                productos = htmlSoup.find_all('div',{'class':'jsx-2974854745 product ie11-product-container'})
                productos_encontrados=[]
                for item in productos:
                    nombre = item.find('h2',{'class':'jsx-2974854745 product-title'}).text
                    precio = item.find('span',{'class':'jsx-4135487716'}).text+item.find('span',{'class':'jsx-4135487716 decimals'}).text
                    precio = precio.replace(',','')
                    precio = float(precio.replace('S/',''))
                    link = item.find('a',{'id':'title-pdp-link'})['href']
                    marca = item.find('div',{'class':'jsx-2974854745 product-brand'}).text
                    productos_encontrados.append({'Nombre':nombre,'Precio':precio,'Link':link,'Marca':marca})
                  
                best_match = self.bestMatch(productos_encontrados)
                nombre = best_match['Nombre']
                precio = best_match['Precio']
                self.url = best_match['Link']
                marca = best_match['Marca']
            marca = marca.lower()

            self.name = nombre
            self.price = precio
            self.brand = marca
        
        # Link redirects to falabella
        elif bool_falabella['content'] == 'Falabella.com':
            print('this is falabella')
            self.domain='sodimac.falabella.com.pe'
            self.sodimac_falabella(htmlSoup)


    def promart(self,htmlSoup):
        
        nombre = htmlSoup.find('h1',{'class':'ficha_name'})
        
        # Assuming 1 element page
        if nombre != None:
            nombre = nombre.find('div').text

            precio = htmlSoup.find('input',{'id':'___rc-p-dv-id'})['value']
            precio = float(precio.replace(',','.'))
            if precio >=9999800:
                precio = 'Agotado'

            marca=htmlSoup.find('div',{'class':'ficha_brand'}).find('a').text
            

        # Multiple page result
        else:
            # Encontrar todos los productos
            productos = htmlSoup.find_all('div',{'class':'item-product product-listado'})
            productos_encontrados=[]
            for item in productos:
                producto = item.find('div')
                nombre = producto['data-name']
                precio = producto['data-list-price']
                precio = precio.replace(',','')
                precio = float(precio.replace('S/',''))
                link = producto.find('a')['href']
                marca = item.find('div',{'class':'brand js-brand'}).find('p').text
                productos_encontrados.append({'Nombre':nombre,'Precio':precio,'Link':link,'Marca':marca})
                
            best_match = self.bestMatch(productos_encontrados)
            nombre = best_match['Nombre']
            precio = best_match['Precio']
            self.url = best_match['Link']
            marca = best_match['Marca']

        marca = marca.lower()
        self.name = nombre
        self.price = precio
        self.brand = marca


    def sodimac_falabella(self,htmlSoup):
        # Assuming 1 element page
        nombre=htmlSoup.find('h1',{'class':'jsx-1442607798'}).find('div').text
        precio = htmlSoup.find('li',{'class':'jsx-2797633547 prices-0'})['data-internet-price']
        precio=float(precio.replace(',',''))

        marca=htmlSoup.find('a',{'id':'pdp-product-brand-link','class':'jsx-1874573512 product-brand-link'}).text
        marca = marca.lower()

        self.name = nombre
        self.price = precio
        self.brand = marca


    def shopstar(self,htmlSoup):
        # Assuming 1 element page
        nombre=htmlSoup.find('h2',{'class':'product-info__detail__name'}).find('div').text
        marca=htmlSoup.find('div',{'class':'product-info__detail'}).find('h5').find('a').text
        marca = marca.lower()

        try: # Interbank price
            precios=htmlSoup.find('div',{'class':'priceInterbank'}).find_all('p')
            print('Shopstar: Precio de oferta encontrado')
            for p in precios:
                precio = p.text
            precio = float(precio.replace('S/',''))
        except: # No hay oferta de interbank
            print('Shopstar: Sin oferta de Intrbank')
            precio_case = htmlSoup.find('strong',{'class':'skuBestPrice'})
            if precio_case != None:
                precio = precio_case.text
                precio = float(precio.replace('S/.',''))
            else:
                precio = pd.NA


        self.name = nombre
        self.price = precio
        self.brand = marca

    def akl(self,htmlSoup):
        # Assuming 1 element page
        title= htmlSoup.find('h1',{'itemprop':'name'})
    
        nombre=title.text
        precio=float(htmlSoup.find('span',{'itemprop':'price'})['content'])

        marca=htmlSoup.find('div',{'class':'product-manufacturer'}).find('img')['alt']
        marca = marca.lower()

        self.name = nombre
        self.price = precio
        self.brand = marca

    def promelsa(self,htmlSoup):
        # Assuming 1 element page
        nombre=htmlSoup.find('span',{'class':'base','itemprop':'name'}).text

        precio= htmlSoup.find('span',{'class':'price'}).text
        precio=precio.replace('S/','')
        precio=float(precio.replace(',',''))

        marca = htmlSoup.find('div',{'class':'frm-marca'}).text
        marca = marca.lower()

        self.name = nombre
        self.price = precio
        self.brand = marca

    def mercado_libre(self,htmlSoup):
        # Assuming multiple products per page
        productos = htmlSoup.find_all('div',{'class':'ui-search-result__wrapper shops__result-wrapper'})
        productos_encontrados=[]
        for item in productos:
            nombre = item.find('a').text
            link = item.find('a')['href']
            precio =item.find('span',{'class':'price-tag-fraction'}).text
            precio = float(precio.replace('.',''))
            productos_encontrados.append({'Nombre':nombre,'Precio':precio,'Link':link})
            
        best_match = self.bestMatch(productos_encontrados)
        self.url = best_match['Link']


        # Get brand in new url
        r=requests.get(self.url,headers=headers)
        time.sleep(1)
        htmlSoup = BeautifulSoup(r.text,"html.parser")
      
        try:
            marca = htmlSoup.find('span',{'class':'andes-table__column--value'}).text
            marca = marca.lower()
        except:
            marca='Desconocida'

        self.brand = marca
        self.name = best_match['Nombre']
        self.price = best_match['Precio']


    def cahema(self,htmlSoup):
        # If individual page
        ending=self.url.split('.')
        if ending[len(ending)-1] =='html':
            nombre = htmlSoup.find('h1',{'class':'h2 product-name'}).text
            precio= float(htmlSoup.find('div',{'class':'price'}).find('span')['content'])
            marca = htmlSoup.find('div',{'class':'product-manufacturer'}).find('a').text
        
        # Multiple items per page
        else:
            productos = htmlSoup.find_all('div',{'class':'product-miniature-information'})
            productos_encontrados=[]
            for item in productos:

                nombre = item.find('a').text
                link = item.find('a')['href']
                precio =item.find('span',{'class':'price'}).text
                precio = float(precio.replace('S/.',''))
                productos_encontrados.append({'Nombre':nombre,'Precio':precio,'Link':link})
                
            best_match = self.bestMatch(productos_encontrados)
            self.url = best_match['Link']
            nombre = best_match['Nombre']
            precio = best_match['Precio']

            # Get brand in new url
            r=requests.get(self.url,headers=headers)
            time.sleep(1)
            htmlSoup = BeautifulSoup(r.text,"html.parser")
            
            marca = htmlSoup.find('div',{'class':'product-manufacturer'}).find('a').text
            
        marca = marca.lower()
        self.brand = marca
        self.name = nombre
        self.price = precio
        

    
        



    # Helper functions
    # None of the following functions modify the original object

    # Best match: returns the product that best ressembles the original search
    # Takes: list of dictionaries with products information
    def bestMatch(self,productsList):
        # Key words
        keyWords=self.product.split()

        for item in productsList:
            matchIx = 0
            title = item['Nombre']
            for word in keyWords: # Find titles that matches description
                try:
                    if re.search(word, title, re.IGNORECASE):
                        matchIx=matchIx+1
                except:
                    if word in title:
                        matchIx=matchIx+1
            item['MatchScore']=matchIx
        
        
        productsList=sorted(productsList,key=lambda e: (-e['MatchScore'], e['Precio']) )
        return productsList[0]