"""
Generador automático del Mapa Sintáctico del Proyecto (AST Repo-Map).

Recorre `main.py`, `src/`, `scripts/`, `tests/` y `data/` usando el módulo nativo
`ast` de Python (cero dependencias externas) y produce `PROJECT_MAP.md` con:
  - Clases, métodos, funciones, firmas con type hints y rangos exactos de líneas.
  - Esquema de archivos CSV (columnas y conteo de filas).
  - Inventario compacto de archivos pesados (GeoJSON, shapefiles, HTML, cachés)
    para evitar que los agentes de IA los abran completos y desperdicien tokens.

Uso:
    python scripts/generar_repo_map.py              # Regenera siempre
    python scripts/generar_repo_map.py --if-stale   # Solo si algún fuente cambió
    python scripts/generar_repo_map.py --hook       # Modo hook de Antigravity (stdout JSON `{}`)
"""

from __future__ import annotations

import ast
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT_DIR / "PROJECT_MAP.md"

SOURCE_DIRS = ["src", "scripts"]
TEST_DIR = "tests"
CSV_DIR = ROOT_DIR / "data" / "csv"
HEAVY_DIRS = [
    ROOT_DIR / "data" / "geojson",
    ROOT_DIR / "data" / "shapefiles",
    ROOT_DIR / "data" / "output",
]


def _primera_linea_doc(nodo: ast.AST) -> str:
    """Extrae la primera línea útil del docstring de un nodo AST."""
    doc = ast.get_docstring(nodo)
    if not doc:
        return ""
    for linea in doc.splitlines():
        limpia = linea.strip(" \t║│")
        if not limpia or set(limpia) <= set("=-─═╔╗╚╝*#_~ "):
            continue
        return limpia[:110] + ("…" if len(limpia) > 110 else "")
    return ""


