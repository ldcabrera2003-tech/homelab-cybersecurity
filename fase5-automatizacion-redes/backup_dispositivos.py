#!/usr/bin/env python3
"""
Backup automático de configuración - Fase 5 del Homelab
Se conecta a una LISTA de dispositivos (aquí solo 1, el sandbox de Cisco,
pero el mismo código funciona igual con 10 o 100 dispositivos) y guarda
la configuración de cada uno en un archivo con fecha y hora.
"""

from netmiko import ConnectHandler
import getpass
import os
from datetime import datetime

# Lista de dispositivos a respaldar. Para agregar más routers/switches en el
# futuro (ej: cuando montes la topología en CML), solo agregas otro
# diccionario aquí - el resto del script no necesita cambiar en nada.
DISPOSITIVOS = [
    {
        "nombre": "sandbox-cat8kv",
        "device_type": "cisco_xe",
        "host": "devnetsandboxiosxec8k.cisco.com",
        "username": "ld.cabrera2003",
        "port": 22,
    },
    # Ejemplo de cómo se vería un segundo dispositivo (comentado):
    # {
    #     "nombre": "router-sucursal-2",
    #     "device_type": "cisco_xe",
    #     "host": "192.168.100.1",
    #     "username": "admin",
    #     "port": 22,
    # },
]

def hacer_backup(info_dispositivo, password):
    """Se conecta a UN dispositivo y guarda su configuración a un archivo."""
    nombre = info_dispositivo["nombre"]
    conexion_datos = {k: v for k, v in info_dispositivo.items() if k != "nombre"}
    conexion_datos["password"] = password

    print(f"[{nombre}] Conectando...")
    try:
        conexion = ConnectHandler(**conexion_datos)
    except Exception as e:
        print(f"[{nombre}] ERROR al conectar: {e}")
        return False

    configuracion = conexion.send_command("show running-config")
    conexion.disconnect()

    # Creamos la carpeta de backups si no existe
    os.makedirs("backups", exist_ok=True)

    # Nombre de archivo único con fecha y hora, para no sobrescribir backups anteriores
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_archivo = f"backups/{nombre}_{marca_tiempo}.cfg"

    with open(ruta_archivo, "w") as archivo:
        archivo.write(configuracion)

    print(f"[{nombre}] Backup guardado en: {ruta_archivo}")
    return True

def main():
    password = getpass.getpass("Contraseña (misma para todos los dispositivos de la lista): ")

    exitosos = 0
    for dispositivo in DISPOSITIVOS:
        if hacer_backup(dispositivo, password):
            exitosos += 1

    print(f"\nResumen: {exitosos}/{len(DISPOSITIVOS)} dispositivos respaldados exitosamente.")

if __name__ == "__main__":
    main()
