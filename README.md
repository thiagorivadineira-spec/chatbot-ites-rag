# chatbot-ites-rag
<img width="1843" height="904" alt="image" src="https://github.com/user-attachments/assets/921f7e41-989b-4d06-a4ea-1ceecff37e92" />

chatbot ignorando temas que no tienen que ver con ITES y respondiendo los que si


Instalación
Clona o descarga este repositorio.
Abre una terminal en la carpeta del proyecto.

Instala las dependencias:
pip install -r requirements.txt
Configuración de variables de entorno
Crea un archivo llamado .env en la raíz del proyecto con el siguiente contenido:

GEMINI_API_KEY=su_api_key_aqui
MODEL_NAME=gemini-3.5-flash-lite
Explicación
API_KEY: clave de acceso a la API de Gemini que puedes conseguir gatis en  https://aistudio.google.com/
MODEL_NAME: nombre del modelo a utilizar

Preparación del PDF
Coloca el archivo PDF:

ites_oferta_academica.pdf
Este archivo debe contener la información relevante sobre ITES
Desde la terminal del proyecto ejecuta:

streamlit run chatbot.py
Luego se abrira automaticamente la web o tendras que abrir la URL local que muestra Streamlit.
