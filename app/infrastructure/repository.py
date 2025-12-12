"""
Repository Interface dan Implementasi In-Memory
Sesuai dengan pattern DDD
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.domain.entities import BookingSession, Client, Trainer, User
from app.domain.value_objects import TimeSlot


class IBookingSessionRepository(ABC):
    """
    Interface Repository untuk BookingSession
    Menyediakan antarmuka penyimpanan untuk entitas booking
    """

    @abstractmethod
    def save(self, booking: BookingSession) -> BookingSession:  # pragma: no cover
        """Menyimpan booking session"""
        pass

    @abstractmethod
    def find_by_id(
        self, booking_id: str
    ) -> Optional[BookingSession]:  # pragma: no cover
        """Mencari booking berdasarkan ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[BookingSession]:  # pragma: no cover
        """Mengambil semua booking"""
        pass

    @abstractmethod
    def find_by_client_id(
        self, client_id: str
    ) -> List[BookingSession]:  # pragma: no cover
        """Mencari booking berdasarkan client ID"""
        pass

    @abstractmethod
    def find_by_trainer_id(
        self, trainer_id: str
    ) -> List[BookingSession]:  # pragma: no cover
        """Mencari booking berdasarkan trainer ID"""
        pass

    @abstractmethod
    def delete(self, booking_id: str) -> bool:  # pragma: no cover
        """Menghapus booking"""
        pass


class InMemoryBookingRepository(IBookingSessionRepository):
    """
    Implementasi In-Memory Repository untuk BookingSession
    Menggunakan dictionary sebagai storage sederhana
    """

    def __init__(self):
        self._storage: dict[str, BookingSession] = {}

    def save(self, booking: BookingSession) -> BookingSession:
        """Menyimpan booking session"""
        self._storage[booking.booking_id] = booking
        return booking

    def find_by_id(self, booking_id: str) -> Optional[BookingSession]:
        """Mencari booking berdasarkan ID"""
        return self._storage.get(booking_id)

    def find_all(self) -> List[BookingSession]:
        """Mengambil semua booking"""
        return list(self._storage.values())

    def find_by_client_id(self, client_id: str) -> List[BookingSession]:
        """Mencari booking berdasarkan client ID"""
        return [b for b in self._storage.values() if b.client_id == client_id]

    def find_by_trainer_id(self, trainer_id: str) -> List[BookingSession]:
        """Mencari booking berdasarkan trainer ID"""
        return [b for b in self._storage.values() if b.trainer_id == trainer_id]

    def delete(self, booking_id: str) -> bool:
        """Menghapus booking"""
        if booking_id in self._storage:
            del self._storage[booking_id]
            return True
        return False


class IClientRepository(ABC):
    """Interface Repository untuk Client"""

    @abstractmethod
    def save(self, client: Client) -> Client:  # pragma: no cover
        pass

    @abstractmethod
    def find_by_id(self, client_id: str) -> Optional[Client]:  # pragma: no cover
        pass

    @abstractmethod
    def find_all(self) -> List[Client]:  # pragma: no cover
        pass


class InMemoryClientRepository(IClientRepository):
    """Implementasi In-Memory Repository untuk Client"""

    def __init__(self):
        self._storage: dict[str, Client] = {}

    def save(self, client: Client) -> Client:
        self._storage[client.client_id] = client
        return client

    def find_by_id(self, client_id: str) -> Optional[Client]:
        return self._storage.get(client_id)

    def find_all(self) -> List[Client]:
        return list(self._storage.values())


class ITrainerRepository(ABC):
    """Interface Repository untuk Trainer"""

    @abstractmethod
    def save(self, trainer: Trainer) -> Trainer:  # pragma: no cover
        pass

    @abstractmethod
    def find_by_id(self, trainer_id: str) -> Optional[Trainer]:  # pragma: no cover
        pass

    @abstractmethod
    def find_all(self) -> List[Trainer]:  # pragma: no cover
        pass


class InMemoryTrainerRepository(ITrainerRepository):
    """Implementasi In-Memory Repository untuk Trainer"""

    def __init__(self):
        self._storage: dict[str, Trainer] = {}

    def save(self, trainer: Trainer) -> Trainer:
        self._storage[trainer.trainer_id] = trainer
        return trainer

    def find_by_id(self, trainer_id: str) -> Optional[Trainer]:
        return self._storage.get(trainer_id)

    def find_all(self) -> List[Trainer]:
        return list(self._storage.values())


class ISchedulingApi(ABC):
    """
    Interface untuk komunikasi dengan Scheduling Context (eksternal)
    Digunakan untuk memvalidasi ketersediaan waktu trainer
    """

    @abstractmethod
    def check_availability(self, trainer_id: str, time_slot: TimeSlot) -> bool:
        """Memeriksa apakah trainer tersedia pada slot waktu tertentu"""
        pass


class MockSchedulingApi(ISchedulingApi):
    """
    Mock implementasi Scheduling API untuk development
    Pada production, ini akan diganti dengan real API call
    """

    def check_availability(self, trainer_id: str, time_slot: TimeSlot) -> bool:
        """
        Mock: selalu return True (tersedia)
        Di production, ini akan memanggil Scheduling Context API
        """
        # Simulasi: cek apakah tidak ada konflik dengan booking lain
        # Untuk demo, kita return True
        return True


class IUserRepository(ABC):
    """Interface Repository untuk User"""

    @abstractmethod
    def save(self, user: User) -> User:  # pragma: no cover
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:  # pragma: no cover
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:  # pragma: no cover
        pass

    @abstractmethod
    def find_all(self) -> List[User]:  # pragma: no cover
        pass


class InMemoryUserRepository(IUserRepository):
    """Implementasi In-Memory Repository untuk User"""

    def __init__(self):
        self._storage: dict[str, User] = {}

    def save(self, user: User) -> User:
        self._storage[user.user_id] = user
        return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._storage.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None

    def find_all(self) -> List[User]:
        return list(self._storage.values())
