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
    return {
        "Título": detalles.get("Título", "Sin título"),
        "Resumen": detalles.get("Resumen", "Sin resumen"),
        "URI": detalles.get("URI", "Sin URI"),
        "ISSN": detalles.get("ISSN", "Sin ISSN"),
        "DOI": detalles.get("DOI", "Sin DOI")
    }

def get_publicaciones(perfil_url):
    """
    Extrae publicaciones asociadas con un perfil desde su URL.
    """
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
                detalle = get_publicacion_detalle(publicacion_url)
                publicaciones.append(detalle)

        startall += 20

    return publicaciones

response = requests.get(base_url + current_url)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    investigadores = soup.find_all('div', class_='item-fields')[:1]  # Limita la iteración para pruebas
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

        investigadores_lista.append({
            "Nombre": nombre,
            "URL del perfil": perfil_url,
            "Perfil": {
                "Email": email
            },
            "Publicaciones": publicaciones,
        })
        time.sleep(1)

with open("investigadores_detalle.json", "w", encoding="utf-8") as file:
    json.dump(investigadores_lista, file, ensure_ascii=False, indent=4)

print(f"Extracción completa. Total investigadores extraídos: {len(investigadores_lista)}")


# import requests
# from bs4 import BeautifulSoup
# import json

# def extract_table_data(url, output_file):
#     """
#     Extrae datos de una tabla con etiquetas y valores consecutivos y los almacena en un archivo JSON.

#     :param url: URL de la página web a analizar.
#     :param output_file: Ruta del archivo JSON donde se guardarán los datos.
#     :return: None
#     """
#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Buscar la tabla con la clase específica
#         table = soup.find('table', class_='table itemDisplayTable')
#         if table:
#             data = {}
#             cells = table.find_all('td')  # Encontrar todos los elementos <td>
#             for i in range(0, len(cells) - 1, 2):  # Iterar en pares (etiqueta, valor)
#                 label = cells[i].get_text(strip=True).replace(":", "")
#                 value = cells[i + 1]

#                 # Procesar contenido del valor
#                 if value.find('br'):  # Si hay etiquetas <br>, combinarlas en una sola línea
#                     value = ' '.join(value.stripped_strings)
#                 elif value.find('a'):  # Si hay enlaces, extraer texto y href
#                     value = ' '.join([a.get_text(strip=True) + f" (Link: {a['href']})" for a in value.find_all('a')])
#                 else:  # Si no, extraer texto limpio
#                     value = value.get_text(strip=True)

#                 data[label] = value

#             # Extraer y mostrar el campo "Título"
#             title = data.get("Título", "No disponible")
#             print(f"Título: {title}")

#             # Guardar los datos en un archivo JSON
#             with open(output_file, 'w', encoding='utf-8') as json_file:
#                 json.dump(data, json_file, ensure_ascii=False, indent=4)

#             print(f"Datos guardados en {output_file}")
#         else:
#             print("No se encontró la tabla especificada en la página.")
#     else:
#         print(f"Error al acceder a la página: {response.status_code}")

# # Ejemplo de uso
# url = "https://accedacris.ulpgc.es/handle/10553/73666"
# output_file = "output_data.json"
# extract_table_data(url, output_file)





