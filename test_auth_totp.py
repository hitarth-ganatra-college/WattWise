"""
Test Suite for WattWise 2FA TOTP Authentication System
======================================================
Tests:
1. Registration endpoint returning user info, TOTP secret, provisioning URI, and QR code image (base64 PNG).
2. Verification endpoint validating TOTP code generated using pyotp.
3. Login endpoint requiring 2FA TOTP code and rejecting invalid/missing TOTP codes.
4. MongoDB user document inspection for totp_secret and totp_enabled fields.
"""

import sys
import os
import pyotp
import uuid
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.api import app, get_db

client = TestClient(app)

def test_totp_auth_flow():
    print("\n--- Starting 2FA TOTP Authentication Test ---")
    
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"operator_{unique_id}@wattwise.io"
    test_password = "SecurePassword123!"
    test_name = f"Test Operator {unique_id}"

    # Step 1: Register User and receive QR code + secret
    reg_payload = {
        "name": test_name,
        "email": test_email,
        "password": test_password,
        "app_password": "mock-app-pass",
        "role": "Grid Controller"
    }

    print(f"[1] Testing /api/auth/register for {test_email}...")
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201, f"Registration failed: {res.text}"
    reg_data = res.json()
    
    assert "totp_secret" in reg_data, "totp_secret missing in registration response"
    assert "totp_uri" in reg_data, "totp_uri missing in registration response"
    assert "qr_code_base64" in reg_data, "qr_code_base64 missing in registration response"
    assert reg_data["qr_code_base64"].startswith("data:image/png;base64,"), "qr_code_base64 format invalid"
    assert reg_data["user"]["totp_verified"] is False, "totp_verified should initially be False"

    totp_secret = reg_data["totp_secret"]
    print(f"    [OK] User registered successfully!")
    print(f"    [OK] Received TOTP secret: {totp_secret}")
    print(f"    [OK] Received Base64 QR Code length: {len(reg_data['qr_code_base64'])} characters")

    # Step 2: Verify user document in MongoDB
    db = get_db()
    user_doc = db['users'].find_one({'email': test_email})
    assert user_doc is not None, "User record not found in MongoDB users collection"
    assert user_doc.get('totp_secret') == totp_secret, "MongoDB totp_secret mismatch"
    assert user_doc.get('totp_verified') is False, "MongoDB totp_verified flag should be False initially"
    print(f"    [OK] MongoDB document verified for user '{test_email}' with totp_secret")

    # Step 3: Test /api/auth/verify-2fa with invalid and valid code
    totp = pyotp.TOTP(totp_secret)
    valid_code = totp.now()
    invalid_code = "000000" if valid_code != "000000" else "111111"

    print("\n[2] Testing /api/auth/verify-2fa...")
    res_bad_verify = client.post("/api/auth/verify-2fa", json={"email": test_email, "totp_code": invalid_code})
    assert res_bad_verify.status_code == 401, f"Expected 401 for bad TOTP, got {res_bad_verify.status_code}"
    print("    [OK] Rejected invalid TOTP code (401 Unauthorized)")

    res_good_verify = client.post("/api/auth/verify-2fa", json={"email": test_email, "totp_code": valid_code})
    assert res_good_verify.status_code == 200, f"Verification failed for valid TOTP code: {res_good_verify.text}"
    print("    [OK] Successfully verified valid 6-digit TOTP code (200 OK)")

    # Step 4: Test /api/auth/login without TOTP (should prompt 2fa_required)
    print("\n[3] Testing /api/auth/login without 2FA TOTP code...")
    res_no_totp_login = client.post("/api/auth/login", json={"email": test_email, "password": test_password})
    assert res_no_totp_login.status_code == 200
    login_no_totp_data = res_no_totp_login.json()
    assert login_no_totp_data.get("status") == "2fa_required", "Expected status '2fa_required'"
    print("    [OK] Login without TOTP code returned '2fa_required' response")

    # Step 5: Test /api/auth/login with invalid TOTP code
    print("\n[4] Testing /api/auth/login with invalid 2FA code...")
    res_bad_totp_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password,
        "totp_code": invalid_code
    })
    assert res_bad_totp_login.status_code == 401, "Expected 401 for invalid TOTP on login"
    print("    [OK] Login with invalid TOTP code rejected (401 Unauthorized)")

    # Step 6: Test /api/auth/login with valid TOTP code
    print("\n[5] Testing /api/auth/login with valid 2FA code...")
    valid_code_now = pyotp.TOTP(totp_secret).now()
    res_good_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password,
        "totp_code": valid_code_now
    })
    assert res_good_login.status_code == 200, f"Login with valid TOTP failed: {res_good_login.text}"
    good_login_data = res_good_login.json()
    assert good_login_data["user"]["email"] == test_email
    assert good_login_data["user"]["totp_verified"] is True
    print("    [OK] Login with valid 2FA code succeeded!")
    print(f"    [OK] Response: {good_login_data['message']}")

    # Step 7: Test user without secret receiving 2fa_setup_required & QR code on login
    print("\n[6] Testing /api/auth/login for user without 2FA secret (returns QR Code)...")
    legacy_email = f"legacy_{unique_id}@wattwise.io"
    db['users'].insert_one({'name': 'Legacy User', 'email': legacy_email, 'password': 'Password123!', 'role': 'Admin'})
    
    res_legacy_login = client.post("/api/auth/login", json={"email": legacy_email, "password": "Password123!"})
    assert res_legacy_login.status_code == 200
    legacy_data = res_legacy_login.json()
    assert legacy_data.get("status") == "2fa_setup_required", "Expected status '2fa_setup_required'"
    assert "qr_code_base64" in legacy_data, "qr_code_base64 missing in 2fa_setup_required response"
    assert "totp_secret" in legacy_data, "totp_secret missing in 2fa_setup_required response"
    print("    [OK] User without secret received QR Code & secret on login (status: 2fa_setup_required)")

    # Complete setup verification for legacy user
    legacy_totp_secret = legacy_data["totp_secret"]
    legacy_code = pyotp.TOTP(legacy_totp_secret).now()
    res_legacy_complete = client.post("/api/auth/login", json={"email": legacy_email, "password": "Password123!", "totp_code": legacy_code})
    assert res_legacy_complete.status_code == 200
    print("    [OK] User completed 2FA setup on login successfully!")

    print("\n=== ALL 2FA TOTP AUTHENTICATION TESTS PASSED PERFECTLY! ===\n")


if __name__ == "__main__":
    test_totp_auth_flow()
