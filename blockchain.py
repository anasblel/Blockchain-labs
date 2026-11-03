import hashlib
import json
import time
class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions # a list (JSON-serializable)
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()
    def compute_hash(self) -> str:
        """SHA-256 of every field of the block, in a stable order."""
        payload = json.dumps(
        {
        "index": self.index,
        "timestamp": self.timestamp,
        "transactions": self.transactions,
        "previous_hash": self.previous_hash,
        "nonce": self.nonce,
        },
        sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    def mine(self, difficulty: int) -> None:
        """Increase the nonce until the hash starts with `difficulty` zeros."""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
    def __repr__(self) -> str:
        return (f"Block(index={self.index}, prev={self.previous_hash[:8]}..., "
        f"hash={self.hash[:8]}..., nonce={self.nonce}, "
        f"txs={len(self.transactions)})")
class Blockchain:
    def __init__(self, difficulty: int = 0):
        self.difficulty = difficulty
        self.chain = [self._create_genesis_block()]
    def _create_genesis_block(self) -> Block:
        genesis = Block(0, ["Genesis block"], "0" * 64, timestamp=0)
        genesis.mine(self.difficulty)
        return genesis
    @property
    def last_block(self) -> Block:
        return self.chain[-1]
    def add_block(self, transactions) -> Block:
        block = Block(len(self.chain), transactions, self.last_block.hash)
        block.mine(self.difficulty)
        self.chain.append(block)
        return block
    def is_valid(self):
        """Return (True, message) if the chain is consistent, else (False, reason)."""
        prefix = "0" * self.difficulty
        for i, block in enumerate(self.chain):
            if block.hash != block.compute_hash():
                return False, f"Block {i}: stored hash does not match its content"
            if not block.hash.startswith(prefix):
                return False, f"Block {i}: hash does not satisfy the difficulty"
            if i == 0:
                if block.previous_hash != "0" * 64:
                    return False, "Genesis block has a wrong previous hash"
            elif block.previous_hash != self.chain[i - 1].hash:
                return False, f"Block {i}: link to block {i - 1} is broken"
        return True, "Chain is valid"

    def print_chain(self) -> None:
        for block in self.chain:
            print(block)
        for tx in block.transactions:
            print(" ", tx)
if __name__ == "__main__":
            bc = Blockchain()
            bc.add_block(["Alice pays Bob 5"])
            bc.add_block(["Bob pays Carol 2", "Carol pays Dave 1"])
            bc.print_chain()
            print(bc.is_valid())
