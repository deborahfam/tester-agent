# Auto Tester

Esta carpeta contiene una implementación de referencia de un **generador y validador automático de ejercicios de programación** basado en modelos de lenguaje y un interfaz web mediante **Streamlit**.  La estructura del proyecto sigue la propuesta descrita por el usuario e incluye módulos independientes para extraer información de un PDF, invocar un modelo de lenguaje de gran tamaño (LLM), analizar esquemas de entrada y salida, generar casos de prueba, validar distintas soluciones y empaquetar todo en un proyecto que pueda ejecutarse con PyTest. 

> **Nota:** Muchos de los componentes que interactúan con servicios externos (como la API de OpenRouter) o analizan de forma profunda el enunciado de un ejercicio se encuentran implementados a modo de *plantilla*.  Se han añadido comentarios y puntos de extensión para que el desarrollador los complete según las necesidades reales.  Esta base sirve como guía y punto de partida para un desarrollo más completo.

### Estructura

```
auto_tester/
├── app.py                # Aplicación Streamlit
├── core/
│   ├── extractor.py      # Extracción y normalización de enunciados
│   ├── generator.py      # Cliente de LLM y generación de soluciones/pruebas
│   ├── validator.py      # Ejecución segura y validación diferencial
│   ├── test_builder.py   # Construcción de archivos de pruebas pytest
│   ├── sandbox.py        # Sandbox de ejecución segura
│   └── utils.py          # Funciones auxiliares
├── prompts/
│   ├── generate_solution.txt  # Plantilla de prompt para soluciones
│   ├── generate_tests.txt     # Plantilla de prompt para casos de prueba
│   └── extract_schema.txt     # Plantilla de prompt para extracción de esquema
├── examples/
│   ├── template.py       # Plantilla de código de ejemplo
│   └── sample_problem.pdf# PDF de ejemplo (puedes sustituir por un PDF real)
└── requirements.txt      # Dependencias del proyecto
```

Cada módulo incluye documentación en forma de docstrings para facilitar su comprensión y posterior ampliación.