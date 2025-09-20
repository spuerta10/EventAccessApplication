# ADR 2: Uso del estilo de arquitectura MVC para la aplicación móvil Staff
- Estado: propuesto
- Responsables: mrodriguev@eafit.edu.co, spuertaf@eafit.edu.co
- Fecha: 2025-sept-19

## Contexto y planteamiento del problema
La aplicación móvil Staff es el medio por el cual los miembros del staff validan tickets el día del evento.  
El **core de validación** ya existe como una librería externa con arquitectura hexagonal y es consumido por la app.  
Por tanto, la app móvil necesita un estilo de arquitectura que organice la UI, la lógica de presentación y la comunicación con el core, pero **sin duplicar responsabilidades del dominio**.  

Se requiere que:
- La UI sea simple y reactiva para el staff.
- La app actúe principalmente como orquestadora: recibe tickets vía NFC, invoca la librería de validación y muestra el resultado.
- Sea fácil de mantener y extender para manejar más protocolos de entrada (ej. QR además de NFC).
- Mantenga la lógica de negocio aislada en el core (sin mezclar reglas en la capa móvil).

## Impulsores de la decisión
- Evitar sobreingeniería en la app móvil, dado que el dominio vive en la librería core.
- Necesidad de claridad en la separación entre UI, controladores y la invocación al core.
- Rapidez de implementación y facilidad de adopción por el equipo de desarrollo móvil.
- El patrón elegido debe facilitar pruebas de integración con el core.

## Opciones consideradas
- **MVC** (Modelo–Vista–Controlador).
- **MVVM** (Model–View–ViewModel).
- **MVP** (Model–View–Presenter).

## Pros y contras de las opciones
### MVC (seleccionada)
- Bueno: Simplicidad y bajo coste de implementación.
- Bueno: El controlador orquesta la comunicación con el core, manteniendo la UI ligera.
- Bueno: Se ajusta a frameworks móviles comunes (Android/iOS, Flutter, React Native).
- Malo: Riesgo de que el controlador crezca demasiado (god class) si no se limita estrictamente su responsabilidad.

### MVVM
- Bueno: Facilita pruebas unitarias sobre la lógica de presentación (ViewModels).
- Bueno: UI reactiva, especialmente útil con data-binding.
- Malo: Introduce complejidad innecesaria dado que el core ya encapsula la lógica de negocio.

### MVP
- Bueno: Buena separación entre vista y lógica de presentación.
- Malo: Requiere más código “boilerplate” que MVC.
- Malo: Similar a MVVM, no aporta un valor diferencial claro cuando el core ya abstrae el dominio.

## Decisión
Se adopta **MVC para la App Staff**, donde:
- **Vista (View)**: pantallas móviles (formularios de escaneo NFC, feedback visual).
- **Controlador (Controller)**: recibe eventos de la vista, invoca la librería core a través de sus puertos y actualiza la vista.
- **Modelo (Model)**: objetos simples que representan datos para la vista (DTOs, no entidades de dominio).

## Consecuencias
- Implementación rápida y clara, con curva de aprendizaje baja.
- El core sigue siendo el responsable exclusivo de la lógica de negocio.
- Riesgo de crecimiento excesivo en los controladores si no se controla el alcance.
- Extensible a nuevos protocolos de entrada con mínima modificación en la app (agregar un nuevo controlador o módulo de entrada).