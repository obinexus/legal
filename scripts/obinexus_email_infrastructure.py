#!/usr/bin/env python3
"""
OBINexus Email Infrastructure Setup Script
Implements the canonical schema for Google Workspace
"""

import os
import sys
import json
from typing import Dict, List, Tuple

class OBINexusEmailSchema:
    """Implements the OBINexus organizational email schema"""
    
    DIVISIONS = ['computing', 'legal', 'publishing', 'uche', 'axis', 'aeroscale']
    DEPARTMENTS = ['public', 'private', 'protected']
    
    # Service mapping by division
    DIVISION_SERVICES = {
        'computing': ['syscall', 'polycall', 'obicall', 'iaas'],
        'legal': ['contracts', 'compliance', 'arbitration'],
        'publishing': ['books', 'journals', 'documentation'],
        'uche': ['fashion', 'knowledge', 'cultural'],
        'axis': ['research', 'development', 'integration'],
        'aeroscale': ['aerospace', 'safety', 'protocols']
    }
    
    def __init__(self):
        self.email_addresses = []
        self.routing_rules = []
        self.dns_records = []
    
    def generate_email_addresses(self) -> List[str]:
        """Generate all email addresses based on schema"""
        addresses = []
        
        # Division base emails
        for division in self.DIVISIONS:
            addresses.append(f"{division}@obinexus.org")
            
        # Service-based emails
        for division, services in self.DIVISION_SERVICES.items():
            for service in services:
                for department in self.DEPARTMENTS:
                    email = f"{service}.{department}.{division}@obinexus.org"
                    addresses.append(email)
        
        # Support infrastructure
        support_emails = [
            "support@obinexus.org",
            "lts@obinexus.org",
            "teams@obinexus.org",
            "constitutional@obinexus.org",
            "compliance@obinexus.org"
        ]
        addresses.extend(support_emails)
        
        self.email_addresses = addresses
        return addresses
    
    def generate_routing_rules(self) -> List[Dict]:
        """Generate email routing rules"""
        rules = [
            {
                "name": "Public Access Routing",
                "pattern": "*.public.*@obinexus.org",
                "route": "public-gateway@obinexus.org",
                "description": "Routes all public access emails through OCS gateway"
            },
            {
                "name": "Protected Access Routing",
                "pattern": "*.protected.*@obinexus.org",
                "route": "payment-gateway@obinexus.org",
                "description": "Routes protected services through payment gateway"
            },
            {
                "name": "Private Access Routing",
                "pattern": "*.private.*@obinexus.org",
                "route": "internal-gateway@obinexus.org",
                "description": "Routes private emails to internal systems only"
            }
        ]
        
        self.routing_rules = rules
        return rules
    
    def generate_gam_commands(self) -> List[str]:
        """Generate Google Admin commands for setup"""
        commands = []
        
        # Create organizational units
        for division in self.DIVISIONS:
            commands.append(f'gam create org "/OBINexus/Divisions/{division.title()}"')
        
        # Create email accounts
        for email in self.email_addresses[:20]:  # Limit for example
            if '.' in email.split('@')[0]:  # Service emails
                parts = email.split('@')[0].split('.')
                if len(parts) == 3:  # service.department.division format
                    division = parts[2]
                    ou = f"/OBINexus/Divisions/{division.title()}"
                    commands.append(f'gam create user {email} orgunit "{ou}"')
        
        # Create groups
        groups = [
            ("obinexus-computing@googlegroups.com", "Computing Division"),
            ("obinexus-legal@googlegroups.com", "Legal Division"),
            ("obinexus-axis-rnd@googlegroups.com", "Axis R&D")
        ]
        
        for group_email, desc in groups:
            commands.append(f'gam create group {group_email} name "{desc}"')
        
        return commands
    
    def generate_dns_config(self) -> Dict:
        """Generate DNS configuration"""
        config = {
            "mx_records": [
                {"priority": 1, "value": "aspmx.l.google.com."},
                {"priority": 5, "value": "alt1.aspmx.l.google.com."},
                {"priority": 5, "value": "alt2.aspmx.l.google.com."},
                {"priority": 10, "value": "alt3.aspmx.l.google.com."},
                {"priority": 10, "value": "alt4.aspmx.l.google.com."}
            ],
            "txt_records": [
                {"name": "@", "value": "v=spf1 include:_spf.google.com ~all"},
                {"name": "_dmarc", "value": "v=DMARC1; p=quarantine; rua=mailto:dmarc@obinexus.org"}
            ],
            "cname_records": []
        }
        
        # Add CNAME records for services
        for division, services in self.DIVISION_SERVICES.items():
            for service in services:
                for department in self.DEPARTMENTS:
                    subdomain = f"{service}.{department}"
                    config["cname_records"].append({
                        "name": subdomain,
                        "value": "ghs.googlehosted.com."
                    })
        
        self.dns_records = config
        return config
    
    def export_configuration(self, output_dir: str = "./schema"):
        """Export all configurations to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export email list
        with open(f"{output_dir}/email_addresses.txt", 'w') as f:
            for email in sorted(self.email_addresses):
                f.write(f"{email}\n")
        
        # Export GAM commands
        with open(f"{output_dir}/gam_setup_commands.sh", 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# OBINexus Email Setup Commands\n\n")
            for cmd in self.generate_gam_commands():
                f.write(f"{cmd}\n")
        
        # Export DNS configuration
        with open(f"{output_dir}/dns_configuration.json", 'w') as f:
            json.dump(self.dns_records, f, indent=2)
        
        # Export routing rules
        with open(f"{output_dir}/routing_rules.json", 'w') as f:
            json.dump(self.routing_rules, f, indent=2)
        
        print(f"Configuration exported to {output_dir}/")
        print(f"Total email addresses: {len(self.email_addresses)}")
        print(f"Total GAM commands: {len(self.generate_gam_commands())}")

def main():
    """Main execution function"""
    schema = OBINexusEmailSchema()
    
    # Generate all configurations
    schema.generate_email_addresses()
    schema.generate_routing_rules()
    schema.generate_dns_config()
    
    # Export to files
    schema.export_configuration()
    
    # Display summary
    print("\nOBINexus Email Schema Implementation")
    print("="*50)
    print(f"Divisions: {', '.join(schema.DIVISIONS)}")
    print(f"Departments: {', '.join(schema.DEPARTMENTS)}")
    print(f"\nSample emails generated:")
    for email in schema.email_addresses[:10]:
        print(f"  - {email}")
    print(f"\n... and {len(schema.email_addresses) - 10} more")

if __name__ == "__main__":
    main()
