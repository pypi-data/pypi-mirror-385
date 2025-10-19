import os
import subprocess
import sys
import re
import termios
import tty
import select
import time
import requests
import signal
import socket
import importlib.metadata

# cli.py
# 𝗠𝗮𝗻𝗮𝗴𝗲𝗱 𝗕𝘆 @Nactire

def print_green(text):
    print("\033[1;32m" + text + "\033[0m")

def print_red(text):
    print("\033[1;31m" + text + "\033[0m")
    
def print_yellow(text):
    print("\033[1;33m" + text + "\033[0m")
    
def print_turquoise(text):
    print("\033[38;2;0;255;234m" + text + "\033[0m")
    
def get_version():
    try:
        version = importlib.metadata.version('nitroexpose')
        return version
    except importlib.metadata.PackageNotFoundError:
        return "Unknown"

def run_command(cmd):
    process = subprocess.Popen(
        cmd, 
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    process.wait()
    return process.returncode

def is_installed(cmd):
    return subprocess.call(
        f"{cmd} > /dev/null 2>&1", 
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0
    
def is_certbot_nginx_plugin_installed():
    try:
        result = subprocess.check_output(
            "dpkg -l | grep python3-certbot-nginx", 
            shell=True, 
            text=True,
            stderr=subprocess.DEVNULL
        )
        return "python3-certbot-nginx" in result
    except subprocess.CalledProcessError:
        return False

def is_port_listening(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', int(port)))
        sock.close()
        return result == 0
    except Exception:
        return False

def restricted_input(prompt, allowed_pattern):
    def handle_sigint(signum, frame):
        print("\n\n")
        sys.exit(1)

    signal.signal(signal.SIGINT, handle_sigint)

    sys.stdout.write("\033[1;32m" + prompt + "\033[0m")
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)

    buffer = ""
    try:
        while True:
            r, _, _ = select.select([fd], [], [], 0)
            if r:
                ch = sys.stdin.read(1)
                if ch == "\n" or ch == "\r":
                    print()
                    break
                elif ch == "\x03":
                    raise KeyboardInterrupt
                elif ch == "\x7f":
                    if buffer:
                        buffer = buffer[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif re.match(allowed_pattern, ch):
                    buffer += ch
                    sys.stdout.write(ch)
                    sys.stdout.flush()
    except KeyboardInterrupt:
        print("\n\n")
        sys.exit(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return buffer

def install_and_verify_package(package_name, check_cmd, install_cmds):
    print_green(f"Installing {package_name} ...")
    
    for cmd in install_cmds:
        run_command(cmd)
    
    if check_cmd():
        print_green(f"{package_name} installed.")
        return True
    else:
        print_red(f"{package_name} installing Error.")
        sys.exit(1)

def is_valid_domain(domain):
    if "http://" in domain or "https://" in domain or " " in domain:
        return False

    if "." not in domain:
        return False

    pattern = r'^[a-zA-Z0-9\.\-]+$'
    if not re.match(pattern, domain):
        return False
    
    return True

def is_subdomain(domain):
    parts = domain.split(".")
    return len(parts) > 2

def remove_domain(domain):
    if os.geteuid() != 0:
        print_red("\nPlease Use Root Environment.\n")
        sys.exit(1)
    
    if not is_valid_domain(domain):
        print_red("\nDomain Format Not Valid.\n")
        sys.exit(1)
    
    if not is_installed("nginx -v"):
        install_and_verify_package(
            "NGINX",
            lambda: is_installed("nginx -v"),
            [
                "sudo apt update -o Acquire::AllowInsecureRepositories=true",
                "sudo apt install -y nginx",
                "sudo systemctl start nginx",
                "sudo systemctl enable nginx"
            ]
        )
    else:
        print_green("NGINX installed.")

    if not is_installed("certbot --version"):
        install_and_verify_package(
            "Certbot",
            lambda: is_installed("certbot --version"),
            [
                "sudo apt update -o Acquire::AllowInsecureRepositories=true",
                "sudo apt install -y certbot python3-certbot-nginx"
            ]
        )
    else:
        print_green("Certbot installed.")
        
    if not is_certbot_nginx_plugin_installed():
        install_and_verify_package(
            "python3-certbot-nginx plugin",
            is_certbot_nginx_plugin_installed,
            [
                "sudo apt update -o Acquire::AllowInsecureRepositories=true",
                "sudo apt install -y python3-certbot-nginx"
            ]
        )
    else:
        print_green("python3-certbot-nginx plugin installed.")
    
    print("\n")
    
    available_path = f"/etc/nginx/sites-available/{domain}"
    enabled_path = f"/etc/nginx/sites-enabled/{domain}"
    
    available_exists = os.path.exists(available_path)
    enabled_exists = os.path.exists(enabled_path)
    
    domain_type = "Subdomain" if is_subdomain(domain) else "Domain"
    
    if not available_exists and not enabled_exists:
        run_command(f"sudo rm -f {available_path}")
        run_command(f"sudo rm -f {enabled_path}")
        run_command("sudo systemctl reload nginx")
        print_red(f"Targeted {domain_type} Doesn't Exist in Your Server.\n")
        sys.exit(1)
    elif not available_exists or not enabled_exists:
        run_command(f"sudo rm -f {available_path}")
        run_command(f"sudo rm -f {enabled_path}")
        run_command("sudo systemctl reload nginx")
        print_red(f"Targeted {domain_type} Doesn't Exist in Your Server.\n")
        sys.exit(1)
    else:
        run_command(f"sudo rm -f {available_path}")
        run_command(f"sudo rm -f {enabled_path}")
        run_command("sudo systemctl reload nginx")
        print_green(f"\n{domain_type} Removed Successfully.\n")
        sys.exit(0)

def main():
    if len(sys.argv) == 2 and sys.argv[1] in ["-v", "--v"]:
        version = get_version()
        print_green(f"V{version}")
        sys.exit(0)

    if len(sys.argv) == 3 and sys.argv[1] == "remove":
        domain = sys.argv[2]
        remove_domain(domain)
        return
    
    if os.geteuid() != 0:
        print_red("\nPlease Use Root Environment.\n")
        sys.exit(1)

    if not is_installed("nginx -v"):
        install_and_verify_package(
            "NGINX",
            lambda: is_installed("nginx -v"),
            [
                "sudo apt update -o Acquire::AllowInsecureRepositories=true",
                "sudo apt install -y nginx",
                "sudo systemctl start nginx",
                "sudo systemctl enable nginx"
            ]
        )
    else:
        print_green("NGINX installed.")

    if not is_installed("certbot --version"):
        install_and_verify_package(
            "Certbot",
            lambda: is_installed("certbot --version"),
            [
                "sudo apt update -o Acquire::AllowInsecureRepositories=true",
                "sudo apt install -y certbot python3-certbot-nginx"
            ]
        )
    else:
        print_green("Certbot installed.")

    if not is_certbot_nginx_plugin_installed():
        install_and_verify_package(
            "python3-certbot-nginx plugin",
            is_certbot_nginx_plugin_installed,
            [
                "sudo apt update -o Acquire::AllowInsecureRepositories=true",
                "sudo apt install -y python3-certbot-nginx"
            ]
        )
    else:
        print_green("python3-certbot-nginx plugin installed.")
        
    print("\n")

    print_turquoise("┌─╼ Enter Domain Or Subdomain")
    domain = restricted_input("\033[38;2;0;255;234m└────╼ ❯❯❯ \033[0m", r"[a-zA-Z0-9\.\-]")
    
    print("\n")
    
    if "." not in domain:
        print_red("Domain is invalid, Operation Failed.")
        sys.exit(1)

    print_turquoise("┌─╼ Enter Port To Expose")
    port = restricted_input("\033[38;2;0;255;234m└────╼ ❯❯❯ \033[0m", r"[0-9]+")
    
    print("\n")

    if not is_port_listening(port):
        print_red("Port Not Listening, Operation Failed.")
        sys.exit(1)

    nginx_temp_conf = f"""
server {{
    server_name {domain};

    location /nitroverify/auth.txt {{
        default_type text/plain;
        return 200 "nitroverify-success";
    }}

    location / {{
        return 404;
    }}

    listen 80;
}}
"""
    conf_path = f"/etc/nginx/sites-available/{domain}"
    with open(conf_path, "w") as f:
        f.write(nginx_temp_conf)

    run_command(f"sudo ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/")
    run_command("sudo systemctl reload nginx")

    print_yellow("Domain verifying...")
    time.sleep(5)

    verified = False
    for url in [f"http://{domain}/nitroverify/auth.txt", f"https://{domain}/nitroverify/auth.txt"]:
        try:
            r = requests.get(url, timeout=5)
            if "nitroverify-success" in r.text:
                verified = True
                break
        except Exception:
            continue

    if not verified:
        print_red("Domain Verification Failed, Check Records Carefully.")
        run_command(f"sudo rm -f /etc/nginx/sites-available/{domain}")
        run_command(f"sudo rm -f /etc/nginx/sites-enabled/{domain}")
        run_command("sudo systemctl reload nginx")
        sys.exit(1)

    print_green("Domain Verification Success.\n")

    run_command(f"sudo rm -f /etc/nginx/sites-available/{domain}")
    run_command(f"sudo rm -f /etc/nginx/sites-enabled/{domain}")
    run_command("sudo systemctl reload nginx")
    
    print_yellow("SSL Cert installing...")

    nginx_conf = f"""
server {{
    server_name {domain};

    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    listen 80;
}}
"""
    conf_path = f"/etc/nginx/sites-available/{domain}"
    with open(conf_path, "w") as f:
        f.write(nginx_conf)

    run_command(f"sudo ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/")
    run_command("sudo systemctl reload nginx")

    run_command(f"sudo certbot --nginx -d {domain} --non-interactive --agree-tos --email nitroexpose@gmail.com")
    run_command("sudo systemctl reload nginx")

    print_yellow("SSL Certificate Checking...")
    time.sleep(2)

    ssl_installed = False
    try:
        r = requests.get(f"https://{domain}", timeout=10)
        if r.status_code == 200:
            ssl_installed = True
    except requests.exceptions.SSLError:
        ssl_installed = False
    except requests.exceptions.RequestException:
        ssl_installed = False

    print("\n")
    if ssl_installed:
        print_green(f"Exposed Successfully On Your Domain\n")
        print_green(f"Exposed On: https://{domain}\n")
        print_green(f"Port: {port}\n")
        print_green(f"SSL Installed Using Let's Encrypt.\n")
        print_yellow(f"- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        print_yellow(f"If You Like NitroExpose, Please Support Us by:\n")
        print_yellow(f" * Join Our Telegram Channel:   https://t.me/NacDevs")
        print_yellow(f" * Please Star Our Project:     https://github.com/yuvrajmodz/NitroExpose")
        print_yellow(f"- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n\n")
    else:
        print_green(f"Exposed Successfully On Your Domain\n")
        print_green(f"Exposed On: http://{domain}\n")
        print_green(f"Port: {port}\n")
        print_yellow(f"Unfortunately, please verify your records carefully. Your server is exposed on your domain, and we are experiencing difficulties while attempting to install an SSL certificate.\n\n")

if __name__ == "__main__":
    main()