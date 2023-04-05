import pandas as pd
import csv, random

# Debugging
debuggingStatus=False

# Currently supported domains
accepted_domains={'plazavea.com.pe':'Supermercados Peruanos Sociedad Anonima',
    'sodimac.com.pe':'Sodimac Peru S.A.',
    'sodimac.falabella.com.pe': 'Sodimac Peru S.A.',
    'shopstar.pe':'SAN BORJA GLOBAL OPPORTUNITIES S.A.C.', 
    'akl.com.pe':'Akl Peru S.A.C.',
    'promelsa.com.pe':'Promotores Electricos S A | Promelsa',
    'promart.pe':'Inversiones Promar E.I.R.L.',
    'listado.mercadolibre.com.pe':'Mercadolibre Peru S.R.L.',
    'cahema.pe':'Grupo Cahema S.A.C.'}

# Change headers so not recognized as bot
# user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'

df = pd.read_csv('UserAgents.csv')
user_agent_list = df.squeeze()
user_agent = user_agent_list.sample().values[0]

headers = {'User-Agent':user_agent}

# Filltro
def agg(g):
    print(g)
    lowest_price = g['Costo x Unidad'].min()
    popular_brand = g['Marca'].value_counts()
    print(popular_brand)
    popular_brand=popular_brand.idxmax()
    lowest_price_brand = g[g['Costo x Unidad']==lowest_price]['Marca'].unique()
    try:
        lowest_price_brand=lowest_price_brand[0]
    except:
        lowest_price_brand = None
   
    return pd.Series({
        'precio_max':g['Costo x Unidad'].max(),
        'precio_promedio': g['Costo x Unidad'].mean(),
        'precio_min': lowest_price,
        'precio_min_marca': lowest_price_brand,
        'marca_popular':popular_brand,
        'marca_popular_min_price':g[g['Marca']==popular_brand]['Costo x Unidad'].min(),
        'marca_popular_avg_price':g[g['Marca']==popular_brand]['Costo x Unidad'].mean()
        
    })
