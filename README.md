# 🛒 Automatización de Web Scraping con n8n

Proyecto de automatización para la **obtención, procesamiento y almacenamiento de información de productos** mediante web scraping.

El sistema combina **Playwright + FastAPI** para el scraping, **n8n** para la orquestación, **PostgreSQL** para el almacenamiento y **Metabase** para la visualización de datos.

## Arquitectura

```text
        n8n (Automatización)
              │ HTTP
              ▼
   Scraper (FastAPI + Playwright)
              │
      ┌───────┴───────┐
      ▼               ▼
    Tía            Coral
      │               │
      └───────┬───────┘
              ▼
        PostgreSQL
              │
              ▼
          Metabase
```

## Tecnologías

Python · Playwright · FastAPI · Uvicorn · n8n · PostgreSQL 16 · Metabase · Docker / Docker Compose

## Estructura del proyecto

```text
pruebas-automatizaci-n/
├── n8n/
│   ├── docker-compose.yml
│   └── Practica Automatizacion.json
└── Practicas_Automatizacion/
    └── WebScraping/
        ├── api.py
        ├── main.py
        ├── tia.py
        ├── coral.py
        ├── Dockerfile
        ├── requirements.txt
        └── productos.csv
```

## Funcionamiento

1. **n8n** dispara la automatización mediante un `Schedule Trigger` (cada 30 min).
2. Hace una petición HTTP al scraper: `http://scraper:8000/scrape`.
3. La API ejecuta los scrapers de las tiendas configuradas.
4. Los resultados vuelven a n8n, que filtra los datos válidos.
5. Los productos se guardan en **PostgreSQL**.
6. **Metabase** consulta esos datos para generar dashboards.

---

## 🚀 Instalación

**Requisitos:** Docker y Docker Compose.

```bash
git clone https://github.com/luisNarvaez20/pruebas-automatizaci-n.git
cd pruebas-automatizaci-n/n8n
docker compose up -d --build
```

Comprueba que todo esté arriba:

```bash
docker compose ps
```

Deberías ver: `n8n`, `webscraping`, `postgres_scraping`, `metabase`.

## Servicios

| Servicio | URL                    |
| -------- | ---------------------- |
| n8n      | http://localhost:5678  |
| Metabase | http://localhost:3000  |
| Scraper  | http://localhost:8000  |

> El scraper no necesita puerto publicado para que n8n lo alcance: ambos comparten la red interna de Docker Compose (`http://scraper:8000/scrape`).

---

## ⚙️ Configuración

### 1. Importar el workflow en n8n

En `http://localhost:5678` → **Import from File** → selecciona `n8n/Practica Automatizacion.json`.

El workflow sigue este flujo:

```text
Schedule Trigger → HTTP Request → Filter → PostgreSQL
```

### 2. Credencial de PostgreSQL en n8n

El workflow importado no trae credenciales — hay que crear una nueva, tipo **Postgres**, con estos valores (definidos en `docker-compose.yml`):

```text
Host: postgres
Port: 5432
Database: scraping
User: scraping_user
Password: scraping_password
```

⚠️ Usa `postgres` como host, **no** `localhost` (n8n se conecta desde otro contenedor).

### 3. Crear la tabla de productos

```bash
docker exec -it postgres_scraping psql -U scraping_user -d scraping
```

```sql
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    tienda VARCHAR(100) NOT NULL,
    nombre_tienda VARCHAR(255) NOT NULL,
    marca_tienda VARCHAR(255),
    precio NUMERIC(10,2),
    stock BOOLEAN,
    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Conectar Metabase

En `http://localhost:3000`, agrega la base de datos usando las mismas credenciales de PostgreSQL de arriba.

---

## ▶️ Ejecutar la automatización

1. Abre el nodo **Postgres** en el workflow y selecciona la credencial creada.
2. Guarda y ejecuta el workflow manualmente para probar.
3. Verifica los resultados:

```sql
SELECT * FROM productos;
```

El workflow queda programado para correr automáticamente cada 30 minutos.

---

## 🧰 Comandos útiles

```bash
docker compose up -d              # Iniciar servicios
docker compose up -d --build      # Reconstruir el scraper
docker compose ps                 # Ver estado
docker compose logs -f            # Logs de todos los servicios
docker logs webscraping           # Logs del scraper
docker compose down               # Detener servicios
docker compose down -v            # Detener y borrar volúmenes (⚠️ borra los datos)
```

---

## 🔒 Seguridad

Este proyecto es un entorno de demostración. No se almacenan en el repositorio contraseñas reales, API keys, tokens ni archivos `.env` sensibles. Las credenciales del `docker-compose.yml` son de prueba, solo para uso local.

---
