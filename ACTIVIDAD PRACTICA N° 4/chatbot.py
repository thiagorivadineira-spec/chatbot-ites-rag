import os
import streamlit as st
import google.generativeai as genai 
from dotenv import load_dotenv
from pypdf import PdfReader

# Configuración básica de la página de Streamlit
st.set_page_config(page_title="Asistente Virtual ITES", page_icon="🤖", layout="wide")

# 1. CARGA DE CREDENCIALES
load_dotenv()
env_api_key = os.getenv("GEMINI_API_KEY")

with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input(
        "Ingresa tu Google Gemini API Key:", 
        value=env_api_key if env_api_key else "",
        type="password",
        help="Obtén tu clave gratis en https://aistudio.google.com/"
    )
    
    st.divider()
    st.header("📊 Estadísticas de Uso")
    
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
        
    st.metric(label="Tokens Totales Consumidos", value=st.session_state.total_tokens)
    
    # Cálculo de costo simulado ($0.075 por cada 1 millón de tokens de entrada en Gemini Flash)
    costo_estimado = (st.session_state.total_tokens / 1_000_000) * 0.075
    st.metric(label="Gasto Estimado (USD)", value=f"${costo_estimado:.6f}")

if not api_key:
    st.title("🤖 Asistente Virtual")
    st.warning("⚠️ Por favor, ingresa una API Key de Google Gemini en la barra lateral para comenzar.")
    st.stop()

# 2. LECTURA DEL PDF 
@st.cache_data(show_spinner="Leyendo manual del Ites...")
def cargar_documento(ruta):
    texto_extraido = ""
    try:
        reader = PdfReader(ruta)
        for pagina in reader.pages:
            if pagina.extract_text():
                texto_extraido += pagina.extract_text() + "\n"
        return texto_extraido
    except Exception as e:
        st.error(f"Error al leer el PDF. Verifica que la ruta exista: {e}")
        st.stop()

# Cargamos el PDF (Ajusta el nombre según tu archivo)
contexto_pdf = cargar_documento("ites_oferta_academica.pdf")

# 3. CONFIGURACIÓN DEL MODELO GEMINI Y RAG
genai.configure(api_key=api_key)

# Inyectamos el texto del PDF directamente en las reglas del sistema
instrucciones_sistema = f"""
Eres el asistente virtual oficial del Instituto Tecnológico de Educación Superior (ITES).
Tu tono debe ser amable, profesional y conciso.

Tu ÚNICA función es responder preguntas basadas estrictamente en la siguiente documentación:
=== DOCUMENTACIÓN DE REFERENCIA ===
{contexto_pdf}
===================================

REGLAS OBLIGATORIAS:
1. Responde únicamente con información explícita en el documento.
2. Si el usuario te pregunta sobre temas fuera del ITES, declina responder educadamente diciendo que tu función es exclusiva para temas de la institución.
"""

# Inicializamos el modelo 
modelo = genai.GenerativeModel(
    model_name=os.getenv("MODEL_NAME", "gemini-3.5-flash"),
    system_instruction=instrucciones_sistema
)

# 4. MANEJO DEL HISTORIAL DE CHAT
st.title("🤖 Asistente Virtual - ITES")
st.markdown("¡Hola! Soy tu asistente. Pregúntame sobre nuestras carreras, sedes o inscripciones.")

# Inicializamos el objeto de chat de Gemini y el historial de UI
if "chat_session" not in st.session_state:
    st.session_state.chat_session = modelo.start_chat(history=[])
    
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostramos los mensajes guardados en el historial
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

# 5. INTERACCIÓN CON EL USUARIO
pregunta = st.chat_input("Ej: ¿Dónde se cursa Bromatología?")

if pregunta:
    with st.chat_message("user"):
        st.markdown(pregunta)
    st.session_state.mensajes.append({"rol": "user", "contenido": pregunta})

    with st.chat_message("assistant"):
        with st.spinner("Buscando información en el manual..."):
            try:
                # Enviamos el mensaje a Gemini
                respuesta = st.session_state.chat_session.send_message(pregunta)
                st.markdown(respuesta.text)
                
                st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta.text})
                
                # Extraemos el uso de tokens oficial de la respuesta
                tokens_uso = respuesta.usage_metadata
                tokens_total_llamada = tokens_uso.total_token_count
                
                # Actualizamos métricas
                st.session_state.total_tokens += tokens_total_llamada
                st.rerun() 
                
            except Exception as e:
                st.error(f"Ocurrió un error de conexión: {e}")