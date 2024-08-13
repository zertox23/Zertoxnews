import subprocess
import platform
import os
import click
import sys


def ensure_root_privileges():
    if os.geteuid() != 0:
        print("This script requires root privileges. Re-running with sudo...")
        try:
            # Re-run the script with root privileges
            subprocess.check_call(["sudo", sys.executable] + sys.argv)
        except subprocess.CalledProcessError as e:
            print(f"Failed to acquire root privileges: {e}")
        sys.exit(1)  # Exit the script as it is now running with sudo


# Ensure the script is running with root privileges
ensure_root_privileges()


def get_distribution():

    try:
        with open("/etc/os-release") as f:
            release_info = f.read().lower()
        if "ubuntu" in release_info:
            return "ubuntu"
        elif "debian" in release_info:
            return "debian"
        elif (
            "centos" in release_info
            or "red hat" in release_info
            or "fedora" in release_info
        ):
            return "redhat"
        else:
            return None
    except FileNotFoundError:
        return None


def install_docker(distro):
    try:
        if distro in ["ubuntu", "debian"]:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "-y",
                    "apt-transport-https",
                    "ca-certificates",
                    "curl",
                    "software-properties-common",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "curl",
                    "-fsSL",
                    "https://download.docker.com/linux/ubuntu/gpg",
                    "|",
                    "sudo",
                    "apt-key",
                    "add",
                    "-",
                ],
                check=True,
                shell=True,
            )
            subprocess.run(
                [
                    "sudo",
                    "add-apt-repository",
                    "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable",
                ],
                check=True,
            )
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "docker-ce"], check=True
            )
        elif distro == "redhat":
            subprocess.run(
                [
                    "sudo",
                    "yum",
                    "install",
                    "-y",
                    "yum-utils",
                    "device-mapper-persistent-data",
                    "lvm2",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "sudo",
                    "yum-config-manager",
                    "--add-repo",
                    "https://download.docker.com/linux/centos/docker-ce.repo",
                ],
                check=True,
            )
            subprocess.run(["sudo", "yum", "install", "-y", "docker-ce"], check=True)
        print("Docker installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Docker: {e}")


def install_docker_compose():
    try:
        subprocess.run(
            [
                "sudo",
                "curl",
                "-L",
                "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)",
                "-o",
                "/usr/local/bin/docker-compose",
            ],
            check=True,
        )
        subprocess.run(
            ["sudo", "chmod", "+x", "/usr/local/bin/docker-compose"], check=True
        )
        subprocess.run(["sudo", "systemctl", "start", "docker"])
        subprocess.run(["sudo", "systemctl", "enable", "docker"])

        print("Docker Compose installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Docker Compose: {e}")


def install_tor_privoxy(distro):
    try:
        if distro in ["ubuntu", "debian"]:
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "tor", "privoxy"], check=True
            )
        elif distro == "redhat":
            subprocess.run(["sudo", "yum", "install", "-y", "epel-release"], check=True)
            subprocess.run(
                ["sudo", "yum", "install", "-y", "tor", "privoxy"], check=True
            )
        print("Tor and Privoxy installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Tor and Privoxy: {e}")


def configure_tor_hidden_service():
    try:
        torrc_path = "/etc/tor/torrc"
        hidden_service_dir = "/var/lib/tor/hidden_service/"
        hidden_service_port = "80"

        with open(torrc_path, "a") as torrc:
            torrc.write("\n")
            torrc.write(f"HiddenServiceDir {hidden_service_dir}\n")
            torrc.write(
                f"HiddenServicePort {hidden_service_port} 127.0.0.1:{hidden_service_port}\n"
            )

        subprocess.run(["sudo", "systemctl", "restart", "tor"], check=True)
        print("Tor hidden service configured successfully")

        with open(os.path.join(hidden_service_dir, "hostname"), "r") as f:
            onion_address = f.read().strip()
        print(f"Your Tor hidden service address is: {onion_address}")
    except Exception as e:
        print(f"Error configuring Tor hidden service: {e}")


def configure_privoxy():
    try:
        privoxy_config_path = "/etc/privoxy/config"
        with open(privoxy_config_path, "a") as privoxy_config:
            privoxy_config.write("\n")
            privoxy_config.write("forward-socks5t / 127.0.0.1:9050 .\n")

        subprocess.run(["sudo", "systemctl", "restart", "privoxy"], check=True)
        print("Privoxy configured to use Tor successfully")
    except Exception as e:
        print(f"Error configuring Privoxy: {e}")


def run_docker_compose(api, discord_bot, web=False):
    docker_compose_content = """version: '3.9'

services:

  db:
    image: mysql:latest
    volumes:
      - mysql-data:/var/lib/mysql
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=123456789010
      - MYSQL_USER=botuser
      - MYSQL_DATABASE=botdb
      - MYSQL_PASSWORD=123456789010
    """

    if api:
        docker_compose_content += f"""
  api:
    build: "./api"
    environment:
      - my_ip={api['ip']}
      - proxy=http://127.0.0.1:8118
    ports:
      - 2222:2222
    """

    docker_compose_content += f"""
  discord_bot:
    build: "./discord_bot"
    environment:
      - proxy=http://127.0.0.1:8118
      - api_url=http://api:2222
      - TOKEN={discord_bot["token"]}
      - MYSQL_URL=mysql+pymysql://botuser:123456789010@db:3306/botdb
      - time_between_checks=15
      - my_ip={api["ip"]}
    depends_on:
      - api
      - db
    """

    if web:
        docker_compose_content += f"""
  web:
    build: "./Ahlullhaqweb/ahlullhaq"
    ports:
      - {web['port']}:8000
    environment:
      - SECRET_KEY="-Hc`.K$DL[i]jxM"[=)ZI+Se8A)EjS"
      - DEBUG="{web['debug']}"
      - DB=db
    depends_on:
      - db
    """

    docker_compose_content += """
volumes:
  mysql-data:
    """

    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)

    try:
        subprocess.run(["sudo", "docker-compose", "up", "-d"], check=True)
        print("Docker Compose started successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running Docker Compose: {e}")


@click.command()
@click.option("--api-ip", prompt="API IP Address", help="The IP address for the API.")
@click.option(
    "--discord-bot-token",
    prompt="Discord Bot Token",
    help="The token for the Discord bot.",
)
@click.option(
    "--web", is_flag=True, help="Include this flag to configure the web service."
)
@click.option(
    "--web-port",
    prompt="Web Port",
    default=8080,
    show_default=True,
    help="The port for the web service.",
)
@click.option(
    "--web-debug",
    prompt="Web Debug Mode",
    default="False",
    show_default=True,
    help="Debug mode for the web service.",
)
def run(api_ip, discord_bot_token, web, web_port, web_debug):
    api_config = {"ip": api_ip}
    discord_bot_config = {"token": discord_bot_token}

    if web:
        web_config = {"port": web_port, "debug": web_debug}
    else:
        web_config = False

    distro = get_distribution()
    install_docker(distro)
    install_docker_compose()
    install_tor_privoxy(distro)
    configure_tor_hidden_service()
    configure_privoxy()
    run_docker_compose(api=api_config, discord_bot=discord_bot_config, web=web_config)


if __name__ == "__main__":
    run()
