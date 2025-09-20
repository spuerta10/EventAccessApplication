# ADR 4: Arquitectura para la aplicación móvil de cara al cliente
- Estado: propuesto
- Responsables: mrodriguev@eafit.edu.co, spuertaf@eafit.edu.co
- Fecha: 2025-sept-19

## Contexto y planteamiento del problema
La App Cliente es utilizada por los asistentes a eventos para:
- Registrar (dar de alta) sus tickets.
- Almacenar localmente la información y credenciales de acceso.
- Transferir dichas credenciales al staff el día del evento mediante NFC, QR u otro protocolo.
- Consultar el historial de tickets y notificaciones.

A diferencia de la App Staff, la App Cliente no valida tickets, sino que funciona como un **contenedor seguro de credenciales** y un **módulo de interacción con el backend** (cuando hay conexión) o con la App Staff (cuando es offline).  

La arquitectura debe ser:
- **Segura**: proteger las seeds/credenciales contra clonación o manipulación.
- **Extensible**: soportar nuevos protocolos de transferencia (ej. QR, BLE).
- **Mantenible**: separar responsabilidades de UI, lógica y almacenamiento.
- **Portátil**: multiplataforma (Android, iOS, frameworks como Flutter o React Native).

## Impulsores de la decisión
- Separar la lógica de presentación de la gestión de credenciales.
- Evitar exponer directamente datos sensibles (tickets, seeds).
- Facilitar la sincronización de tickets con backend en caso de conexión.
- Facilitar la prueba de componentes clave (transferencia NFC, almacenamiento seguro).

## Opciones consideradas
### Opción 1: MVC
- Bueno: Simplicidad, rápida curva de aprendizaje.
- Malo: Riesgo de controladores demasiado grandes.
- Malo: Poca claridad al manejar credenciales y sincronización.

### Opción 2: MVVM + repositorios
- Bueno: Patrón ampliamente adoptado en móviles.
- Bueno: Separa UI (Views) de la lógica de presentación (ViewModels).
- Bueno: Uso de repositorios para abstraer acceso a datos (local DB, backend).
- Malo: Mayor complejidad que MVC.
- Malo: Requiere disciplina en manejo de dependencias.

### Opción 3: Clean Architecture adaptada a móvil
- Bueno: Aísla completamente el dominio (credenciales, tickets) de la UI y frameworks.
- Bueno: Facilita añadir protocolos de transferencia como plugins.
- Bueno: Facilita pruebas unitarias.
- Malo: Mayor esfuerzo inicial y curva de aprendizaje.
- Malo: Puede ser percibida como sobreingeniería si el alcance fuese muy reducido.

## Decisión
Se selecciona **MVVM con repositorios** como arquitectura para la App Cliente.  

## Razón fundamental
- Provee un **equilibrio entre simplicidad y separación de responsabilidades**.  
- La UI (Views) se mantiene reactiva y ligera.  
- La lógica de presentación vive en los **ViewModels**, que orquestan las operaciones.  
- El acceso a datos se abstrae en **repositorios**, los cuales deciden si leer del **backend** o de la **DB local segura (SQLite/Realm/Keychain/EncryptedSharedPreferences)**.  
- MVVM es un estándar en desarrollo móvil moderno, con soporte en Android, iOS y frameworks multiplataforma.  
- Se evita la sobrecarga de Clean Architecture completa, ya que el dominio central (validación) no vive aquí, sino en la App Staff.  

## Consecuencias
- UI desacoplada y fácil de probar.  
- Posibilidad de soportar múltiples protocolos de transferencia con adaptadores en el repositorio.  
- Seguridad reforzada al centralizar el almacenamiento de seeds/credenciales en repositorios con acceso controlado.  
- Mayor mantenibilidad que MVC puro, pero menor complejidad que Clean Architecture.  
