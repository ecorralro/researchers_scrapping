################################################################################


import requests
from bs4 import BeautifulSoup
import json
import time


# URL base de la página
base_url = "https://accedacris.ulpgc.es"

# URL inicial de la página con investigadores
current_url = "/simple-search?query=&location=researcherprofiles"

# Lista para almacenar la información de los investigadores
investigadores_lista = []


def get_publicaciones():
    """
    Extrae todas las publicaciones del perfil navegando por todas las páginas.
    :param perfil_url: URL base del perfil del investigador.
    :return: Lista de diccionarios con los títulos de las publicaciones.
    """
    publicaciones = []
    startall = 0  # Índice de inicio para las publicaciones
    base_publicaciones_url = f"{perfil_url}/publicaciones.html?open=all&sort_byall=1&orderall=desc&rppall=20&etalall=-1&startall="

    while True:
        current_url = f"{base_publicaciones_url}{startall}"
        print(f"Accediendo a la URL de publicaciones: {current_url}")
        
        response = requests.get(current_url)
        if response.status_code != 200:
            print(f"Error al acceder a {current_url}")
            break
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extraer publicaciones de la página actual
        items = soup.find_all('div', id='item_fields')
        print(f"Publicaciones encontradas en esta página: {len(items)}")
        
        if not items:
            # No hay más publicaciones, salir del bucle
            print("No se encontraron más publicaciones. Finalizando paginación.")
            break

        for item in items:
            titulo_element = item.find('div', id='dc.title')
            if titulo_element and titulo_element.find('a'):
                titulo = titulo_element.find('a').text.strip()
                publicaciones.append({"Título": titulo})
            else:
                print("No se encontró título para un elemento.")
        
        # Avanzar al siguiente conjunto de publicaciones
        startall += 20  # Incrementar el índice para obtener la siguiente página de resultados

    return publicaciones





def get_proyectos():
    """
    Extrae todos los proyectos de investigación de la página actual.
    :param perfil_url: URL base del perfil del investigador.
    :return: Lista de diccionarios con los títulos de los proyectos.
    """
    proyectos = []
    current_url = f"{perfil_url}/projects.html"

    print(f"Accediendo a la URL de proyectos: {current_url}")
    response = requests.get(current_url)
    if response.status_code != 200:
        print(f"Error al acceder a {current_url}")
        return proyectos  # Retorna una lista vacía si hay error
    
    soup = BeautifulSoup(response.content, "html.parser")
    # Extraer proyectos de la página actual
    items = soup.find_all('div', id='item_fields')
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
    :param perfil_url: URL base del perfil del investigador.
    :return: Lista de diccionarios con los títulos de las tesis.
    """
    tesis = []
    current_url = f"{perfil_url}/tesis.html"

    print(f"Accediendo a la URL de tesis: {current_url}")
    response = requests.get(current_url)
    if response.status_code != 200:
        print(f"Error al acceder a {current_url}")
        return tesis  # Retorna una lista vacía si hay error
    
    soup = BeautifulSoup(response.content, "html.parser")
    # Extraer tesis de la página actual
    items = soup.find_all('div', id='item_fields')
    
    if not items:  # Verificar si no se encontraron tesis
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
    :param perfil_url: URL base del perfil del investigador.
    :return: Lista de diccionarios con los títulos y contribuyentes de las patentes.
    """
    patentes = []
    current_url = f"{perfil_url}/patentes.html"

    print(f"Accediendo a la URL de patentes: {current_url}")
    response = requests.get(current_url)
    if response.status_code != 200:
        print(f"Error al acceder a {current_url}")
        return patentes  # Retorna una lista vacía si hay error
    
    soup = BeautifulSoup(response.content, "html.parser")
    # Extraer patentes de la página actual
    items = soup.find_all('div', id='item_fields')
    
    if not items:  # Verificar si no se encontraron patentes
        print("No se encontraron patentes en esta página.")
        return patentes

    print(f"Patentes encontradas en esta página: {len(items)}")
    for item in items:
        # Extraer el título de la patente
        titulo_element = item.find('div', id='dc.title')
        titulo = titulo_element.find('a').text.strip() if titulo_element and titulo_element.find('a') else "Sin título"
        
        # Extraer los contribuyentes de la patente
        contribuyentes_element = item.find('div', id='dc.contributor.author')
        if contribuyentes_element:
            contribuyentes = [c.strip() for c in contribuyentes_element.text.split(';')]
        else:
            contribuyentes = ["Sin contribuyentes"]
        
        # Agregar la información a la lista
        patentes.append({
            "Título": titulo,
            "Contribuyentes": contribuyentes
        })

    return patentes



# Realizar la solicitud HTTP a la página actual
print(f"Extrayendo datos de la página: {base_url + current_url}")
response = requests.get(base_url + current_url)

# Verificar que la solicitud fue exitosa
if response.status_code != 200:
    print("Error al acceder a la página:", response.status_code)
