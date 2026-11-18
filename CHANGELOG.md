# Rutina · Changelog

## v1.7 · 18 nov 2026
- Publicación en GitHub Pages con GitHub Actions: pruebas automáticas antes de cada publicación.
- `gen/build_ics.py` genera `rutina.ics` (hábitos y compromisos fijos, zona Europe/Madrid, aviso −5 min, plan del día en la descripción).
- Ajustes › «Suscribir el calendario»: enlace webcal para iPhone y URL para Google Calendar.

## v1.6.1 · 18 nov 2026
- Navegación de semanas visible: botones «‹ Anterior» / «Siguiente ›», etiqueta relativa con rango de fechas (toca para volver a hoy) y gesto de deslizar.

## v1.6 · 18 nov 2026 (plan v10)
- Plan completo por hábito (`fullPlan`): todas las fechas (programa, fechas sueltas, programación, movidos, extras y registros) hasta la meta, agrupadas por mes, con estado, buscador y filtros.
- Meta por hábito (`goal` en el plan): cuenta atrás de días, semanas y sesiones.
- Acceso desde el detalle del hábito y desde el menú de cada tarjeta.

## v1.5 · 18 nov 2026
- Total semanal por hábito (minutos): objetivo = suma de bloques planificados (anular no lo baja; pausa sí), hecho = `e.mins` / `e.v` / duración del bloque.
- Un día programado sin hacer solo es fallo si la semana ya terminó y no se llegó al total (`missCounts`); rachas, % y revisión lo aplican.
- «⏱ Tiempo que has hecho» en el menú de cada hábito; tarjeta «Esta semana» en Hoy; historial de 10 semanas en el detalle.
- Tests: 7 casos nuevos (compensación del francés, pausa vs anular).

## v1.4.1 · 18 nov 2026
- Regla: un día con el hábito completado siempre cuenta (racha, %, total, revisión), aunque se haya cambiado la hora, movido, anulado después o no estuviera programado.
- Sesiones extra (`in:<id>` con `extra:true`): botón «➕ Añadir sesión extra» en Hoy; hueco libre automático; si no se hace, no cuenta como fallo; «Quitar sesión extra» en la agenda.
- Bloqueado mover un hábito ya completado ese día.
- Tests: 7 casos nuevos con el boxeo.

## v1.4 · 18 nov 2026 (plan v9)
- Hoy: tarjeta «Ahora / Después» con cuenta atrás; banners de revisión semanal, copia de seguridad y fin de agenda.
- Día mínimo (versión corta por hábito, `e.min`), métricas por hábito (`e.m`, `e.note`) con último, mejor y gráfica.
- Revisión semanal con «Copiar resumen para Claude».
- Deshacer (toast con acción), diálogo propio en lugar de `confirm()`.
- Pausas con motivo y rango; exportar agenda a .ics con alarma −5 min; notificaciones con la app abierta; aviso al cumplir el cronómetro y píldora flotante.
- Agenda: vista 3 días, «A mañana» con búsqueda de hueco libre, aviso de clases sin cargar.
- Clase anulada → fuerza pasa a sesión completa (`alt`).
- Mapas de calor y estadísticas desde el inicio de cada hábito; texto de frecuencia legible; tarjetas plegables.
- `userEdited`: las ediciones manuales sobreviven a actualizaciones del plan.
- Esquema 3: plan y agenda en clave aparte (`rutina_plan_v1`); migración automática.
- Plan hasta el 20 jun 2027.

## v1.3.1 · 18 nov 2026
- Vista semana tipo Google Calendar: horas marcadas, bloques con nombre y hora, solo lo importante.
- Vista día: cada hora en su franja con la hora bien visible.

## v1.3 · 18 nov 2026
- Nueva pestaña **Agenda**: día hora a hora (comidas, trayectos, clases, fútbol, partido, sueño y hábitos) y vista semanal.
- Toca cualquier bloque: ver qué toca, anularlo, cambiar la hora o moverlo de día.
- Los cambios se reflejan en Hoy (orden por hora), rachas y estadísticas; un día anulado no cuenta como fallo.
- Guía «Antes de empezar» en cada hábito.
- Datos versionados (esquema 2) con migraciones automáticas.
- Tests: `tests/test_agenda.py` (revisa la agenda) y `tests/test_app.py` (prueba la app en un navegador).

## v1.2 · 18 nov 2026
- Plan completo cargado desde plan.json: entreno, francés (HyperLingua), inglés (B2 First), estudio, diagnóstico diferencial.

## v1.0 · 18 nov 2026
- Primera versión: hábitos, rachas, mapas de calor, estadísticas, copias de seguridad.
