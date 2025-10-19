"""Debug script to test nonce verification"""
import device_fingerprinting
import base64
import json
import time

print("="*80)
print("Testing Server Nonce Creation and Verification")
print("="*80)

# Enable PQC
print("\n1. Enabling PQC...")
success = device_fingerprinting.enable_post_quantum_crypto("Dilithium3")
print(f"   PQC enabled: {success}")

# Create nonce
print("\n2. Creating server nonce...")
nonce, signature = device_fingerprinting.create_server_nonce()
print(f"   Nonce length: {len(nonce)} bytes")
print(f"   Signature length: {len(signature)} bytes")
print(f"   Nonce: {nonce[:60]}...")
print(f"   Signature: {signature[:60]}...")

# Decode nonce to inspect
print("\n3. Inspecting nonce structure...")
try:
    nonce_decoded = base64.b64decode(nonce).decode('utf-8')
    nonce_data = json.loads(nonce_decoded)
    print(f"   Nonce value: {nonce_data['nonce']}")
    print(f"   Timestamp: {nonce_data['timestamp']}")
    print(f"   Algorithm: {nonce_data['algorithm']}")
    print(f"   Current time: {int(time.time())}")
    print(f"   Age: {int(time.time()) - nonce_data['timestamp']} seconds")
except Exception as e:
    print(f"   ERROR: {e}")

# Decode signature to inspect
print("\n4. Inspecting signature structure...")
try:
    sig_decoded = base64.b64decode(signature).decode('utf-8')
    sig_data = json.loads(sig_decoded)
    print(f"   Type: {sig_data.get('type')}")
    print(f"   Version: {sig_data.get('version')}")
    print(f"   Signature type: {sig_data.get('signature_type')}")
    print(f"   Algorithm: {sig_data.get('algorithm')}")
    print(f"   Has pqc_timestamp: {('pqc_timestamp' in sig_data)}")
    if 'pqc_timestamp' in sig_data:
        print(f"   PQC timestamp: {sig_data['pqc_timestamp']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test backend directly
print("\n5. Testing backend directly...")
try:
    from device_fingerprinting.hybrid_pqc import HybridPQCBackend
    backend = HybridPQCBackend("Dilithium3")
    test_data = b"test"
    test_sig = backend.sign(test_data)
    test_result = backend.verify(test_sig, test_data)
    print(f"   Backend sign/verify: {test_result}")
except Exception as e:
    print(f"   ERROR: {e}")

# Verify nonce
print("\n6. Verifying server nonce...")
try:
    result = device_fingerprinting.verify_server_nonce(nonce, signature)
    print(f"   Verification result: {result}")
    if not result:
        print("   ❌ FAILED - Nonce verification returned False")
    else:
        print("   ✅ SUCCESS - Nonce verified!")
except Exception as e:
    print(f"   ERROR: {type(e).__name__}: {e}")

print("\n" + "="*80)
