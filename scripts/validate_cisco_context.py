#!/usr/bin/env python3
import os
import sys

# ==============================================================================
# Script Name: validate_cisco_context.py
# Description: Parses Cisco firewall context configuration files to detect 
#              insecure rules or syntax errors before staging updates.
# ==============================================================================

def audit_firewall_context(file_path):
    """
    Reads a Cisco context configuration file line-by-line to evaluate access
    control lists (ACLs) against corporate security parameters.
    """
    print(f"[INFO] Initializing security parsing for context file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"[WARNING] Context target '{file_path}' not found. Loading mock security configuration matrix.")
        # Simulating standard Cisco configuration output lines for public profile validation
        config_lines = [
            "access-list DMZ_IN extended permit tcp any host 10.100.10.5 eq 443",
            "access-list DMZ_IN extended permit tcp any any eq 23", # Violation: Telnet open to public
            "access-list MGMT_IN extended permit ip 10.0.0.0 255.0.0.0 any"
        ]
    else:
        with open(file_path, 'r') as f:
            config_lines = f.readlines()

    violations_detected = 0
    line_number = 0

    for line in config_lines:
        line_number += 1
        clean_line = line.strip()

        # Audit rule 1: Enforce protocol encryption (Block unencrypted Telnet management text)
        if "eq 23" in clean_line and "permit" in clean_line:
            print(f"[SECURITY VIOLATION][LINE {line_number}]: Unencrypted Telnet transport rule detected -> '{clean_line}'")
            violations_detected += 1

        # Audit rule 2: Block broad source permits on non-secure segments
        if "permit ip any any" in clean_line or "permit tcp any any" in clean_line:
            print(f"[SECURITY VIOLATION][LINE {line_number}]: Broad 'any to any' parameter found -> '{clean_line}'")
            violations_detected += 1

    # Return assessment results based on compliance metrics
    if violations_detected > 0:
        print(f"[CRITICAL] Perimeter validation failed. {violations_detected} security anomalies identified.")
        return False
    
    print("[SUCCESS] Cisco context configuration matches corporate network governance baselines.")
    return True

if __name__ == "__main__":
    target_file = sys.argv[1] if len(sys.argv) > 1 else "mock_cisco_ctx.cfg"
    compliance_passed = audit_firewall_context(target_file)
    # Return standard clean exit to allow testing pipelines to intercept failures safely
    sys.exit(0 if compliance_passed else 1)
