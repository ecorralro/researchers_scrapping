import requests
from bs4 import BeautifulSoup
import json
import time

# URL base de la página
base_url = "https://accedacris.ulpgc.es"

# URL inicial de la página con investigadores
current_url = "/simple-search?query=&location=researcherprofiles"

investigadores_lista = []

def get_publicacion_detalle(publicacion_url):
    response = requests.get(publicacion_url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    detalles = []  # Usamos una lista para almacenar todas las entradas

    filas = soup.find_all('tr')  # Encuentra todas las filas de metadatos
    
    for fila in filas:
        etiqueta_element = fila.find('td', class_='metadataFieldLabel')
        valor_element = fila.find('td', class_='metadataFieldValue')
        
        if etiqueta_element and valor_element:
            etiqueta = etiqueta_element.get_text(strip=True).replace(":", "").strip()
            
            # Si el valor es un enlace, extraer el href, de lo contrario, extraer texto
            if valor_element.find('a'):
                valor = valor_element.find('a')['href']
            else:
                valor = valor_element.get_text(strip=True)
            
            # Agregar cada entrada como un diccionario individual a la lista
            detalles.append({etiqueta: valor})

    return detalles






# def get_publicacion_detalle(publicacion_url):
#     response = requests.get(publicacion_url)
#     if response.status_code != 200:
#         return {}

#     soup = BeautifulSoup(response.content, "html.parser")

#     # Diccionario para almacenar los detalles
#     detalles = {}

#     # Buscar todas las filas de metadatos
#     filas = soup.find_all('tr')

#     for fila in filas:
#         etiqueta_element = fila.find('td', class_='metadataFieldLabel')
#         valor_element = fila.find('td', class_='metadataFieldValue')

#         if etiqueta_element and valor_element:
#             etiqueta = etiqueta_element.get_text(strip=True).replace(':', '').strip()
#             if valor_element.find('a'):
#                 valor = valor_element.find('a').get('href')
#             else:
#                 valor = valor_element.get_text(strip=True)
#             detalles[etiqueta] = valor

#     return detalles

def get_publicaciones(perfil_url):
    publicaciones = []
    startall = 0
    base_publicaciones_url = f"{perfil_url}/publicaciones.html?open=all&sort_byall=1&orderall=desc&rppall=20&etalall=-1&startall="

    while True:
        current_url = f"{base_publicaciones_url}{startall}"
        response = requests.get(current_url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, "html.parser")
        items = soup.find_all('div', id='item_fields')

        if not items:
            break

        for item in items:
            titulo_element = item.find('div', id='dc.title')
            if titulo_element and titulo_element.find('a'):
                titulo = titulo_element.find('a').text.strip()
                publicacion_url = base_url + titulo_element.find('a')['href']
                detalles = get_publicacion_detalle(publicacion_url)
                for detalle in detalles:
                    publicaciones.append(detalle) 

        startall += 20

    return publicaciones

def get_proyectos(perfil_url):
    proyectos = []
    current_url = f"{perfil_url}/projects.html"
    response = requests.get(current_url)
    if response.status_code != 200:
        return proyectos  
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all('div', id='item_fields')
    for item in items:
        titulo_element = item.find('div', id='crisproject.title')
        if titulo_element and titulo_element.find('a'):
            titulo = titulo_element.find('a').text.strip()
            proyectos.append({"Título": titulo})
    return proyectos

def get_tesis(perfil_url):
    tesis = []
    current_url = f"{perfil_url}/tesis.html"
    response = requests.get(current_url)
    if response.status_code != 200:
        return tesis
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all('div', id='item_fields')
    for item in items:
        titulo_element = item.find('div', id='dc.title')
        if titulo_element and titulo_element.find('a'):
            titulo = titulo_element.find('a').text.strip()
            tesis.append({"Título": titulo})
    return tesis

def get_patentes(perfil_url):
    patentes = []
    current_url = f"{perfil_url}/patentes.html"
    response = requests.get(current_url)
    if response.status_code != 200:
        return patentes
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all('div', id='item_fields')
    for item in items:
        titulo_element = item.find('div', id='dc.title')
        titulo = titulo_element.find('a').text.strip() if titulo_element and titulo_element.find('a') else "Sin título"
        contribuyentes_element = item.find('div', id='dc.contributor.author')
        contribuyentes = [c.strip() for c in contribuyentes_element.text.split(';')] if contribuyentes_element else ["Sin contribuyentes"]
        patentes.append({"Título": titulo, "Contribuyentes": contribuyentes})
    return patentes

response = requests.get(base_url + current_url)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    investigadores = soup.find_all('div', class_='item-fields')[:1] ########### LIMITO ITERACIÓN(QUITAR!!)
    for investigador in investigadores:
        nombre_elemento = investigador.find('div', id='crisrp.fullname')
        nombre = nombre_elemento.text.strip() if nombre_elemento else "N/A"
        perfil_url = base_url + nombre_elemento.find('a')['href'].strip() if nombre_elemento and nombre_elemento.find('a') else "N/A"

        perfil_response = requests.get(perfil_url)
        if perfil_response.status_code != 200:
            continue

        perfil_soup = BeautifulSoup(perfil_response.content, 'html.parser')
        email_element = perfil_soup.find('div', id='emailDiv')
        email = email_element.text.strip() if email_element else "N/A"

        publicaciones = get_publicaciones(perfil_url)
        proyectos = get_proyectos(perfil_url)
        tesis = get_tesis(perfil_url)
        patentes = get_patentes(perfil_url)

        investigadores_lista.append({
            "Nombre": nombre,
            "URL del perfil": perfil_url,
            "Perfil": {
                "Email": email
            },
            "Publicaciones": publicaciones,
            "Proyectos": proyectos,
            "Tesis": tesis,
            "Patentes": patentes
        })
        time.sleep(1)

with open("investigadores_detalle.json", "w", encoding="utf-8") as file:
    json.dump(investigadores_lista, file, ensure_ascii=False, indent=4)

print(f"Extracción completa. Total investigadores extraídos: {len(investigadores_lista)}")
