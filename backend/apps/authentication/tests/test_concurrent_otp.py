from django.test import TestCase
import threading
import time
import os

from apps.authentication.managers.otp_manager import OTPManager
from apps.authentication.services.otp_service import VerifyOTPService
from apps.authentication.dtos.otp_dto import VerifyOTPDTO
from apps.authentication.repositories.user_repository import UserRepository


class ConcurrentOTPTest(TestCase):
    def setUp(self):
        self.email = os.getenv('TEST_OTP_EMAIL', 'test-otp@empsphere.local')
        # create a user document directly in MongoDB so repositories can find it
        self.user_repo = UserRepository()
        user_data = {
            'email': self.email.lower(),
            'username': 'testuser',
            'role': 'USER',
            'password': None,
        }
        self.user_id = self.user_repo.create(user_data)
        self.user = self.user_repo.get_by_email(self.email)

    def test_concurrent_otp_verify_only_one_succeeds(self):
        otp = OTPManager().create_and_send(self.email, 'email_verification')

        results = []
        lock = threading.Lock()

        def worker(idx, otp_value):
            svc = VerifyOTPService()
            dto = VerifyOTPDTO(self.email, otp_value, 'email_verification')
            try:
                res = svc.verify(dto)
                with lock:
                    results.append((idx, True, res))
            except Exception as e:
                with lock:
                    results.append((idx, False, str(e)))

        threads = [threading.Thread(target=worker, args=(i, otp)) for i in range(6)]

        for t in threads:
            t.start()
            time.sleep(0.01)

        for t in threads:
            t.join()

        success_count = sum(1 for r in results if r[1])
        self.assertEqual(success_count, 1, f"Expected exactly one success, got {success_count}. Results: {results}")
