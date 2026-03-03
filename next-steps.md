# codespaces-lab-boilerplate — Plan de Implementación

> Documento de contexto para Claude. Contiene todas las decisiones arquitectónicas
> tomadas y el plan de implementación paso a paso.
> El usuario escribe el código; Claude guía qué crear y dónde.

---

## ▶️ CONTINUAR AQUÍ

**Fases 1, 2 y 3 completas. Próximo: Fase 4 — `scripts/new-lab.sh`**

---

## Contexto del proyecto

Este es un **boilerplate de laboratorios educativos** que funciona con GitHub Codespaces.
El proyecto de referencia es `codespaces-demo` (lab de Playwright), ubicado en
`WebstormProjects/codespaces-demo`.

**Concepto central:** cada lab vive en su propio repo independiente generado desde este
boilerplate. El boilerplate NO es una dependencia en runtime; es una fábrica de labs.

---

## Decisiones arquitectónicas (no volver a discutir)

### 1. Estructura del repo
Un solo repo con carpetas por tecnología bajo `templates/`. No hay monorepo de labs.

```
codespaces-lab-boilerplate/
├── templates/
│   ├── playwright/          ← migrado y simplificado desde codespaces-demo
│   └── python-ai/           ← nuevo, primer template a construir
├── scripts/
│   └── new-lab.sh           ← copia template + git init
└── docs/
    ├── how-to-create-a-lab.md
    ├── grader-guide.md
    └── template-differences.md
```

### 2. Grader usa el runner nativo de cada tecnología
| Template     | Grader runner        | Comando                      |
|--------------|----------------------|------------------------------|
| playwright   | Playwright test      | `npm run grade`              |
| python-ai    | pytest               | `pytest .grader/checks/`     |
| java-spring  | JUnit 5 + Maven      | `mvn test -Pgrader`          |
| java-quarkus | Quarkus Test + Maven | `mvn quarkus:test -Pgrader`  |

### 3. Patrón unificado de grade.yml
```
checkout → setup (específico por tech) → grade → summarize → post comment → upload artifact
```

El PR comment se genera con un script nativo del template (`summarize.js` / `summarize.py`)
que produce `grader-report.md`. El posting usa la acción
`marocchino/sticky-pull-request-comment@v2` (reemplaza el script JavaScript inline actual).

### 4. Contrato grader-results.json
Todos los templates producen este JSON estándar:
```json
{
  "lab": "string",
  "score": 8,
  "total": 10,
  "duration": 4500,
  "categories": [
    {
      "name": "Structure",
      "score": 3,
      "total": 3,
      "checks": [
        { "name": "descripción del check", "passed": true, "hint": null },
        { "name": "otro check", "passed": false, "hint": "pista para el estudiante" }
      ]
    }
  ]
}
```
El `summarize.*` script de cada template es responsable de producirlo.

### 5. Template es neutro respecto al contenido del lab
- `src/` puede estar vacío, tener código base, o solución de referencia → decisión del profesor
- `.grader/checks/` contiene ejemplos que el profesor reemplaza con sus checks reales
- `docs/instructions.md` es una plantilla en blanco que el profesor completa

### 6. .env para API keys (python-ai)
```bash
# Cloud providers — uncomment the one you use
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Local LLM (if your machine supports it)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2
```
No hay Ollama en el devcontainer por defecto (requiere GPU/RAM que Codespaces no garantiza).
Se documenta como opción local.

---

## Estado actual del proyecto de referencia (codespaces-demo)

### Lo que existe y es reutilizable
- `.grader/checks/structure.test.ts` — valida estructura de directorios
- `.grader/checks/quality.test.ts` — valida patrones de código (locators, faker, imports, etc.)
- `.grader/checks/execution.test.ts` — ejecuta los tests del estudiante y valida resultado
- `.grader/grader.config.ts` — config de Playwright para el grader (reporters: html + json)
- `.devcontainer/devcontainer.json` — Node 22 + Playwright + VS Code extensions
- `package.json` — scripts: test, grade; deps: playwright, faker, typescript

### Lo que necesita cambiar al migrar al template
- `grade.yml`: reemplazar el bloque `actions/github-script@v7` (150 líneas de JS inline)
  con `summarize.js` + `marocchino/sticky-pull-request-comment@v2`
