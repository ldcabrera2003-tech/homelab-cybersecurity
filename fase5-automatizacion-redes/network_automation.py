#!/usr/bin/env python3
"""
Automatización de red con Netmiko - Fase 5 del Homelab
Se conecta a un router Cisco IOS XE (Cisco DevNet Sandbox), extrae
información de sus interfaces, y aplica un cambio de configuración
de forma automatizada.
"""

from netmiko import ConnectHandler
import getpass

def main():
    # Pedimos la contraseña de forma oculta en vez de escribirla en el código.
    password = getpass.getpass("Contraseña del router: ")

    # Diccionario de conexión: así le dice Netmiko cómo hablar con el dispositivo.
    dispositivo = {
        "device_type": "cisco_xe",   # le dice a Netmiko qué "dialecto" de CLI usar
        "host": "devnetsandboxiosxec8k.cisco.com",
        "username": "ld.cabrera2003",
        "password": password,
        "port": 22,
    }

    print("Conectando al router...")
    try:
        conexion = ConnectHandler(**dispositivo)
    except Exception as e:
        print(f"No se pudo conectar: {e}")
        return

    print("Conexión establecida.\n")

    # --- PARTE 1: Lectura de información (equivalente a comandos 'show') ---
    print("=" * 60)
    print("ESTADO ACTUAL DE LAS INTERFACES")
    print("=" * 60)
    salida = conexion.send_command("show ip interface brief")
    print(salida)

    # --- PARTE 2: Escritura de configuración (modo de configuración) ---
    print("\n" + "=" * 60)
    print("APLICANDO CONFIGURACIÓN A Loopback99")
    print("=" * 60)

    comandos_config = [
        "interface Loopback99",
        "description Configurado automaticamente por Python - Leandro Cabrera",
    ]
    # send_config_set entra en modo 'configure terminal' automáticamente,
    # aplica cada línea de la lista en orden, y sale al terminar.
    resultado_config = conexion.send_config_set(comandos_config)
    print(resultado_config)

    # --- PARTE 3: Verificación del cambio aplicado ---
    print("\n" + "=" * 60)
    print("VERIFICACIÓN: configuración actual de Loopback99")
    print("=" * 60)
    verificacion = conexion.send_command("show run interface Loopback99")
    print(verificacion)

    conexion.disconnect()
    print("\nConexión cerrada correctamente.")

if __name__ == "__main__":
    main()
