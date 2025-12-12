"""
API Routes untuk Client Management
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.application.services import ClientService
from app.auth.dependencies import get_current_active_user
from app.domain.entities import Client, User

router = APIRouter(prefix="/clients", tags=["Clients"])


# Request/Response DTOs
class CreateClientRequest(BaseModel):
    name: str
    email: str
    phone: str
    fitness_goals: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+6281234567890",
                "fitness_goals": "Weight loss and muscle building",
            }
        }


class ClientResponse(BaseModel):
    client_id: str
    user_id: str
    name: str
    email: str
    phone: str
    fitness_goals: Optional[str]

    @classmethod
    def from_entity(cls, client: Client):
        return cls(
            client_id=client.client_id,
            user_id=client.user_id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            fitness_goals=client.fitness_goals,
        )


# Dependency injection
def get_client_service() -> ClientService:
    from app.main import client_service

    return client_service


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(
    request: CreateClientRequest,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Membuat client baru

    **Memerlukan autentikasi (JWT token)**
    """
    try:
        client = service.create_client(
            name=request.name,
            email=request.email,
            phone=request.phone,
            fitness_goals=request.fitness_goals,
        )
        return ClientResponse.from_entity(client)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ClientResponse])
def get_all_clients(
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mengambil semua clients

    **Memerlukan autentikasi (JWT token)**
    """
    clients = service.get_all_clients()
    return [ClientResponse.from_entity(c) for c in clients]


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mengambil detail client berdasarkan ID

    **Memerlukan autentikasi (JWT token)**
    """
    client = service.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=404, detail=f"Client {client_id} tidak ditemukan"
        )
    return ClientResponse.from_entity(client)
