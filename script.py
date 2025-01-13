import requests
from bs4 import BeautifulSoup
import json
import time

# URL base de la página
base_url = "https://accedacris.ulpgc.es"

# Lista para almacenar la información de los investigadores
investigadores_lista = []


def get_publicaciones():
    """
    Extrae todas las publicaciones del perfil navegando por todas las páginas.
    :return: Lista de diccionarios con los títulos de las publicaciones.
    """
    publicaciones = []
    startall = 0  # Índice de inicio para las publicaciones
    base_publicaciones_url = f"{perfil_url}/publicaciones.html?open=all&sort_byall=1&orderall=desc&rppall=20&etalall=-1&startall="

    while True:
        current_url = f"{base_publicaciones_url}{startall}"
        print(f"Accediendo a la página de publicaciones: {startall // 20 + 1} ({current_url})")
        
        response = requests.get(current_url)
        if response.status_code != 200:
            print(f"Error al acceder a {current_url}")
            break
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        items = soup.find_all('div', id='item_fields')
        print(f"Publicaciones encontradas en esta página: {len(items)}")
        
        if not items:
            print("No se encontraron más publicaciones. Finalizando paginación.")
            break

        for item in items:
            titulo_element = item.find('div', id='dc.title')
            if titulo_element and titulo_element.find('a'):
                titulo = titulo_element.find('a').text.strip()
                publicaciones.append({"Título": titulo})
            else:
                print("No se encontró título para un elemento.")
        
        startall += 20  # Avanzar al siguiente conjunto de publicaciones

    return publicaciones


def get_proyectos():
    """
    Extrae todos los proyectos de investigación de la página actual.
    :return: Lista de diccionarios con los títulos de los proyectos.
    """
    proyectos = []
    current_url = f"{perfil_url}/projects.html"

    print(f"Accediendo a la página de proyectos: {current_url}")
    response = requests.get(current_url)
    if response.status_code != 200:
        print(f"Error al acceder a {current_url}")
        return proyectos
    
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all('div', id='item_fields')
    
    if not items:
        print("No se encontraron proyectos en esta página.")
        return proyectos

    print(f"Proyectos encontrados en esta página: {len(items)}")
    for item in items:
        titulo_element = item.find('div', id='crisproject.title')
        if titulo_element and titulo_element.find('a'):
            titulo = titulo_element.find('a').text.strip()
            proyectos.append({"Título": titulo})
        else:
            print("No se encontró título para un proyecto.")

    return proyectos


def get_tesis():
    """
    Extrae todas las tesis de investigación de la página actual.
    :return: Lista de diccionarios con los títulos de las tesis.
    """
    tesis = []
    current_url = f"{perfil_url}/tesis.html"

    print(f"Accediendo a la página de tesis: {current_url}")
    response = requests.get(current_url)
    if response.status_code != 200:
        print(f"Error al acceder a {current_url}")
        return tesis
    
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all('div', id='item_fields')
    
    if not items:
        print("No se encontraron tesis en esta página.")
        return tesis

    print(f"Tesis encontradas en esta página: {len(items)}")
    for item in items:
        titulo_element = item.find('div', id='dc.title')
        if titulo_element and titulo_element.find('a'):
            titulo = titulo_element.find('a').text.strip()
            tesis.append({"Título": titulo})
        else:
            print("No se encontró título para una tesis.")

    return tesis


def get_patentes():
    """
    Extrae todas las patentes de investigación de la página actual.
    :return: Lista de diccionarios con los títulos y contribuyentes de las patentes.
    """
    patentes = []
    current_url = f"{perfil_url}/patentes.html"

    print(f"Accediendo a la página de patentes: {current_url}")
    response = requests.get(current_url)
    if response.status_code != 200:
        print(f"Error al acceder a {current_url}")
        return patentes
    
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all('div', id='item_fields')
    
    if not items:
        print("No se encontraron patentes en esta página.")
        return patentes

    print(f"Patentes encontradas en esta página: {len(items)}")
    for item in items:
        titulo_element = item.find('div', id='dc.title')
        titulo = titulo_element.find('a').text.strip() if titulo_element and titulo_element.find('a') else "Sin título"
        
        contribuyentes_element = item.find('div', id='dc.contributor.author')
        if contribuyentes_element:
            contribuyentes = [c.strip() for c in contribuyentes_element.text.split(';')]
        else:
            contribuyentes = ["Sin contribuyentes"]
        
        patentes.append({"Título": titulo, "Contribuyentes": contribuyentes})

    return patentes


# Realizar la solicitud HTTP para cada página de investigadores
start = 0  # Índice de paginación
rpp = 50  # Investigadores por página
page_number = 1  # Contador de páginas

while True:
    current_url = f"{base_url}/simple-search?query=&location=researcherprofiles&sort_by=crisrp.fullName_sort&order=asc&rpp={rpp}&etal=5&start={start}"
    print(f"Accediendo a la página {page_number}: {current_url}")
    response = requests.get(current_url)

    if response.status_code != 200:
        print("Error al acceder a la página:", response.status_code)
        break

    soup = BeautifulSoup(response.content, 'html.parser')
    investigadores = soup.find_all('div', class_='item-fields')

    if not investigadores:
        print("No se encontraron más investigadores. Finalizando paginación.")
        break

    for investigador in investigadores:
        nombre_elemento = investigador.find('div', id='crisrp.fullname')
        nombre = nombre_elemento.text.strip() if nombre_elemento else "N/A"
        
        perfil_url = (
            base_url + nombre_elemento.find('a')['href'].strip()
            if nombre_elemento and nombre_elemento.find('a')
            else "N/A"
        )
        
        print(f"Accediendo al perfil de {nombre}: {perfil_url}")
        
        publicaciones = get_publicaciones()
        proyectos = get_proyectos()
        tesis = get_tesis()
        patentes = get_patentes()

        investigadores_lista.append({
            "Nombre": nombre,
            "URL del perfil": perfil_url,
            "Publicaciones": publicaciones,
            "Tesis": tesis,
            "Proyectos": proyectos,
            "Patentes": patentes
        })

        time.sleep(1)

    start += rpp
    page_number += 1

# Guardar la información en un archivo JSON
with open("investigadores_detalle.json", "w", encoding="utf-8") as file:
    json.dump(investigadores_lista, file, ensure_ascii=False, indent=4)

print(f"Extracción completa. Datos almacenados en 'investigadores_detalle.json'. Total investigadores extraídos: {len(investigadores_lista)}")
