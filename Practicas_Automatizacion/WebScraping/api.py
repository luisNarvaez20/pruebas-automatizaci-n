from fastapi import FastAPI
import tia
import coral

app = FastAPI()


@app.get("/scrape")
def scrape():

    resultados_tia = tia.scrape_tienda_tia()
    resultados_coral = coral.scrape_tienda_coral()

    resultados = resultados_tia + resultados_coral

    return resultados