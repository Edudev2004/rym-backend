"""
Configuración y fixtures para pruebas con pytest
"""
import sys
import os

# Agregar rym-backend al path para que las importaciones funcionen limpiamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
