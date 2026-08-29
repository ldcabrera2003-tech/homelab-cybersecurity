#!/usr/bin/env python3
"""
Port Scanner propio - Fase 3 del Homelab
Escanea un rango de puertos TCP en un host, sin depender de nmap.
Uso: python3 port_scanner.py <IP> <puerto_inicio> <puerto_fin>
Ejemplo: python3 port_scanner.py 192.168.56.159 1 1000
"""

import socket
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

def escanear_puerto(ip, puerto, timeout=1):
    """
    Intenta conectar a un puerto TCP específico.
    Devuelve (puerto, True) si está abierto, (puerto, False) si no.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    resultado = sock.connect_ex((ip, puerto))  # devuelve 0 si conecta con éxito
    sock.close()
    return (puerto, resultado == 0)

def obtener_banner(ip, puerto, timeout=1):
    """
    Intenta leer el 'banner' que algunos servicios envían al conectar
    (ej: la versión de SSH). No todos los servicios lo hacen.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, puerto))
        banner = sock.recv(1024).decode(errors='ignore').strip()
        sock.close()
        return banner if banner else "Sin banner"
    except Exception:
        return "Sin banner"

def main():
    parser = argparse.ArgumentParser(description="Port scanner propio en Python")
    parser.add_argument("ip", help="IP del objetivo a escanear")
    parser.add_argument("puerto_inicio", type=int, help="Puerto inicial del rango")
    parser.add_argument("puerto_fin", type=int, help="Puerto final del rango")
    parser.add_argument("--hilos", type=int, default=100, help="Cantidad de hilos concurrentes (default: 100)")
    args = parser.parse_args()

    print(f"Escaneando {args.ip} - puertos {args.puerto_inicio} a {args.puerto_fin}")
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 50)

    puertos_abiertos = []
    rango_puertos = range(args.puerto_inicio, args.puerto_fin + 1)

    # ThreadPoolExecutor permite escanear muchos puertos EN PARALELO,
    # en vez de uno por uno secuencialmente (que sería muy lento).
    with ThreadPoolExecutor(max_workers=args.hilos) as executor:
        resultados = executor.map(lambda p: escanear_puerto(args.ip, p), rango_puertos)
        for puerto, abierto in resultados:
            if abierto:
                puertos_abiertos.append(puerto)

    print(f"\nPuertos abiertos encontrados: {len(puertos_abiertos)}")
    print("-" * 50)
    for puerto in sorted(puertos_abiertos):
        banner = obtener_banner(args.ip, puerto)
        print(f"Puerto {puerto:>5}/tcp  ABIERTO   {banner}")

    print("-" * 50)
    print(f"Fin: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
