# Offline Ticket Validation
## Descripcion
El miembro del staff utiliza la aplicación móvil para validar la entrada de un usuario, quien comparte su credencial (ticket) mediante NFC. La app ejecuta la validación a través del core local y actualiza el estado del ticket en la base de datos interna. Luego, el cambio se propaga entre los dispositivos del staff conectados al mismo gate/zona mediante un protocolo de gossip, asegurando que todos los nodos mantengan un estado sincronizado aun sin conexión a internet.
## Diagrama de clases
```mermaid
classDiagram
    %% Core agrupado en namespace
    namespace Core {
        class Ticket {
            - id: UUID
            - userId: UUID
            - eventId: UUID
            - status: TicketStatus
            + validate(): bool
            + markAsUsed(): void
        }

        class AccessCredential {
            - credentialId: UUID
            - ticketId: UUID
            - type: CredentialType
            + isValid(): bool
        }

        class Gate {
            - gateId: UUID
            - zone: String
            + allowAccess(ticket: Ticket): bool
        }

        class AttendanceLog {
            - logId: UUID
            - staffId: UUID
            - ticketId: UUID
            - timestamp: DateTime
        }

        class TicketValidator {
            + validateTicket(ticket: Ticket, credential: AccessCredential, gate: Gate): ValidationResult
        }

        class ValidationResult {
            - success: bool
            - message: String
            + isSuccess(): bool
        }
    }

    %% Relaciones del Core (usar nombres simples)
    Ticket "1" --> "1" AccessCredential : has
    Ticket "1" --> "0..*" AttendanceLog : produces
    Gate "1" --> "0..*" AttendanceLog : records
    TicketValidator --> Ticket : uses
    TicketValidator --> AccessCredential : uses
    TicketValidator --> Gate : uses
    TicketValidator --> ValidationResult : returns

    %% Adaptadores externos
    class StaffApp {
        + readNFC(): AccessCredential
        + callValidation(ticket, credential, gate): ValidationResult
        + propagateChange(log: AttendanceLog): void
    }

    class NFCAdapter {
        + readCredential(): AccessCredential
        + sendAck(result: ValidationResult): void
    }

    class GossipAdapter {
        + propagateLog(log: AttendanceLog): void
        + receiveLog(log: AttendanceLog): void
    }

    %% Relaciones adaptadores <-> Core
    StaffApp --> TicketValidator : invokes
    StaffApp --> NFCAdapter : uses
    StaffApp --> GossipAdapter : uses
```
## Diagrama de secuencia
```mermaid
sequenceDiagram
    participant U as Usuario (App móvil)
    participant NFC as Adaptador NFC (Staff)
    participant Core as Core Hexagonal
    participant Repo as TicketRepositoryPort
    participant Gossip as GossipAdapter (Red de nodos)
    participant DB as DB Local (SQLite/RocksDB)

    U->>NFC: Enviar ticket vía NFC
    NFC->>Core: validateTicket(ticket)
    Core->>Repo: get_ticket(ticket_id)
    Repo->>DB: Buscar ticket en DB local
    DB-->>Repo: Ticket encontrado
    Repo-->>Core: Retorna ticket
    Core->>Core: Reglas de negocio (válido/duplicado/fraude)
    alt Ticket válido
        Core-->>NFC: SUCCESS
        NFC-->>U: ACK SUCCESS
        Core->>Repo: mark_as_used(ticket_id, gate_id, ts)
        Repo->>DB: Actualizar estado local
        Repo->>Gossip: Propagar cambio
        Gossip->>OtrosNodos: Difundir evento ticket_used
    else Ticket inválido
        Core-->>NFC: FAIL
        NFC-->>U: ACK FAIL
    end
```
## Diagrama contenedores (Staff App)
```mermaid
C4Container
title App Staff - Arquitectura interna

System_Boundary(sb1, "App Staff") {
    Container(ui, "UI Móvil", "Flutter/React Native/Android", "Interfaz para staff (escaneo, validación, feedback al usuario)")
    Container(core, "Core Library (Hexagonal)", "Librería local", "Lógica de negocio, validación de tickets")
    Container(localdb, "Base de datos local", "SQLite/Realm/Room", "Almacena tickets y su estado de validación")
    Container(comm, "Módulo Gossip", "Networking local (Bluetooth/WiFi Direct)", "Propaga cambios de tickets a otros nodos")
}

Rel(ui, core, "Invoca validaciones")
Rel(core, localdb, "Lee/Escribe tickets")
Rel(ui, comm, "Informa cambios a propagar")
Rel(comm, comm, "Sincroniza estados con otros nodos")
```

