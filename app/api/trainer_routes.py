"""
API Routes untuk Trainer Management
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.domain.entities import Trainer, User
from app.application.services import TrainerService
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/trainers", tags=["Trainers"])


# Request/Response DTOs
class CreateTrainerRequest(BaseModel):
    name: str
    email: str
    phone: str
    specialty: Optional[str] = None
    certification: Optional[str] = None
    experience: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+6281234567891",
                "specialty": "Strength training, Weight loss",
                "certification": "NASM-CPT, ACE",
                "experience": 5
            }
        }


class TrainerResponse(BaseModel):
    trainer_id: str
    user_id: str
    name: str
    email: str
    phone: str
    specialty: Optional[str]
    certification: Optional[str]
    experience: Optional[int]
    
    @classmethod
    def from_entity(cls, trainer: Trainer):
        return cls(
            trainer_id=trainer.trainer_id,
            user_id=trainer.user_id,
            name=trainer.name,
            email=trainer.email,
            phone=trainer.phone,
            specialty=trainer.specialty,
            certification=trainer.certification,
            experience=trainer.experience
        )


# Dependency injection
def get_trainer_service() -> TrainerService:
    from app.main import trainer_service
    return trainer_service


@router.post("/", response_model=TrainerResponse, status_code=201)
def create_trainer(
    request: CreateTrainerRequest,
    service: TrainerService = Depends(get_trainer_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Membuat trainer baru
    
    **Memerlukan autentikasi (JWT token)**
    """
    try:
        trainer = service.create_trainer(
            name=request.name,
            email=request.email,
            phone=request.phone,
            specialty=request.specialty,
            certification=request.certification,
            experience=request.experience
        )
        return TrainerResponse.from_entity(trainer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TrainerResponse])
def get_all_trainers(
    service: TrainerService = Depends(get_trainer_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mengambil semua trainers
    
    **Memerlukan autentikasi (JWT token)**
    """
    trainers = service.get_all_trainers()
    return [TrainerResponse.from_entity(t) for t in trainers]


@router.get("/{trainer_id}", response_model=TrainerResponse)
def get_trainer(
    trainer_id: str,
    service: TrainerService = Depends(get_trainer_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mengambil detail trainer berdasarkan ID
    
    **Memerlukan autentikasi (JWT token)**
    """
    trainer = service.get_trainer(trainer_id)
    if not trainer:
        raise HTTPException(status_code=404, detail=f"Trainer {trainer_id} tidak ditemukan")
    return TrainerResponse.from_entity(trainer)
