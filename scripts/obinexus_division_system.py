#!/usr/bin/env python3
"""
OBINexus Division System Generator
Implements HITL-to-HOTL Dual Gated Systems for secure credential management
Based on Civil Collapse Distributed Governance principles
"""
from datetime import datetime, timezone

import os
import sys
import json
import csv
import argparse
import hashlib
import zipfile
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

@dataclass
class DivisionCredential:
    """Represents a credential within a division following Constitutional compliance"""
    service: str
    access_level: str
    division: str
    email: str
    password_hash: str
    created_at: str
    rotated_at: Optional[str] = None
    ocs_score: int = 750  # OpenX Credit Score threshold
    gate_status: str = "HITL"  # HITL or HOTL
    
@dataclass
class Division:
    """Represents an OBINexus Division with dual-gating protocols"""
    name: str
    status: str  # "division" or "sector"
    services: List[str]
    access_levels: List[str] = None
    credentials: List[DivisionCredential] = None
    gate_protocol: str = "HITL"  # Human-In-The-Loop initially
    trust_score: float = 0.0
    
    def __post_init__(self):
        if self.access_levels is None:
            self.access_levels = ["public", "protected", "private"]
        if self.credentials is None:
            self.credentials = []

class OBINexusDivisionSystem:
    """
    Implements the distributed governance model with peer-to-peer network architecture
    and dual-gated HITL-to-HOTL progression systems
    """
    
    def __init__(self, base_path: str = "obinexus_divisions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.divisions_path = self.base_path / "divisions"
        self.divisions_path.mkdir(exist_ok=True)
        self.credentials_path = self.base_path / "credentials"
        self.credentials_path.mkdir(exist_ok=True)
        
        # Constitutional compliance tracking
        self.audit_log = []
        self.constitutional_violations = []
        
    def generate_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key using PBKDF2 - Constitutional Compliance"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,  # Per Confio framework specification
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def create_division(self, name: str, services: List[str], 
                       initial_gate: str = "HITL") -> Division:
        """Create a new division with initial HITL gate protocol"""
        division = Division(
            name=name,
            status="division",
            services=services,
            gate_protocol=initial_gate
        )
        
        # Generate email addresses for all service/access combinations
        for service in services:
            for access_level in division.access_levels:
                email = f"{service}.{access_level}.{name}@obinexus.org"
                
                # Generate secure password
                password = secrets.token_urlsafe(32)
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                credential = DivisionCredential(
                    service=service,
                    access_level=access_level,
                    division=name,
                    email=email,
                    password_hash=password_hash,
                    created_at=datetime.now(timezone.utc).isoformat(),
                    gate_status=initial_gate
                )
                
                division.credentials.append(credential)
        
        self._save_division(division)
        self._log_constitutional_action(f"Created division: {name}")
        return division
    
    def transition_to_hotl(self, division_name: str, trust_threshold: float = 0.85):
        """
        Transition division from HITL to HOTL based on trust metrics
        Implements the systematic automation through trust building
        """
        division = self._load_division(division_name)
        if not division:
            raise ValueError(f"Division {division_name} not found")
        
        if division.trust_score >= trust_threshold:
            division.gate_protocol = "HOTL"
            for credential in division.credentials:
                credential.gate_status = "HOTL"
            
            self._save_division(division)
            self._log_constitutional_action(
                f"Transitioned {division_name} to HOTL with trust score {division.trust_score}"
            )
            return True
        return False
    
    def export_credentials_secure(self, division_name: str, 
                                password: str, output_format: str = "csv") -> Path:
        """
        Export credentials with dual-gating security protocol
        Password is used to encrypt the ZIP file containing CSV/TSV files
        """
        division = self._load_division(division_name)
        if not division:
            raise ValueError(f"Division {division_name} not found")
        
        # Create temporary files
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_filename = f"{division_name}_credentials_{timestamp}"
        
        # Generate CSV/TSV based on format
        if output_format == "csv":
            file_path = self._export_to_csv(division, base_filename)
        else:
            file_path = self._export_to_tsv(division, base_filename)
        
        # Create encrypted ZIP
        zip_path = self.credentials_path / f"{base_filename}.zip"
        salt = os.urandom(16)
        key = self.generate_key_from_password(password, salt)
        
        # Store salt in filename for decryption
        salt_hex = salt.hex()
        encrypted_zip_path = self.credentials_path / f"{base_filename}_{salt_hex}.enc.zip"
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(file_path, file_path.name)
        
        # Encrypt the ZIP file
        fernet = Fernet(key)
        with open(zip_path, 'rb') as f:
            encrypted_data = fernet.encrypt(f.read())
        
        with open(encrypted_zip_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Clean up temporary files
        os.remove(file_path)
        os.remove(zip_path)
        
        self._log_constitutional_action(
            f"Exported encrypted credentials for {division_name}"
        )
        
        return encrypted_zip_path
    
    def _export_to_csv(self, division: Division, base_filename: str) -> Path:
        """Export division credentials to CSV format"""
        csv_path = self.credentials_path / f"{base_filename}.csv"
        
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['service', 'access_level', 'division', 'email', 
                         'created_at', 'gate_status', 'ocs_score']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for credential in division.credentials:
                writer.writerow({
                    'service': credential.service,
                    'access_level': credential.access_level,
                    'division': credential.division,
                    'email': credential.email,
                    'created_at': credential.created_at,
                    'gate_status': credential.gate_status,
                    'ocs_score': credential.ocs_score
                })
        
        return csv_path
    
    def _export_to_tsv(self, division: Division, base_filename: str) -> Path:
        """Export division credentials to TSV format"""
        tsv_path = self.credentials_path / f"{base_filename}.tsv"
        
        with open(tsv_path, 'w', newline='') as f:
            fieldnames = ['service', 'access_level', 'division', 'email', 
                         'created_at', 'gate_status', 'ocs_score']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for credential in division.credentials:
                writer.writerow({
                    'service': credential.service,
                    'access_level': credential.access_level,
                    'division': credential.division,
                    'email': credential.email,
                    'created_at': credential.created_at,
                    'gate_status': credential.gate_status,
                    'ocs_score': credential.ocs_score
                })
        
        return tsv_path
    
    def _save_division(self, division: Division):
        """Save division data with constitutional compliance"""
        division_file = self.divisions_path / f"{division.name}.json"
        
        # Convert to dict for JSON serialization
        division_dict = asdict(division)
        
        with open(division_file, 'w') as f:
            json.dump(division_dict, f, indent=2)
    
    def _load_division(self, name: str) -> Optional[Division]:
        """Load division data from storage"""
        division_file = self.divisions_path / f"{name}.json"
        
        if not division_file.exists():
            return None
        
        with open(division_file, 'r') as f:
            data = json.load(f)
        
        # Reconstruct credentials
        credentials = []
        for cred_data in data.get('credentials', []):
            credentials.append(DivisionCredential(**cred_data))
        
        data['credentials'] = credentials
        return Division(**data)
    
    def _log_constitutional_action(self, action: str):
        """Log actions for constitutional compliance audit trail"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'constitutional_compliance': True
        }
        self.audit_log.append(log_entry)
        
        # Also write to audit file
        audit_file = self.base_path / "constitutional_audit.log"
        with open(audit_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def create_sector_from_divisions(self, sector_name: str, 
                                   division_names: List[str], 
                                   shared_policies: List[str]) -> Dict:
        """
        Create a sector when divisions share policies/operations
        Following the hybrid model from Civil Collapse framework
        """
        sector = {
            'name': sector_name,
            'status': 'sector',
            'composition': division_names,
            'shared_policies': shared_policies,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        sector_file = self.divisions_path / f"{sector_name}_sector.json"
        with open(sector_file, 'w') as f:
            json.dump(sector, f, indent=2)
        
        self._log_constitutional_action(
            f"Created sector {sector_name} from divisions: {', '.join(division_names)}"
        )
        
        return sector

def main():
    """CLI interface for OBINexus Division System"""
    parser = argparse.ArgumentParser(
        description="OBINexus Division System Generator - HITL-to-HOTL Implementation"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create division command
    create_parser = subparsers.add_parser('create', help='Create a new division')
    create_parser.add_argument('name', help='Division name (e.g., computing, legal)')
    create_parser.add_argument('services', nargs='+', help='Services provided by division')
    create_parser.add_argument('--gate', default='HITL', choices=['HITL', 'HOTL'],
                             help='Initial gate protocol (default: HITL)')
    
    # Export credentials command
    export_parser = subparsers.add_parser('export', help='Export division credentials')
    export_parser.add_argument('division', help='Division name')
    export_parser.add_argument('password', help='Password for encryption')
    export_parser.add_argument('--format', default='csv', choices=['csv', 'tsv'],
                             help='Export format (default: csv)')
    
    # Transition to HOTL command
    hotl_parser = subparsers.add_parser('transition', help='Transition division to HOTL')
    hotl_parser.add_argument('division', help='Division name')
    hotl_parser.add_argument('--trust', type=float, default=0.85,
                           help='Trust threshold (default: 0.85)')
    
    # Create sector command
    sector_parser = subparsers.add_parser('sector', help='Create sector from divisions')
    sector_parser.add_argument('name', help='Sector name')
    sector_parser.add_argument('--divisions', nargs='+', required=True,
                             help='Divisions to include')
    sector_parser.add_argument('--policies', nargs='+', required=True,
                             help='Shared policies')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize system
    system = OBINexusDivisionSystem()
    
    if args.command == 'create':
        division = system.create_division(args.name, args.services, args.gate)
        print(f"Created division: {division.name}")
        print(f"Services: {', '.join(division.services)}")
        print(f"Initial gate protocol: {division.gate_protocol}")
        print(f"Generated {len(division.credentials)} credentials")
        
    elif args.command == 'export':
        try:
            export_path = system.export_credentials_secure(
                args.division, args.password, args.format
            )
            print(f"Exported encrypted credentials to: {export_path}")
            print("Use the same password to decrypt the ZIP file")
            
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == 'transition':
        success = system.transition_to_hotl(args.division, args.trust)
        if success:
            print(f"Successfully transitioned {args.division} to HOTL")
        else:
            print(f"Trust score too low for {args.division} to transition to HOTL")
    
    elif args.command == 'sector':
        sector = system.create_sector_from_divisions(
            args.name, args.divisions, args.policies
        )
        print(f"Created sector: {sector['name']}")
        print(f"Composed of: {', '.join(sector['composition'])}")

if __name__ == "__main__":
    main()
