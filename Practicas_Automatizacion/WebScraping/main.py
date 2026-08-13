"""
Web scraping de dos tiendas online: Tía y Coral.

Lee los productos del CSV, realiza las búsquedas
en ambas tiendas y obtiene sus datos.
"""

import json
import tia
import coral


def main():

    resultados_tia = tia.scrape_tienda_tia()
    resultados_coral = coral.scrape_tienda_coral()

    resultados = resultados_tia + resultados_coral

    print(json.dumps(resultados, ensure_ascii=False))


if __name__ == "__main__":
    main()