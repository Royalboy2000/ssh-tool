# OnlyRAT
> Blue Cosmo | 01/07/2022
---

```
                                                                     _;,
                                                 ,,=-,--,,__     _,-;:;;},,,_
            _,oo,         Ll                 _,##&&&&$$&&$$$&-=;%%^%&;v:&& @ `=,_
          ,oO" `0}        Ll              ,%#####&#>&&$$$$&$$$&,&'$$#`"%%;,,,*%^<}
      _,--O;_,  0_        Ll            ,%%%%%&%-#&###$$"$$$$$*;&&$,#;%^*%$$^{,%;'
   ,cC'oO`'CC  ,OnnNNNNn, Ll  YY,      ,%#&%%$$$$%%%%%##&&^$%^%&&&$$'&#,-%%--"'
  ,CCCO"   `C ,0`Nn`  `Nn Ll   YY,    ,;;##&,$$$$$$$;,%%%&&%%%&&&&&&$$%%'
  {CC{       ,0' NN    NN Ll    Yy  yY';#&,#,$$$$$%%%%%%%%&%%%&&&&&&%%`
  CCC(     _o0   NN    NN Ll     YyyY ,;&##&###%%$$%&&%%%%#^%^&&&&&%{`
 ,OCC{    ,0C    NN    NN Ll      YY   ;#&&#####&%;%&&,%%%%#%=%%%&^%%
,O`'"Cc_.o0cC    NN    NN Ll y,   YY   ;&&&^##&&&$%&&&%%%"`     `%%%%
o0    _o0"` '`   NN    NN Ll  Yy,yYY  '^%%&VGh%%%%%&&"^%_,,       "%%%,_      _,.,_
0o,_,oo0"        NN    NN Ll   `YyY`    ``'"lIG9ubHkg,,""''`        ""%%>_,;VyIG5lZ;,
"00O"`                                          ``'``""UkFUIHlvdSdsbCBldm;"       `"WQ=,
```

OnlyRAT (Only Remote Access Tool) is a powerful, network-oriented SSH-based RAT designed for security researchers and educational purposes. It enables full remote control over a Windows 10 Home target via SSH, featuring file uploads, downloads, and remote command execution with minimal footprint.

---

## ⚠️ Disclaimer
**For educational and ethical use only.**
Only use OnlyRAT on systems you own or have explicit permission to test. Unauthorized access to computer systems is illegal. By using this tool, you take full responsibility for your actions. This tool enables persistence that could be exploited by others if not secured properly.

---

## 🚀 Features
- **Advanced Builder:** Automate configuration and compile EXE stagers with one command.
- **interact.sh Support:** Exfiltrate session data to interact.sh for easier management.
- **EXE Stagers:** Built-in support for compiling C-based stagers for Windows.
- **Fileless Execution:** Operates primarily through network commands and SSH.
- **Remote Console:** Full access to the target's terminal.
- **File Transfer:** Easy upload and download capabilities via SCP.
- **Persistence:** Configurable to survive reboots.
- **Local & Remote Support:** Works within local networks or across the internet via VPS.
- **Stealth:** Hides the `onlyrat` user from the Windows login screen and start menu.
- **Hak5 Integration:** Support for USB Rubber Ducky and Bash Bunny.

---

## 📋 Requirements
### Attacker PC
- **OS:** Debian-based Linux (Kali Linux, Parrot OS, etc.)
- **Tools:** `python3`, `sshpass`, `openssh-client`, `ssh-keygen`, `ssh-copy-id`

### Target PC
- **OS:** Windows 10 Home

---

## ⚙️ Installation

### 1. Attacker Setup
Clone the repository and run the installation script. **Note:** The installation directory will be moved to `~/.MK01-OnlyRAT` and the source folder will be deleted.
```bash
git clone https://github.com/CosmodiumCS/MK01-OnlyRAT.git
cd MK01-OnlyRAT
bash install.sh
```
Restart your terminal after installation. You can now run the tool using the `onlyrat` command.

### 2. Advanced Builder & EXE Generation
To simplify setup, you can use the built-in builder. This will prompt you for your connection details (VPS/Local), exfiltration URLs (Discord/Interact.sh), and automatically patch the necessary files and compile a `.exe` stager.

```bash
onlyrat --build
```
This requires `mingw-w64` and `python3-paramiko` to be installed on your Kali system:
```bash
sudo apt install mingw-w64 python3-paramiko
```

The builder now supports automated VPS deployment using a built-in Python web server. This avoids conflicts with existing Nginx/Apache installations and allows you to specify a custom web directory and port.

---

## 🌐 How It Works

OnlyRAT supports two main connection modes: **Local** and **VPS (Remote)**.

### A. Local Connection (Same Network)
This mode is best for testing within a local network.

**Workflow:**
1.  **Preparation:** The attacker configures `installers/from-github.cmd` with a Discord Webhook URL.
2.  **Execution:** The target runs the `.cmd` file, which downloads and executes a PowerShell payload (`g2.ps1`).
3.  **Setup:** The payload creates a hidden local administrator user `onlyrat`, enables the OpenSSH server, and configures it to start automatically.
4.  **Exfiltration:** A `.rat` configuration file (containing the target's local IP, password, and working directory) is generated and sent to the attacker's Discord Webhook.
5.  **Connection:** The attacker runs `onlyrat <file>.rat`. The tool uses `sshpass` to connect directly to the target's local IP via SSH (Port 22).

### B. VPS Connection (Over the Internet)
This mode allows control from anywhere by using a VPS to bypass NAT and firewalls.

**Workflow:**
1.  **Preparation:** The attacker runs `onlyrat --setup` to configure their VPS (enabling `GatewayPorts` and `AllowTcpForwarding` in SSH) and generates SSH keys.
2.  **Configuration:** The attacker updates the VPS installers and payloads with their VPS IP and username.
3.  **Execution:** The target runs `from-vps.cmd`, which triggers `v2.ps1`.
4.  **Reverse Tunnel:** The target downloads the attacker's public key from the VPS and establishes a **Reverse SSH Tunnel** back to the VPS. This maps a port on the VPS (e.g., 2583) to the target's local SSH port (22).
5.  **Persistence:** A startup script is created on the target to ensure the reverse tunnel is re-established upon reboot.
6.  **Exfiltration:** The `.rat` config file is uploaded to the VPS via SCP.
7.  **Connection:** The attacker downloads the config (`onlyrat -d`) and connects. Traffic is routed through the VPS IP on the forwarded port, which tunnels directly to the target's SSH service.

---

## 🔐 Security Note
By design, the VPS method involves placing an SSH private key on a web-accessible server so the target can download it for SCP exfiltration. **This is a significant security risk.** Ensure that your VPS is well-secured, and consider using restricted SSH users or temporary keys to mitigate the risk of your VPS being compromised.

---

## 🎮 Usage
Once you have a session active, you can use the following commands:

### Command & Control
- `orconsole`: Open a remote shell.
- `upload`: Upload a file to the target.
- `download`: Download a file from the target.
- `set connection local/remote`: Toggle connection modes.
- `restart`/`shutdown`: Control target power state.
- `killswitch`: Completely remove OnlyRAT from the target.

### Management
- `help`: Show the help menu.
- `config`: View the current target's configuration.
- `update`: Update OnlyRAT to the latest version.
- `uninstall`: Remove OnlyRAT from your attacker machine.

---

## 🛠️ Payload Options
The `installers/` directory contains various deployment methods:
- **`from-github.cmd`**: Standard local installer.
- **`from-vps.cmd`**: Standard remote installer.
- **`onlyduck-*.txt`**: DuckyScript for USB Rubber Ducky.
- **`OnlyBUGS-*`**: Payloads for Bash Bunny.

---

## 📚 Resources
- [YouTube Channel](https://youtube.com/cosmodiumcs)
- [Official Website](https://cosmodiumcs.com)
- [Detailed Technical Article](https://www.cosmodiumcs.com/research/onlyrat-ssh.md)

---
*Created by the CosmodiumCS Team.*
