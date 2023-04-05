import streamlit as st
import pandas as pd
from searchEngine import searchEngine
from config import agg,accepted_domains
from stqdm import stqdm
from io import BytesIO
import pickle

@st.cache
def df2csv(df):
    return df.to_csv().encode('utf-8')

@st.cache
def df2xslx(df):
    """
    Return pandas.DataFrame as xlsx.

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame to be converted.

    Return
    ------
    xlsx file
        Same file.
    """
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

@st.cache
def format_carga_masiva(df_productos):
    """
    Return cleaned up version of data frame. 
    Gets rid of non ASCII characters

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame containing Precio, Producto, Nombre, Dominio, Cantidad.

    Return
    ------
    pandas.DataFrame
        File with no non-ASCII characters. Monedad added.
    """
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
   
    return df_clean


# Takes: df_productos(df of all products)
# Returns: series of products and average prices
@st.cache
def price_summary(df_productos):
    """
    Return summary of Precio of each Product based on Marca. 

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame containing Precio, Producto, Marca.

    Return
    ------
    pandas.DataFrame
        Summary of Precios groupped by Producto.
        precio_max: max price,
        precio_promedio: average price,
        precio_min: lowest price,
        precio_min_marca: marca del precio mas bajo,
        marca_popular: marca más encontrada,
        marca_popular_min_price: precio minimo de la marca más encontrada,
        marca_popular_avg_price: precio promedio de la marca más encontrada
    """
    df_clean = df_productos.copy()
    df_clean.loc[df_clean["Precio"] == "Agotado", "Precio"] = pd.NA
    df_clean.loc[df_clean["Precio"] == "<NA>", "Precio"] = pd.NA
    df_clean.loc[df_clean["Precio"] == "0", "Precio"] = pd.NA
    df_clean.loc[df_clean["Precio"] == "nan", "Precio"] = pd.NA
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
        return pd.DataFrame(columns=['Nombre de producto Solicitado','Cantidad'])
    # Read file
    df = pd.read_excel(file)
    if 'Nombre de producto Solicitado' in df.columns:

        productosToSearch = df[['Producto Solicitado','Nombre de producto Solicitado', 'Cantidad Solicitada']]
        # # Change comas for periods
        # productosToSearch['Cantidad Solicitada']=productosToSearch['Cantidad Solicitada'].astype(str)
        # productosToSearch['Cantidad Solicitada'] = productosToSearch['Cantidad Solicitada'].str.replace(',','.')
        # productosToSearch['Cantidad Solicitada'] = pd.to_numeric(productosToSearch["Cantidad Solicitada"])
        # # Change column name to something smaller
        # productosToSearch.rename(columns = {'Producto Solicitado (Usar menos de 80 Letras)':'Producto'}, inplace = True)
        return productosToSearch
    else:
        return pd.DataFrame(columns=['Nombre de producto Solicitado','Cantidad'])


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
    productos_n = len(productosToSearch.index)
    if productos_n==0:
        return pd.DataFrame()

    # Web scrape each product
    info_all = None
    
    for i in stqdm(range(productos_n),desc="Buscando los mejores precios"):
        p=productosToSearch.at[i, 'Nombre de producto Solicitado']
        n=productosToSearch.at[i,'Cantidad Solicitada']
        t=productosToSearch.at[i,'Producto Solicitado'] # TRAZA
        info_found = searchEngine(p,n,t)
        if info_all is None:
            info_all = info_found
            # open a file, where you ant to store the data
            file = open('important', 'wb')

            # dump information to that file
            pickle.dump(info_found, file)
            
        else:
            info_all=info_all.append(info_found)
            pickle.dump(info_found, file)
    # close the file
    file.close()
    
    return info_all




# Main page--------
st.title('Buscador de precios')
st.write('El archivo elegido debe tener la columna *Producto Solicitado (Usar menos de 80 Letras)* ')
file =st.file_uploader('Porfavor escoja el archivo con los productos que desea encontrar', type=['xlsx'])

productosToSearch_df=encontrar_productos(file)

# Side bar---------
# Filter prices shown based on selection
options = ['Todos']
options.extend(productosToSearch_df["Nombre de producto Solicitado"].values.tolist())
producto_to_show =st.sidebar.selectbox('Productos mostrados',options)
df_productos=buscar_precios(productosToSearch_df)


# Once file has been uploaded -----------
if len(productosToSearch_df)!=0:
    # Show results
    st.write('## Productos encontrados')
    st.dataframe(df_productos)

    # Download data
    # Complete
    if file != None:
        og_name =file.name.split('.')
    else:
        og_name = 'debugging'
    name_productos = 'BusquedaRapida_'+og_name[0]+'.xlsx'
    xlsx_productos = df2xslx(df_productos)
    st.download_button(
        label="Descargar busqueda",
        data=xlsx_productos,
        file_name=name_productos,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    # Ready for carga masiva
    name_carga_masiva='CargaMasiva_'+og_name[0]+'.csv'
    formatted = format_carga_masiva(df_productos)
    csv_carga_masiva = df2csv(formatted)
    st.download_button(
        label="Descargar carga masiva",
        data=csv_carga_masiva,
        file_name=name_carga_masiva,
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
    xlsx_resumen=df2xslx(summary_df)
    name_resumen = 'ResumenBusquedaRapida_'+og_name[0]+'.xlsx'
    st.download_button(
        label="Descargar resumen",
        data=xlsx_resumen,
        file_name=name_resumen,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )







