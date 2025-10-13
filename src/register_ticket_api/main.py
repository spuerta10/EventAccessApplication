from controllers import TicketsController
from fastapi import FastAPI
from infraestructure import PostgreSQLDbContext
from repositories import TicketRepository, UserRepository
from services import TicketService

app = FastAPI()

psql_context = PostgreSQLDbContext()
user_repo = UserRepository(psql_context)
ticket_repo = TicketRepository(db_context=psql_context)
ticket_service = TicketService(user_repo=user_repo, ticket_repo=ticket_repo)
tickets_controller = TicketsController(ticket_service=ticket_service)

app.include_router(tickets_controller.router)

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa S104