else:
    # Parsear el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar todos los investigadores
    investigadores = soup.find_all('div', class_='item-fields')
    
    # Extraer la información de cada investigador
    for investigador in investigadores:
        nombre_elemento = investigador.find('div', id='crisrp.fullname')
        nombre = nombre_elemento.text.strip() if nombre_elemento else "N/A"
        
        perfil_url = (
            base_url + nombre_elemento.find('a')['href'].strip()
            if nombre_elemento and nombre_elemento.find('a')
            else "N/A"
        )
        
        categoria_elemento = investigador.find('div', id='crisrp.category')
        categoria = categoria_elemento.text.strip() if categoria_elemento else "N/A"
        
        print(f"Accediendo al perfil de {nombre}: {perfil_url}")
        
        # Acceder al perfil del investigador
        perfil_response = requests.get(perfil_url)
        
        if perfil_response.status_code != 200:
            print(f"Error al acceder al perfil de {nombre}: {perfil_response.status_code}")
            continue
        
        perfil_soup = BeautifulSoup(perfil_response.content, 'html.parser')
        

        ####################################
        # EXTRAER INFORMACION PERFIL
        email_element = perfil_soup.find('div', id='emailDiv')
        email = email_element.text.strip() if email_element else "N/A"

        departamento_element = perfil_soup.find('div', id='categoryDiv')
        departamento = departamento_element.text.strip() if departamento_element else "N/A"

        phone_element = perfil_soup.find('div', id='phoneDiv')
        phone = phone_element.text.strip() if phone_element else "N/A"

        knowledge_node_element = perfil_soup.find('div', id='ramaconocimientoDiv')
        knowledge_node = knowledge_node_element.text.strip() if knowledge_node_element else "N/A"

        knowledge_element = perfil_soup.find('div', id='areaDiv')
        knowledge = knowledge_element.text.strip() if knowledge_element else "N/A"

        # Nuevos elementos añadidos
        picture_element = perfil_soup.find('div', id='personalpictureDiv')
        picture = picture_element.text.strip() if picture_element else "N/A"

        affiliations_element = perfil_soup.find('div', id='deptDiv')
        if affiliations_element:
            # Extraer solo los textos de los enlaces dentro del contenedor
            affiliations = [a.text.strip() for a in affiliations_element.find_all('a')]
        else:
            affiliations = []



        field_element = perfil_soup.find('div', id='campocneaiDiv')
        field = field_element.text.strip() if field_element else "N/A"

        biography_element = perfil_soup.find('div', id='biographyDiv')
        biography = biography_element.text.strip() if biography_element else "N/A"

        personal_page_element = perfil_soup.find('div', id='otherpersonalsiteDiv')
        personal_page = personal_page_element.text.strip() if personal_page_element else "N/A"

        researchgate_element = perfil_soup.find('div', id='researchgateDiv')
        researchgate = researchgate_element.text.strip() if researchgate_element else "N/A"

        google_scholar_element = perfil_soup.find('div', id='GoogleScholarDiv')
        google_scholar = google_scholar_element.text.strip() if google_scholar_element else "N/A"

        orcid_element = perfil_soup.find('div', id='orcidDiv')
        orcid = orcid_element.text.strip() if orcid_element else "N/A"

        scopus_element = perfil_soup.find('div', id='scopusidDiv')
        scopus = scopus_element.text.strip() if scopus_element else "N/A"

        researcher_id_element = perfil_soup.find('div', id='researcheridDiv')
        researcher_id = researcher_id_element.text.strip() if researcher_id_element else "N/A"

        dialnet_id_element = perfil_soup.find('div', id='dialnetidDiv')
        dialnet_id = dialnet_id_element.text.strip() if dialnet_id_element else "N/A"

        ####################################
        # EXTRAER INFORMACION ADICIONAL
        publicaciones = get_publicaciones()

        proyectos = get_proyectos()

        tesis = get_tesis()
        
        patentes = get_patentes()

        # Agregar la información del investigador a la lista
        investigadores_lista.append({
            "Nombre": nombre,
            "URL del perfil": perfil_url,
            "Perfil": {
                "Categoría": categoria,
                "Email": email,
                "Departamento": departamento,
                "Telefono": phone,
                "Area de Conocimiento": knowledge,
                "Rama del Conocimiento": knowledge_node,
                "Fotografía": picture,
                "Afiliaciones": affiliations,
                "Campo CNEAI": field,
                "Biografía": biography,
                "Página Personal": personal_page,
                "ResearchGate": researchgate,
                "Google Scholar": google_scholar,
                "ORCID": orcid,
                "Scopus ID": scopus,
                "Researcher ID": researcher_id,
                "Dialnet ID": dialnet_id
            },
            "Publicaciones": publicaciones,
            "Tesis": tesis,
            "Proyectos": proyectos,
            "Patentes": patentes
        })

        
        # Agregar un pequeño retraso entre solicitudes para evitar ser bloqueado
        time.sleep(1)

# Guardar la información de los investigadores en un archivo JSON
with open("investigadores_detalle.json", "w", encoding="utf-8") as file:
    json.dump(investigadores_lista, file, ensure_ascii=False, indent=4)

print(f"Extracción completa. Datos almacenados en 'investigadores_detalle.json'. Total investigadores extraídos: {len(investigadores_lista)}")
