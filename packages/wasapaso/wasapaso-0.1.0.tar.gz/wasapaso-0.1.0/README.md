# Wasapaso Python SDK

[![PyPI version](https://badge.fury.io/py/wasapaso.svg)](https://badge.fury.io/py/wasapaso)
[![Python Versions](https://img.shields.io/pypi/pyversions/wasapaso.svg)](https://pypi.org/project/wasapaso/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/victalejo/wasapaso-python-sdk/workflows/CI/badge.svg)](https://github.com/victalejo/wasapaso-python-sdk/actions)
[![codecov](https://codecov.io/gh/victalejo/wasapaso-python-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/victalejo/wasapaso-python-sdk)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

SDK oficial de Python para la API de Wasapaso. Gestiona sesiones de WhatsApp y envía mensajes de manera sencilla y eficiente.

## Características

- **Soporte asíncrono completo**: Usa `async/await` para operaciones concurrentes
- **Type hints**: Completamente tipado para mejor autocompletado en IDEs
- **Modelos validados**: Utiliza Pydantic para validación de datos
- **Fácil de usar**: API intuitiva y bien documentada
- **Manejo de errores**: Excepciones específicas para diferentes tipos de errores
- **Testing**: Suite completa de tests con alta cobertura

## Instalación

```bash
pip install wasapaso
```

## Inicio Rápido

```python
from wasapaso import WasapasoClient

# Inicializar el cliente con tu API key
client = WasapasoClient(api_key="wsk_your_api_key_here")

# Crear una sesión de WhatsApp
session = client.sessions.create({"name": "Mi Primera Sesión"})

# Iniciar la sesión
client.sessions.start(session.id)

# Enviar un mensaje de texto
result = client.messages.send_text(
    session_id=session.id,
    to="1234567890",
    message="¡Hola desde Wasapaso!"
)
```

## Uso Asíncrono

```python
import asyncio
from wasapaso import WasapasoClient

async def main():
    client = WasapasoClient(api_key="wsk_your_api_key_here")

    # Crear sesión de forma asíncrona
    session = await client.sessions.create_async({"name": "Sesión Async"})

    # Enviar mensaje de forma asíncrona
    result = await client.messages.send_text_async(
        session_id=session.id,
        to="1234567890",
        message="¡Hola async!"
    )

asyncio.run(main())
```

## Documentación

### Autenticación

Obtén tu API key desde el [dashboard de Wasapaso](https://wasapaso.com/dashboard/api-keys).

```python
from wasapaso import WasapasoClient

client = WasapasoClient(
    api_key="wsk_your_api_key",
    base_url="https://api.wasapaso.com",  # Opcional
    timeout=30.0  # Timeout en segundos (opcional)
)
```

### Gestión de Sesiones

#### Crear una sesión

```python
session = client.sessions.create({
    "name": "Mi Sesión",
    "webhookUrl": "https://myapp.com/webhook",  # Opcional
    "webhookEvents": ["message", "message.ack"],  # Opcional
})
```

#### Listar sesiones

```python
sessions = client.sessions.list(page=1, limit=20, status="WORKING")

for session in sessions.data:
    print(f"{session.name}: {session.status}")
```

#### Obtener una sesión

```python
session = client.sessions.get("session_id")
print(f"Status: {session.status}")
```

#### Iniciar una sesión

```python
session = client.sessions.start("session_id")
```

#### Obtener código QR

```python
qr = client.sessions.get_qr("session_id")
print(qr.qr)  # Código QR en base64 o formato especificado
```

#### Solicitar código de emparejamiento

```python
pairing = client.sessions.request_pairing_code("session_id", "+1234567890")
print(f"Código: {pairing.code}")
```

#### Actualizar sesión

```python
session = client.sessions.update("session_id", {
    "name": "Nuevo Nombre",
    "metadata": {"custom_field": "value"}
})
```

#### Detener sesión

```python
session = client.sessions.stop("session_id")
```

#### Eliminar sesión

```python
result = client.sessions.delete("session_id")
```

### Envío de Mensajes

#### Mensaje de texto

```python
result = client.messages.send_text(
    session_id="session_id",
    to="1234567890",
    message="Hola, ¿cómo estás?",
    reply_to="message_id"  # Opcional
)
```

#### Mensaje con imagen

```python
result = client.messages.send_media(
    session_id="session_id",
    to="1234567890",
    media_type="image",
    media_url="https://example.com/image.jpg",
    caption="Mira esta imagen!",
    mimetype="image/jpeg"
)
```

#### Mensaje con video

```python
result = client.messages.send_media(
    session_id="session_id",
    to="1234567890",
    media_type="video",
    media_url="https://example.com/video.mp4",
    caption="Video interesante",
    mimetype="video/mp4"
)
```

#### Mensaje con archivo

```python
result = client.messages.send_media(
    session_id="session_id",
    to="1234567890",
    media_type="file",
    media_url="https://example.com/document.pdf",
    filename="documento.pdf",
    mimetype="application/pdf"
)
```

#### Enviar ubicación

```python
result = client.messages.send_location(
    session_id="session_id",
    to="1234567890",
    latitude=40.7128,
    longitude=-74.0060,
    title="Nueva York"
)
```

#### Listar mensajes

```python
messages = client.messages.list(
    session_id="session_id",
    chat_id="1234567890@c.us",  # Opcional
    limit=50,
    offset=0
)

for msg in messages.data:
    print(f"{msg.from_}: {msg.body}")
```

#### Obtener un mensaje

```python
message = client.messages.get("message_id")
```

#### Marcar como leído

```python
client.messages.mark_as_read("message_id")
```

#### Reaccionar a un mensaje

```python
client.messages.react("message_id", "👍")
```

#### Eliminar un mensaje

```python
client.messages.delete("message_id", delete_for_everyone=True)
```

## Manejo de Errores

El SDK proporciona excepciones específicas para diferentes tipos de errores:

```python
from wasapaso import WasapasoClient
from wasapaso.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    WasapasoError
)

try:
    client = WasapasoClient(api_key="wsk_invalid_key")
    session = client.sessions.get("invalid_id")
except AuthenticationError:
    print("API key inválida")
except NotFoundError:
    print("Sesión no encontrada")
except RateLimitError:
    print("Límite de tasa excedido")
except ValidationError as e:
    print(f"Error de validación: {e.message}")
except WasapasoError as e:
    print(f"Error general: {e.message}")
```

## Ejemplos Avanzados

### Enviar múltiples mensajes en paralelo

```python
import asyncio
from wasapaso import WasapasoClient

async def send_bulk_messages():
    client = WasapasoClient(api_key="wsk_your_api_key")

    recipients = ["1111111111", "2222222222", "3333333333"]

    tasks = [
        client.messages.send_text_async(
            session_id="session_id",
            to=recipient,
            message=f"Hola {recipient}!"
        )
        for recipient in recipients
    ]

    results = await asyncio.gather(*tasks)
    return results

asyncio.run(send_bulk_messages())
```

### Usar con context manager

```python
from wasapaso import WasapasoClient

def main():
    client = WasapasoClient(api_key="wsk_your_api_key")

    # Crear sesión
    session = client.sessions.create({"name": "Temp Session"})

    try:
        # Usar la sesión
        client.sessions.start(session.id)
        client.messages.send_text(
            session_id=session.id,
            to="1234567890",
            message="Test"
        )
    finally:
        # Limpiar
        client.sessions.delete(session.id)
```

## Desarrollo

### Instalación para desarrollo

```bash
git clone https://github.com/wasapaso/sdk-python.git
cd sdk-python
pip install -e ".[dev]"
```

### Ejecutar tests

```bash
pytest
```

### Ejecutar tests con cobertura

```bash
pytest --cov=wasapaso --cov-report=html
```

### Formatear código

```bash
black wasapaso tests
```

### Type checking

```bash
mypy wasapaso
```

## Requisitos

- Python >= 3.8
- httpx >= 0.25.0
- pydantic >= 2.0.0

## Soporte

- Documentación: [https://docs.wasapaso.com/sdk/python](https://docs.wasapaso.com/sdk/python)
- Issues: [https://github.com/wasapaso/sdk-python/issues](https://github.com/wasapaso/sdk-python/issues)
- Email: support@wasapaso.com

## Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## Contribuir

Las contribuciones son bienvenidas! Por favor lee nuestra [guía de contribución](CONTRIBUTING.md) antes de enviar un pull request.

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para detalles de cambios en cada versión.

---

Desarrollado con ❤️ por el equipo de Wasapaso
