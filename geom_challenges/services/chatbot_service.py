import traceback
from pathlib import Path
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = Path(__file__).resolve().parents[1] / "vector_store"
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Eres un asistente experto en el juego Ojo Mágico con Figuras Geométricas.
Tus respuestas deben:
- Explicar reglas y consignas del juego cuando el usuario tenga dudas.
- Dar pistas concretas sobre la figura actual sin revelar directamente la solución.
- Nunca develar la figura oculta si no se solicita una pista específica.
- Siempre que ofrezcas ayuda/una pista, añade la etiqueta oculta [PISTA_ENTREGADA] al final del texto.
- Si el usuario adivina correctamente la figura, responde con una confirmación breve y añade la etiqueta oculta [RESPUESTA_CORRECTA].
- No incluyas las etiquetas en el texto visible final del usuario; son solo para el backend.
- Mantén el tono amable, claro y enfocado en el juego.
"""


class DirectGroqChain:
    def invoke(self, payload):
        return self._call(payload)

    def run(self, payload):
        return self._call(payload)

    def _call(self, payload):
        user_input = payload.get("user_input", "")
        current_shape = payload.get("current_shape", "cuadrado")
        started_at = time.perf_counter()
        provider = "groq"
        model = "llama-3.1-8b-instant"

        logger.info(
            "chat_model_call_started provider=%s model=%s current_shape=%s user_message=%s",
            provider,
            model,
            current_shape,
            user_input,
        )

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error(
                "chat_model_call_failed provider=%s model=%s reason=missing_api_key current_shape=%s duration_ms=%.2f",
                provider,
                model,
                current_shape,
                (time.perf_counter() - started_at) * 1000,
            )
            raise RuntimeError("No se encontró GROQ_API_KEY. Define la variable de entorno para usar el servicio real del chatbot.")

        try:
            from groq import Groq
        except Exception as exc:
            logger.exception(
                "chat_model_call_failed provider=%s model=%s reason=client_import_error current_shape=%s duration_ms=%.2f",
                provider,
                model,
                current_shape,
                (time.perf_counter() - started_at) * 1000,
            )
            raise RuntimeError("No se pudo importar el cliente de Groq. Verifique la instalación del paquete groq.") from exc

        client = Groq(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Usuario: {user_input}\n"
                            f"Figura actual: {current_shape}\n"
                            "Responde de forma clara y útil para explicar cómo jugar."
                        ),
                    },
                ],
            )
        except Exception:
            logger.exception(
                "chat_model_call_failed provider=%s model=%s reason=provider_request_error current_shape=%s duration_ms=%.2f",
                provider,
                model,
                current_shape,
                (time.perf_counter() - started_at) * 1000,
            )
            raise

        if response and getattr(response, "choices", None):
            message = response.choices[0].message
            content = getattr(message, "content", None)
            if content:
                logger.info(
                    "chat_model_call_completed provider=%s model=%s current_shape=%s response_length=%s duration_ms=%.2f",
                    provider,
                    model,
                    current_shape,
                    len(content),
                    (time.perf_counter() - started_at) * 1000,
                )
                return content

        logger.error(
            "chat_model_call_invalid_response provider=%s model=%s current_shape=%s duration_ms=%.2f",
            provider,
            model,
            current_shape,
            (time.perf_counter() - started_at) * 1000,
        )
        raise RuntimeError("Groq no devolvió una respuesta válida.")


_chat_chain = None


def get_retrieval_chain():
    return DirectGroqChain()


def get_fallback_chain():
    return DirectGroqChain()


def get_chat_chain():
    global _chat_chain
    if _chat_chain is None:
        try:
            _chat_chain = get_retrieval_chain()
        except Exception as exc:
            traceback.print_exc()
            raise RuntimeError("No se pudo inicializar el chatbot real.") from exc
    return _chat_chain

def parse_bot_response(raw_response: str):
    points = 0
    text = raw_response

    if "[PISTA_ENTREGADA]" in text:
        points = -1
        text = text.replace("[PISTA_ENTREGADA]", "").strip()

    if "[RESPUESTA_CORRECTA]" in text:
        points = 5
        text = text.replace("[RESPUESTA_CORRECTA]", "").strip()

    return text, points


def invoke_chatbot(user_input: str, current_shape: str = "cuadrado"):
    chain = get_chat_chain()

    if hasattr(chain, "invoke"):
        raw_response = chain.invoke({"user_input": user_input, "current_shape": current_shape})
    else:
        raw_response = chain.run({"user_input": user_input, "current_shape": current_shape})

    if hasattr(raw_response, "content"):
        raw_response = raw_response.content

    return parse_bot_response(raw_response)


def main():
    try:
        text, points = invoke_chatbot("como juego?")
        print("RESPUESTA:")
        print(text)
        print(f"PUNTOS: {points}")
    except Exception as exc:
        error_message = str(exc)
        print("ERROR AL INVOCAR EL CHATBOT:")
        print(error_message)
        if "GROQ_API_KEY" in error_message:
            print("Configura la variable de entorno GROQ_API_KEY con una clave válida de Groq.")
        elif "401" in error_message or "invalid_api_key" in error_message.lower():
            print("La clave de Groq proporcionada no es válida. Verifica que sea correcta y que tenga acceso a la API.")
        else:
            traceback.print_exc()


if __name__ == "__main__":
    main()
