# Comandos utilizados — Fase 1: Hardening de Ubuntu Server

Referencia rápida de todos los comandos ejecutados durante este proyecto, organizados por sección. Reemplaza `tu_usuario`, `IP_SERVIDOR` y rutas de llave según corresponda a tu entorno.

## Acceso SSH por llave pública

```bash
# En el cliente (Windows / Git Bash): generar par de llaves dedicado
ssh-keygen -t ed25519 -C "ubuntu-server-lab" -f ~/.ssh/id_ed25519_ubuntuserver

# Copiar la llave pública al servidor (requiere contraseña la última vez)
ssh-copy-id -i ~/.ssh/id_ed25519_ubuntuserver.pub tu_usuario@IP_SERVIDOR

# Probar conexión por llave
ssh -i ~/.ssh/id_ed25519_ubuntuserver tu_usuario@IP_SERVIDOR
```

Configuración de acceso simplificado en `~/.ssh/config` (cliente):
```
Host ubuntu-lab
    HostName IP_SERVIDOR
    User tu_usuario
    IdentityFile ~/.ssh/id_ed25519_ubuntuserver
```

En el servidor, deshabilitar contraseña y login root:
```bash
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
# PermitRootLogin no

sudo systemctl restart ssh
```

**Nota importante (ver problemas en el README):** si el cambio no surte efecto, revisar también:
```bash
sudo nano /etc/ssh/sshd_config.d/50-cloud-init.conf

# Verificar configuración EFECTIVA (combina todos los archivos):
sudo sshd -T | grep passwordauthentication
```

## Firewall local (UFW)

```bash
sudo apt install ufw -y

sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 22/tcp
sudo ufw allow 'Nginx HTTP'

sudo ufw enable
sudo ufw status verbose
sudo ufw app list
```

## fail2ban

```bash
sudo apt install fail2ban -y

sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
# [DEFAULT]
# bantime = 1h
# findtime = 10m
# maxretry = 5
#
# [sshd]
# enabled = true

sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban
sudo fail2ban-client status sshd
```

## Nginx

```bash
sudo apt install nginx -y
sudo systemctl status nginx
```
Verificación desde navegador: `http://IP_SERVIDOR`

## Script de auditoría

```bash
nano auditoria.sh
chmod +x auditoria.sh
./auditoria.sh
```

Comandos individuales que usa el script internamente:
```bash
sudo ss -tulnp                                          # puertos abiertos
getent group sudo | cut -d: -f4                         # usuarios con sudo
apt list --upgradable                                   # actualizaciones pendientes
systemctl list-units --type=service --state=running     # servicios activos
```

## Actualizaciones del sistema

```bash
sudo apt update && sudo apt upgrade -y

# Forzar paquetes retenidos por "phased updates" si hace falta
sudo apt upgrade --with-new-pkgs -o APT::Get::Always-Include-Phased-Updates=true

# Revisar historial de parches automáticos
cat /var/log/unattended-upgrades/unattended-upgrades.log | tail -30
```

## Reducción de superficie de ataque (servicios innecesarios en una VM de servidor)

```bash
sudo systemctl disable --now ModemManager fwupd multipathd packagekit upower
```

## Diagnóstico de red (usados durante el troubleshooting de la Fase 0/1)

```bash
ip a                                    # ver IP asignada
ping IP_DESTINO                         # conectividad básica
sudo nmap -sn 192.168.56.0/24           # descubrir hosts activos en la red
```
En Windows (PowerShell), para descartar bloqueo de puerto específico:
```powershell
Test-NetConnection -ComputerName IP_SERVIDOR -Port 22
```