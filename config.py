import pandas as pd

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
user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
headers = {'User-Agent':user_agent}

# Filltro
def agg(g):
    print('Here')
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
        'precio_promedio': g['Precio'].mean(),
        'precio_min': lowest_price,
        'precio_min_marca': lowest_price_brand,
        'marca_popular':popular_brand,
        'marca_popular_min_price':g[g['Marca']==popular_brand]['Precio'].min(),
        'marca_popular_avg_price':g[g['Marca']==popular_brand]['Precio'].mean()
        
    })
