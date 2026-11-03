import hashlib
import json
from ecdsa import SECP256k1, BadSignatureError, SigningKey, VerifyingKey
from blockchain import Blockchain


def address_from_public_key(public_key_bytes: bytes) -> str:
    return hashlib.sha256(public_key_bytes).hexdigest()[:40]


def signable_bytes(tx: dict) -> bytes:
    """The exact bytes that are signed: sender, receiver, amount."""
    content = {k: tx[k] for k in ("sender", "receiver", "amount")}
    return json.dumps(content, sort_keys=True).encode("utf-8")


class Wallet:
    def __init__(self, name: str):
        self.name = name
        self._private_key = SigningKey.generate(curve=SECP256k1)
        public_key = self._private_key.get_verifying_key()
        self.public_key_hex = public_key.to_string().hex()
        self.address = address_from_public_key(public_key.to_string())

    def create_transaction(self, receiver_address: str, amount: float) -> dict:
        tx = {
            "sender": self.address,
            "receiver": receiver_address,
            "amount": amount,
            "public_key": self.public_key_hex,
        }
        tx["signature"] = self._private_key.sign(
            signable_bytes(tx), hashfunc=hashlib.sha256
        ).hex()
        return tx


def verify_transaction(tx: dict) -> bool:
    try:
        if tx["amount"] <= 0:
            return False

        public_key_bytes = bytes.fromhex(tx["public_key"])

        # Rule 1: the key must match the claimed sender address
        if address_from_public_key(public_key_bytes) != tx["sender"]:
            return False

        # Rule 2: the signature must be valid for this content
        verifying_key = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
        return verifying_key.verify(
            bytes.fromhex(tx["signature"]), signable_bytes(tx), hashfunc=hashlib.sha256
        )

    except (BadSignatureError, KeyError, ValueError):
        return False


def add_transactions(bc: Blockchain, transactions: list) -> None:
    """Add a block containing only the valid transactions."""
    accepted = []
    for tx in transactions:
        ok = verify_transaction(tx)
        print(f" tx {tx['amount']:>6} : {'ACCEPTED' if ok else 'REJECTED'}")
        if ok:
            accepted.append(tx)

    if accepted:
        bc.add_block(accepted)


if __name__ == "__main__":
    alice, bob, mallory = Wallet("Alice"), Wallet("Bob"), Wallet("Mallory")

    bc = Blockchain(difficulty=3)

    print("Block 1: honest payment")
    add_transactions(bc, [alice.create_transaction(bob.address, 5)])

    print("Block 2: three attempts")
    honest = bob.create_transaction(alice.address, 2)

    modified = alice.create_transaction(bob.address, 5)
    modified["amount"] = 500  # amount changed after signing

    forged = mallory.create_transaction(bob.address, 10)
    forged["sender"] = alice.address  # Mallory pretends to be Alice

    add_transactions(bc, [honest, modified, forged])

    print()
    bc.print_chain()
    print("Chain valid?", bc.is_valid())