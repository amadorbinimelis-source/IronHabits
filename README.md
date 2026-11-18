# Rutina

PWA personal de hábitos con el plan exacto de cada día (entreno, francés, inglés B2, estudio y dx diferencial).

- **App:** `index.html` (un solo archivo, datos en el móvil con localStorage).
- **Plan:** `plan.json`, generado con `python gen/build_plan.py`.
- **Calendario:** `rutina.ics`, generado con `python gen/build_ics.py` (no se sube: lo crea la publicación).
- **Pruebas:** `python tests/test_agenda.py` y `python tests/test_app.py` (necesita un servidor en el puerto 8765).
- **Publicación:** cada push a `main` pasa las pruebas y publica en GitHub Pages (`.github/workflows/publicar.yml`).

Historial de cambios: `CHANGELOG.md`.
