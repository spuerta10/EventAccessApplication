# ADR 1: Uso del estilo de arquitectura microkernal + hexagonal
- Estado: propuesto
- Responsables: spuertaf@eafit.edu.co
- Fecha: 2025-sept-15
## Contexto y planteamiento del problema
Event Access Application pretende ser una aplicacion que facilita el acceso a eventos masivos. Los usuarios registran (dan de alta) una entrada o acceso en la aplicacion, posteriomente, en el dia del evento un miembro del Staff registra su asistencia.

Se ha considerado exportar este modelo de negocio a otra clase de escenarios como hoteles, aeropuertos o festivales. 

A su vez, se ha optado por hacer uso de la tecnologia NFC como medio por el cual se comparte la entrada entre el cliente y el revisor. Esto implica que la arquitectura debe ser compatible con dispositivos físicos como pulseras NFC y teléfonos con chip NFC, tratándolos como mecanismos de transporte de credenciales de acceso.

Se requiere de una arquitectura extensible, ya que se ha pensado tambien en la construccion de modulos de analiticas post evento, la cual oculte y posea alta seguridad alrededor de la logica de validacion de la entrada.

## Impulsores de la decision
- Diseño inicial de una arquitectura de referencia para la aplicacion.

## Opciones consideradas
- Microservicios + capas
- Microkernel 
- Microkernel + hexagonal

## Pros y contras de las opciones
### Microservicios + capas
- Bueno: Este estilo de arquitectura provee de una extensbilidad quasi ilimitada.
- Bueno: Dividir los servicios en diferentes capas oculta y provee de mas seguridad a la logica central de validacion de la entrada.
- Bueno: Provee de mucha flexibilidad y adaptabilidad a la hora de realizar integraciones con terceras partes.
- Malo: Bastante costoso de implementar y supone a largo plazo de un equipo grande de desarrolladores para mantener.
- Malo: No es posible de adaptar a ambientes o entornos sin conexion a internet. 
- Malo: Mucha complejidad en sincronizacion offline para NFC.
- Malo: Si bien es escalable y flexible, nos obliga a que otras aplicaciones usen los microservicios existentes, en otras palabras, nos fuerza a adoptar una unica manera de resolver futuros problemas.

### Microkernel 
- Bueno: Este estilo de arquitectura provee una alta extensibilidad, permitiendo añadir nuevos módulos (ej. analíticas, integraciones, NFC, etc.) como plugins sin necesidad de modificar el core.
- Bueno: El core (validación de entradas) y los casos de uso específicos se encuentran claramente separados, facilitando la evolución de funcionalidades externas sin comprometer la lógica central.
- Malo: Los plugins se acoplan a los formatos/protocolos de comunicación definidos por el core. Esto implica que, a medida que aumentan los casos de uso (ej. NFC offline, BLE, QR vía app), se requiere adaptar los plugins o ampliar el core, generando cierta fricción.
- Malo: El aislamiento del core no es tan explícito como en otros estilos (ej. hexagonal). La validación puede terminar con dependencias implícitas hacia la forma en que los plugins le envían datos.

### Microkernel + hexagonal (seleccionada)
- Bueno: Altisima extensibilidad, permitiendo añadir nuevos modulos sin necesidad de modificar el core.
- Bueno: Los puertos definen contratos (abstracciones) para hablar con el core, no les importa el protocolo de comunicacion, solo que el contrato definido para la comunicacion se respete.
- Bueno: Alta portabilidad, se puede desarrollar en forma de libreria e instalar el core y sus validaciones tanto en dispositivos mobiles, como en servidores y talanqueras.
- Bueno: El enfoque hexagonal proporciona mucho mas aislamiento de la logica central.
- Malo: Se supone un core estatico y de poco cambio, para el dominio del problema actual esta bien, pero es un riesgo a tener en cuenta.
- Malo: Requiere más disciplina de diseño (definir puertos, adaptadores y contratos) y un esfuerzo inicial mayor.