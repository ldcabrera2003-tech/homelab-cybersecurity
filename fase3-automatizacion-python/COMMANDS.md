# Comandos utilizados — Fase 3: Automatización con Python

Referencia rápida de todos los comandos ejecutados durante esta fase. Los scripts completos (`port_scanner.py`, `log_parser.py`, `inventario_red.py`) están en esta misma carpeta.

## Herramienta 1: Port scanner propio

```bash
# Contra el servidor hardenizado (Fase 1)
python3 port_scanner.py 192.168.56.159 1 1000

# Contra Metasploitable2 (Fase 2), rango más amplio
python3 port_scanner.py 192.168.56.113 1 10000

# Ajustar cantidad de hilos concurrentes (default: 100)
python3 port_scanner.py 192.168.56.113 1 10000 --hilos 200
```

## Herramienta 2: Parser de logs SSH

```bash
# Generar intentos fallidos de prueba (desde Kali, contra Ubuntu Server)
ssh usuario_falso@192.168.56.159
ssh admin@192.168.56.159
ssh test123@192.168.56.159

# Copiar el script hacia Ubuntu Server (ejecutar desde donde está el archivo)
scp -i ~/.ssh/id_ed25519_ubuntuserver log_parser.py leandro@192.168.56.159:~/

# Ejecutar DENTRO de Ubuntu Server (requiere sudo por los permisos del log)
sudo python3 log_parser.py /var/log/auth.log

# Ajustar el umbral de intentos para marcar como sospechoso (default: 5)
sudo python3 log_parser.py /var/log/auth.log --umbral 3

# Validación cruzada con fail2ban
sudo fail2ban-client status sshd
```

## Herramienta 3: Inventario de red con SQLite

```bash
# Escanear la red y guardar/actualizar el historial
python3 inventario_red.py 192.168.56

# Instalar el cliente de terminal de SQLite (distinto al módulo de Python, que ya viene incluido)
sudo apt install sqlite3 -y

# Consultar la base de datos manualmente
sqlite3 inventario_red.db "SELECT * FROM inventario;"

# Consulta más legible con nombres de columna
sqlite3 -header -column inventario_red.db "SELECT * FROM inventario;"
```
