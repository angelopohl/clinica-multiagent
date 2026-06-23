# Appointment Multi-Agent System

Este es un sistema inteligente para la reserva de citas basado en arquitectura multiagente. Permite a los usuarios agendar citas, verificar disponibilidad y consultar dudas frecuentes, todo manejado por agentes de IA especializados.

## Descripción del Sistema
El sistema se presenta como una API REST (con FastAPI) a la que se puede conectar cualquier frontend (Web, WhatsApp, Telegram, n8n). Su corazón es un **Orquestador** que distribuye los mensajes del usuario a diferentes agentes especializados en detección de intenciones, validación de reglas de negocio, consulta de bases de datos vectoriales (RAG) y acciones transaccionales (booking/notificación).

## Arquitectura y Explicación Académica

Este proyecto implementa varios conceptos clave:

1. **SMA (Sistemas Multiagente):** En lugar de tener un único prompt masivo y monolítico que intente hacer todo, la inteligencia se divide en "agentes" especializados. Cada agente tiene un prompt de sistema muy delimitado (ej. "Sólo extrae la intención", "Sólo valida si faltan datos"). Esto reduce las alucinaciones y hace que el sistema sea determinista en sus puntos críticos.
2. **Hiperautomatización y RPA:** Este asistente inteligente es el "cerebro" detrás de la automatización de un proceso de negocio (reservar cita). Un agente extrae y estructura la data no estructurada del lenguaje natural, y cuando la data está lista, ejecuta la tarea en la base de datos (Booking), que luego podría conectarse a un flujo RPA clásico usando un webhook hacia una herramienta como **n8n**.
3. **RAG (Retrieval-Augmented Generation):** El agente de conocimiento (`rag_agent`) utiliza ChromaDB. En lugar de depender del conocimiento general del LLM (que no sabe a qué hora abre *tu* negocio), el agente recupera textualmente las políticas de tu documento (`knowledge_base.txt`) y le pide al LLM que responda **sólo** basado en eso.
4. **LangChain / LangGraph & MCP:** Aunque la implementación actual utiliza el SDK de Gemini puro estructurado mediante Python nativo (para máxima claridad académica y control del estado), sigue conceptualmente el modelo de LangGraph (un flujo de estado que transita entre nodos/agentes) y sienta las bases para MCP (Model Context Protocol), ya que cada herramienta (base de datos, RAG) está claramente desacoplada y disponible para que el modelo la consuma como un servicio externo.

### Diagrama Textual del Flujo

```
Usuario -> [ POST /chat ]
             |
             v
    [ OrchestratorAgent ]
             |-- 1. Consulta intención -> [ IntentAgent ]
             |
             |-- 2. Si es consulta general -> [ RagAgent ] (Consulta ChromaDB) -> Responde
             |
             |-- 3. Si es reserva -> Inicia Flujo de Reserva
                     |
                     |--> [ ValidationAgent ] (Faltan datos? Pide al usuario)
                     |--> [ AvailabilityAgent ] (Consulta SQLite: ¿Hay cupo?)
                     |--> [ BookingAgent ] (Guarda en SQLite)
                     |--> [ NotificationAgent ] (Genera confirmación)
                     |
             <-------+ (Devuelve respuesta final al usuario)
```

## Agentes Implementados

* **OrchestratorAgent:** Controlador principal. Maneja el estado conversacional del usuario y enruta los flujos.
* **IntentAgent:** Extrae la intención principal ("reservar", "consultar", etc.) y entidades del texto.
* **RagAgent:** Atiende preguntas frecuentes basadas en la base de datos vectorial ChromaDB.
* **AvailabilityAgent:** Revisa los horarios disponibles y sugiere alternativas si un horario está ocupado.
* **ValidationAgent:** Revisa qué datos faltan para completar una reserva.
* **BookingAgent:** Interactúa con SQLite para registrar la cita.
* **NotificationAgent:** Simula el envío de una confirmación (preparado para integrarse con RPA/n8n).

## Tecnologías Usadas

* **Python 3.11+**
* **FastAPI + Uvicorn:** Para la API rápida y asíncrona.
* **Google Generative AI (Gemini):** LLM principal (`gemini-1.5-flash`).
* **ChromaDB:** Base de datos vectorial embebida.
* **SQLite + SQLAlchemy:** Base de datos transaccional local.
* **Pydantic:** Validaciones estrictas de datos.

## Instalación y Configuración

1. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuración de .env:**
   Copia el archivo de ejemplo y agrega tu API Key de Gemini:
   ```bash
   cp .env.example .env
   # Edita el .env y pon tu GEMINI_API_KEY
   ```

3. **Inicializar bases de datos (Seed & Ingest):**
   ```bash
   python app/database/seed_data.py
   python app/vectorstore/ingest_documents.py
   ```

## Cómo Ejecutar

Arranca el servidor localmente:
```bash
python run.py
```
El servidor estará disponible en: `http://localhost:8000`
La documentación de la API Swagger en: `http://localhost:8000/docs`

## Ejemplos de Prueba con cURL

### 1. Consultar base de conocimiento (RAG)
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "¿Cuáles son las políticas de cancelación?"}'
```

### 2. Verificar horarios de atención
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "¿A qué hora abren los sábados?"}'
```

### 3. Flujo de Reserva paso a paso
*Inicia la reserva:*
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Quiero reservar una cita para corte de cabello mañana"}'
```
*(El sistema te pedirá el nombre, contacto, y horario, puedes seguir respondiendo mediante el mismo endpoint simlulando el chat).*

### 4. Consultar citas registradas (Directo)
```bash
curl -X GET http://localhost:8000/appointments
```
