"""AES-256 Vault: Securely encrypt and decrypt environment files for GitHub.

Uses AES-GCM (Authenticated Encryption) with PBKDF2-HMAC-SHA256 (100,000 iterations).

Usage:
    python scripts/vault.py encrypt [source] [destination]
    python scripts/vault.py decrypt [source] [destination]

Examples:
    python scripts/vault.py encrypt backend/.env backend/.env.enc
    python scripts/vault.py decrypt backend/.env.enc backend/.env
"""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_file(src_path: Path, dest_path: Path, password: str) -> None:
    if not src_path.exists():
        print(f"Error: Source file '{src_path}' does not exist.")
        sys.exit(1)

    plaintext = src_path.read_bytes()
    salt = os.urandom(16)
    key = derive_key(password, salt)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    # File format: [16 bytes salt] + [12 bytes nonce] + [ciphertext + 16 bytes tag]
    dest_path.write_bytes(salt + nonce + ciphertext)
    print(f"[OK] Encrypted '{src_path}' -> '{dest_path}' ({len(salt + nonce + ciphertext)} bytes).")


def decrypt_file(src_path: Path, dest_path: Path, password: str) -> None:
    if not src_path.exists():
        print(f"Error: Source file '{src_path}' does not exist.")
        sys.exit(1)

    payload = src_path.read_bytes()
    if len(payload) < 28:
        print("Error: Encrypted payload is corrupted or too short.")
        sys.exit(1)

    salt = payload[:16]
    nonce = payload[16:28]
    ciphertext = payload[28:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        dest_path.write_bytes(plaintext)
        print(f"[OK] Successfully decrypted '{src_path}' -> '{dest_path}'.")
    except Exception:
        print("[ERROR] Decryption failed. Incorrect password or modified ciphertext.")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/vault.py [encrypt|decrypt] [src] [dest]")
        sys.exit(1)

    action = sys.argv[1].lower()
    default_src = Path("backend/.env")
    default_dest = Path("backend/.env.enc")

    if action == "encrypt":
        src = Path(sys.argv[2]) if len(sys.argv) > 2 else default_src
        dest = Path(sys.argv[3]) if len(sys.argv) > 3 else default_dest
        pwd = os.getenv("VAULT_PASSWORD")
        if not pwd:
            pwd = getpass.getpass("Enter encryption password: ")
            pwd_confirm = getpass.getpass("Confirm encryption password: ")
            if pwd != pwd_confirm:
                print("Passwords do not match!")
                sys.exit(1)
        encrypt_file(src, dest, pwd)

    elif action == "decrypt":
        src = Path(sys.argv[2]) if len(sys.argv) > 2 else default_dest
        dest = Path(sys.argv[3]) if len(sys.argv) > 3 else default_src
        pwd = os.getenv("VAULT_PASSWORD")
        if not pwd:
            pwd = getpass.getpass("Enter decryption password: ")
        decrypt_file(src, dest, pwd)
    else:
        print(f"Unknown action '{action}'. Use 'encrypt' or 'decrypt'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
