import hashlib
from ecdsa import SECP256k1, BadSignatureError, SigningKey

if __name__ == "__main__":

    # 1) Generate a key pair on the same curve as Bitcoin and Ethereum
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()

    print("Private key (SECRET!):", private_key.to_string().hex())
    print("Public key :", public_key.to_string().hex())

    # 2) A simplified address: first 40 hex chars of SHA-256(public key)
    address = hashlib.sha256(public_key.to_string()).hexdigest()[:40]
    print("Address (simplified) :", address)

    # 3) Sign a message
    message = b"Alice pays Bob 5 coins"
    signature = private_key.sign(message, hashfunc=hashlib.sha256)

    print("\nSignature :", signature.hex()[:64], "...")

    # 4) Verify the genuine message
    print("Genuine message valid?", public_key.verify(signature, message, hashfunc=hashlib.sha256))

    # 5) Verify a modified message
    tampered = b"Alice pays Bob 500 coins"
    try:
        public_key.verify(signature, tampered, hashfunc=hashlib.sha256)
        print("Tampered message valid? True (this should NEVER happen)")
    except BadSignatureError:
        print("Tampered message valid? False (signature rejected)")

    # 6) Verify with somebody else's public key
    other_public = SigningKey.generate(curve=SECP256k1).get_verifying_key()
    try:
        other_public.verify(signature, message, hashfunc=hashlib.sha256)
        print("Wrong public key valid? True (this should NEVER happen)")
    except BadSignatureError:
        print("Wrong public key valid? False (not signed by that key)")