import pandas as pd

# Currently supported domains
accepted_domains=['plazavea.com.pe','sodimac.com.pe',
'sodimac.falabella.com.pe','shopstar.pe', 'akl.com.pe','promelsa.com.pe','promart.pe']

# Change headers so not recognized as bot
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

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
