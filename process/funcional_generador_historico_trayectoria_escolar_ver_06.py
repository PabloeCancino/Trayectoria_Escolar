# -*- coding: utf-8 -*-
"""Funcional_Generador_historico_trayectoria_escolar_ver_06.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1unkBj1j7HNkfhBExalWSFwsY7ppu4SfP
"""

pip install Faker

!pip install pandas pymongo dnspython
import pymongo
from pymongo import MongoClient

# -*- coding: utf-8 -*-
"""
Este script genera datos históricos de trayectorias escolares con una perspectiva institucional.

Requiere la biblioteca Faker para generar datos ficticios. Favor de asegurarse de instalarla ejecutando:

pip install Faker

Este script asume que los archivos CSV necesarios están disponibles localmente o en una URL accesible.
"""

import pandas as pd
import numpy as np
import random as rnd
import json
from datetime import datetime
import hashlib
import subprocess
import sys


# Importar la biblioteca de Google Colab sólo si se está ejecutando en Colab
try:
    from google.colab import files
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# Asegurarse de que Faker esté instalado, si no, instalarlo
try:
    from faker import Faker
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'faker'])
    from faker import Faker

fake = Faker('es_MX')

# Función para importar datos desde archivos CSV
def importar_datos(url_o_path):
    try:
        return pd.read_csv(url_o_path)
    except Exception as e:
        print(f"Error al importar datos desde {url_o_path}: {e}")
        return pd.DataFrame()

# Importar bases de datos
mapa_curricular = importar_datos("https://raw.githubusercontent.com/PabloeCancino/Trayectoria_Escolar/master/mapa_curricular_generador.csv")
Ingreso_Hist = importar_datos("https://raw.githubusercontent.com/PabloeCancino/Trayectoria_Escolar/master/Historico_ingreso_generador.csv")
nomFem = importar_datos("https://raw.githubusercontent.com/PabloeCancino/Trayectoria_Escolar/master/raw/nomFem.csv")
nomMasc = importar_datos("https://raw.githubusercontent.com/PabloeCancino/Trayectoria_Escolar/master/raw/nomMasc.csv")

# Extraer los valores únicos de 'U_de_Aprend' para usarlos como encabezados de columna
u_de_aprend_encabezados = mapa_curricular["U_de_Aprend"].unique()

# Diccionario de mapeo para relacionar U_de_Aprend con ColCurr
ua_semestre = pd.Series(mapa_curricular['semestre'].values, index=mapa_curricular['U_de_Aprend']).to_dict()

# DataFrame principal inicializado
df_principal = pd.DataFrame()

# Funciones necesarias
def generar_numeros_unicos(num, digitos=4):
    """Genera un conjunto de números únicos de longitud especificada."""
    numeros = set()
    while len(numeros) < num:
        nuevo_numero = rnd.randint(0, 10**digitos)
        numeros.add(f"{nuevo_numero:0{digitos}d}")
    return list(numeros)

def generar_estructura_calificaciones(perfil, ingreso, semestre):
    """Genera una estructura de calificaciones basada en el perfil, año de ingreso y columna curricular."""
    estructura = []

    oportunidad, i = 1, 1
    while oportunidad < 7:
        calificación_obtenida = generar_calif_aleatoria_por_perfil(perfil) if oportunidad == i else None
        fecha_generada = generar_fecha(ingreso, semestre, oportunidad) if oportunidad == i else None
        docente = fake.name() if oportunidad == i else None

        estructura.append({
            'oport': oportunidad,
            'calif': calificación_obtenida,
            'fecha': fecha_generada,
            'docente': docente,
            'acta': rnd.randint(100000,999999)
        })

        # Si la calificación es menor a 60 y aún hay oportunidades disponibles, continuar el ciclo
        if calificación_obtenida is not None and calificación_obtenida < 60:
            oportunidad += 1
            i += 1
        else:
            break

    return estructura


def generar_calif_aleatoria_por_perfil(perfil):
    """Genera una calificación aleatoria basada en el perfil del estudiante."""
    rangos = {
        'A': (90, 98),
        'MA': (83, 90),
        'MB': (73, 83),
        'B': (60, 73)
    }
    media, maximo = rangos.get(perfil, (0, 0))
    desviacion = rnd.randint(8, 11)
    calif = round(rnd.normalvariate(media, desviacion))
    return max(0, min(calif, 100))