- `grader.config.ts`: remover `baseURL` (es específico del lab, no del template)
- `devcontainer.json`: cambiar el `name` a genérico ("Playwright Lab")
- `package.json`: cambiar `name` a genérico, limpiar descripción

### El PR comment actual (para mantener el mismo estilo)
El comment tiene:
- Score con barra de progreso: `█████░░░░░ 50%`
- Mensaje motivacional según porcentaje
- Secciones colapsables por categoría (`<details>`)
- Tabla de checks con ✅/❌ y hint en caso de fallo
- Bloque de errores de ejecución si aplica
- Sección "Getting Started" si el estudiante no ha escrito código
- Sección de recursos al final

---

## Plan de implementación — Fases en orden

### FASE 1: Fundación del repo ✅
**Archivos creados:**

1. `README.md` ✅
2. `.gitignore` ✅

**Cómo inicializar:**
```bash
cd WebstormProjects/codespaces-lab-boilerplate
git init
git add .
git commit -m "feat: initial boilerplate structure"
```

---

### FASE 2: templates/playwright/ ✅

Migración del proyecto `codespaces-demo` con simplificaciones.

**Estructura completa:**
```
templates/playwright/
├── .devcontainer/
│   └── devcontainer.json          ✅
├── .github/
│   └── workflows/
│       └── grade.yml              ✅
├── .grader/
│   ├── grader.config.ts           ✅
│   ├── summarize.js               ✅
│   └── checks/
│       ├── structure.test.ts      ✅
│       ├── quality.test.ts        ✅
│       └── execution.test.ts      ✅
├── src/
│   ├── pages/.gitkeep             ✅
│   ├── tests/.gitkeep             ✅
│   └── data/.gitkeep              ✅
├── docs/
│   └── instructions.md            ✅
├── .gitignore                     ✅
├── package.json                   ✅
├── playwright.config.ts           ✅
├── tsconfig.json                  ✅
└── README.md                      ✅
```

**grade.yml simplificado (~40 líneas):**
```yaml
name: Grade Lab

on:
  pull_request:
    branches: [main]

permissions:
  pull-requests: write

jobs:
  grade:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: npm

      - name: Install dependencies
        run: npm ci && npx playwright install --with-deps chromium

      - name: Run grader
        run: npm run grade
        continue-on-error: true

      - name: Generate report
        run: node .grader/summarize.js

      - name: Post comment
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: grader
          path: grader-report.md

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: grader-results
          path: grader-results.json
          retention-days: 30
```

**summarize.js — qué debe hacer:**
- Leer `grader-results.json` (producido por Playwright's JSON reporter en grader.config.ts)
  NOTA: el formato de este JSON es el de Playwright (`suites[].suites[].specs[]`), no el
  formato estándar definido en la Sección 4 arriba.
- Parsear las categorías (cada `describe()` es una categoría) y sus specs
- Escribir `grader-results.json` en el formato estándar del boilerplate
- Escribir `grader-report.md` con el PR comment formateado

El PR comment debe mantener el mismo estilo del actual (progress bar, collapsible sections,
hints, etc.) pero el código vive en el script, no en el YAML.

**grader.config.ts ajustado:**
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: './checks',
    fullyParallel: false,
    retries: 0,
    workers: 1,
    reporter: [
        ['html', { outputFolder: '../grader-report', open: 'never' }],
        ['json', { outputFile: '../grader-results-raw.json' }],
        ['list'],
    ],
    // Sin baseURL — el lab específico lo define en su propio playwright.config.ts
});
```
NOTA: el output del grader se llama `grader-results-raw.json` para diferenciarlo del
`grader-results.json` estándar que produce summarize.js.

---

### FASE 3: templates/python-ai/

Template nuevo desde cero.

**Estructura completa:**
```
templates/python-ai/
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   └── workflows/
│       └── grade.yml
├── .grader/
│   ├── conftest.py                ← configuración pytest (fixtures si se necesitan)
│   ├── summarize.py               ← lee pytest JSON → grader-results.json + grader-report.md
│   └── checks/
│       ├── test_structure.py      ← ejemplo: verifica archivos .py en src/, .env.example, etc.
│       ├── test_quality.py        ← ejemplo: verifica imports AI, funciones definidas, etc.
│       └── test_execution.py      ← ejemplo: ejecuta código del estudiante y verifica output
├── src/
│   └── .gitkeep
├── docs/
│   └── instructions.md            ← plantilla en blanco
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

