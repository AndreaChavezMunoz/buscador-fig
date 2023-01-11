import pandas as pd
from searchEngine import searchEngine, searchPrices
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


#  Test summary

df_clean = pd.read_csv('/Users/chavezmunoz.a/Downloads/BusquedaRapida_Lista de Construcción UL777- FIGSAC.csv')
df_clean.loc[df_clean["Precio"] == "Agotado", "Precio"] = pd.NA
df_clean.loc[df_clean["Precio"] == "<NA>", "Precio"] = pd.NA
df_clean.dropna(inplace=True)
df_clean["Precio"] = pd.to_numeric(df_clean["Precio"])

df_summary = df_clean.groupby('Producto').apply(agg)