def _formatear_firma(nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Construye la firma compacta de una función o método con type hints."""
    args = nodo.args
    partes: List[str] = []

    pos_args = list(args.posonlyargs) + list(args.args)
    defaults = [None] * (len(pos_args) - len(args.defaults)) + list(args.defaults)

    for arg, default in zip(pos_args, defaults):
        texto = arg.arg
        if arg.annotation is not None:
            texto += f": {ast.unparse(arg.annotation)}"
        if default is not None:
            val = ast.unparse(default)
            if len(val) > 24:
                val = "…"
            texto += f" = {val}"
        partes.append(texto)

    if args.vararg is not None:
        v = f"*{args.vararg.arg}"
        if args.vararg.annotation is not None:
            v += f": {ast.unparse(args.vararg.annotation)}"
        partes.append(v)
    elif args.kwonlyargs:
        partes.append("*")

    for kwarg, kwdef in zip(args.kwonlyargs, args.kw_defaults):
        texto = kwarg.arg
        if kwarg.annotation is not None:
            texto += f": {ast.unparse(kwarg.annotation)}"
        if kwdef is not None:
            val = ast.unparse(kwdef)
            if len(val) > 24:
                val = "…"
            texto += f" = {val}"
        partes.append(texto)

    if args.kwarg is not None:
        k = f"**{args.kwarg.arg}"
        if args.kwarg.annotation is not None:
            k += f": {ast.unparse(args.kwarg.annotation)}"
        partes.append(k)

    prefijo = "async def " if isinstance(nodo, ast.AsyncFunctionDef) else "def "
    ret = f" -> {ast.unparse(nodo.returns)}" if nodo.returns is not None else ""
    return f"{prefijo}{nodo.name}({', '.join(partes)}){ret}"


def _extraer_constantes(arbol: ast.Module) -> List[str]:
    """Extrae nombres de constantes top-level en MAYÚSCULAS."""
    constantes: List[str] = []
    for stmt in arbol.body:
        targets = []
        if isinstance(stmt, ast.Assign):
            targets = stmt.targets
        elif isinstance(stmt, ast.AnnAssign) and stmt.target is not None:
            targets = [stmt.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id.isupper() and not t.id.startswith("_"):
                constantes.append(f"{t.id} (L{stmt.lineno})")
    return constantes


def _analizar_archivo_python(ruta: Path) -> Tuple[int, List[str]]:
    """Parsea un archivo Python y devuelve (total_lineas, lineas_markdown)."""
    contenido = ruta.read_text(encoding="utf-8", errors="replace")
    total_lineas = len(contenido.splitlines())
    rel = ruta.relative_to(ROOT_DIR).as_posix()

    try:
        arbol = ast.parse(contenido, filename=rel)
    except SyntaxError as exc:
        return total_lineas, [f"### `{rel}` (L1–L{total_lineas}) — Error de sintaxis: {exc}"]

    salida: List[str] = []
    doc_mod = _primera_linea_doc(arbol)
    encabezado = f"### `{rel}` (`{total_lineas}` líneas)"
    if doc_mod:
        encabezado += f" — {doc_mod}"
    salida.append(encabezado)

    constantes = _extraer_constantes(arbol)
    if constantes:
        vista = ", ".join(constantes[:12])
        if len(constantes) > 12:
            vista += f" (+{len(constantes) - 12} más)"
        salida.append(f"- **Constantes:** `{vista}`")

    for stmt in arbol.body:
        if isinstance(stmt, ast.ClassDef):
            bases = [ast.unparse(b) for b in stmt.bases]
            base_str = f"({', '.join(bases)})" if bases else ""
            doc_c = _primera_linea_doc(stmt)
            rango = f"L{stmt.lineno}-L{stmt.end_lineno}"
            linea_c = f"- `class {stmt.name}{base_str}` `[{rango}]`"
            if doc_c:
                linea_c += f" — {doc_c}"
            salida.append(linea_c)

            for item in stmt.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    firma = _formatear_firma(item)
                    r_m = f"L{item.lineno}-L{item.end_lineno}"
                    doc_m = _primera_linea_doc(item)
                    linea_m = f"  - `{firma}` `[{r_m}]`"
                    if doc_m:
                        linea_m += f" — {doc_m}"
                    salida.append(linea_m)

        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            firma = _formatear_firma(stmt)
            rango = f"L{stmt.lineno}-L{stmt.end_lineno}"
            doc_f = _primera_linea_doc(stmt)
            linea_f = f"- `{firma}` `[{rango}]`"
            if doc_f:
                linea_f += f" — {doc_f}"
            salida.append(linea_f)

    salida.append("")
    return total_lineas, salida


def _analizar_tests() -> Tuple[int, List[str]]:
    """Genera un índice compacto de la suite de pruebas."""
    carpeta = ROOT_DIR / TEST_DIR
    if not carpeta.exists():
        return 0, []

    total_lineas = 0
    salida: List[str] = []
    for ruta in sorted(carpeta.rglob("*.py")):
        if "__pycache__" in ruta.parts or ruta.name == "__init__.py":
            continue
        contenido = ruta.read_text(encoding="utf-8", errors="replace")
        n_lineas = len(contenido.splitlines())
        total_lineas += n_lineas
        rel = ruta.relative_to(ROOT_DIR).as_posix()
        try:
            arbol = ast.parse(contenido, filename=rel)
        except SyntaxError:
            salida.append(f"- `{rel}` ({n_lineas} L)")
            continue

        elementos: List[str] = []
        for stmt in arbol.body:
            if isinstance(stmt, ast.ClassDef):
                n_metodos = sum(
                    1
                    for m in stmt.body
                    if isinstance(m, ast.FunctionDef) and m.name.startswith("test_")
                )
                elementos.append(f"{stmt.name} ({n_metodos} tests, L{stmt.lineno})")
            elif isinstance(stmt, ast.FunctionDef) and stmt.name.startswith("test_"):
                elementos.append(f"{stmt.name} (L{stmt.lineno})")

        resumen = ", ".join(elementos) if elementos else "utilidades"
        salida.append(f"- `{rel}` (`{n_lineas}` L): {resumen}")

    return total_lineas, salida


def _analizar_csvs() -> List[str]:
    """Resume los esquemas (columnas y número de filas) de `data/csv/*.csv`."""
    if not CSV_DIR.exists():
        return []
    lineas = [
        "| Archivo | Filas | Columnas |",
        "| :--- | ---: | :--- |",
    ]
    for ruta in sorted(CSV_DIR.glob("*.csv")):
        rel = ruta.relative_to(ROOT_DIR).as_posix()
        try:
            with ruta.open("r", encoding="utf-8-sig", newline="") as f:
                lector = csv.reader(f)
                cabecera = next(lector, [])
                filas = sum(1 for _ in lector)
            cols = ", ".join(f"`{c}`" for c in cabecera)
            lineas.append(f"| `{rel}` | {filas} | {cols} |")
        except OSError as exc:
            lineas.append(f"| `{rel}` | ? | Error: {exc} |")
    return lineas


def _formato_tamano(n_bytes: int) -> str:
    """Formatea bytes a KB o MB legibles."""
    if n_bytes >= 1024 * 1024:
        return f"{n_bytes / (1024 * 1024):.2f} MB"
    return f"{n_bytes / 1024:.1f} KB"


def _analizar_activos_pesados() -> List[str]:
    """Lista archivos pesados/generados para prevenir lecturas accidentales."""
    lineas = [
        "| Archivo | Tamaño | Nota |",
        "| :--- | ---: | :--- |",
    ]
    encontrados = False
    for carpeta in HEAVY_DIRS:
        if not carpeta.exists():
            continue
        for ruta in sorted(carpeta.iterdir()):
            if not ruta.is_file() or ruta.name.startswith("."):
                continue
            encontrados = True
            rel = ruta.relative_to(ROOT_DIR).as_posix()
            tam = _formato_tamano(ruta.stat().st_size)
            nota = "Archivo binario/generado — no leer completo"
            if ruta.suffix == ".geojson":
                try:
                    data = json.loads(ruta.read_text(encoding="utf-8"))
                    feats = len(data.get("features", []))
                    nota = f"GeoJSON ({feats} features) — consultar vía script"
                except Exception:
                    nota = "GeoJSON — consultar vía script"
            elif ruta.name == "rutas_cache.json":
                try:
                    data = json.loads(ruta.read_text(encoding="utf-8"))
                    nota = f"Caché OSRM/ríos ({len(data)} rutas) — NO borrar ni leer entero"
                except Exception:
                    nota = "Caché OSRM — NO borrar"
            elif ruta.suffix == ".html":
                nota = "HTML generado por pipeline — editar en `src/visualization/`"
            elif ruta.suffix in {".shp", ".dbf", ".shx", ".prj", ".cpg", ".zip"}:
                nota = "Geometría SIG fluvial — procesar vía `route_geometry.py`"
            lineas.append(f"| `{rel}` | {tam} | {nota} |")

    return lineas if encontrados else ["_(Sin activos pesados detectados)_"]


def _archivos_monitoreados() -> List[Path]:
    """Devuelve la lista de archivos fuente que invalidan el mapa si cambian."""
    archivos: List[Path] = []
    main_py = ROOT_DIR / "main.py"
    if main_py.exists():
        archivos.append(main_py)
    for carpeta in SOURCE_DIRS + [TEST_DIR]:
        p = ROOT_DIR / carpeta
        if p.exists():
            archivos.extend(
                r for r in p.rglob("*.py") if "__pycache__" not in r.parts
            )
    if CSV_DIR.exists():
        archivos.extend(CSV_DIR.glob("*.csv"))
    return archivos


def esta_desactualizado() -> bool:
    """Retorna True si `PROJECT_MAP.md` no existe o algún archivo fuente es más reciente."""
    if not OUTPUT_PATH.exists():
        return True
    mtime_mapa = OUTPUT_PATH.stat().st_mtime
    for archivo in _archivos_monitoreados():
        try:
            if archivo.stat().st_mtime > mtime_mapa:
                return True
        except OSError:
            continue
    return False


def generar_mapa() -> Tuple[int, int]:
    """Genera `PROJECT_MAP.md` y devuelve (lineas_codigo_indexadas, lineas_mapa)."""
    archivos_py: List[Path] = []
    main_py = ROOT_DIR / "main.py"
    if main_py.exists():
        archivos_py.append(main_py)

    for carpeta in SOURCE_DIRS:
        p = ROOT_DIR / carpeta
        if not p.exists():
            continue
        for ruta in sorted(p.rglob("*.py")):
            if "__pycache__" in ruta.parts or ruta.name == "__init__.py":
                continue
            archivos_py.append(ruta)

    total_lineas_codigo = 0
    bloques_codigo: List[str] = []
    for ruta in archivos_py:
        n_lin, bloque = _analizar_archivo_python(ruta)
        total_lineas_codigo += n_lin
        bloques_codigo.extend(bloque)

    n_lin_tests, bloque_tests = _analizar_tests()
    total_lineas_codigo += n_lin_tests

    bloque_csvs = _analizar_csvs()
    bloque_pesados = _analizar_activos_pesados()

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    cuerpo: List[str] = [
        "# PROJECT_MAP.md — Mapa Sintáctico Automático (AST Repo-Map)",
        "",
        f"> **Generado automáticamente:** `{ahora}` vía `scripts/generar_repo_map.py`  ",
        "> **Propósito:** Permite a cualquier agente de Antigravity navegar clases, firmas y líneas exactas sin abrir archivos completos ni desperdiciar tokens.",
        "",
        "## 1. Arquitectura Python (Firmas y Rangos de Línea)",
        "",
        *bloques_codigo,
        "## 2. Esquema de Datos CSV (`data/csv/`)",
        "",
        *bloque_csvs,
        "",
        "## 3. Suite de Pruebas (`tests/`)",
        "",
        *bloque_tests,
        "",
        "## 4. Activos Pesados y Salidas Generadas (NO leer completos)",
        "",
        *bloque_pesados,
        "",
    ]

    # Insertar estadística real de compresión en la cabecera
    lineas_mapa = len(cuerpo) + 2
    reduccion = (
        max(0.0, (1.0 - (lineas_mapa / total_lineas_codigo)) * 100.0)
        if total_lineas_codigo > 0
        else 0.0
    )
    cuerpo.insert(
        4,
        f"> **Compresión de contexto:** `{total_lineas_codigo:,}` líneas de código Python condensadas en `{lineas_mapa}` líneas (**{reduccion:.1f}% de ahorro**).",
    )
    cuerpo.insert(5, "")

    OUTPUT_PATH.write_text("\n".join(cuerpo), encoding="utf-8")
    return total_lineas_codigo, lineas_mapa


def main(argv: Optional[List[str]] = None) -> int:
    """Punto de entrada CLI y soporte para hooks de Antigravity."""
    args = set(argv if argv is not None else sys.argv[1:])
    modo_hook = "--hook" in args
    solo_si_cambio = "--if-stale" in args or modo_hook

    if modo_hook:
        try:
            if not solo_si_cambio or esta_desactualizado():
                generar_mapa()
        except Exception:
            pass
        print("{}")
        return 0

    if solo_si_cambio and not esta_desactualizado():
        print("[OK] PROJECT_MAP.md ya está actualizado.")
        return 0

    total_cod, total_map = generar_mapa()
    ahorro = (1.0 - total_map / total_cod) * 100.0 if total_cod else 0.0
    print(
        f"[OK] PROJECT_MAP.md generado: {total_cod:,} líneas -> {total_map} líneas ({ahorro:.1f}% ahorro)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