## Plan de pruebas unitarias
| **ID** | **Clase / Módulo** | **Método a probar** | **Descripción de la prueba**                                 | **Entrada**                          | **Salida esperada**                               |
| ------ | ------------------ | ------------------- | ------------------------------------------------------------ | ------------------------------------ | ------------------------------------------------- |
| TC-01  | `Ticket`           | `__init__`          | Crear un ticket con datos válidos.                           | `id="T1", content="data1"`           | Ticket con `id="T1"`, `content="data1"`.          |
| TC-02  | `Ticket`           | `update_content`    | Actualizar el contenido de un ticket.                        | `content="nuevo valor"`              | El ticket refleja el nuevo contenido.             |
| TC-03  | `Ticket`           | `__eq__`            | Comparar dos tickets iguales.                                | `Ticket("T1") == Ticket("T1")`       | `True`.                                           |
| TC-04  | `Ticket`           | `__eq__`            | Comparar dos tickets diferentes.                             | `Ticket("T1") == Ticket("T2")`       | `False`.                                          |
| TC-05  | `Node`             | `__init__`          | Crear nodo con identificador válido.                         | `node_id="N1"`                       | Nodo con `id="N1"`, lista de tickets vacía.       |
| TC-06  | `Node`             | `add_ticket`        | Asociar un ticket a un nodo.                                 | `node.add_ticket(Ticket("T1"))`      | El nodo contiene el ticket.                       |
| TC-07  | `Node`             | `get_ticket`        | Recuperar ticket existente.                                  | `node.get_ticket("T1")`              | Retorna el ticket correcto.                       |
| TC-08  | `Node`             | `get_ticket`        | Intentar recuperar ticket inexistente.                       | `node.get_ticket("T999")`            | Retorna `None` o lanza excepción controlada.      |
| TC-09  | `Node`             | `update_ticket`     | Actualizar ticket existente en el nodo.                      | `update_ticket("T1", "nuevo valor")` | Ticket actualizado.                               |
| TC-10  | `Node`             | `update_ticket`     | Intentar actualizar ticket inexistente.                      | `update_ticket("T999", "valor")`     | Excepción `TicketNotFoundError`.                  |
| TC-11  | `Node`             | `list_tickets`      | Listar todos los tickets del nodo.                           | Tickets `T1, T2`                     | Retorna lista `[T1, T2]`.                         |
| TC-12  | `Core`             | `register_node`     | Registrar un nodo en el core.                                | `core.register_node(Node("N1"))`     | Nodo agregado en la lista del core.               |
| TC-13  | `Core`             | `find_node`         | Buscar nodo existente.                                       | `find_node("N1")`                    | Retorna el nodo correcto.                         |
| TC-14  | `Core`             | `find_node`         | Buscar nodo inexistente.                                     | `find_node("N999")`                  | Retorna `None` o excepción `NodeNotFoundError`.   |
| TC-15  | `Core`             | `propagate_change`  | Propagar actualización de ticket a varios nodos registrados. | Actualizar `T1` en `N1`              | Todos los nodos con `T1` reflejan el nuevo valor. |
| TC-16  | `Core`             | `propagate_change`  | Intentar propagar un ticket inexistente.                     | `T999`                               | Excepción `TicketNotFoundError`.                  |
