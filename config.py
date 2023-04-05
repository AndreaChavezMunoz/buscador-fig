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
file = open('UserAgents.csv', "r")
user_agent_list = list(csv.reader(file, delimiter=","))
file.close()
user_agent = random.choice(user_agent_list)[0]

headers = {'User-Agent':user_agent}

# Filltro
def agg(g):
    print(g)
    lowest_price = g['Precio'].min()
    popular_brand = g['Marca'].value_counts()
    print(popular_brand)
    popular_brand=popular_brand.idxmax()
    lowest_price_brand = g[g['Precio']==lowest_price]['Marca'].unique()
    try:
        lowest_price_brand=lowest_price_brand[0]
    except:
        lowest_price_brand = None
   
    return pd.Series({
        'precio_max':g['Precio'].max(),
        'precio_promedio': g['Precio'].mean(),
        'precio_min': lowest_price,
        'precio_min_marca': lowest_price_brand,
        'marca_popular':popular_brand,
        'marca_popular_min_price':g[g['Marca']==popular_brand]['Precio'].min(),
        'marca_popular_avg_price':g[g['Marca']==popular_brand]['Precio'].mean()
        
    })
