"""
Tests for application services layer
"""
import pytest
from datetime import datetime, timedelta
from app.application.services import (
    BookingService,
    ClientService,
    TrainerService
)
from app.domain.entities import (
    BookingSession,
    Client,
    Trainer,
    User,
    BookingStatus
)
from app.domain.value_objects import TimeSlot, SessionDuration


class TestBookingService:
    """Tests untuk BookingService"""
    
    def test_create_booking_success(self, booking_service, client_repo, trainer_repo):
        """Test create booking yang sukses"""
        # Setup
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        # Test
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        booking = booking_service.create_booking(
            client_id="CL001",
            trainer_id="TR001",
            start_time=start_time,
            end_time=end_time
        )
        
        assert booking.client_id == "CL001"
        assert booking.trainer_id == "TR001"
        assert booking.status == BookingStatus.PENDING
    
    def test_create_booking_with_nonexistent_client(self, booking_service, trainer_repo):
        """Test create booking dengan client yang tidak ada"""
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        trainer_repo.save(trainer)
        
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        
        with pytest.raises(ValueError) as exc_info:
            booking_service.create_booking(
                client_id="NONEXISTENT",
                trainer_id="TR001",
                start_time=start_time,
                end_time=end_time
            )
        assert "Client tidak ditemukan" in str(exc_info.value)
    
    def test_create_booking_with_nonexistent_trainer(self, booking_service, client_repo):
        """Test create booking dengan trainer yang tidak ada"""
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        client_repo.save(client)
        
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        
        with pytest.raises(ValueError) as exc_info:
            booking_service.create_booking(
                client_id="CL001",
                trainer_id="NONEXISTENT",
                start_time=start_time,
                end_time=end_time
            )
        assert "Trainer tidak ditemukan" in str(exc_info.value)
    
    def test_create_booking_with_conflicting_schedule(self, booking_service, client_repo, trainer_repo):
        """Test create booking dengan jadwal yang bentrok"""
        # Setup
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        # Create first booking
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        booking_service.create_booking(
            client_id="CL001",
            trainer_id="TR001",
            start_time=start_time,
            end_time=end_time
        )
        
        # Try to create conflicting booking
        conflicting_start = start_time + timedelta(minutes=30)
        conflicting_end = conflicting_start + timedelta(minutes=60)
        
        with pytest.raises(ValueError) as exc_info:
            booking_service.create_booking(
                client_id="CL001",
                trainer_id="TR001",
                start_time=conflicting_start,
                end_time=conflicting_end
            )
        assert "Jadwal bentrok" in str(exc_info.value) or "overlap" in str(exc_info.value).lower()
    
    def test_get_booking_by_id_success(self, booking_service, client_repo, trainer_repo):
        """Test get booking by ID yang sukses"""
        # Setup
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        created_booking = booking_service.create_booking(
            client_id="CL001",
            trainer_id="TR001",
            start_time=start_time,
            end_time=end_time
        )
        
        # Test
        booking = booking_service.get_booking(created_booking.booking_id)
        assert booking is not None
        assert booking.booking_id == created_booking.booking_id
    
    def test_get_booking_with_nonexistent_id(self, booking_service):
        """Test get booking dengan ID yang tidak ada"""
        booking = booking_service.get_booking("NONEXISTENT")
        assert booking is None
    
    def test_confirm_booking_success(self, booking_service, client_repo, trainer_repo):
        """Test confirm booking yang sukses"""
        # Setup
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        booking = booking_service.create_booking(
            client_id="CL001",
            trainer_id="TR001",
            start_time=start_time,
            end_time=end_time
        )
        
        # Test
        confirmed_booking = booking_service.confirm_booking(booking.booking_id, "TR001")
        assert confirmed_booking.status == BookingStatus.CONFIRMED
        assert confirmed_booking.confirmed_date is not None
    
    def test_cancel_booking_success(self, booking_service, client_repo, trainer_repo):
        """Test cancel booking yang sukses"""
        # Setup
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        booking = booking_service.create_booking(
            client_id="CL001",
            trainer_id="TR001",
            start_time=start_time,
            end_time=end_time
        )
        
        # Test
        cancelled_booking = booking_service.cancel_booking(
            booking.booking_id, 
            "CL001", 
            "Berhalangan hadir"
        )
        assert cancelled_booking.status == BookingStatus.CANCELLED
        assert cancelled_booking.cancellation_reason == "Berhalangan hadir"
    
    def test_get_client_bookings(self, booking_service, client_repo, trainer_repo):
        """Test get all bookings untuk client tertentu"""
        # Setup
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        # Create multiple bookings
        for i in range(3):
            start_time = datetime.now() + timedelta(days=i+1)
            end_time = start_time + timedelta(minutes=60)
            booking_service.create_booking(
                client_id="CL001",
                trainer_id="TR001",
                start_time=start_time,
                end_time=end_time
            )
        
        # Test
        bookings = booking_service.get_client_bookings("CL001")
        assert len(bookings) == 3
        assert all(b.client_id == "CL001" for b in bookings)
    
    def test_get_trainer_bookings(self, booking_service, client_repo, trainer_repo):
        """Test get all bookings untuk trainer tertentu"""
        # Setup
        client = Client(
            user_id="CL001",
            name="Test Client",
            email="client@test.com",
            hashed_password="hashedpass",
            phone="08123456789"
        )
        trainer = Trainer(
            user_id="TR001",
            name="Test Trainer",
            email="trainer@test.com",
            hashed_password="hashedpass",
            phone="08198765432",
            specialization="Yoga"
        )
        client_repo.save(client)
        trainer_repo.save(trainer)
        
        # Create multiple bookings
        for i in range(2):
            start_time = datetime.now() + timedelta(days=i+1)
            end_time = start_time + timedelta(minutes=60)
            booking_service.create_booking(
                client_id="CL001",
                trainer_id="TR001",
                start_time=start_time,
                end_time=end_time
            )
        
        # Test
        bookings = booking_service.get_trainer_bookings("TR001")
        assert len(bookings) == 2
        assert all(b.trainer_id == "TR001" for b in bookings)


