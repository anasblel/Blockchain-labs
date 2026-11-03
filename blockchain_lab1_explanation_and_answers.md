# Lab 1 --- Building a Mini Blockchain in Python

## Introduction

In this lab, we built a small blockchain in Python. The goal was to
understand the main ideas behind a blockchain by implementing them
ourselves:

-   **Hashing:** turning data into a fixed-size digital fingerprint.
-   **Blocks:** storing transactions and a reference to the previous
    block.
-   **Chain validation:** checking whether the blocks still fit together
    correctly.
-   **Tampering detection:** seeing what happens when someone changes
    stored data.
-   **Proof of Work (PoW):** making block creation require computational
    effort.
-   **Digital signatures:** proving that a transaction was authorized by
    the owner of a private key.
-   **Signed transactions:** accepting only transactions that pass the
    verification rules.

The lab contains six parts. Each part builds on the previous one.

------------------------------------------------------------------------

# Part A --- Hash functions

## 1. What we did

We created `hash_demo.py`. It uses Python's built-in `hashlib` library
to calculate SHA-256 hashes.

A hash function takes an input of any size and produces a fixed-size
result. SHA-256 produces a 256-bit digest, usually displayed as 64
hexadecimal characters.

### The `sha256_hex()` function

``` python
def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

What happens here?

1.  `text` is the input string.
2.  `.encode("utf-8")` converts the string into bytes because the hash
    function works with bytes.
3.  `hashlib.sha256(...)` calculates the SHA-256 hash.
4.  `.hexdigest()` displays the result as hexadecimal characters.

### The `differing_bits()` function

``` python
def differing_bits(hex_a: str, hex_b: str) -> int:
    return bin(int(hex_a, 16) ^ int(hex_b, 16)).count("1")
