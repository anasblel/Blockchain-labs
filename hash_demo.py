import hashlib


def sha256_hex(text: str) -> str:
    """Calculate the SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def differing_bits(hex_a: str, hex_b: str) -> int:
    """Count how many bits are different between two hashes."""
    return bin(int(hex_a, 16) ^ int(hex_b, 16)).count("1")


if __name__ == "__main__":

    samples = ["hello", "Hello", "hello!", "", "Alice pays Bob 5 coins"]

    # Display hashes
    for s in samples:
        print(f"{s!r:30} -> {sha256_hex(s)}")

    print()

    # 1. Determinism
    print(
        "Same input twice, same hash?",
        sha256_hex("hello") == sha256_hex("hello")
    )

    # 2. Fixed size
    long_text = "blockchain " * 100_000
    print(
        "Digest length for a 1.1 MB input:",
        len(sha256_hex(long_text)),
        "hex chars"
    )

    # 3. Avalanche effect
    a = sha256_hex("hello")
    b = sha256_hex("Hello")

    print(
        f"Bits that differ between 'hello' and 'Hello': "
        f"{differing_bits(a, b)} / 256"
    )