class TestClientService:
    """Tests untuk ClientService"""
    
    def test_create_client_success(self, client_service):
        """Test create client yang sukses"""
        client = client_service.create_client(
            name="Test Client",
            email="client@test.com",
            password="password123",
            phone="08123456789"
        )
        
        assert client.name == "Test Client"
        assert client.email == "client@test.com"
        assert client.phone == "08123456789"
        assert client.hashed_password != "password123"  # Should be hashed
    
    def test_create_client_with_duplicate_email(self, client_service):
        """Test create client dengan email yang sudah ada"""
        client_service.create_client(
            name="Test Client 1",
            email="duplicate@test.com",
            password="password123",
            phone="08123456789"
        )
        
        with pytest.raises(ValueError) as exc_info:
            client_service.create_client(
                name="Test Client 2",
                email="duplicate@test.com",
                password="password456",
                phone="08198765432"
            )
        assert "sudah terdaftar" in str(exc_info.value).lower() or "already exists" in str(exc_info.value).lower()
    
    def test_get_client_by_id_success(self, client_service):
        """Test get client by ID yang sukses"""
        created_client = client_service.create_client(
            name="Test Client",
            email="client@test.com",
            password="password123",
            phone="08123456789"
        )
        
        client = client_service.get_client(created_client.user_id)
        assert client is not None
        assert client.user_id == created_client.user_id
    
    def test_get_client_with_nonexistent_id(self, client_service):
        """Test get client dengan ID yang tidak ada"""
        client = client_service.get_client("NONEXISTENT")
        assert client is None
    
    def test_get_client_by_email_success(self, client_service):
        """Test get client by email yang sukses"""
        created_client = client_service.create_client(
            name="Test Client",
            email="client@test.com",
            password="password123",
            phone="08123456789"
        )
        
        client = client_service.get_client_by_email("client@test.com")
        assert client is not None
        assert client.email == created_client.email
    
    def test_get_client_by_nonexistent_email(self, client_service):
        """Test get client dengan email yang tidak ada"""
        client = client_service.get_client_by_email("nonexistent@test.com")
        assert client is None
    
    def test_get_all_clients(self, client_service):
        """Test get all clients"""
        # Create multiple clients
        for i in range(3):
            client_service.create_client(
                name=f"Test Client {i}",
                email=f"client{i}@test.com",
                password="password123",
                phone=f"0812345678{i}"
            )
        
        clients = client_service.get_all_clients()
        assert len(clients) >= 3
    
    def test_update_client_success(self, client_service):
        """Test update client yang sukses"""
        client = client_service.create_client(
            name="Test Client",
            email="client@test.com",
            password="password123",
            phone="08123456789"
        )
        
        updated_client = client_service.update_client(
            user_id=client.user_id,
            name="Updated Name",
            phone="08198765432"
        )
        
        assert updated_client.name == "Updated Name"
        assert updated_client.phone == "08198765432"