def generar_fecha(ingreso, semestre, oportunidad):
    """Genera una fecha de examen basada en el año de ingreso, semestre y oportunidad de examen."""
    ajustes_año = {
        1: {1: 0, 2: 1, 3: 1, 4: 1, 5: 2},
        2: {1: 1, 2: 1, 3: 1, 4: 1, 5: 2},
        3: {1: 1, 2: 2, 3: 2, 4: 2, 5: 3},
        4: {1: 2, 2: 2, 3: 2, 4: 2, 5: 3},
        5: {1: 2, 2: 3, 3: 3, 4: 3, 5: 4},
        6: {1: 3, 2: 3, 3: 3, 4: 3, 5: 4},
        7: {1: 3, 2: 4, 3: 4, 4: 4, 5: 5},
        8: {1: 4, 2: 4, 3: 4, 4: 4, 5: 5},
    }
    año_ajustado = ingreso + ajustes_año.get(semestre, {1: 0}).get(oportunidad, 0)

    ajustes_mes = {
        1: {1: 12, 2: 1, 3: 2, 4: 12, 5: 1},
        2: {1: 6, 2: 7, 3: 8, 4: 12, 5: 1},
        3: {1: 12, 2: 1, 3: 2, 4: 12, 5: 1},
        4: {1: 6, 2: 7, 3: 8, 4: 12, 5: 1},
        5: {1: 12, 2: 1, 3: 2, 4: 12, 5: 1},
        6: {1: 6, 2: 7, 3: 8, 4: 12, 5: 1},
        7: {1: 12, 2: 1, 3: 2, 4: 12, 5: 1},
        8: {1: 6, 2: 7, 3: 8, 4: 12, 5: 1},
    }
    mes_ajustado = ajustes_mes.get(semestre, {1: 12}).get(oportunidad, 11)

    ajustes_dia = {
        1: {1: 15, 2: 28, 3: 15, 4: 15, 5: 28},
        2: {1: 25, 2: 28, 3: 15, 4: 15, 5: 28},
        3: {1: 15, 2: 28, 3: 15, 4: 15, 5: 28},
        4: {1: 25, 2: 28, 3: 15, 4: 15, 5: 28},
        5: {1: 15, 2: 28, 3: 15, 4: 15, 5: 28},
        6: {1: 25, 2: 28, 3: 15, 4: 15, 5: 28},
        7: {1: 15, 2: 28, 3: 15, 4: 15, 5: 28},
        8: {1: 25, 2: 28, 3: 15, 4: 15, 5: 28},
    }
    dia_ajustado = ajustes_dia.get(semestre, {1: 0}).get(oportunidad, 20)

    if mes_ajustado < 1 or mes_ajustado > 12:
      raise ValueError(f"Mes ajustado inválido: {mes_ajustado}")

    if dia_ajustado < 1 or dia_ajustado > 31:
      raise ValueError(f"Día ajustado inválido: {dia_ajustado}")

    fecha = datetime(año_ajustado, mes_ajustado, dia_ajustado)
    return fecha.strftime('%Y-%m-%d')

def generar_oid():
    """Genera un pseudo ObjectId como en MongoDB."""
    return hashlib.md5(str(rnd.random()).encode()).hexdigest()[:24]

def obtener_genero(ingresos):
    sexoRnd = [fake.random_element(elements=('Masc', 'Fem')) for _ in range(ingresos)]
    return sexoRnd

def obtener_nombre_por_genero(sexoRndList):
    nombres = []
    for sexoRnd in sexoRndList:
        if sexoRnd == 'Fem':
            nombres.append(rnd.choice(nomFem['nombre'].tolist()) + ' ' + rnd.choice(nomFem['nombre'].tolist()))
        elif sexoRnd == 'Masc':
            nombres.append(rnd.choice(nomMasc['nombre'].tolist()) + ' ' + rnd.choice(nomMasc['nombre'].tolist()))
        else:
            nombres.append("Género no especificado correctamente")
    return nombres


# Bucle principal para generar datos
for año, ingresos in zip(ingreso_Hist['generacion'], ingreso_Hist['nvo_ingreso']):
    numeros_unicos = generar_numeros_unicos(ingresos)
    perfiles = ['A', 'MA', 'MB', 'B'] * (ingresos // 4 + 1)
    rnd.shuffle(perfiles)
    generos = obtener_genero(ingresos)
    nombres = obtener_nombre_por_genero(generos)

    df_temp = pd.DataFrame({
        #'_id': [generar_oid() for _ in range(ingresos)],
        'matricula': [f"{año}{num}" for num in numeros_unicos],
        'ingreso': [año] * ingresos,
        'nombre': nombres,
        'apellidos': [fake.last_name() + ' ' + fake.last_name() for _ in range(ingresos)],
        'perfil': perfiles[:ingresos],
        'sexo': generos,
        'regular': [fake.boolean(chance_of_getting_true=75) for _ in range(ingresos)],
        'telefono': [[fake.phone_number(), fake.phone_number()] for _ in range(ingresos)]
    })

    for ua in u_de_aprend_encabezados:
        semestre_actual = ua_semestre[ua]
        df_temp[ua] = [generar_estructura_calificaciones(perfil, año, semestre_actual) for perfil in df_temp['perfil']]

    df_principal = pd.concat([df_principal, df_temp], ignore_index=True)

# Guardar o procesar df_principal según sea necesario
# df_principal

# Función personalizada para ajustar la serialización de '_id' y otros campos
def my_converter(o):
    if isinstance(o, np.generic):
        return o.item()

# Convertir el DataFrame a JSON con el formato deseado
resultado_json = df_principal.to_json(orient="records", default_handler=my_converter)

# Modificar la cadena JSON para ajustar el formato de '_id'
resultado_json_modificado = resultado_json.replace('"_id":', '"_id": {"$oid":')

# Guardar el resultado en un archivo
with open("db_historico_trayectoria_escolar.json", "w") as archivo_json:
    archivo_json.write(resultado_json_modificado)

# Descargar el archivo si se ejecuta en un entorno que lo permite, como Google Colab
if IN_COLAB:
    files.download("db_historico_trayectoria_escolar.json")

# Guardar los resultados en un archivo json
df_principal.to_json("db_historico_trayectoria_escolar.json", orient="records")

# Descargar el archivo de texto
files.download("db_historico_trayectoria_escolar.json")

############ Descargar csv ##########################################

# Guardar los resultados en un archivo txt
df_principal.to_csv("db_historico_trayectoria_escolar.csv", sep=',', index=False, encoding='utf-8')

# Descargar el archivo de texto
files.download("db_historico_trayectoria_escolar.csv")
