# Offline Ticket Validation
## Descripcion
Un visitante transfiere su ticket digital y una seed de seguridad al celular del staff mediante NFC. La App Staff, usando su Core Library, valida que la seed coincida con las almacenadas localmente y que el ticket tenga acceso permitido al gate correspondiente. Según el resultado, se autoriza o rechaza el ingreso directamente desde el dispositivo, sin necesidad de conexión a internet.
## Diagrama de clases
```mermaid
classDiagram
    %% ========================
    %% CORE (Hexagonal)
    %% ========================
    namespace Core {
        class Ticket {
            +id: String
            +zoneId: String
            +status: String
            +isValid(): bool
        }

        class Seed {
            +id: String
            +value: String
            +validate(token: String): bool
        }

        class CoreValidator {
            +validateCredential(credential: AccessCredential): ValidationResult
            -verifyTicket(ticket: Ticket): bool
            -verifySeed(seed: Seed, token: String): bool
            -verifyGate(ticket: Ticket, gate: Gate): bool
        }

        class ValidationResult {
            +status: String  // SUCCESS | FAIL
            +message: String
        }
    }

    %% ========================
    %% EXTERNOS (Adapters, DB, NFC, Gate)
    %% ========================
    class AccessCredential {
        +ticketId: String
        +seedToken: String
    }

    class Gate {
        +id: String
        +zoneId: String
        +validateAccess(ticket: Ticket): bool
    }

    class LocalDB {
        +storeTicket(ticket: Ticket)
        +getTicket(ticketId: String): Ticket
        +updateTicket(ticket: Ticket)
    }

    %% ========================
    %% RELACIONES
    %% ========================
    AccessCredential --> Ticket : refiere
    AccessCredential --> Seed : usa token
    CoreValidator --> Ticket : valida
    CoreValidator --> Seed : valida
    CoreValidator --> Gate : valida
    CoreValidator --> ValidationResult : produce
    CoreValidator --> LocalDB : consulta
    LocalDB --> Ticket : almacena
```
## Diagrama de secuencia
```mermaid
sequenceDiagram
    autonumber
    participant UserApp as User App (NFC)
    participant StaffApp as Staff App (UI)
    participant Core as Core Library
    participant LocalDB as Local DB

    UserApp->>StaffApp: Transfiere Ticket + Token(seed) vía NFC
    StaffApp->>Core: Invoca validación (ticket + token)
    Core->>LocalDB: Verifica ticket (vigencia, estado)
    LocalDB-->>Core: Retorna información del ticket
    Core->>Core: Valida seed/token (HMAC / referencia)
    Core->>Core: Verifica acceso a zona/gate
    alt Validación exitosa
        Core-->>StaffApp: ACK SUCCESS
        StaffApp->>LocalDB: Marca ticket como usado
        StaffApp->>UserApp: Retorna SUCCESS
    else Validación fallida
        Core-->>StaffApp: ACK FAIL
        StaffApp->>UserApp: Retorna FAIL
    end
```
## Diagrama de contenedores
```mermaid
C4Container
    title Sistema de Validación Offline - Staff App

    Person(visitor, "Visitante", "Persona que porta un ticket digital.")

    Container_Boundary(staff_app, "App Staff (Android/iOS)") {
        Container(ui, "UI Móvil", "Flutter/React Native", "Interfaz de validación para el staff.")
        Container(core, "Core Library (Hexagonal)", "Librería local", "Valida ticket, seed y acceso permitido.")
        Container(localdb, "Base de datos local", "SQLite/Realm/Room", "Almacena tickets, seeds y resultados de validación.")
        Container(nfc_module, "Módulo NFC", "NFC", "Recibe ticket y seed desde el dispositivo del visitante.")
    }

    %% Relaciones
    Rel(visitor, nfc_module, "Transfiere ticket + seed", "NFC")
    Rel(nfc_module, core, "Envía datos para validación")
    Rel(core, localdb, "Consulta/actualiza tickets y seeds")
    Rel(core, ui, "Retorna resultado de validación")
```
## Plan de pruebas unitarias
| ID   | Caso de prueba                                         | Entrada                                                                 | Proceso validado                                                                 | Resultado esperado                                                                 |
|------|---------------------------------------------------------|------------------------------------------------------------------------|----------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| TC01 | Validación exitosa de ticket con seed válida           | Ticket válido + seed válida                                             | Core valida ticket y compara seed con base local                                  | Retorna `SUCCESS`, se autoriza ingreso                                             |
| TC02 | Ticket válido pero seed inválida                       | Ticket válido + seed no registrada en el dispositivo staff              | Core valida ticket, falla en validación de seed                                   | Retorna `FAIL`, acceso denegado                                                    |
| TC03 | Ticket inválido                                        | Ticket no registrado en base local                                      | Core busca ticket en DB                                                           | Retorna `FAIL`, acceso denegado                                                    |
| TC04 | Ticket válido pero no autorizado en gate específico    | Ticket válido + seed válida pero sin acceso al gate en contexto         | Core valida ticket, compara zona/gate                                             | Retorna `FAIL`, acceso denegado                                                    |
| TC05 | Ticket válido previamente usado                        | Ticket válido + seed válida pero ya marcado como “usado” en la base     | Core valida ticket, detecta estado previo                                         | Retorna `FAIL`, acceso denegado                                                    |
| TC06 | Seed válida pero formato corrupto en el ticket         | Ticket con estructura alterada + seed válida                            | Core intenta parsear ticket                                                       | Lanza excepción de validación / retorna `FAIL`                                     |
| TC07 | Validación simultánea en múltiples gates (consistencia)| Ticket válido + seed válida (2 nodos en gossip network con BD local)    | Core valida ticket y módulo gossip propaga cambio                                 | Ambos nodos registran ticket como “usado” y no lo aceptan nuevamente               |
| TC08 | Ticket válido con seed expirada                        | Ticket válido + seed válida pero expirada                               | Core valida vigencia de seed                                                      | Retorna `FAIL`, acceso denegado                                                    |
| TC09 | Reconexión de nodo con tickets validados offline       | Nodo staff se reconecta con base desactualizada                         | Gossip propaga tickets validados previamente                                      | Nodo actualiza su DB local correctamente                                           |
| TC10 | Validación de performance (tiempo de respuesta)        | Ticket válido + seed válida                                             | Core procesa validación offline                                                   | Respuesta en < 300ms                                                               |