"""
Script de scraping web utilizando IA para extraer datos.

Este script utiliza la biblioteca crawl4ai para:
1. Navegar a una página web específica
2. Extraer datos de una tabla usando un LLM (utilizando el proveedor elegido)
3. Validar y guardar los resultados en formato JSON

Requisitos:
- Python 3.9+
- Dependencias: crawl4ai
- Variable de entorno: OPENAI_API_KEY y DEEPSEEK_API_KEY en .env
"""

import asyncio
import json
import os

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Configuración constante
URL_TO_SCRAPE = "https://web.lmarena.ai/leaderboard"
INSTRUCTION_TO_LLM = (
    "Extrae todas las filas de la tabla principal como objetos con: "
    "'Rank', 'Model', 'arena score', '95% CI', 'votes', 'organization', 'License'."
    "Ten en cuenta que el Model tiene que ser el nombre del modelo AI, por ejemplo: 'Claude 3.5 Sonnet (20241022)'."
)
OUTPUT_FILE = "leaderboard_data.json"
AI_MODEL="openai/gpt-4o-mini" # Cambiar a "deepseek/deepseek-chat" para Deepseek
API_KEY=os.getenv("OPENAI_API_KEY") # Cambiar a "DEEPSEEK_API_KEY" para Deepseek

# Modelo Pydantic para validar la estructura de los datos extraídos
class LeaderboardEntry(BaseModel):
    """Modelo Pydantic para validar la estructura de los datos extraídos."""
    rank: int = Field(..., description="Posición en el ranking")
    model: str = Field(..., description="Nombre del modelo AI (Ej: Claude 3.5 Sonnet (20241022))")
    arena_score: float = Field(..., alias="arena score", description="Puntuación principal")
    ci_95: str = Field(..., alias="95% CI", description="Intervalo de confianza del 95%")
    votes: int = Field(..., description="Número de votos recibidos")
    organization: str = Field(..., description="Empresa o organización responsable")
    license: str = Field(..., description="Tipo de licencia del modelo")

async def main():
    """
    Función principal que ejecuta el proceso completo de scraping:
    1. Configura la estrategia de extracción con LLM
    2. Inicia el crawler web
    3. Procesa y guarda los resultados
    """
    # Configuración de la estrategia de extracción
    llm_strategy = LLMExtractionStrategy(
        provider=AI_MODEL,
        api_token=API_KEY,
        schema=LeaderboardEntry.model_json_schema(),
        extraction_type="schema",
        instruction=INSTRUCTION_TO_LLM,
        chunk_token_threshold=1000,
        overlap_rate=0.0,
        apply_chunking=True,
        input_format="markdown",
        extra_args={
            "temperature": 0.0,  # Determinismo
            "max_tokens": 800    # Límite para controlar el coste
        }
    )

    # Configuración del crawler
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,  # Ignora caché para datos actualizados
        process_iframes=False,
        remove_overlay_elements=True,  # Elimina popups y cookies banners
        exclude_external_links=True,   # Limita el scraping al dominio principal
    )

    # Configuración del navegador headless
    browser_config = BrowserConfig(
        headless=True,   # Ejecución sin interfaz gráfica
        verbose=True,    # Logs detallados
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=URL_TO_SCRAPE, config=crawl_config)

        if result.success:
            try:
                # Convertir y validar los datos extraídos
                raw_data = json.loads(result.extracted_content)
                validated_data = [LeaderboardEntry(**item) for item in raw_data]
                
                # Mostrar resultados en consola
                print(f"Datos extraídos exitosamente ({len(validated_data)} registros):")
                for entry in validated_data[:3]:  # Muestra primeros 3 como ejemplo
                    print(f" - {entry.model} ({entry.organization}): {entry.arena_score}")

                # Guardar resultados en archivo
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(
                        [item.model_dump(by_alias=True) for item in validated_data],
                        f,
                        indent=2,
                        ensure_ascii=False
                    )
                print(f"\nDatos guardados en: {OUTPUT_FILE}")

                # Mostrar métricas de uso
                llm_strategy.show_usage()

            except json.JSONDecodeError:
                print("Error: Los datos extraídos no son JSON válido")
            except Exception as e:
                print(f"Error inesperado al procesar datos: {str(e)}")
        else:
            print(f"Error en el scraping: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
