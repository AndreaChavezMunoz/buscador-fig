import streamlit as st
import pandas as pd
from searchEngine import searchEngine
from config import agg
from stqdm import stqdm

# Converts df to csv
@st.cache
def convert_df(df):
    return  df.to_csv().encode('utf-8')

# Takes: df_productos(df of all products)
# Returns: series of products and average prices
@st.cache
def price_summary(df_productos):
    df_clean = df_productos.copy()
    df_clean.loc[df_clean["Precio"] == "Agotado", "Precio"] = pd.NA
    df_clean.loc[df_clean["Precio"] == "<NA>", "Precio"] = pd.NA
    df_clean["Precio"] = pd.to_numeric(df_clean["Precio"])
    df_summary = df_clean.groupby('Producto').apply(agg)
    return df_summary
    

# Reads file 
# Returns: list of products to search (str)
@st.cache
def encontrar_productos(file):
    if file is None:
        return []
    # Read file
    df = pd.read_excel(file)
    productosToSearch = df['Producto Solicitado (Usar menos de 80 Letras)'].tolist()
    return productosToSearch


# Takes: File
# Returns: Products found online and prices(df), product names used to search online (list)
@st.experimental_memo
def buscar_precios(productosToSearch):
    
    if len(productosToSearch)==0:
        return pd.DataFrame()

    # Web scrape each product
    info_all = []
    for i in stqdm(range(len(productosToSearch)),desc="Buscando los mejores precios"):
        p = productosToSearch[i]
        info_found = searchEngine(p)
        info_all = info_all+info_found
    df_productos= pd.DataFrame(info_all)

    return df_productos


# Main page
st.title('Buscador de precios')
file =st.file_uploader('Porfavor escoja el archivo con los productos que desea encontrar', type=['xlsx'])

productosToSearch=encontrar_productos(file)

# Side bar
# Filter prices shown based on selection
options = ['Todos']
options.extend(productosToSearch)
producto_to_show =st.sidebar.selectbox('Productos mostrados',options)
df_productos=buscar_precios(productosToSearch)



if len(productosToSearch)!=0:
    # Show results
    st.write('## Productos encontrados')
    st.dataframe(df_productos)

    # Show summary of prices
    st.write('## Resumen de precios')
    summary_df = price_summary(df_productos)

    # Download data
    og_name =file.name.split('.')
    name_productos = 'BusquedaRapida_'+og_name[0]+'.csv'
    csv_productos = convert_df(df_productos)
    st.download_button(
        label="Descargar busqueda",
        data=csv_productos,
        file_name=name_productos,
        mime='text/csv',
    )


    if producto_to_show =='Todos':
        st.write(summary_df)

    # Individual summary
    else:
        # Summary info
        st.write(f'### {producto_to_show}' )

        try: 
            # Get labels
            min_brand = summary_df.loc[producto_to_show,'precio_min_marca']
            popular_brand = summary_df.loc[producto_to_show,'marca_popular']
            # Show info
            col11, col21, col31,= st.columns(3)
            col12, col22, col32,= st.columns(3)
            col11.metric(label="Precio promedio", value='S/. '+ str(summary_df.loc[producto_to_show,'precio_promedio']))
            col21.metric(label="Precio minimo", value='S/. '+ str(summary_df.loc[producto_to_show,'precio_min']))
            col31.metric(label="Marca con precio min", value= min_brand)
            col12.metric(label="Marca popular", value=popular_brand)
            col22.metric(label="Marca popular precio min", value='S/. '+ str(summary_df.loc[producto_to_show,'marca_popular_min_price']))
            col32.metric(label="Marca popular precio promedio", value='S/. '+ str(summary_df.loc[producto_to_show,'marca_popular_avg_price']))

        except:
            st.write('Producto no encontrado')

        # Link de proveedores
        st.write('#### Posibles proveedores encontrados en:')
        proveedores =df_productos[df_productos['Producto']==producto_to_show]['Link']
        for p in proveedores.tolist():
            st.markdown("- " + p)

    
    csv_resumen=convert_df(summary_df)
    name_resumen = 'ResumennBusquedaRapida_'+og_name[0]+'.csv'
    st.download_button(
        label="Descargar resumen",
        data=csv_resumen,
        file_name=name_resumen,
        mime='text/csv',
    )






