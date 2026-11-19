"""Pruebas unitarias para el generador automático de AST Repo-Map."""

import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "generar_repo_map.py"
MAP_PATH = ROOT_DIR / "PROJECT_MAP.md"


def test_generacion_project_map():
    """Verifica que el script genera PROJECT_MAP.md con símbolos clave y ahorro."""
    res = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stderr
    assert MAP_PATH.exists()

    contenido = MAP_PATH.read_text(encoding="utf-8")
    for simbolo in ("GrafoLogistico", "def dijkstra(", "def floyd_warshall(", "aristas.csv"):
        assert simbolo in contenido, f"Falta símbolo esperado en PROJECT_MAP.md: {simbolo}"


def test_modo_hook_retorna_json_valido():
    """Verifica que el modo --hook cumple el contrato de Antigravity (stdout JSON `{}`)."""
    res = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--hook"],
        input='{"hookEventName": "SessionStart"}',
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert res.returncode == 0, res.stderr
    data = json.loads(res.stdout.strip())
    assert data == {}
