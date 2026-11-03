import sys
import time
from blockchain import Blockchain


def forge_from(bc: Blockchain, start: int) -> None:
    """Attacker recomputes (and re-mines) every block from `start` onward."""
    for i in range(start, len(bc.chain)):
        block = bc.chain[i]
        block.previous_hash = bc.chain[i - 1].hash
        block.nonce = 0
        block.hash = block.compute_hash()
        block.mine(bc.difficulty)


if __name__ == "__main__":
    difficulty = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    bc = Blockchain(difficulty=difficulty)
    bc.add_block(["Alice pays Bob 5"])
    bc.add_block(["Bob pays Carol 2"])
    bc.add_block(["Carol pays Dave 1"])

    print("1) Honest chain :", bc.is_valid())

    # --- Attack 1: change data only ---------------------------------------
    bc.chain[1].transactions = ["Alice pays Bob 50"]
    print("2) Data edited :", bc.is_valid())

    # --- Attack 2: also recompute the hash of the edited block ------------
    bc.chain[1].hash = bc.chain[1].compute_hash()
    bc.chain[1].mine(bc.difficulty)
    print("3) Block 1 re-hashed :", bc.is_valid())

    # --- Attack 3: recompute every later block too ------------------------
    start = time.time()
    forge_from(bc, 1)
    elapsed = time.time() - start

    print("4) Whole tail forged :", bc.is_valid(), f"(took {elapsed:.3f} s)")