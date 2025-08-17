#!/usr/bin/env python3
"""
OBINexus Legal Credential Manager
Secure storage for legal division credentials with constitutional compliance
"""

import os
import sys
import json
import base64
import zipfile
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class LegalCredentialManager:
    """Manages secure storage of legal division credentials"""
    
    def __init__(self, secure_base: str = ".obinexus-secure"):
        self.base_path = Path(secure_base) / "legal-division"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.cred_path = self.base_path / "credentials"
        self.backup_path = self.base_path / "backups"
        self.audit_path = self.base_path / "audit-logs"
        
        for path in [self.cred_path, self.backup_path, self.audit_path]:
            path.mkdir(exist_ok=True)
            
        # Set restrictive permissions on Unix-like systems
        if os.name == 'posix':
            os.chmod(self.base_path, 0o700)
            
    def generate_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key using PBKDF2 - Constitutional Compliance"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,  # Confio framework requirement
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def store_legal_counsel_credential(self, 
                                     google_password: str,
                                     encryption_password: str) -> Path:
        """Store legal-counsel@obinexus.org credential securely"""
        
        # Create credential data structure
        credential_data = {
            "email": "legal-counsel@obinexus.org",
            "password": google_password,
            "service": "Google Workspace Business Standard",
            "division": "legal",
            "access_level": "constitutional-authority",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "constitutional_compliance": True,
            "rotation_schedule": "annual",
            "next_rotation": "2026-08-10",
            "tier_level": 3,  # Tier 3 Constitutional Protection
            "gate_status": "HITL"  # Human-In-The-Loop verification required
        }
        
        # Generate salt for encryption
        salt = os.urandom(16)
        key = self.generate_key_from_password(encryption_password, salt)
        
        # Create Fernet instance for encryption
        fernet = Fernet(key)
        
        # Convert credential data to JSON
        json_data = json.dumps(credential_data, indent=2)
        
        # Create temporary file for credentials
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        temp_file = self.cred_path / f"legal_counsel_temp_{timestamp}.json"
        
        with open(temp_file, 'w') as f:
            f.write(json_data)
        
        # Create ZIP file
        zip_filename = f"legal_counsel_{timestamp}.zip"
        zip_path = self.cred_path / "primary" / zip_filename
        zip_path.parent.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(temp_file, "legal_counsel_credential.json")
        
        # Read ZIP file and encrypt it
        with open(zip_path, 'rb') as f:
            encrypted_data = fernet.encrypt(f.read())
        
        # Save encrypted file with salt in filename
        salt_hex = salt.hex()
        encrypted_filename = f"legal_counsel_{timestamp}_{salt_hex}.enc.zip"
        encrypted_path = self.cred_path / "primary" / encrypted_filename
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Clean up temporary files
        os.remove(temp_file)
        os.remove(zip_path)
        
        # Log for constitutional compliance
        self._log_credential_operation("STORE", "legal-counsel@obinexus.org", encrypted_path)
        
        # Create backup
        backup_filename = f"backup_{timestamp}_{encrypted_filename}"
        backup_full_path = self.backup_path / backup_filename
        
        with open(encrypted_path, 'rb') as src, open(backup_full_path, 'wb') as dst:
            dst.write(src.read())
        
        print(f"✓ Credential stored successfully: {encrypted_path}")
        print(f"✓ Backup created: {backup_full_path}")
        print(f"✓ Salt (save this): {salt_hex}")
        print(f"\nIMPORTANT: Store the encryption password and salt securely!")
        
        return encrypted_path
    
    def retrieve_credential(self, 
                          encrypted_file: str,
                          encryption_password: str,
                          salt_hex: str) -> Dict:
        """Retrieve and decrypt stored credential"""
        
        encrypted_path = self.cred_path / "primary" / encrypted_file
        
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
        
        # Recreate encryption key
        salt = bytes.fromhex(salt_hex)
        key = self.generate_key_from_password(encryption_password, salt)
        fernet = Fernet(key)
        
        # Read and decrypt file
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Extract ZIP content
        temp_zip = self.cred_path / "temp_decrypted.zip"
        with open(temp_zip, 'wb') as f:
            f.write(decrypted_data)
        
        # Extract JSON from ZIP
        with zipfile.ZipFile(temp_zip, 'r') as zf:
            json_content = zf.read("legal_counsel_credential.json")
        
        # Clean up
        os.remove(temp_zip)
        
        # Parse and return credential data
        credential_data = json.loads(json_content.decode())
        
        # Log access for compliance
        self._log_credential_operation("RETRIEVE", credential_data['email'], encrypted_path)
        
        return credential_data
    
    def _log_credential_operation(self, operation: str, email: str, file_path: Path):
        """Log credential operations for constitutional compliance"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "credential": email,
            "file": str(file_path),
            "constitutional_compliance": True,
            "audit_trail": "blockchain-ready"
        }
        
        # Write to audit log
        audit_file = self.audit_path / "credential_access.log"
        with open(audit_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

def main():
    """CLI interface for legal credential management"""
    parser = argparse.ArgumentParser(
        description="OBINexus Legal Credential Manager"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Store command
    store_parser = subparsers.add_parser('store', help='Store legal credential')
    store_parser.add_argument('--google-password', required=True, 
                            help='Google Workspace password')
    store_parser.add_argument('--encryption-password', required=True,
                            help='Password to encrypt the credential file')
    
    # Retrieve command
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve stored credential')
    retrieve_parser.add_argument('--file', required=True,
                               help='Encrypted credential filename')
    retrieve_parser.add_argument('--encryption-password', required=True,
                               help='Password to decrypt the file')
    retrieve_parser.add_argument('--salt', required=True,
                               help='Salt hex string from storage')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = LegalCredentialManager()
    
    if args.command == 'store':
        manager.store_legal_counsel_credential(
            args.google_password,
            args.encryption_password
        )
    
    elif args.command == 'retrieve':
        try:
            credential = manager.retrieve_credential(
                args.file,
                args.encryption_password,
                args.salt
            )
            print("\nRetrieved Credential:")
            print(f"Email: {credential['email']}")
            print(f"Service: {credential['service']}")
            print(f"Created: {credential['created_at']}")
            print(f"Next Rotation: {credential['next_rotation']}")
            # Don't print the actual password unless specifically requested
            
        except Exception as e:
            print(f"Error retrieving credential: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
