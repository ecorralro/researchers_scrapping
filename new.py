import requests
from bs4 import BeautifulSoup
import json
import time
import random

# URL base de la página
base_url = "https://accedacris.ulpgc.es"

def get_detalle(publicacion_url):
    """
    Extrae los detalles de una publicación específica desde su URL.
    
    Args:
        publicacion_url (str): URL de la publicación.

    Returns:
        dict: Un diccionario con los detalles extraídos de la publicación.
    """
    response = requests.get(publicacion_url)
    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.content, "html.parser")
    detalles = {}

    table = soup.find('table', class_='table itemDisplayTable')
    if table:
        cells = table.find_all('td')
        for i in range(0, len(cells) - 1, 2):
            label = cells[i].get_text(strip=True).replace(":", "")
            value = cells[i + 1]

            if value.find('br'):
                value = ' '.join(value.stripped_strings)
            elif value.find('a'):
                value = ' '.join([a.get_text(strip=True) + f" (Link: {a['href']})" for a in value.find_all('a')])
            else:
                value = value.get_text(strip=True)

            detalles[label] = value
    return detalles

def get_section_items(perfil_url, section_path, title_id):
    """
    Obtiene los elementos de una sección específica de un perfil de investigador.
    
    Args:
        perfil_url (str): URL del perfil del investigador.
        section_path (str): Ruta de la sección a extraer.
        title_id (str): Identificador del título en el HTML.

    Returns:
        list: Lista de diccionarios con los detalles de cada elemento extraído.
    """
    items_list = []
    current_url = f"{perfil_url}/{section_path}.html"
    response = requests.get(current_url)
    if response.status_code != 200:
        return items_list

    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all('div', id='item_fields')

    for item in items:
        titulo_element = item.find('div', id=title_id)
        if titulo_element and titulo_element.find('a'):
            titulo = titulo_element.find('a').text.strip()
            item_url = base_url + titulo_element.find('a')['href']
            detalles = get_detalle(item_url)
            items_list.append(detalles)

    return items_list

def get_publicaciones(perfil_url):
    """
    Obtiene la lista de publicaciones de un investigador.
    
    Args:
        perfil_url (str): URL del perfil del investigador.

    Returns:
        list: Lista de diccionarios con los detalles de cada publicación.
    """
    return get_section_items(perfil_url, 'publicaciones', 'dc.title')

def get_proyectos(perfil_url):
    """
    Obtiene la lista de proyectos de un investigador.
    
    Args:
        perfil_url (str): URL del perfil del investigador.

    Returns:
        list: Lista de diccionarios con los detalles de cada proyecto.
    """
    return get_section_items(perfil_url, 'projects', 'crisproject.title')

def get_tesis(perfil_url):
    """
    Obtiene la lista de tesis de un investigador.
    
    Args:
        perfil_url (str): URL del perfil del investigador.

    Returns:
        list: Lista de diccionarios con los detalles de cada tesis.
    """
    return get_section_items(perfil_url, 'tesis', 'dc.title')

def get_patentes(perfil_url):
    """
    Obtiene la lista de patentes de un investigador.
    
    Args:
        perfil_url (str): URL del perfil del investigador.

    Returns:
        list: Lista de diccionarios con los detalles de cada patente.
    """
    return get_section_items(perfil_url, 'patentes', 'dc.title')

# Inicialización de la extracción de datos
investigadores_lista = []
current_url = "/simple-search?query=&location=researcherprofiles"
response = requests.get(base_url + current_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    investigadores = soup.find_all('div', class_='item-fields')[:3] ### LÍMITE PRUEBA! QUITAR!!

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
            "Perfil": {"Email": email},
            "Publicaciones": publicaciones,
            "Proyectos": proyectos,
            "Tesis": tesis,
            "Patentes": patentes
        })

        time.sleep(random.uniform(0.5, 2))

# Guardar resultados en un archivo JSON
with open("investigadores_detalle.json", "w", encoding="utf-8") as file:
    json.dump(investigadores_lista, file, ensure_ascii=False, indent=4)

print(f"Extracción completa. Total investigadores extraídos: {len(investigadores_lista)}")
