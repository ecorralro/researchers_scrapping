# from langchain_openai import ChatOpenAI
# from browser_use import Agent
# import asyncio

# base_url = "https://accedacris.ulpgc.es/simple-search?query=&location=researcherprofiles"
# async def main():
#     agent = Agent(
#         task=(
#             f"Go to {base_url}, extract the names of all researchers visible on the page. "
#             "If the page contains pagination, navigate through all pages and extract the names "
#             "from each one. Ensure no names are missed."
#         ),
#         llm=ChatOpenAI(model="gpt-4o-mini"),
#     )
#     result = await agent.run()
#     print(result)

# asyncio.run(main())



from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
import json

base_url = "https://accedacris.ulpgc.es/simple-search?query=&location=researcherprofiles"

async def main():
    # Crear el agente
    agent = Agent(
        task=(
            f"Go to {base_url}, extract the names of the first two researchers visible on the page. "
            "Only return the names of the first two researchers. Ensure no duplicates."
        ),
        llm=ChatOpenAI(model="gpt-4o"),
    )

    # Ejecutar la tarea del agente
    try:
        result = await agent.run()
        print("-"*100)
        # Extraer los datos de los resultados
        extracted_data = []
        if hasattr(result, "results"):
            for action_result in result.results:
                if hasattr(action_result, "extracted_content") and action_result.extracted_content:
                    extracted_data.append(action_result.extracted_content)

        # Limitar a los dos primeros investigadores
        limited_data = extracted_data[:2]

        # Guardar los resultados en un archivo JSON
        with open("investigadores_limited.json", "w", encoding="utf-8") as file:
            json.dump(limited_data, file, ensure_ascii=False, indent=4)

        print("Extracción completa. Datos almacenados en 'investigadores_limited.json'.")

    except Exception as e:
        print("Error al ejecutar el agente:", e)


# Ejecutar el script
asyncio.run(main())
