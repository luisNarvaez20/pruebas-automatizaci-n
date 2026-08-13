import logging

import pandas as pd
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

BASE_URL = "https://coralhipermercados.com/"

logger = logging.getLogger(__name__)


def cargar_productos():
    return pd.read_csv("./productos.csv")


def buscar_producto(page, producto):

    nombre = str(producto["nombre"]).strip()
    marca = str(producto["marca"]).strip()
    presentacion = str(producto["presentacion"]).strip()

    logger.info(
        f"Buscando: {nombre} | {marca} | {presentacion}"
    )

    resultado = {
        "tienda": "Coral",
        "nombre_tienda": None,
        "marca_tienda": None,
        "precio": None,
        "stock": None,
    }

    try:

        page.goto(
            BASE_URL,
            wait_until="domcontentloaded",
            timeout=30000
        )

        search_input = page.locator(
            "#minisearch-input-top-search"
        )

        search_input.wait_for(
            state="visible",
            timeout=10000
        )

        termino = f"{nombre} {marca} {presentacion}"

        logger.info(
            f"Consulta: {termino}"
        )

        search_input.fill(termino)

        page.wait_for_timeout(1000)

        search_input.press("Enter")

        page.wait_for_timeout(2000)

        # Verificar si Coral encontró un producto.
        if page.locator('[itemprop="sku"]').count() == 0:

            logger.warning(
                f"Producto no encontrado en Coral: {nombre}"
            )

            return resultado

        # Nombre
        resultado["nombre_tienda"] = (
            page.locator("h1.page-title .base")
            .inner_text()
            .strip()
        )

        logger.info(
            f"Nombre: {resultado['nombre_tienda']}"
        )

        # Marca
        descripcion = page.locator(
            '[itemprop="description"]'
        )

        if descripcion.count() > 0:

            texto = descripcion.inner_text()

            for linea in texto.splitlines():

                if "Marca:" in linea:

                    resultado["marca_tienda"] = (
                        linea
                        .replace("Marca:", "")
                        .strip()
                    )

                    break

        logger.info(
            f"Marca: {resultado['marca_tienda']}"
        )

        # Precio
        precio = page.locator(
            "[data-price-amount]"
        ).first.get_attribute(
            "data-price-amount"
        )

        if precio:

            resultado["precio"] = round(
                float(precio),
                2
            )

        logger.info(
            f"Precio: {resultado['precio']}"
        )

        # Stock
        resultado["stock"] = (
            page.locator(".stock.available").count() > 0
        )

        logger.info(
            f"Stock: {resultado['stock']}"
        )

        logger.info(
            "Producto procesado correctamente."
        )

    except PlaywrightTimeoutError:

        logger.warning(
            f"Timeout buscando: {nombre}"
        )

    except Exception as e:

        logger.error(
            f"Error buscando {nombre}: {e}"
        )

    return resultado


def scrape_tienda_coral():

    productos = cargar_productos()
    resultados = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        for _, producto in productos.iterrows():

            resultado = buscar_producto(
                page,
                producto
            )

            resultados.append(resultado)

        browser.close()

    return resultados