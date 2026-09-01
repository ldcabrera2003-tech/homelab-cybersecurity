# Homelab — Fase 5: Automatización de redes

## Objetivo del proyecto

Aplicar automatización real de infraestructura de red usando Python, sobre un dispositivo Cisco IOS XE genuino (no simulado), conectando la teoría de protocolos de enrutamiento y CLI de Cisco (CCNA) con herramientas modernas de Network Automation usadas en la industria: Netmiko y NAPALM.

## Arquitectura

A diferencia de las fases anteriores, este laboratorio no vive dentro de la red interna `192.168.56.0/24` — el dispositivo objetivo es un router real alojado en la nube por Cisco (DevNet Sandbox), accesible por internet. Esto evitó consumir los recursos locales ya ajustados del homelab (RAM/disco).

```
Kali Linux (192.168.56.128)
   │
   │ SSH sobre Internet (vía NAT de OPNsense)
   ▼
Cisco Catalyst 8000v — "Cat8kv"
IOS XE 17.15.4c
Cisco DevNet Sandbox (Always-On, compartido públicamente)
```

## Tecnologías utilizadas

- **Python 3** con las librerías **Netmiko** y **NAPALM**
- **Cisco DevNet Sandbox** (Catalyst 8000v Always-On) — router real, gratuito, sin necesidad de VPN
- **SSH** como transporte de todas las conexiones

## Las herramientas construidas

### 1. `network_automation.py` — Primer script de automatización
Se conecta al router, lee el estado de las interfaces (`show ip interface brief`), aplica un cambio de configuración real (agrega una descripción a la interfaz `Loopback99`), y verifica el cambio aplicado (`show running-config` de esa interfaz). Ciclo completo de lectura → escritura → verificación con Netmiko.

### 2. `backup_dispositivos.py` — Backup automático y escalable
Diseñado con una lista de dispositivos (`DISPOSITIVOS`) en vez de una conexión única "quemada" en el código — el mismo script funciona igual con 1 o con 100 dispositivos, sin modificar la lógica interna. Descarga la configuración completa (`show running-config`) de cada uno y la guarda en un archivo con marca de tiempo única, evitando sobrescribir backups anteriores.

### 3. `napalm_demo.py` — Datos estructurados multi-vendor
Usa NAPALM en vez de Netmiko para demostrar la diferencia entre obtener texto plano (que requeriría parseo manual con regex) y obtener diccionarios de Python ya estructurados (`get_facts()`, `get_interfaces()`, `get_interfaces_ip()`). El mismo código funcionaría contra un dispositivo Juniper o Arista cambiando solo el nombre del driver (`"ios"` → `"junos"`, etc.).

## Validación y resultados

- ✅ Cambio de configuración aplicado y verificado exitosamente sobre un router Cisco real (Loopback99 con descripción personalizada).
- ✅ Backup completo de configuración (6999 bytes) generado y almacenado localmente con éxito.
- ✅ NAPALM confirmado devolviendo datos ya tipados correctamente (`is_up` como booleano, `prefix_length` en formato CIDR), sin necesidad de ninguna expresión regular.

## Hallazgos y consideraciones

### Los cambios no son permanentes
Los sandboxes "Always-On" de Cisco se resetean periódicamente por diseño (para mantener el entorno limpio para todos los usuarios). El cambio de la Loopback99 podría desaparecer en un reseteo futuro — se documenta como limitación conocida, no como fallo del script.

### Un router de producción trae mucho más de lo esperado
El backup reveló configuración real de nivel empresarial: autenticación AAA con TACACS+, NETCONF/RESTCONF habilitados, certificados PKI autofirmados, y contraseñas ya cifradas con hash tipo scrypt — buena exposición a cómo luce un dispositivo real más allá de lo que se ve en un curso introductorio de CCNA.

## Diseño del código: por qué escala sin reescribirse

El patrón central de `backup_dispositivos.py` separa la lógica de "cómo respaldar un dispositivo" (función `hacer_backup()`) de la lógica de "sobre cuáles dispositivos iterar" (`main()` recorriendo la lista `DISPOSITIVOS`). Gracias a esta separación, agregar un dispositivo nuevo a un futuro despliegue (por ejemplo, una topología montada en Cisco Modeling Labs) es tan simple como agregar un diccionario más a la lista — cero cambios en la lógica de conexión o backup.

## Aprendizajes clave

- Diferencia entre `send_command()` (lectura) y `send_config_set()` (escritura/configuración) en Netmiko.
- Por qué nunca se debe escribir una contraseña directamente en un script (`getpass` como alternativa segura).
- El patrón de diseño "loop sobre lista de dispositivos" como base de cualquier automatización que necesite escalar.
- Diferencia filosófica entre Netmiko (texto plano, tú decides cómo parsearlo) y NAPALM (datos ya estructurados y normalizados entre fabricantes).
- Cómo se ve la configuración real de un dispositivo de producción (AAA, TACACS+, NETCONF/RESTCONF, PKI) más allá de un laboratorio didáctico simple.

## Próximos pasos

- (Opcional, trabajo futuro) Montar una topología pequeña en Cisco Modeling Labs (ya disponible) con 2-3 dispositivos, y aplicar el mismo `backup_dispositivos.py` sin modificaciones, solo agregando entradas a la lista `DISPOSITIVOS` — demostración real de escalabilidad.
- **Fase 6:** proyecto integrador uniendo las fases anteriores en un entorno cohesivo de detección y respuesta.

---
*Proyecto de aprendizaje práctico — Leandro Cabrera, Ingeniero en Telecomunicaciones (UCAB)*
