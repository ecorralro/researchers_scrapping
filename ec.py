import json
from pymongo import MongoClient, errors

# Conexión a la base de datos MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['universidad']

# Colecciones
collections = {
    'investigadores': db['investigadores'],
    'publicaciones': db['publicaciones'],
    'proyectos': db['proyectos'],
    'tesis': db['tesis'],
    'patentes': db['patentes']
}

# Crear índices para optimizar las búsquedas
for collection in collections.values():
    collection.create_index("_id")

def insertar_o_actualizar(coleccion, documento):
    try:
        coleccion.update_one({"_id": documento["_id"]}, {"$set": documento}, upsert=True)
    except errors.DuplicateKeyError:
        print(f"Documento duplicado detectado: {documento['_id']}")

def procesar_datos(data):
    for item in data:
        investigador = {
            "_id": item.get("URL del perfil"),
            "nombre": item.get("Nombre"),
            "email": item.get("Perfil", {}).get("Email")
        }
        insertar_o_actualizar(collections['investigadores'], investigador)

        for pub in item.get("Publicaciones", []):
            publicacion = {
                "_id": pub.get("URI"),
                "titulo": pub.get("Título"),
                "autores": pub.get("Autores/as"),
                "clasificacion_unesco": pub.get("Clasificación UNESCO"),
                "palabras_clave": pub.get("Palabras clave"),
                "fecha_publicacion": pub.get("Fecha de publicación"),
                "investigador_id": item.get("URL del perfil")
            }
            insertar_o_actualizar(collections['publicaciones'], publicacion)

        for proy in item.get("Proyectos", []):
            proyecto = {
                "_id": proy.get("URI", "Desconocido"),
                "titulo": proy.get("Título"),
                "fecha_inicio": proy.get("Fecha de inicio"),
                "fecha_fin": proy.get("Fecha de fin"),
                "descripcion": proy.get("Descripción"),
                "clasificacion_unesco": proy.get("Clasificación UNESCO"),
                "investigador_id": item.get("URL del perfil")
            }
            insertar_o_actualizar(collections['proyectos'], proyecto)

        for tesis in item.get("Tesis", []):
            tesis_doc = {
                "_id": tesis.get("URI"),
                "titulo": tesis.get("Título"),
                "autores": tesis.get("Autores/as"),
                "clasificacion_unesco": tesis.get("Clasificación UNESCO"),
                "fecha_publicacion": tesis.get("Fecha de publicación"),
                "investigador_id": item.get("URL del perfil")
            }
            insertar_o_actualizar(collections['tesis'], tesis_doc)

        for patente in item.get("Patentes", []):
            patente_doc = {
                "_id": patente.get("URI", "Desconocido"),
                **patente,
                "investigador_id": item.get("URL del perfil")
            }
            insertar_o_actualizar(collections['patentes'], patente_doc)

# Ejemplo de ejecución
def main():
    try:
        with open('data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            procesar_datos(data)
            print("Datos importados exitosamente a MongoDB.")
    except FileNotFoundError:
        print("El archivo data.json no fue encontrado.")
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")

if __name__ == "__main__":
    main()
