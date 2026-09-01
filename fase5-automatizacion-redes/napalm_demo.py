#!/usr/bin/env python3
"""
Automatización con NAPALM - Fase 5 del Homelab
A diferencia de Netmiko (que devuelve texto plano tal cual lo vería un
humano en la terminal), NAPALM devuelve diccionarios de Python ya
estructurados y listos para usar en código, sin necesidad de parsear
texto con expresiones regulares.
"""

from napalm import get_network_driver
import getpass
import json

def main():
    password = getpass.getpass("Contraseña del router: ")

    # 'ios' le dice a NAPALM que hable el "dialecto" de Cisco IOS/IOS-XE.
    # Si mañana trabajaras con un switch Juniper, solo cambiarías esto a 'junos'
    # y el resto del código seguiría funcionando exactamente igual.
    driver = get_network_driver("ios")

    dispositivo = driver(
        hostname="devnetsandboxiosxec8k.cisco.com",
        username="ld.cabrera2003",
        password=password,
        optional_args={"port": 22},
    )

    print("Conectando con NAPALM...")
    dispositivo.open()

    # --- get_facts(): información general del equipo ---
    print("\n" + "=" * 60)
    print("DATOS GENERALES DEL DISPOSITIVO (get_facts)")
    print("=" * 60)
    datos = dispositivo.get_facts()
    print(json.dumps(datos, indent=2))

    # --- get_interfaces(): estado de cada interfaz, YA estructurado ---
    print("\n" + "=" * 60)
    print("INTERFACES (get_interfaces) - sin necesidad de regex")
    print("=" * 60)
    interfaces = dispositivo.get_interfaces()
    for nombre_interfaz, detalles in interfaces.items():
        estado = "UP" if detalles["is_up"] else "DOWN"
        print(f"{nombre_interfaz:<20} Estado: {estado:<6} Velocidad: {detalles['speed']} Mbps")

    # --- get_interfaces_ip(): las IPs configuradas, también estructurado ---
    print("\n" + "=" * 60)
    print("DIRECCIONES IP POR INTERFAZ (get_interfaces_ip)")
    print("=" * 60)
    ips = dispositivo.get_interfaces_ip()
    for nombre_interfaz, direcciones in ips.items():
        if "ipv4" in direcciones:
            for ip, info in direcciones["ipv4"].items():
                print(f"{nombre_interfaz:<20} {ip}/{info['prefix_length']}")

    dispositivo.close()
    print("\nConexión cerrada.")

if __name__ == "__main__":
    main()
