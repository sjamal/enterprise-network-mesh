#!/usr/bin/env python3
# ==============================================================================
# Script Name: verify_vpn_tunnel.py
# Description: Verifies cross-premises line-of-sight connectivity over 
#              Site-to-Site (S2S) IPsec VPN tunnels, measuring performance metrics.
# ==============================================================================

import os
import sys
import subprocess
import re

def evaluate_vpn_transit(target_ip, count=4):
    """
    Executes standard network diagnostics against an internal cross-premises
    IP endpoint to evaluate transit availability and tunnel packet health.
    """
    print(f"[INFO] Initializing transit-layer verification for S2S VPN target: {target_ip}")
    
    # Formulate ping command arguments based on underlying runtime platforms
    command = ["ping", "-c", str(count), "-W", "2", target_ip]
    
    try:
        # Trigger non-interactive sub-process loop to capture response streams
        execution = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        response_output = execution.stdout
        
        # Parse output signatures to isolate operational loss metrics
        loss_match = re.search(r"(\d+)% packet loss", response_output)
        packet_loss = int(loss_match.group(1)) if loss_match else 100
        
        print(f"[INFO] S2S Tunnel Packet Loss Metric: {packet_loss}%")
        
        if packet_loss > 0:
            print(f"[WARNING] Degradation or packet drops identified on secure channel link: {packet_loss}% loss.")
            if packet_loss == 100:
                print("[CRITICAL] Total routing blackout discovered across cross-premises transit boundaries.")
                return False
                
        print("[SUCCESS] Cross-premises Site-to-Site VPN path verified healthy.")
        return True
        
    except subprocess.CalledProcessError as err:
        print(f"[CRITICAL] Boundary link down. Execution path failed to reach targeted remote subnet: {err.stderr.strip()}")
        return False

if __name__ == "__main__":
    # Internal target IP example (e.g., Azure Private Endpoint or On-Prem Gateway Interface)
    vpn_target_gateway = os.getenv("VPN_TARGET_GATEWAY_IP", "10.200.10.1")
    is_tunnel_active = evaluate_vpn_transit(vpn_target_gateway)
    sys.exit(0 if is_tunnel_active else 1)
