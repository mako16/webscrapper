# scrapper_ollama.py

Este script permite realizar scraping recursivo (tipo web crawler) sobre un sitio web, extrayendo el texto de todas las páginas internas sin límite de profundidad. Luego, utiliza un modelo LLM local (Ollama) para analizar el contenido y devolver un resumen con los puntos más importantes, haciendo énfasis en los contactos públicos de las personas mencionadas (emails, teléfonos, redes sociales, etc).

## Instalación

1. Clona este repositorio o copia los archivos en tu proyecto.
2. Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

3. Copia el archivo `.env_sample` a `.env` y ajusta los parámetros de configuración según tus necesidades:

```bash
cp .env_sample .env
```

- `MODEL`: Nombre del modelo Ollama a utilizar (por defecto: llama3)
- `OLLAMA_URL`: URL de la API de Ollama (por defecto: http://localhost:11434/api/generate)
- `TIMEOUT`: Timeout de requests HTTP en segundos (por defecto: 10)

## Uso

Haz ejecutable el script (solo la primera vez):

```bash
chmod +x scrapper_ollama.py
```

Ejecuta el script pasando la URL inicial como argumento:

```bash
./scrapper_ollama.py https://ejemplo.com
```

El script recorrerá recursivamente el sitio, extraerá el texto y enviará el contenido a Ollama para obtener un resumen y los contactos públicos encontrados.

## Parámetro opcional

- **Regex**: Si se indica, el script recopila todo el texto durante el scraping pero solo envía a Ollama la información que coincide con ese patrón. El regex debe pasarse entre comillas ("...") si contiene espacios o caracteres especiales. Si no se indica, se envía todo el texto extraído.

### Ejemplo de uso avanzado

```bash
./scrapper_ollama.py https://ejemplo.com "contacto|email"
```

En este ejemplo, "contacto|email" está entre comillas para asegurar que el patrón se interprete correctamente.

- Buscará coincidencias con "contacto" o "email" en el texto.

## Funcionamiento del resumen

- El script muestra un breve resumen de cada URL recorrida, generado por Ollama.
- Si se pasa el parámetro opcional **regex**, solo se resumen las URLs cuyo contenido coincide con ese patrón (el resumen se omite para las que no matchean).
- Si no se pasa regex, se resume el contenido de cada URL visitada.
- El resumen es solo del contenido, no incluye ni busca contactos, emails ni teléfonos.

## Requisitos
- Python 3.7+
- Un modelo Ollama corriendo localmente (https://ollama.com/)

## Notas
- El script solo sigue enlaces internos (mismo dominio).
- No visita la misma URL más de una vez.
- Puedes ajustar la profundidad y otros parámetros desde el archivo `.env`.
