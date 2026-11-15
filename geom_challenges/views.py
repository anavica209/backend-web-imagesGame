"""

Module to model de web view.

"""

import random
import logging
import time
import uuid
from typing import List

from django.core.files.base import ContentFile
from django.http import JsonResponse
from rest_framework.decorators import api_view

from .services.chatbot_service import get_chat_chain, parse_bot_response
from .constants import BORDER_WIDTH, FIGURE_NAMES, SHAPE_COLORS
from .services.figure_generator import FiguresGenerator
from .models import ImageTask


generator = FiguresGenerator()
logger = logging.getLogger(__name__)


def _random_shape_color() -> str:
    return random.choice(SHAPE_COLORS)


def _build_options(correct_answer: str) -> List[str]:
    """Build a randomized list of four answer options containing the correct one."""
    options = [correct_answer]
    distractors = [name for name in FIGURE_NAMES if name != correct_answer]
    random.shuffle(distractors)
    while len(options) < 4:
        options.append(distractors.pop())
    random.shuffle(options)
    return options


@api_view(["GET"])
def next_challenge(request):
    """Create a new challenge task and return its image and answer options."""
    request_id = str(uuid.uuid4())
    started_at = time.perf_counter()
    correct_answer = random.choice(FIGURE_NAMES)
    prompt = f"Draw a {correct_answer}"

    logger.info(
        "challenge_generation_started request_id=%s method=%s path=%s figure=%s prompt=%s",
        request_id,
        request.method,
        request.path,
        correct_answer,
        prompt,
    )

    task = ImageTask.objects.create(
        prompt=prompt,
        status="processing",
        correct_answer=correct_answer,
    )

    try:
        image_bytes, extension = generator.build_image(correct_answer, _random_shape_color(), border_width=BORDER_WIDTH)
        file_name = f"{prompt}_{extension}.png"
        task.image_file.save(file_name, ContentFile(image_bytes), save=False)
        task.image_url = request.build_absolute_uri(task.image_file.url)
        task.status = "completed"
        task.save(update_fields=["image_file", "image_url", "status"])
    except Exception:
        task.status = "failed"
        task.save(update_fields=["status"])
        logger.exception(
            "challenge_generation_failed request_id=%s task_id=%s figure=%s duration_ms=%.2f",
            request_id,
            task.pk,
            correct_answer,
            (time.perf_counter() - started_at) * 1000,
        )
        return JsonResponse({"detail": "No se pudo generar la imagen"}, status=500)

    options = _build_options(task.correct_answer)
    logger.info(
        "challenge_generation_completed request_id=%s task_id=%s figure=%s options=%s image_extension=%s image_size_bytes=%s duration_ms=%.2f status_code=200",
        request_id,
        task.pk,
        task.correct_answer,
        options,
        extension,
        len(image_bytes),
        (time.perf_counter() - started_at) * 1000,
    )

    return JsonResponse(
        {
            "id": str(prompt),
            "imageUrl": task.image_url,
            "correctAnswer": task.correct_answer,
            "options": options,
        }
    )


@api_view(["POST"])
def chat(request):
    request_id = str(uuid.uuid4())
    started_at = time.perf_counter()
    user_message = request.data.get("mensaje") or request.data.get("message")
    current_shape = request.data.get("figura_actual") or request.data.get("current_shape")

    logger.info(
        "chat_interaction_received request_id=%s method=%s path=%s user_message=%s current_shape=%s",
        request_id,
        request.method,
        request.path,
        user_message,
        current_shape,
    )

    if not user_message:
        logger.warning("chat_interaction_rejected request_id=%s reason=missing_user_message status_code=400", request_id)
        return JsonResponse({"detail": "Falta el mensaje del usuario."}, status=400)
    if not current_shape:
        logger.warning("chat_interaction_rejected request_id=%s reason=missing_current_shape status_code=400", request_id)
        return JsonResponse({"detail": "Falta la figura actual."}, status=400)

    try:
        chain = get_chat_chain()
        raw_response = chain.run({"user_input": user_message, "current_shape": current_shape})
        response_text, points = parse_bot_response(raw_response)
        if "[RESPUESTA_INCORRECTA]" in raw_response:
            result = "respuesta_incorrecta"
        else:
            result = {5: "respuesta_correcta", -1: "pista", 0: "respuesta_normal"}.get(points, "respuesta_normal")

        logger.info(
            "chat_interaction_completed request_id=%s current_shape=%s result=%s points=%s response=%s response_length=%s duration_ms=%.2f status_code=200",
            request_id,
            current_shape,
            result,
            points,
            response_text,
            len(response_text),
            (time.perf_counter() - started_at) * 1000,
        )

        return JsonResponse(
            {
                "respuesta": response_text,
                "puntos_a_sumar_o_restar": points,
            }
        )
    except Exception as e:
        logger.exception(
            "chat_interaction_failed request_id=%s current_shape=%s duration_ms=%.2f status_code=500 error=%s",
            request_id,
            current_shape,
            (time.perf_counter() - started_at) * 1000,
            str(e),
        )
        return JsonResponse(
            {
                "detail": "Error al procesar la consulta del chatbot.",
                "error": str(e),
                "hint": "Compruebe que el backend tenga instaladas las dependencias de embeddings y que el entorno de Python sea compatible.",
            },
            status=500,
        )
