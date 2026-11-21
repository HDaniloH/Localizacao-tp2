"""Configuração do Sphinx para geração automática da documentação do backend."""

import os
import sys

sys.path.insert(0, os.path.abspath("../../backend"))

project = "Sistema de Ocorrências Urbanas - TP2"
copyright = "2026, Grupo TP2 - UnB"
author = "Equipe TP2"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

html_theme = "sphinx_rtd_theme"
