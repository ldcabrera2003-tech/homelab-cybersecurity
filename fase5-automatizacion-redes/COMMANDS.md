# Comandos utilizados — Fase 5: Automatización de redes

Referencia rápida de todos los comandos ejecutados durante esta fase. Los scripts completos (`network_automation.py`, `backup_dispositivos.py`, `napalm_demo.py`) están en esta misma carpeta.

## Acceso al sandbox de Cisco DevNet

- Registro gratuito: https://developer.cisco.com/
- Catálogo de sandboxes: https://developer.cisco.com/site/sandbox/
- Sandbox usado: **Catalyst 8000 Always-On Sandbox** (IOS XE en Cat8kv)

```bash
# Prueba de conexión SSH manual (confirmar credenciales antes de automatizar)
ssh ld.cabrera2003@devnetsandboxiosxec8k.cisco.com
```

Comandos de reconocimiento corridos manualmente dentro del router, para documentación:
```
show version | include Cisco IOS
show ip interface brief
```

## Preparación del entorno Python (en Kali)

```bash
ping -c 3 8.8.8.8            # confirmar salida a internet antes de automatizar

pip install netmiko --break-system-packages
pip install napalm --break-system-packages
```

## Script 1: Primera automatización (lectura + escritura + verificación)

```bash
python3 network_automation.py
```
Pide la contraseña de forma oculta (no se escribe en el código, usa `getpass`).

## Script 2: Backup automático escalable

```bash
python3 backup_dispositivos.py

# Verificar los backups generados
ls backups/
cat backups/sandbox-cat8kv_*.cfg
```

## Script 3: NAPALM (datos estructurados multi-vendor)

```bash
python3 napalm_demo.py
```
