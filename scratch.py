import pandas as pd
from searchEngine import searchEngine, searchPrices,searchURLs
from config import agg

# # Test document
# df = pd.read_excel('/Users/chavezmunoz.a/Downloads/Lista de Construcción UL777- FIGSAC.xlsx')
# productosToSearch = df['Producto Solicitado (Usar menos de 80 Letras)'].tolist()
# print(productosToSearch)
# info_all = []
# for p in  productosToSearch:
#     info_found = searchEngine(p)
#     info_all = info_all+info_found


# # Test buscador de tiendas
# producto = [{'Producto':'','Dominio':'promart.pe','Link':'https://www.promart.pe/herramientas/herramientas-electricas-portatiles/taladros'}]
# searchPrices(producto)


#  Get new stores

# # Get all urls
# df = pd.read_excel('/Users/chavezmunoz.a/Downloads/Lista de Construcción UL777- FIGSAC.xlsx')
# productosToSearch = df['Producto Solicitado (Usar menos de 80 Letras)'].tolist()
# all_urls=[]
# for p in productosToSearch:
#     urls=searchURLs(p)
#     all_urls=all_urls+urls
# df=pd.DataFrame(all_urls)
# df.to_csv('urls_found.csv',index=False)

# # Select most frequent stores
# df = pd.read_csv('urls_found.csv')
# popular_stores=df['Dominio'].value_counts()#.nlargest(20)
# print(popular_stores)

# Test store
urls=[{'Dominio':'listado.mercadolibre.com.pe','Link':'https://listado.mercadolibre.com.pe/dobladora-de-estribos-manual-telescopica','Producto':'Tubos para doblar estribos '}]
df = searchPrices(urls)