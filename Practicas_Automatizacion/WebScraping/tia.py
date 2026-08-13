import logging

import pandas as pd
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

BASE_URL = "https://www.tia.com.ec/"

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
        "tienda": "Tía",
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
            "input.amsearch-input"
        ).first

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

        search_button = page.locator(
            "button.amsearch-button.-loupe"
        )

        search_button.wait_for(
            state="visible",
            timeout=10000
        )

        search_button.click()

        page.wait_for_timeout(2000)

        # Obtener resultados
        productos = page.locator(
            "li.product-item"
        )

        if productos.count() == 0:

            logger.warning(
                f"No se encontraron resultados para: {nombre}"
            )

            return resultado

        # Tía devuelve el resultado principal primero.
        producto = productos.first

        # Nombre
        resultado["nombre_tienda"] = (
            producto
            .locator(".product-item-link")
            .inner_text()
            .strip()
        )

        logger.info(
            f"Nombre: {resultado['nombre_tienda']}"
        )

        # Marca
        marca_elemento = producto.locator(
            ".product-item-brand"
        )

        if marca_elemento.count() > 0:

            resultado["marca_tienda"] = (
                marca_elemento
                .inner_text()
                .replace("Marca", "")
                .strip()
            )

        logger.info(
            f"Marca: {resultado['marca_tienda']}"
        )

        # Precio
        precio_texto = (
            producto
            .locator(".price")
            .first
            .inner_text()
            .strip()
        )

        precio_limpio = (
            precio_texto
            .replace("$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

        resultado["precio"] = float(
            precio_limpio
        )

        logger.info(
            f"Precio: {resultado['precio']}"
        )

        # Stock
        resultado["stock"] = (
            producto
            .locator("button.action.tocart")
            .count() > 0
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


def scrape_tienda_tia():

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
