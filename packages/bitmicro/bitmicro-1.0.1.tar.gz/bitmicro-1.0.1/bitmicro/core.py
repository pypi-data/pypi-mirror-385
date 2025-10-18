"""
bitmicro — MicroBitcoin Python library (Bitcash-style)
Fully compatible with MicroBitcoin (MBC) mainnet.
Author: neoncorp(code creator) & Volbil(Api Creator)
"""

import os
import base58
import hashlib
import requests
from ecdsa import SECP256k1, SigningKey

API_BASE = "https://api.mbc.wiki"


# ==========================
#  CRYPTO UTILITIES
# ==========================

def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def ripemd160(b: bytes) -> bytes:
    h = hashlib.new('ripemd160')
    h.update(b)
    return h.digest()


def hash160(b: bytes) -> bytes:
    """RIPEMD160(SHA256(b))"""
    return ripemd160(sha256(b))


def double_sha256(b: bytes) -> bytes:
    return sha256(sha256(b))


def to_wif(privkey: bytes, compressed: bool = False) -> str:
    """Convert private key bytes to WIF (uncompressed by default)."""
    prefix = b'\x80' + privkey + (b'\x01' if compressed else b'')
    checksum = double_sha256(prefix)[:4]
    return base58.b58encode(prefix + checksum).decode()


def pubkey_to_address(pubkey: bytes) -> str:
    """Convert public key to Base58Check P2PKH MicroBitcoin address."""
    h160 = hash160(pubkey)
    prefix = b'\x1a' + h160  # 0x26 = “B” prefix (MicroBitcoin)
    checksum = double_sha256(prefix)[:4]
    return base58.b58encode(prefix + checksum).decode()


def wif_to_privkey(wif: str) -> bytes:
    """Decode WIF -> private key bytes."""
    decoded = base58.b58decode(wif)
    key = decoded[1:-4]
    # Remove compression byte if present
    if len(key) == 33 and key[-1] == 0x01:
        key = key[:-1]
    return key


# ==========================
#  NETWORK WRAPPER
# ==========================

class Network:
    @staticmethod
    def get(endpoint: str) -> dict:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        return r.json()

    @staticmethod
    def post(endpoint: str, data: dict) -> dict:
        r = requests.post(f"{API_BASE}/{endpoint}", json=data, timeout=10)
        return r.json()

    # ---- API methods ----
    @staticmethod
    def info(): return Network.get("info")

    @staticmethod
    def balance(address): return Network.get(f"balance/{address}")

    @staticmethod
    def unspent(address): return Network.get(f"unspent/{address}")

    @staticmethod
    def history(address): return Network.get(f"history/{address}")

    @staticmethod
    def transaction(txid): return Network.get(f"transaction/{txid}")

    @staticmethod
    def broadcast(raw): return Network.post("broadcast", {"raw": raw})


# ==========================
#  WALLET CLASS
# ==========================

class Wallet:
    def __init__(self, privkey: bytes):
        self.privkey = privkey
        self.signing_key = SigningKey.from_string(privkey, curve=SECP256k1)
        self.verifying_key = self.signing_key.verifying_key
        # Use uncompressed public key (0x04 + raw)
        pubkey = b'\x04' + self.verifying_key.to_string()
        self.address = pubkey_to_address(pubkey)
        self.wif = to_wif(privkey, compressed=False)

    # ---- Static creation methods ----
    @staticmethod
    def new():
        """Generate a new wallet with random private key."""
        return Wallet(os.urandom(32))

    @staticmethod
    def from_wif(wif: str):
        """Load wallet from existing WIF."""
        return Wallet(wif_to_privkey(wif))

    # ---- Network methods ----
    def get_balance(self):
        res = Network.balance(self.address)
        if res["error"]:
            return 0
        return res["result"]["balance"]

    def get_unspent(self):
        res = Network.unspent(self.address)
        return res.get("result", [])

    def get_history(self):
        res = Network.history(self.address)
        return res["result"]["tx"]

    # ---- Transaction (stub/demo) ----
    def create_tx(self, to_address: str, amount: int, fee: int = 10):
        """
        Create a simple transaction (not fully serialized).
        """
        utxos = self.get_unspent()
        if not utxos:
            raise Exception("No unspent outputs found")

        utxo = utxos[0]
        change = utxo["value"] - amount - fee
        if change < 0:
            raise Exception("Insufficient funds")

        tx = {
            "inputs": [utxo],
            "outputs": [
                {"address": to_address, "value": amount},
                {"address": self.address, "value": change}
            ]
        }
        return tx

    def sign_tx(self, tx: dict):
        """Dummy sign – replace with full Bitcoin TX serialization."""
        raw = str(tx).encode()
        sig = self.signing_key.sign_deterministic(sha256(raw))
        return raw.hex() + sig.hex()

    def send(self, to_address: str, amount: int):
        tx = self.create_tx(to_address, amount)
        raw = self.sign_tx(tx)
        res = Network.broadcast(raw)
        if res["error"]:
            raise Exception(res["error"])
        return res["result"]


# ==========================
#  TEST ENTRY POINT
# ==========================

if __name__ == "__main__":
    print("Uhh?")
