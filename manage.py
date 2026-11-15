#!/usr/bin/env python
import os
import sys

# Evitar importaciones globales de librerías pesadas que pueden fallar al arrancar el servidor.
# Los módulos como transformers / sentence_transformers deben cargarse solo cuando sean necesarios.
if __name__ == "__main__":
    # Start the Django management entrypoint.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    print(sys.argv)
    execute_from_command_line(sys.argv)
