import streamlit as st
import pandas as pd
from searchEngine import searchEngine
from config import agg,accepted_domains
from stqdm import stqdm
from io import BytesIO


# Converts df to csv
@st.cache
def convert_df(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

    #return  df.to_csv().encode('utf-8')

# Formato para carga masiva en sistema FIG
@st.cache
def format_carga_masiva(df_productos):
    df_clean = df_productos.copy()
    df_clean.loc[df_clean["Precio"] == "Agotado", "Precio"] = pd.NA
    df_clean.loc[df_clean["Precio"] == "<NA>", "Precio"] = pd.NA
    df_clean.dropna(inplace=True)
    df_clean = df_clean.replace('ñ','n', regex=True)
    df_clean = df_clean.replace('á','a', regex=True)
    df_clean = df_clean.replace('é','e', regex=True)
    df_clean = df_clean.replace('í','i', regex=True)
    df_clean = df_clean.replace('ó','o', regex=True)
    df_clean = df_clean.replace('ú','u', regex=True)
    df_clean = df_clean.replace('"','', regex=True)
    df_clean['Producto']=df_clean['Producto'].str.encode('ascii', 'ignore').str.decode('ascii')
    df_clean['Nombre']=df_clean['Nombre'].str.encode('ascii', 'ignore').str.decode('ascii')
    df_clean = df_clean.replace({"Dominio": accepted_domains})

    df_clean.rename(columns = {'Dominio':'Proveedor', 'Producto':'Producto Solicitado', 'Nombre':'Producto Ofrecido',
                              'Precio':'Costo x Unidad'}, inplace = True)
    df_clean['Moneda']='Soles'
    df_clean['Cantidad']=0

   
    return df_clean


# Takes: df_productos(df of all products)
# Returns: series of products and average prices
@st.cache
def price_summary(df_productos):
    
    df_clean = df_productos.copy()
    df_clean.loc[df_clean["Precio"] == "Agotado", "Precio"] = pd.NA
    df_clean.loc[df_clean["Precio"] == "<NA>", "Precio"] = pd.NA
    df_clean.dropna(inplace=True)
    df_clean["Precio"] = pd.to_numeric(df_clean["Precio"])
    df_summary = df_clean.groupby('Producto').apply(agg)

    return df_summary
    
@st.cache
def encontrar_productos(file):
    """
    Return the names and quantities of products in file.

    Parameters
    ----------
    file : str
        Location of excel file to be read by pandas.

    Return
    ------
    pandas.DataFrame
        Subset of the original DataFrame with names and quantities of products.
    """
    if file is None:
        return pd.DataFrame(columns=['Producto','Cantidad'])
    # Read file
    df = pd.read_excel(file)
    if 'Producto Solicitado (Usar menos de 80 Letras)' in df.columns:

        productosToSearch = df[['Producto Solicitado (Usar menos de 80 Letras)', 'Cantidad']]
        # Change comas for periods
        productosToSearch['Cantidad'] = productosToSearch['Cantidad'].str.replace(',','.')
        productosToSearch['Cantidad'] = pd.to_numeric(productosToSearch["Cantidad"])
        # Change column name to something smaller
        productosToSearch.rename(columns = {'Producto Solicitado (Usar menos de 80 Letras)':'Producto'}, inplace = True)
        return productosToSearch
    else:
        return pd.DataFrame(columns=['Producto','Cantidad'])


# Takes: dictionary with product name: quantity
# Returns: Products found online and prices(df), product names used to search online (list)
@st.experimental_memo
def buscar_precios(productosToSearch):
    """
    Return the search results of all products.

    Parameters
    ----------
    productosToSearch : pandas.DataFrame
        Names and quantities of products.

    Return
    ------
    pandas.DataFrame
        Products found online with domain, name, price, brand, link, and quantity.
    """
    
    if len(productosToSearch)==0:
        return pd.DataFrame()

    # Web scrape each product
    info_all = []
    for i in stqdm(range(len(productosToSearch)),desc="Buscando los mejores precios"):
        p=productosToSearch.at[i, 'Producto']
        n=productosToSearch.at[i,'Cantidad']
        info_found = searchEngine(p,n)
        info_all = info_all+info_found
    df_productos= pd.DataFrame(info_all)

    return df_productos


# Main page--------
st.title('Buscador de precios')
st.write('El archivo elegido debe tener la columna *Producto Solicitado (Usar menos de 80 Letras)* ')
file =st.file_uploader('Porfavor escoja el archivo con los productos que desea encontrar', type=['xlsx'])

productosToSearch_df=encontrar_productos(file)

# Side bar---------
# Filter prices shown based on selection
options = ['Todos']
options.extend(productosToSearch_df["Producto"].values.tolist())
producto_to_show =st.sidebar.selectbox('Productos mostrados',options)
df_productos=buscar_precios(productosToSearch_df)


# Once file has been uploaded -----------
if len(productosToSearch_df)!=0:
    # Show results
    st.write('## Productos encontrados')
    st.dataframe(df_productos)

    # Download data
    og_name =file.name.split('.')
    name_productos = 'BusquedaRapida_'+og_name[0]+'.xlsx'
    csv_productos = convert_df(df_productos)
    st.download_button(
        label="Descargar busqueda",
        data=csv_productos,
        file_name=name_productos,
        mime='text/csv',
    )


    # Show summary of prices
    summary_df = price_summary(df_productos)
    st.write(f"""## Resumen de precios
    Productos encontrados: {len(summary_df)}/{len(productosToSearch_df)}
    """)

    
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

    
    summary_df=summary_df.reset_index()
    csv_resumen=convert_df(summary_df)
    name_resumen = 'ResumenBusquedaRapida_'+og_name[0]+'.xlsx'
    st.download_button(
        label="Descargar resumen",
        data=csv_resumen,
        file_name=name_resumen,
        mime='text/csv',
    )


# # Add features 
# else:
#     st.write('## Productos cargados')
#     df_productos=pd.read_excel('/Users/chavezmunoz.a/Downloads/BusquedaRapida_R2022-777- Listado de Ing.xlsx')
#     st.dataframe(df_productos)

#     st.write('Clean')
#     formatted = format_carga_masiva(df_productos)
#     st.dataframe(formatted)





