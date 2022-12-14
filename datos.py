import os
import requests
import logging
from datetime import datetime
from Direcciones import Direcion_Museos, Direcion_Cines, Direcion_Bibliotecas
import pandas as pd

logging.basicConfig(level = logging.INFO,
                    format='%(asctime)s: %(levelname)s - %(message)s')

today = datetime.today()
current_date = today.strftime("%d-%m-%Y")

year_month = today.strftime('%Y-%b')

logging.info('Almacenamiento y extraccion de los datos')
#Almacenamos localmente los archivos cvs con el nombre requerido
def obtencion_organizacion(Direcciones, categoria):
    
    try:
        #obtenemos el dato y los almacenamos
        datos = requests.get(Direcciones)        
        os.makedirs(categoria + '/' + year_month)
        open(categoria 
             + '/'
             + year_month
             + '/' 
             + categoria 
             + '-' 
             + current_date 
             + '.csv', 'wb').write(datos.content)
    
    except FileExistsError:
        logging.info('El archivo ya existe. Continuando con el proceso')
    

logging.info('CVS creados')
obtencion_organizacion(Direcion_Museos, 'Museos')
obtencion_organizacion(Direcion_Cines, 'Salas_cines')
obtencion_organizacion(Direcion_Bibliotecas, 'Bibliotecas')


logging.info('Normalizacion y procesamiento de los datos')

#leemos los archivos cvs
df_museos = pd.read_csv('Museos/'
                        + year_month
                        +'/Museos-'
                        + current_date 
                        + '.csv', encoding='UTF-8')
df_cines = pd.read_csv('Salas_cines/'
                             + year_month
                             + '/Salas_cines-'
                             + current_date 
                             + '.csv', encoding='UTF-8')
df_bibliotecas = pd.read_csv('Bibliotecas/'
                             + year_month
                             + '/Bibliotecas-'
                             + current_date 
                             + '.csv', encoding='UTF-8')

#Normalizamos los nombres que nos interesan.
df_museos2 = df_museos.rename(columns={'Cod_Loc':'cod_localidad', 'IdProvincia':'id_provincia', 'IdDepartamento':'id_departamento', 'categoria':'categor??a', 'direccion':'domicilio', 'CP':'c??digo postal', 'telefono':'n??mero de tel??fono',  'Mail':'mail', 'Web':'web'})
df_cines2 = df_cines.rename(columns={'Cod_Loc':'cod_localidad', 'IdProvincia':'id_provincia', 'IdDepartamento':'id_departamento', 'Categor??a':'categor??a', 'Provincia':'provincia','Direcci??n':'domicilio', 'CP':'c??digo postal', 'Tel??fono':'n??mero de tel??fono',  'Mail':'mail', 'Web':'web'})
df_bibliotecas2 = df_bibliotecas.rename(columns={'Cod_Loc':'cod_localidad', 'IdProvincia':'id_provincia', 'IdDepartamento':'id_departamento', 'Categor??a':'categor??a', 'Provincia':'provincia', 'Localidad':'localidad', 'Nombre':'nombre', 'Domicilio':'domicilio', 'CP':'c??digo postal', 'Tel??fono':'n??mero de tel??fono',  'Mail':'mail', 'Web':'web'})

#Eliminamos las columnas que no vamos a usar

df_museos2 = df_museos2.drop(['Observaciones', 'subcategoria', 'piso', 'cod_area', 'Latitud', 'Longitud', 'TipoLatitudLongitud', 'Info_adicional', 'fuente', 'jurisdiccion', 'a??o_inauguracion', 'actualizacion'], axis=1)
df_cines2 = df_cines2.drop(['Observaciones', 'Departamento','Piso', 'cod_area', 'Informaci??n adicional','Latitud', 'Longitud', 'TipoLatitudLongitud', 'Fuente', 'tipo_gestion',	'Pantallas',	'Butacas',	'espacio_INCAA', 'a??o_actualizacion'], axis=1)
df_bibliotecas2 = df_bibliotecas2.drop(['Observacion', 'Subcategoria', 'Departamento','Piso', 'Cod_tel', 'Informaci??n adicional','Latitud', 'Longitud', 'TipoLatitudLongitud','Fuente', 'Tipo_gestion',	'a??o_inicio',	'A??o_actualizacion'], axis=1)


# Tabla unificada
Tabla_unificada = pd.concat([df_museos2, df_cines2, df_bibliotecas2])


#Agregamos la fecha que se unifico la tabla
Tabla_unificada['Fecha_de_actualizacion'] = current_date



#Cantidad de registros totales por categor??a

total_categoria = Tabla_unificada.groupby(['categor??a']).size().to_frame(name = 'Total por categor??a')

#Cantidad de registros totales por fuente
total_fuentes =  Tabla_unificada.groupby(['categor??a','fuente']).size().to_frame(name = 'Total por fuente')

#Cantidad de registros por provincia y categor??a

total_provincias_categorias =  Tabla_unificada[['categor??a', 'provincia']].value_counts().to_frame('Cantidad de registros por provincia y categor??a')



#Creamos la tabla general para visualizar los registros
tabla2 = total_categoria.merge(total_fuentes, how='outer',
                               left_index=True, right_index=True)
tabla_regristros= tabla2.merge(total_provincias_categorias, how='outer',
                     left_index=True, right_index=True)
tabla_regristros['Fecha_de_actualizacion'] = current_date


#Tabla de cine - Provincia con: Cantidad de pantallas, Cantidad de butacas, Cantidad de espacios INCAA
#Nos quedamos con las columnas a usar
Tabla_cine = df_cines[['Provincia', 'Pantallas', 'Butacas', 'espacio_INCAA']]
#normalizamos los datos de la columna espacio_INCAA
Tabla_cine['espacio_INCAA'] = Tabla_cine['espacio_INCAA'].replace('si', 'SI').replace('SI', 1)
Tabla_cine['espacio_INCAA'] = Tabla_cine['espacio_INCAA'].fillna(0)
Tabla_cine['espacio_INCAA'] = Tabla_cine['espacio_INCAA'].astype("int")
Tabla_cine = Tabla_cine.groupby('Provincia').sum()
Tabla_cine['fecha_de_carga'] = current_date