**devcontainer.json para Python AI:**
```json
{
  "name": "Python AI Lab",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "postCreateCommand": "pip install -e '.[dev]'",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.black-formatter"
      }
    }
  }
}
```

**pyproject.toml:**
```toml
[project]
name = "lab-python-ai"
version = "0.1.0"
description = "Python AI Lab"
requires-python = ">=3.12"

dependencies = [
    "langchain>=0.3",
    "langchain-openai>=0.2",
    "langchain-anthropic>=0.2",
    "langchain-community>=0.3",
    "chromadb>=0.5",
    "python-dotenv>=1.0",
    "ollama>=0.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-json-report>=1.5",
]
grader = [
    "pytest>=8.0",
    "pytest-json-report>=1.5",
]

[tool.pytest.ini_options]
testpaths = ["src"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"
```

**grade.yml para python-ai:**
```yaml
name: Grade Lab

on:
  pull_request:
    branches: [main]

permissions:
  pull-requests: write

jobs:
  grade:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install dependencies
        run: pip install -e ".[grader]"

      - name: Run grader
        run: pytest .grader/checks/ -v --json-report --json-report-file=grader-raw.json
        continue-on-error: true

      - name: Generate report
        run: python .grader/summarize.py

      - name: Post comment
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: grader
          path: grader-report.md

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: grader-results
          path: grader-results.json
          retention-days: 30
```

**summarize.py — qué debe hacer:**
- Leer `grader-raw.json` (formato de pytest-json-report)
- El formato de pytest-json-report tiene: `tests[]` con `nodeid`, `outcome` (passed/failed),
  `keywords` (para detectar la categoría via `describe` equivalente en pytest: markers o
  el path del archivo), y `longrepr` para mensajes de error
- Parsear y mapear al formato estándar del boilerplate (Sección 4)
- Escribir `grader-results.json` (formato estándar)
- Escribir `grader-report.md` (mismo estilo visual que el de Playwright)

**Estructura de checks pytest — convención:**
Cada archivo de checks es una categoría. El nombre de la categoría es el `describe`
equivalente, que en pytest se define con una clase o con el nombre del archivo.
Convención: usar clases con `pytest.mark` para agrupar:

```python
# test_structure.py
import pytest

class TestStructure:
    """Structure"""   # ← este docstring es el nombre de la categoría

    def test_src_has_python_files(self):
        """src/ has Python files"""   # ← este docstring es el nombre del check
        ...
```

summarize.py lee el `nodeid` y la clase para determinar categoría y nombre del check.

**Ejemplo test_structure.py:**
```python
import pytest
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent.parent / "src"

class TestStructure:
    """Structure"""

    def test_src_has_python_files(self):
        """src/ has Python files"""
        py_files = list(SRC_DIR.glob("*.py")) + list(SRC_DIR.glob("**/*.py"))
        assert len(py_files) > 0, "No .py files found in src/"

    def test_env_example_exists(self):
        """.env.example exists"""
        env_example = Path(__file__).parent.parent.parent / ".env.example"
        assert env_example.exists(), ".env.example not found in project root"

    def test_requirements_defined(self):
        """pyproject.toml or requirements.txt exists"""
        root = Path(__file__).parent.parent.parent
        assert (root / "pyproject.toml").exists() or (root / "requirements.txt").exists()
```

---

### FASE 3: templates/java-spring/ ✅

Template nuevo para labs de Java con Spring Boot.

**Decisiones arquitectónicas:**
- JDK 21 (LTS, requerido por Spring Boot 3.x)
- Maven como build tool
- Grader: JUnit 5 en mini-proyecto Maven separado en `.grader/`
- Reportes: Surefire XML → `summarize.js` los parsea sin dependencias externas
- grade.yml usa `actions/setup-java@v4`, mismo patrón que playwright

**Estructura completa:**
```
templates/java-spring/
├── .devcontainer/
│   └── devcontainer.json          ✅
├── .github/
│   └── workflows/
│       └── grade.yml              ✅
├── .grader/
│   ├── pom.xml                    ✅
│   ├── summarize.js               ✅
│   └── src/test/java/grader/
│       ├── StructureTest.java     ✅
│       ├── QualityTest.java       ✅
│       └── ExecutionTest.java     ✅
├── src/
│   ├── main/java/.gitkeep         ✅
│   └── test/java/.gitkeep         ✅
├── docs/
│   └── instructions.md            ✅
├── .gitignore                     ✅
├── pom.xml                        ✅
└── README.md                      ✅
```