```

This function counts how many bits are different between two hashes:

1.  `int(hex_a, 16)` converts the first hexadecimal hash into an
    integer.
2.  The same conversion is done for the second hash.
3.  `^` performs XOR. A bit is `1` in the result when the two
    corresponding bits are different.
4.  `bin(...)` converts the result to binary.
5.  `.count("1")` counts the different bits.

## 2. The experiments

### Experiment 1 --- Determinism

We calculate the hash of `"hello"` twice and compare the results.

**Observation:** The result is `True`.

**Meaning:** The same input always produces the same hash, provided the
same hash algorithm is used.

### Experiment 2 --- Fixed-size output

We create a long string:

``` python
long_text = "blockchain " * 100_000
```

Then we calculate its SHA-256 hash and measure the length of the
hexadecimal result.

**Observation:** The digest is always 64 hexadecimal characters.

**Meaning:** The output size does not depend on the input size. A short
string and a very long string both produce a 256-bit digest.

### Experiment 3 --- Avalanche effect

We compare:

-   `hello`
-   `Hello`

Only one character changes: lowercase `h` becomes uppercase `H`.

**Observation:** The two hashes are very different. Around half of their
256 bits should differ.

**Meaning:** A tiny input change creates a large and
unpredictable-looking change in the hash.

## 3. Answers to Part A checkpoint questions

### Q1. Why is the digest always 64 characters long?

SHA-256 always produces 256 bits. One hexadecimal character represents 4
bits, so:

`256 / 4 = 64`

Therefore, the hexadecimal digest always contains 64 characters.

### Q2. About how many bits should differ after a one-letter change if the avalanche effect holds?

About half of the 256 bits should differ:

`256 / 2 = 128 bits`

The exact number is not always 128. It can be higher or lower because
the output behaves like a random-looking value.

### Q3. Try five more pairs of strings that differ by one character. What range of differing bits do you observe?

The exact results depend on the strings tested. The values should
generally be around 128 out of 256, but they will vary. For example,
some pairs may have around 115 different bits and others around 140.

The important observation is that changing only one character changes
many bits of the hash. There is no requirement for every result to be
exactly 128.

------------------------------------------------------------------------

# Part B --- The Block and Blockchain classes

## 1. What we did

We created `blockchain.py`. It contains two classes:

-   `Block`: represents one block.
-   `Blockchain`: manages the list of blocks and checks whether the
    chain is valid.

## 2. Understanding the `Block` class

A block stores:

  Field             Meaning
  ----------------- -------------------------------------
  `index`           The block's position in the chain
  `timestamp`       The time when the block was created
  `transactions`    The data stored in the block
  `previous_hash`   The hash of the previous block
  `nonce`           A number changed during mining
  `hash`            The block's own calculated hash

### The constructor: `__init__()`

When a block is created, the constructor stores its fields and
calculates its hash using `compute_hash()`.

If no timestamp is provided, it uses the current time with
`time.time()`.

### The `compute_hash()` method

This method:

1.  Collects all important block fields in a dictionary.
2.  Uses `json.dumps(..., sort_keys=True)` to convert the dictionary
    into a stable JSON string.
3.  Encodes the JSON string into bytes.
4.  Calculates its SHA-256 hash.

The hash covers the block's index, timestamp, transactions, previous
hash, and nonce. If one of these fields changes, the calculated hash
should change too.

**Why `sort_keys=True`?** It makes the JSON keys appear in a consistent
order. This helps ensure that the same data is serialized in the same
way before hashing.

### The `mine()` method

The method tries different nonce values until the block hash starts with
the required number of zeros.

In Part B, the blockchain uses difficulty `0`. Therefore, no leading
zero is required and mining finishes immediately.

### The `__repr__()` method

This method controls how a block is displayed when we print it. It shows
a short version of the block's index, previous hash, hash, nonce, and
number of transactions.

## 3. Understanding the `Blockchain` class

### Creating the chain

``` python
self.chain = [self._create_genesis_block()]
```

This creates a list containing the first block, called the **genesis
block**.

### The genesis block

The genesis block:

-   Has index `0`.
-   Contains `"Genesis block"` as its transaction.
-   Uses `"0" * 64` as its previous hash.
-   Uses timestamp `0`.

The fixed timestamp helps every run create the same genesis block when
the other fields and difficulty are also the same.

### The `last_block` property

It returns the last block in the chain:

``` python
return self.chain[-1]
```

### The `add_block()` method

When we add a new block:

1.  Its index is set to the current chain length.
2.  Its `previous_hash` is set to the hash of the current last block.
3.  The new block is mined using the selected difficulty.
4.  The block is appended to the chain.

This is how the blocks become linked.

### The `is_valid()` method

This method checks the chain:

1.  It recalculates each block's hash and compares it with the stored
    hash.
2.  It checks that each hash satisfies the difficulty.
3.  It checks that the genesis block has the expected previous hash.
4.  It checks that every later block points to the hash of the block
    immediately before it.

If all checks pass, it returns:

`(True, 'Chain is valid')`

Otherwise, it returns `False` and a reason.

## 4. What happened when we ran the file?

The main section created a blockchain and added two blocks:

-   Block 0: Genesis block.
-   Block 1: Alice pays Bob 5.
-   Block 2: Bob pays Carol 2 and Carol pays Dave 1.

The program printed the blocks and then checked the chain.

**Expected final result:** `(True, 'Chain is valid')`

## 5. Answers to Part B checkpoint questions

### Q1. Which line of the code creates the chain property?

The line is:

``` python
block = Block(len(self.chain), transactions, self.last_block.hash)
```

This line creates a new block. Most importantly, it gives the new block
the hash of the previous block through `self.last_block.hash`.

The block is then added to the chain with:

``` python
self.chain.append(block)
```

Together, these operations create the linked chain.

### Q2. Why do we sort the JSON keys? What would happen if we did not?

We use `sort_keys=True` to serialize dictionary keys in a consistent
order.

Without consistent serialization, the same information could potentially
be represented in a different order and produce different JSON bytes.
Different bytes produce different hashes. This could cause different
nodes to calculate different hashes for what should be the same block.

### Q3. Why is the genesis block's timestamp fixed to 0 and not `time.time()`?

A fixed timestamp makes the genesis block reproducible. If each node
used its own current time, each node could create a different genesis
block and therefore a different chain.

------------------------------------------------------------------------

# Part C --- Tampering and detection

## 1. What we did

We created `tamper_demo.py`. It demonstrates how changing a block
affects the blockchain.

The script first creates a chain with three blocks after the genesis
block, then performs three tampering experiments.

## 2. Understanding `forge_from()`

This function goes through blocks from a selected starting index to the
end of the chain.

For each block, it:

1.  Updates `previous_hash` to point to the preceding block's current
    hash.
2.  Resets the nonce to `0`.
3.  Recalculates the block hash.
4.  Mines the block again using the chain's difficulty.

In this lab, the function demonstrates how recalculating later links can
make a modified single-copy chain consistent again. It is a teaching
demonstration, not a complete model of attacking a real blockchain
network.

## 3. The four experiments

### Step 1 --- Honest chain

The program creates the original chain and calls `bc.is_valid()`.

**Expected result:** `True`.

The blocks have matching hashes and links.

### Step 2 --- Change the transaction data only

The program changes:

`Alice pays Bob 5`

to:

`Alice pays Bob 50`

It does not recalculate the block's hash.

**Expected result:** Invalid.

The stored hash no longer matches the content of the block.

### Step 3 --- Recalculate the edited block's hash

The program recalculates and mines the hash of block 1.

**Expected result:** Still invalid.

Block 2 still contains the old hash of block 1 in its `previous_hash`
field. Therefore, the link between blocks 1 and 2 is broken.

### Step 4 --- Recalculate the later blocks

The program calls `forge_from(bc, 1)`. It recalculates the edited block
and the following blocks so that their links match again.

**Expected result:** The chain can become valid again.

With difficulty 0, this is very fast. With difficulty 4, the
recalculation and mining require more work.

## 4. Answers to Part C discussion questions

### Q1. What do Steps 2 and 3 show?

They show that the blockchain is **tamper-evident**.

-   In Step 2, changing transaction data makes the block's stored hash
    incorrect.
-   In Step 3, recalculating that block's hash causes the next block's
    previous-hash link to become incorrect.

The validator detects both problems.

### Q2. What does Step 4 show? Why is a real network different?

Step 4 shows that a person who controls the only copy of a chain can
recalculate the hashes and links of the modified block and the later
blocks.

A real blockchain is distributed across many independent nodes. An
attacker cannot simply change one local copy and make every other node
accept it. The attacker must also overcome the network's consensus rules
and the work performed by honest participants.

### Q3. Why does higher difficulty increase the attacker's cost?

Higher difficulty requires more attempts to find a hash with the
required number of leading zeros. If an attacker must re-mine several
blocks, the extra work makes the modification more expensive and
time-consuming.

------------------------------------------------------------------------

# Part D --- A taste of Proof of Work

## 1. What we did

We created `mining_demo.py`. It tests mining at difficulty levels from 1
to 5.

For every difficulty, the script:

1.  Creates a block with a fixed timestamp of `0`.
2.  Records the starting time.
3.  Calls `block.mine(difficulty)`.
4.  Records the ending time.
5.  Prints the difficulty, nonce, elapsed time, and beginning of the
    resulting hash.

The fixed timestamp makes the block's starting data reproducible. The
nonce found for each difficulty is therefore deterministic with this
exact code and environment-independent hash algorithm, while the
measured time depends on the computer.

## 2. What is Proof of Work?

Proof of Work is a process where a computer repeatedly changes a nonce
and calculates the block hash until it finds a hash that satisfies a
rule.

For example:

-   Difficulty 1: hash starts with `0`.
-   Difficulty 2: hash starts with `00`.
-   Difficulty 3: hash starts with `000`.
-   Difficulty 4: hash starts with `0000`.
-   Difficulty 5: hash starts with `00000`.

The computer cannot directly calculate the nonce that will work. It
tries values until it finds one.

## 3. Answers to Part D questions

### Q1. Each extra zero hex character multiplies the expected number of attempts by what factor?

Each extra zero multiplies the expected number of attempts by **16**.

One hexadecimal character has 16 possible values (`0` to `f`). The
probability that a hash starts with one specific hexadecimal character,
`0`, is 1 in 16.

Therefore, each additional required leading zero makes success
approximately 16 times less likely.

### Q2. Using your measured time at difficulty 5, estimate the time for difficulty 8. Why should we not run it?

Difficulty 8 is three levels higher than difficulty 5.

The expected work is multiplied by:

`16 × 16 × 16 = 16³ = 4,096`

So the estimated time at difficulty 8 is approximately:

`time at difficulty 5 × 4,096`

We should not run it for this lab because it could take a very long time
on a normal computer. The lab asks us to use the estimate instead.

### Q3. Bitcoin block hashes have started with roughly 19--20 zero hexadecimal characters. What does this tell you about the hardware miners use?

It shows that Bitcoin mining requires an enormous amount of
computational work. Miners use specialised, highly efficient hardware
called **ASICs** (Application-Specific Integrated Circuits), rather than
relying on ordinary CPUs.

### Q4. Verification takes one hash; finding takes millions. Why is this asymmetry essential?

Finding a valid hash must be difficult so that creating blocks requires
significant work. Verifying a proposed block must be easy so that other
nodes can quickly check it.

This makes it expensive to produce blocks but inexpensive for the
network to verify them.

------------------------------------------------------------------------

# Part E --- Keys and digital signatures

## 1. What we did

We created `keys_demo.py`. It uses the `ecdsa` Python library to
generate keys, sign a message, and verify the signature.

We installed the library with:

``` powershell
pip install ecdsa
```

The script uses the `SECP256k1` elliptic curve, which is also used by
Bitcoin.

## 2. Understanding the key pair

### Private key

The private key is secret. It is used to create digital signatures.

### Public key

The public key can be shared. It is used to verify signatures created by
the corresponding private key.

The script generates the pair with:

``` python
private_key = SigningKey.generate(curve=SECP256k1)
public_key = private_key.get_verifying_key()
```

### Simplified address

The program calculates SHA-256 of the public key and keeps the first 40
hexadecimal characters.

This creates a simplified address for the exercise. It is not the
complete address-generation process used by Bitcoin or Ethereum.

## 3. Signing and verifying a message

The message is:

`Alice pays Bob 5 coins`

The private key signs it:

``` python
signature = private_key.sign(message, hashfunc=hashlib.sha256)
```

The public key then verifies the signature.

The script tests three situations:

1.  The original message with the correct public key.
2.  A modified message with the original public key.
3.  The original message with another person's public key.

## 4. Answers to Part E checkpoint questions

### Q1. Run the script twice. Why are the keys different each time?

The keys are generated randomly each time the program runs. The random
generation creates a new private key and a corresponding public key.

Therefore, the keys and simplified address are different between runs.

### Q2. Which key is used to sign? Which key is used to verify?

-   The **private key** signs the message.
-   The **public key** verifies the signature.

The private key must remain secret. The public key can be shared.

### Q3. Which guarantees are demonstrated by Step 5 and Step 6?

The three guarantees are:

-   **Authentication:** checking that the signature was created using
    the private key corresponding to a particular public key.
-   **Integrity:** detecting whether the signed message was changed.
-   **Non-repudiation:** a digital signature can provide evidence that
    the holder of a private key authorized a message, assuming the key
    was controlled securely and the signing process can be trusted.

**Step 5 --- Modified message:** It demonstrates integrity. The
signature was created for the original message, so verification fails
when the message is changed.

**Step 6 --- Wrong public key:** It demonstrates that the signature must
be checked with the matching public key. This supports authentication:
another person's public key cannot verify the signature.

### Q4. The private key is only 32 bytes. Where would you store it in a real application?

It should be stored securely, for example:

-   In a hardware wallet or hardware security module.
-   In a secure operating-system keystore.
-   In an encrypted file with strong access protection.

It must never be written directly in source code, committed to Git, or
shared in a message.

The keys generated in this lab are for learning only. Do not reuse them
for real transactions.

------------------------------------------------------------------------

# Part F --- A chain of signed transactions

## 1. What we did

We created `signed_chain.py`. This part combines the previous ideas:

-   A blockchain stores blocks.
-   Each transaction is signed with a private key.
-   The transaction is checked with the corresponding public key.
-   Only valid transactions are added to a block.

The script creates three wallets: Alice, Bob, and Mallory.

## 2. Understanding the important functions

### `address_from_public_key()`

This function calculates a simplified address from the public key. It
uses SHA-256 and keeps the first 40 hexadecimal characters.

### `signable_bytes()`

This function selects the transaction fields that must be signed:

-   `sender`
-   `receiver`
-   `amount`

It serializes them as JSON with sorted keys and converts the result into
bytes.

The public key and signature are not included in the signed content.

### The `Wallet` class

Each wallet generates its own private/public key pair and calculates its
address.

The `create_transaction()` method:

1.  Creates a transaction with sender, receiver, amount, and public key.
2.  Signs the selected transaction content using the wallet's private
    key.
3.  Adds the signature to the transaction.
4.  Returns the completed transaction.

### `verify_transaction()`

This function checks whether a transaction should be accepted.

It applies three main checks:

1.  **Positive amount:** the amount must be greater than zero.
2.  **Address and public key match:** the address calculated from the
    supplied public key must match the claimed sender address.
3.  **Valid signature:** the signature must be valid for the
    transaction's sender, receiver, and amount.

If a check fails, the function returns `False`.

### `add_transactions()`

This function checks every transaction in a list.

-   Valid transactions are added to the `accepted` list.
-   Invalid transactions are rejected.
-   If at least one transaction is accepted, the accepted transactions
    are added as a new block.

## 3. The three attempts

### Attempt 1 --- Honest payment

Alice creates a transaction to pay Bob 5 coins.

The transaction has Alice's address, Alice's public key, and a valid
signature.

**Result:** ACCEPTED.

### Attempt 2 --- Modified transaction

Alice signs a transaction for 5 coins. After signing, the script changes
the amount to 500.

The signature still belongs to the original content, not the modified
amount.

**Result:** REJECTED.

### Attempt 3 --- Forged sender

Mallory creates a transaction using her own key. The script then changes
the sender field to Alice's address.

The public key still belongs to Mallory, so the address calculated from
that key does not match Alice's claimed address.

**Result:** REJECTED.

The final blockchain is valid because only the accepted transactions
were added.

## 4. Answers to Part F questions

### Q1. Why is the modified transaction rejected? Which cryptographic property protects against it?

It is rejected because the amount is changed from 5 to 500 after the
transaction was signed.

The signature was calculated using the original amount. When the
verifier checks the modified transaction, the signature no longer
matches.

The cryptographic property is **integrity**: the signature helps detect
changes to the signed transaction content.

### Q2. Why is the forged transaction rejected? Which rule catches it?

Mallory signs the transaction with her own private key but changes the
sender field to Alice's address.

The verifier calculates an address from the public key included in the
transaction. That address belongs to Mallory, not Alice.

The transaction is rejected by **Rule 1: the public key must match the
claimed sender address**.

### Q3. Where in the code would you add a balance check? What data would you need?

The balance check should be added inside `verify_transaction()` or in
the transaction-acceptance process before a transaction is added to the
accepted list.

We need to know:

-   The sender's current balance.
-   The transaction amount.
-   The transaction history from previous blocks.
-   Any initial balances or coinbase transactions.

A balance function could replay the blockchain from the beginning and
calculate each address's balance by subtracting sent amounts and adding
received amounts.

If the sender's balance is lower than the transaction amount, the
transaction should be rejected.

### Q4. Someone replays an accepted transaction in a later block. Does the current code detect it?

No. The current code does not detect replayed transactions.

A transaction with a valid signature remains valid whenever it is
checked again. The program does not store transaction IDs or
sender-specific transaction counters.

To prevent replay, the lab suggests adding a **nonce or counter per
sender**. The nonce must be included in the signed transaction content,
and the verifier must reject a nonce that has already been used.

------------------------------------------------------------------------

# Part C discussion paragraph --- Why a hash chain alone is not secure, and what is missing

A hash chain helps detect changes because each block contains the hash
of the previous block. If someone changes a block, its hash changes and
the link to the next block becomes invalid. However, a hash chain alone
is not enough to protect a blockchain. If an attacker controls the only
copy, they can change the data and recalculate the hashes of the
modified block and all following blocks. Proof of Work makes this more
difficult by requiring computational effort to create valid blocks. A
real blockchain also uses a distributed network of independent nodes and
consensus rules. Digital signatures provide another important protection
by allowing nodes to verify that transactions were authorized by the
owner of the sender's private key.

------------------------------------------------------------------------

# Important limitations of this mini blockchain

This lab is an educational demonstration, not a production-ready
cryptocurrency.

The current implementation does not fully provide:

-   **Balance validation:** a wallet can send more coins than it owns.
-   **Double-spend protection:** balances are not tracked.
-   **Replay protection:** an accepted signed transaction can be
    submitted again.
-   **Real network consensus:** the program runs with one local chain
    rather than a distributed network of nodes.
-   **Production address formats:** the address-generation method is
    simplified.
-   **Secure wallet storage:** the lab generates keys for demonstration
    and does not implement a complete wallet-security system.

These limitations are intentional learning opportunities. The bonus
challenges ask you to improve some of them.

------------------------------------------------------------------------

# Final summary

  -----------------------------------------------------------------------
  Part                    What we implemented     Main lesson
  ----------------------- ----------------------- -----------------------
  A --- Hash functions    SHA-256 and hash        A small input change
                          comparison              creates a very
                                                  different hash

  B --- Blockchain        `Block` and             Each block stores the
                          `Blockchain` classes    previous block's hash

  C --- Tampering         Changed data and        A hash chain detects
                          recalculated hashes     changes, but a single
                                                  copy can be rewritten

  D --- Mining            Nonce search and        Higher difficulty
                          difficulty              requires more expected
                                                  work

  E --- Digital           Key generation,         Private keys sign;
  signatures              signing, and            public keys verify
                          verification            

  F --- Signed            Wallets and transaction Only transactions with
  transactions            validation              matching addresses and
                                                  valid signatures are
                                                  accepted
  -----------------------------------------------------------------------

## Suggested bonus challenge

A good first challenge is **Challenge 3 --- Replay protection**.

Add a nonce (counter) to each transaction, include it in the signed
content, and reject a transaction if that sender has already used the
same nonce.

This teaches an important blockchain security idea: a valid signature
alone does not prevent someone from submitting the same valid
transaction more than once.
