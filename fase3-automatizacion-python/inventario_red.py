#!/usr/bin/env python3
"""
Inventario de red - Fase 3 del Homelab
Hace un ping sweep de una subred, guarda los resultados en una base de
datos SQLite, y detecta si aparece algún host nuevo respecto a escaneos anteriores.

Uso: python3 inventario_red.py <prefijo_red>
Ejemplo: python3 inventario_red.py 192.168.56
(esto escanea 192.168.56.1 hasta 192.168.56.254)
"""

import subprocess
import sqlite3
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

NOMBRE_DB = "inventario_red.db"

def crear_tabla_si_no_existe(conexion):
    """
    Crea la tabla donde se guarda el historial, solo si no existe ya
    (para no borrar datos de escaneos anteriores cada vez que corres el script).
    """
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            ip TEXT PRIMARY KEY,
            primera_deteccion TEXT,
            ultima_deteccion TEXT,
            veces_visto INTEGER
        )
    """)
    conexion.commit()

def hacer_ping(ip, timeout=1):
    """
    Llama al comando 'ping' real del sistema operativo (Linux) y revisa
    si respondió exitosamente. -c 1 = un solo paquete, -W = timeout en segundos.
    """
    resultado = subprocess.run(
        ["ping", "-c", "1", "-W", str(timeout), ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # ping devuelve 0 si hubo respuesta, cualquier otro número si falló
    return (ip, resultado.returncode == 0)

def escanear_red(prefijo_red, hilos=50):
    """
    Genera todas las IPs posibles de la subred (ej: 192.168.56.1 a .254)
    y las revisa en paralelo con hilos, igual que hicimos con el port scanner.
    """
    ips_a_revisar = [f"{prefijo_red}.{ultimo_octeto}" for ultimo_octeto in range(1, 255)]
    hosts_activos = []

    with ThreadPoolExecutor(max_workers=hilos) as executor:
        resultados = executor.map(hacer_ping, ips_a_revisar)
        for ip, activo in resultados:
            if activo:
                hosts_activos.append(ip)

    return hosts_activos

def actualizar_inventario(conexion, hosts_activos):
    """
    Por cada host activo detectado: si ya existía en la base de datos,
    actualiza su 'última vez visto' y suma 1 a su contador.
    Si es la primera vez que aparece, lo inserta como registro nuevo.
    Devuelve la lista de IPs que son COMPLETAMENTE NUEVAS en este escaneo.
    """
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hosts_nuevos = []

    for ip in hosts_activos:
        cursor = conexion.execute("SELECT ip FROM inventario WHERE ip = ?", (ip,))
        existe = cursor.fetchone()

        if existe:
            conexion.execute("""
                UPDATE inventario
                SET ultima_deteccion = ?, veces_visto = veces_visto + 1
                WHERE ip = ?
            """, (ahora, ip))
        else:
            conexion.execute("""
                INSERT INTO inventario (ip, primera_deteccion, ultima_deteccion, veces_visto)
                VALUES (?, ?, ?, 1)
            """, (ip, ahora, ahora))
            hosts_nuevos.append(ip)

    conexion.commit()
    return hosts_nuevos

def hosts_ausentes(conexion, hosts_activos):
    """
    Revisa la base de datos completa y devuelve qué IPs se conocían
    de escaneos anteriores pero NO aparecieron en el escaneo actual.
    """
    cursor = conexion.execute("SELECT ip FROM inventario")
    todas_las_conocidas = {fila[0] for fila in cursor.fetchall()}
    activas_ahora = set(hosts_activos)
    return todas_las_conocidas - activas_ahora

def main():
    parser = argparse.ArgumentParser(description="Inventario de red con historial en base de datos")
    parser.add_argument("prefijo_red", help="Prefijo de red a escanear, ej: 192.168.56")
    args = parser.parse_args()

    print(f"Escaneando red {args.prefijo_red}.0/24 ...")
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")

    conexion = sqlite3.connect(NOMBRE_DB)
    crear_tabla_si_no_existe(conexion)

    hosts_activos = escanear_red(args.prefijo_red)
    hosts_nuevos = actualizar_inventario(conexion, hosts_activos)
    ausentes = hosts_ausentes(conexion, hosts_activos)

    print("\n" + "=" * 50)
    print(f"Hosts activos encontrados: {len(hosts_activos)}")
    for ip in sorted(hosts_activos):
        marca_nuevo = " 🆕 NUEVO" if ip in hosts_nuevos else ""
        print(f"  {ip}{marca_nuevo}")

    if ausentes:
        print(f"\n⚠️  Hosts conocidos que NO respondieron esta vez ({len(ausentes)}):")
        for ip in sorted(ausentes):
            print(f"  {ip}")

    print("=" * 50)
    print(f"Datos guardados en: {NOMBRE_DB}")
    conexion.close()

if __name__ == "__main__":
    main()
