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
    Extrae todas las publicaciones del perfil, incluyendo título, descripción, fecha de publicación, 
    autor, categorías y número de comentarios.
    
    :param perfil_url: URL base del perfil del investigador.
    :return: Lista de diccionarios con los detalles de las publicaciones.
    """
    publicaciones = []
    startall = 0  # Índice de inicio para las publicaciones
    base_publicaciones_url = f"{perfil_url}/publicaciones.html?open=all&sort_byall=1&orderall=desc&rppall=20&etalall=-1&startall="

    while True:
        current_url = f"{base_publicaciones_url}{startall}"
        print(f"Accediendo a la URL de publicaciones: {current_url}")

        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error al acceder a {current_url}: {e}")
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
            # Extracción con validación de presencia de elementos
            titulo_element = item.find('div', id='dc.title')
            titulo = titulo_element.find('a').text.strip() if titulo_element and titulo_element.find('a') else None

            descripcion_element = item.find('div', id='dc.description')
            descripcion = descripcion_element.text.strip() if descripcion_element else None

            fecha_element = item.find('div', id='dc.date')
            fecha_publicacion = fecha_element.text.strip() if fecha_element else None

            autor_element = item.find('div', id='dc.contributor.author')
            autor = autor_element.text.strip() if autor_element else None

            categorias_element = item.find('div', id='dc.subject')
            categorias = categorias_element.text.strip() if categorias_element else None

            comentarios_element = item.find('div', id='comments')
            comentarios = comentarios_element.text.strip() if comentarios_element else "0"

            # Validación de datos extraídos
            if titulo and len(titulo) > 5:  # Validación básica de texto mínimo
                publicacion = {
                    "Nombre": nombre,
                    "Título": titulo,
                    "Descripción": descripcion,
                    "Fecha de Publicación": fecha_publicacion,
                    "Autor": autor,
                    "Categorías": categorias,
                    "Número de Comentarios": comentarios
                }
                publicaciones.append(publicacion)
            else:
                print("Publicación ignorada por datos insuficientes.")

        # Avanzar al siguiente conjunto de publicaciones
        startall += 20

    # Guardar los resultados en un archivo JSON
    with open('publicaciones.json', 'w', encoding='utf-8') as json_file:
        json.dump(publicaciones, json_file, ensure_ascii=False, indent=4)

    print("Extracción completada y datos guardados en 'publicaciones.json'")
    return publicaciones

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

publicaciones = get_publicaciones()