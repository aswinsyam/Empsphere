"""
Concurrent OTP verification test.

Run this from the repository root using the backend venv:

    backend/venv/Scripts/python.exe backend/scripts/concurrent_otp_test.py

It will:
- create an OTP for a given email
- spawn several threads that call VerifyOTPService.verify() concurrently
- print which threads succeeded and which failed

This validates that the atomic claim (`claim_active_otp`) prevents multiple successes.
"""

import os
import sys
import threading
import time

# Configure Django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.authentication.managers.otp_manager import OTPManager
from apps.authentication.services.otp_service import VerifyOTPService
from apps.authentication.dtos.otp_dto import VerifyOTPDTO

EMAIL = os.getenv('TEST_OTP_EMAIL', 'admin@empsphere.com')
THREADS = 6

results = []
lock = threading.Lock()

def worker(idx, otp_value):
    svc = VerifyOTPService()
    dto = VerifyOTPDTO(EMAIL, otp_value, 'login')
    try:
        res = svc.verify(dto)
        with lock:
            results.append((idx, True, res))
        print(f"[THREAD {idx}] SUCCESS: returned tokens (user_id={res.get('user_id')})")
    except Exception as e:
        with lock:
            results.append((idx, False, str(e)))
        print(f"[THREAD {idx}] FAIL: {e}")


def main():
    print('Creating OTP for', EMAIL)
    otp = OTPManager().create_and_send(EMAIL, 'login')
    print('Plain OTP (dev only):', otp)

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=worker, args=(i+1, otp))
        threads.append(t)

    # Start threads nearly simultaneously
    for t in threads:
        t.start()
        time.sleep(0.01)

    for t in threads:
        t.join()

    success_count = sum(1 for r in results if r[1])
    fail_count = len(results) - success_count
    print('\nSummary:')
    print('  Total threads:', len(results))
    print('  Successes:', success_count)
    print('  Failures:', fail_count)

    if success_count == 1:
        print('Atomic claim succeeded: only one verification succeeded.')
    else:
        print('WARNING: expected exactly one success. See results for details.')


if __name__ == '__main__':
    main()
