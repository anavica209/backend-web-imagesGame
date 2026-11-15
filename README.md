# Geometry Challenge Backend

This project provides a simple Django REST API that generates mock geometric challenge images and returns randomized answer options.

## Requirements
- Python 3.13+
- pip

## Install dependencies
From the backend folder, run:

```bash
pip install -r requirements.txt
```

## Configure the chatbot
Copy `.env.example` to `.env` and add your Groq API key:

```powershell
Copy-Item .env.example .env
```

Then set `GROQ_API_KEY` in `.env`. Keep `.env` private; it is excluded by `.gitignore`.

## Run the server
```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The API will be available at:
- http://127.0.0.1:8000/api/next-challenge/

`GET /api/next-challenge/` returns a challenge with `id`, `imageUrl`, and
`options`. The correct answer is not included in this response.

Submit an answer with `POST /api/challenges/{challengeId}/answer/` and a JSON
body containing `answer`. A correct answer adds 5 points, increments the
streak, and returns the next challenge. An incorrect answer leaves the score
unchanged, resets the streak, and returns `nextChallenge: null`. The score,
streak, and active challenge are tracked in the Django session.

## Stop the server
If the server is running in a terminal, press:

```bash
Ctrl + C
```

## Restart the server
Run the start command again:
## PS C:\Users\anavi\My Code\backend> .\.venv\Scripts\python.exe .\manage.py runserver 0.0.0.0:8000
## python -m geom_challenges.services.chatbot_service
```bash
python manage.py runserver 0.0.0.0:8000
```

## Run tests
```bash
python manage.py test geom_challenges
```

## Nuevas funcionalidades añadidas
- Se agregó un endpoint de chat RAG en `api/chat/` para responder preguntas sobre los PDFs de `pdf_files/`.
- El backend usa LangChain con Groq para chat y embeddings localmente con Chroma.
- El puntaje se ajusta con reglas de juego: `-1` por solicitar pista y `+5` por respuesta correcta.
- Asegúrate de instalar las dependencias actualizadas en `requirements.txt` antes de ejecutar el servidor.

La base de datos SQLite se guarda en `data/db.sqlite3`; los archivos multimedia se guardan en `media/`.
