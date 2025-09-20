# ADR 3: Selección de base de datos para almacenamiento local de tickets en App Staff
- Estado: propuesto
- Responsables: mrodriguev@eafit.edu.co, spuertaf@eafit.edu.co
- Fecha: 2025-sept-19

## Contexto y planteamiento del problema
La App Staff debe validar tickets incluso en entornos **sin conexión a internet**.  
Esto implica que la aplicación debe almacenar localmente:
- Tickets registrados (con su estado: válido, usado, inválido).
- Referencias a seeds para validación de seguridad.
- Resultados de validaciones para sincronización posterior con la nube.  

La base de datos debe:
- Funcionar offline-first con sincronización eventual.
- Ser rápida y confiable en validaciones en tiempo real.
- Integrarse fácilmente con la aplicación móvil (Android/iOS).
- Escalar en volumen de tickets sin degradar el rendimiento.

## Impulsores de la decisión
- **Performance:** validación en menos de 300ms en dispositivos móviles.
- **Consistencia:** garantizar que un ticket validado no pueda usarse nuevamente.
- **Portabilidad:** la solución debe funcionar en Android, iOS y frameworks multiplataforma.
- **Soporte:** debe ser una tecnología madura, con comunidad amplia y soporte a largo plazo.

## Opciones consideradas
### Opción 1: Relacional (SQLite/Room/Core Data)
- Bueno: Amplio soporte nativo en Android e iOS.
- Bueno: Queries flexibles y robustas (ej. búsqueda por ID, filtros por estado).
- Bueno: Confiabilidad y madurez probada en producción.
- Malo: Verbosidad en implementación si no se usa un ORM.
- Malo: Overhead inicial en definir esquemas.

### Opción 2: Orientada a objetos (Realm, ObjectBox)
- Bueno: Muy rápida y optimizada para móvil.
- Bueno: API sencilla, acceso directo con objetos.
- Malo: Dependencia en librerías de terceros menos estándar.
- Malo: Menor interoperabilidad multiplataforma comparada con SQLite.
- Malo: Riesgo de lock-in tecnológico.

### Opción 3: Cache / clave-valor (Hive, MMKV, SharedPreferences)
- Bueno: Simplicidad de implementación.
- Bueno: Ideal para configuraciones ligeras.
- Malo: No apto para estructuras complejas ni queries avanzadas.
- Malo: Riesgo de inconsistencia al manejar grandes volúmenes de tickets.

## Decisión
Se selecciona **SQLite con ORM (Room en Android, Core Data en iOS, o plugin SQLite en multiplataforma)** como base de datos local para la App Staff.  

## Razón fundamental
SQLite fue seleccionada porque:
1. Es la opción **más madura y estandarizada** en entornos móviles, reduciendo riesgo técnico.  
2. Ofrece **soporte multiplataforma** (Android, iOS, Flutter, React Native).  
3. Soporta **queries complejas** necesarias para validaciones rápidas (ej. `SELECT ticket WHERE id=... AND gate=...`).  
4. Permite **alta confiabilidad en entornos offline**, evitando inconsistencias de estado.  
5. La comunidad y soporte son más amplios que los de soluciones alternativas, reduciendo deuda técnica a largo plazo.  

## Consecuencias
- La App Staff tendrá almacenamiento local confiable y consistente.  
- Soporte a operaciones críticas (buscar, actualizar estado de ticket, invalidar duplicados) de forma eficiente.  
- Flexibilidad para sincronización eventual con backend central.  
- Coste inicial de configuración mayor que otras alternativas, pero con beneficios en estabilidad y mantenibilidad.  