import pandas as pd
from searchEngine import searchEngine, searchPrices

# Test document
df = pd.read_excel('/Users/chavezmunoz.a/Downloads/Lista de Construcción UL777- FIGSAC.xlsx')
productosToSearch = df['Producto Solicitado (Usar menos de 80 Letras)'].tolist()
print(productosToSearch)
info_all = []
for p in  productosToSearch:
    info_found = searchEngine(p)
    info_all = info_all+info_found


# # Test buscador de tiendas
# producto = [{'Producto':'','Dominio':'promart.pe','Link':'https://www.promart.pe/herramientas/herramientas-electricas-portatiles/taladros'}]
# searchPrices(producto)