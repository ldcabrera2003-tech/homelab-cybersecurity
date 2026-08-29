#!/usr/bin/env python3
"""
Parser de logs SSH - Fase 3 del Homelab
Analiza /var/log/auth.log en busca de intentos de autenticación fallidos
y detecta posibles patrones de fuerza bruta por IP.

Uso: python3 log_parser.py [ruta_al_log] [--umbral N]
Ejemplo: python3 log_parser.py /var/log/auth.log --umbral 5
"""

import re
import argparse
from collections import Counter
from datetime import datetime

# Patrones de líneas que indican un intento fallido de autenticación.
# Cada patrón captura la IP de origen entre paréntesis - eso es un "grupo" en regex.
PATRONES_FALLO = [
    r"Failed password for .* from (\d+\.\d+\.\d+\.\d+)",
    r"Invalid user .* from (\d+\.\d+\.\d+\.\d+)",
    r"Failed publickey for .* from (\d+\.\d+\.\d+\.\d+)",
    r"Connection closed by invalid user .* (\d+\.\d+\.\d+\.\d+)",
    r"authentication failure.*rhost=(\d+\.\d+\.\d+\.\d+)",
]

def analizar_log(ruta_log):
    """
    Lee el archivo de log línea por línea y extrae las IPs
    asociadas a intentos fallidos de autenticación.
    """
    contador_ips = Counter()
    lineas_sospechosas = []

    try:
        with open(ruta_log, "r", errors="ignore") as archivo:
            for linea in archivo:
                for patron in PATRONES_FALLO:
                    coincidencia = re.search(patron, linea)
                    if coincidencia:
                        ip = coincidencia.group(1)
                        contador_ips[ip] += 1
                        lineas_sospechosas.append((ip, linea.strip()))
                        break  # ya encontramos coincidencia, no revisar los demás patrones en esta línea
    except FileNotFoundError:
        print(f"No se encontró el archivo: {ruta_log}")
        return None, None
    except PermissionError:
        print(f"Sin permisos para leer {ruta_log}. Prueba ejecutar con: sudo python3 log_parser.py {ruta_log}")
        return None, None

    return contador_ips, lineas_sospechosas

def generar_reporte(contador_ips, lineas_sospechosas, umbral):
    print("=" * 55)
    print(f"   REPORTE DE ANÁLISIS DE LOGS SSH")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    if not contador_ips:
        print("\nNo se encontraron intentos fallidos de autenticación.")
        return

    print(f"\nTotal de intentos fallidos: {sum(contador_ips.values())}")
    print(f"IPs distintas involucradas: {len(contador_ips)}")
    print("\nResumen por IP (de mayor a menor cantidad de intentos):")
    print("-" * 55)

    for ip, cantidad in contador_ips.most_common():
        marca = " ⚠️  SOSPECHOSA (posible fuerza bruta)" if cantidad >= umbral else ""
        print(f"{ip:<20} {cantidad:>5} intento(s){marca}")

    ips_sospechosas = [ip for ip, cant in contador_ips.items() if cant >= umbral]
    if ips_sospechosas:
        print("\n" + "=" * 55)
        print(f"⚠️  {len(ips_sospechosas)} IP(s) superaron el umbral de {umbral} intentos:")
        for ip in ips_sospechosas:
            print(f"   - {ip}")
        print("Considera bloquear estas IPs o revisar si fail2ban ya actuó sobre ellas.")

def main():
    parser = argparse.ArgumentParser(description="Parser de logs SSH para detectar fuerza bruta")
    parser.add_argument("ruta_log", nargs="?", default="/var/log/auth.log",
                         help="Ruta al archivo de log (default: /var/log/auth.log)")
    parser.add_argument("--umbral", type=int, default=5,
                         help="Cantidad de intentos para marcar una IP como sospechosa (default: 5)")
    args = parser.parse_args()

    contador_ips, lineas_sospechosas = analizar_log(args.ruta_log)
    if contador_ips is not None:
        generar_reporte(contador_ips, lineas_sospechosas, args.umbral)

if __name__ == "__main__":
    main()
