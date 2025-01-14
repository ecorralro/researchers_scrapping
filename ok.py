import requests
from bs4 import BeautifulSoup
import json
import time

# URL base de la página
base_url = "https://accedacris.ulpgc.es"

# URL inicial de la página con investigadores
current_url = "/simple-search?query=&location=researcherprofiles"

investigadores_lista = []

def get_detalle(publicacion_url):
    """
    Extrae detalles de una publicación específica desde su URL.
    """
    response = requests.get(publicacion_url)
    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.content, "html.parser")
    detalles = {}

    # Buscar la tabla con la clase específica
    table = soup.find('table', class_='table itemDisplayTable')
    if table:
        cells = table.find_all('td')  # Encontrar todos los <td>
        for i in range(0, len(cells) - 1, 2):  # Iterar en pares (etiqueta, valor)
            label = cells[i].get_text(strip=True).replace(":", "")
            value = cells[i + 1]

            # Procesar contenido del valor
            if value.find('br'):  # Si hay etiquetas <br>, combinarlas en una sola línea
                value = ' '.join(value.stripped_strings)
            elif value.find('a'):  # Si hay enlaces, extraer texto y href
                value = ' '.join([a.get_text(strip=True) + f" (Link: {a['href']})" for a in value.find_all('a')])
            else:  # Si no, extraer texto limpio
                value = value.get_text(strip=True)

            detalles[label] = value

    # Devolver el diccionario con la información extraída
    return detalles

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
                detalle = get_detalle(publicacion_url)
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
            proyecto_url = base_url + titulo_element.find('a')['href']
            detalles = get_detalle(proyecto_url)
            for detalle in detalles:
                proyectos.append(detalle)
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
            tesis_url = base_url + titulo_element.find('a')['href']
            detalles = get_detalle(tesis_url)
            for detalle in detalles:
                tesis.append(detalle)
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
