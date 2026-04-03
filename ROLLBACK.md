# 🛡️ Protocolo de Rollback - Sistema de Alquiler (videoclub_project)

Este documento define los procedimientos de emergencia para restaurar la operatividad del sistema ante fallos críticos en producción.

---

### 1. Detección de Fallos
Si el sistema presenta errores tras un despliegue, ejecutar:
* `python manage.py check` (Verificación de integridad).
* `python manage.py test tienda` (Validación de lógica de negocio).

### 2. Rollback de Código (Git)
Si el error es de lógica o sintaxis:
1. Listar versiones: `git log --oneline -n 5`
2. Regresar a versión estable: `git reset --hard [HASH_ESTABLE]`
3. Reiniciar el servicio: `sudo systemctl restart gunicorn`

### 3. Rollback de Base de Datos (Migraciones)
Si el error afecta el esquema de la base de datos:
1. Listar migraciones: `python manage.py showmigrations tienda`
2. Revertir a la migración estable: `python manage.py migrate tienda [NOMBRE_MIGRACION]`

### 4. Verificación de Salud
Tras cualquier rollback, es **obligatorio** verificar:
* **Integridad de Datos:** `python manage.py check` (Tarea 11)
* **Regresión de Bugs:** `python manage.py test tienda` (Tarea 10)

---
*Documentado para garantizar la continuidad operativa en Iquitos.*