---

### FASE 4: scripts/new-lab.sh

Script simple interactivo:

```bash
#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOILERPLATE_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧪 Labs Boilerplate — New Lab"
echo ""

# Listar templates disponibles
echo "Available templates:"
ls "$BOILERPLATE_ROOT/templates/"
echo ""

read -p "Template: " TEMPLATE
read -p "Lab name (e.g. lab-02-api-testing): " LAB_NAME
read -p "Output directory [../]: " OUTPUT_DIR
OUTPUT_DIR="${OUTPUT_DIR:-../}"

SOURCE="$BOILERPLATE_ROOT/templates/$TEMPLATE"
TARGET="$OUTPUT_DIR/$LAB_NAME"

if [ ! -d "$SOURCE" ]; then
  echo "❌ Template '$TEMPLATE' not found"
  exit 1
fi

cp -r "$SOURCE" "$TARGET"
cd "$TARGET"
git init
git add .
git commit -m "feat: initial lab structure from $TEMPLATE template"

echo ""
echo "✅ Lab created at $TARGET"
echo ""
echo "Next steps:"
echo "  1. Edit docs/instructions.md   ← define the lab exercise"
echo "  2. Edit .grader/checks/        ← write your grading criteria"
echo "  3. Edit src/ if needed         ← add starter code (optional)"
echo "  4. Push to GitHub as a new repo"
```

---

### FASE 5: docs/

**how-to-create-a-lab.md** — guía para el profesor:
1. Clonar el boilerplate
2. Correr `bash scripts/new-lab.sh`
3. Personalizar `docs/instructions.md`
4. Escribir los checks del grader (con referencia a grader-guide.md)
5. Decidir si agregar código base en `src/`
6. Push a GitHub, habilitar GitHub Actions, configurar como Template Repository (opcional)
7. Compartir link con estudiantes

**grader-guide.md** — cómo escribir checks:
- Estructura de categorías (Structure / Quality / Execution)
- Cómo escribir checks en Playwright (TypeScript)
- Cómo escribir checks en pytest (Python)
- El formato de grader-results.json
- Cómo agregar hints para los estudiantes

**template-differences.md** — diferencias entre templates:
- playwright vs python-ai: runner, lenguaje, estructura de src/, config files
- Qué es igual: grade.yml pattern, grader-results.json, PR comment format, scripts/new-lab.sh

---

## Orden de trabajo recomendado

1. **Fase 1** — repo foundation (5 min)
2. **Fase 2** — playwright template (empezar por grade.yml + summarize.js, que es el cambio más importante)
3. **Fase 3** — python-ai template (empezar por devcontainer + pyproject.toml + grade.yml, luego los checks)
4. **Fase 4** — new-lab.sh
5. **Fase 5** — docs/

Empezar siempre por el "andamiaje" (config files, grade.yml) antes que los checks del grader.

---

## Modo de trabajo — IMPORTANTE

**El usuario escribe todos los archivos. Claude NO crea ni edita archivos del proyecto.**

Claude guía de a un archivo por vez:
1. Dice qué archivo crear y dónde
2. Muestra el contenido exacto listo para copiar
3. Explica brevemente las decisiones relevantes (qué se cambió respecto al demo y por qué)
4. Espera confirmación antes de pasar al siguiente

Si hay decisiones dentro de un archivo (por ejemplo, qué checks incluir), dar una
recomendación concreta con el razonamiento en una línea.

## Notas adicionales para Claude

- El PR comment de Playwright (en `summarize.js`) debe mantener el mismo estilo visual
  que el del proyecto `codespaces-demo` (progress bar, collapsibles, hints, etc.)
- La preferencia del usuario es: simple, mantenible, agradable. Evitar over-engineering.
- El usuario habla español; responder en español salvo que pida inglés.

---

## Referencias útiles

- Proyecto de referencia: `WebstormProjects/codespaces-demo`
- Action para PR comments: https://github.com/marocchino/sticky-pull-request-comment
- pytest-json-report: https://github.com/numirias/pytest-json-report
- devcontainer Python image: `mcr.microsoft.com/devcontainers/python:3.12`
- devcontainer Node image: `mcr.microsoft.com/devcontainers/typescript-node:22`