class TestTrainerService:
    """Tests untuk TrainerService"""
    
    def test_create_trainer_success(self, trainer_service):
        """Test create trainer yang sukses"""
        trainer = trainer_service.create_trainer(
            name="Test Trainer",
            email="trainer@test.com",
            password="password123",
            phone="08198765432",
            specialization="Yoga"
        )
        
        assert trainer.name == "Test Trainer"
        assert trainer.email == "trainer@test.com"
        assert trainer.specialization == "Yoga"
        assert trainer.hashed_password != "password123"
    
    def test_create_trainer_with_duplicate_email(self, trainer_service):
        """Test create trainer dengan email yang sudah ada"""
        trainer_service.create_trainer(
            name="Test Trainer 1",
            email="duplicate@test.com",
            password="password123",
            phone="08198765432",
            specialization="Yoga"
        )
        
        with pytest.raises(ValueError) as exc_info:
            trainer_service.create_trainer(
                name="Test Trainer 2",
                email="duplicate@test.com",
                password="password456",
                phone="08123456789",
                specialization="Pilates"
            )
        assert "sudah terdaftar" in str(exc_info.value).lower() or "already exists" in str(exc_info.value).lower()
    
    def test_get_trainer_by_id_success(self, trainer_service):
        """Test get trainer by ID yang sukses"""
        created_trainer = trainer_service.create_trainer(
            name="Test Trainer",
            email="trainer@test.com",
            password="password123",
            phone="08198765432",
            specialization="Yoga"
        )
        
        trainer = trainer_service.get_trainer(created_trainer.user_id)
        assert trainer is not None
        assert trainer.user_id == created_trainer.user_id
    
    def test_get_trainer_with_nonexistent_id(self, trainer_service):
        """Test get trainer dengan ID yang tidak ada"""
        trainer = trainer_service.get_trainer("NONEXISTENT")
        assert trainer is None
    
    def test_get_all_trainers(self, trainer_service):
        """Test get all trainers"""
        # Create multiple trainers
        for i in range(3):
            trainer_service.create_trainer(
                name=f"Test Trainer {i}",
                email=f"trainer{i}@test.com",
                password="password123",
                phone=f"0819876543{i}",
                specialization="Yoga"
            )
        
        trainers = trainer_service.get_all_trainers()
        assert len(trainers) >= 3
    
    def test_get_trainers_by_specialization(self, trainer_service):
        """Test get trainers by specialization"""
        # Create trainers with different specializations
        trainer_service.create_trainer(
            name="Yoga Trainer",
            email="yoga@test.com",
            password="password123",
            phone="08198765432",
            specialization="Yoga"
        )
        trainer_service.create_trainer(
            name="Pilates Trainer",
            email="pilates@test.com",
            password="password123",
            phone="08123456789",
            specialization="Pilates"
        )
        
        yoga_trainers = trainer_service.get_trainers_by_specialization("Yoga")
        assert len(yoga_trainers) >= 1
        assert all(t.specialization == "Yoga" for t in yoga_trainers)
    
    def test_update_trainer_success(self, trainer_service):
        """Test update trainer yang sukses"""
        trainer = trainer_service.create_trainer(
            name="Test Trainer",
            email="trainer@test.com",
            password="password123",
            phone="08198765432",
            specialization="Yoga"
        )
        
        updated_trainer = trainer_service.update_trainer(
            user_id=trainer.user_id,
            name="Updated Name",
            specialization="Pilates"
        )
        
        assert updated_trainer.name == "Updated Name"
        assert updated_trainer.specialization == "Pilates"
