# Homelab — Fase 1: Hardening de Ubuntu Server

## Objetivo del proyecto

Endurecer (hardening) un servidor Ubuntu Server desde una instalación base hasta un estado con buenas prácticas de seguridad: acceso remoto seguro, firewall local, protección contra fuerza bruta, y un servicio real corriendo y protegido — replicando el proceso que seguiría un administrador de sistemas o analista de seguridad al preparar un servidor para producción.

Este proyecto construye sobre la infraestructura de red creada en la [Fase 0](../fase0-red-segmentada/README.md).

## Arquitectura

El servidor Ubuntu Server vive dentro de la red interna del laboratorio (`192.168.56.0/24`), detrás del firewall OPNsense, y es administrado remotamente desde el PC Windows vía SSH.

```
PC Windows (192.168.56.2)
        │
        │ SSH (llave, sin contraseña)
        ▼
Ubuntu Server (192.168.56.159)
   ├── SSH (puerto 22)      → acceso remoto por llave
   ├── UFW                  → firewall local, deniega todo salvo lo permitido
   ├── fail2ban              → bloquea IPs con intentos fallidos de SSH
   ├── Nginx (puerto 80)    → servicio web real, protegido y monitoreado
   └── unattended-upgrades   → parcheo automático de seguridad
```

## Tecnologías utilizadas

- **Ubuntu Server LTS 26.04**
- **OpenSSH** (autenticación por llave pública)
- **UFW** (Uncomplicated Firewall)
- **fail2ban**
- **Nginx**
- **Bash** (script propio de auditoría)

## Cómo se construyó (resumen cronológico)

### 1. Error inicial: instalación equivocada

La primera VM usada por error fue **Ubuntu Desktop** en vez de Ubuntu Server (ver sección de problemas). Todo el proceso se completó primero ahí como aprendizaje, y luego se **migró íntegramente** a una VM real de Ubuntu Server, aprovechando el error como ejercicio de migración de configuración entre servidores.

### 2. Acceso SSH por llave pública

- Se generó un par de llaves SSH dedicado en el equipo Windows (cliente), usando el algoritmo `ed25519`.
- Se copió la llave pública al servidor con `ssh-copy-id`.
- Se configuró `~/.ssh/config` en el cliente para simplificar la conexión (`ssh ubuntu-lab`).
- Se desactivó el login por contraseña y el login root remoto, dejando como único método de acceso la autenticación por llave.

### 3. Firewall local con UFW

- Política por defecto: denegar todo el tráfico entrante, permitir todo el saliente.
- Excepciones explícitas: puerto 22 (SSH) y el perfil `Nginx HTTP` (puerto 80).
- Verificado que el firewall no interrumpiera el propio acceso SSH antes de considerarlo definitivo.

### 4. fail2ban contra fuerza bruta

- Instalado y configurado con `jail.local` (nunca se edita `jail.conf` directamente, ya que se sobreescribe en actualizaciones).
- Parámetros: `bantime = 1h`, `findtime = 10m`, `maxretry = 5`.
- Jail `[sshd]` activado explícitamente.

### 5. Servicio real: Nginx

- Instalado como el "servicio expuesto" del servidor, para practicar el ciclo completo de exponer un puerto nuevo de forma controlada (instalar → decidir si se expone → permitir explícitamente en UFW → verificar).

### 6. Script de auditoría propio

Se creó un script en Bash (`auditoria.sh`) que revisa: puertos abiertos, usuarios con privilegios sudo, actualizaciones de seguridad pendientes, y servicios activos. Ver el archivo `auditoria.sh` en esta misma carpeta.

### 7. Actualizaciones del sistema

- Se confirmó que `unattended-upgrades` aplica parches de seguridad automáticamente en segundo plano (evidencia en los logs, ver sección de hallazgos).
- Se corrió `apt upgrade` manual para confirmar el estado del sistema.

## Problemas encontrados y cómo se resolvieron

### 1. Instalación equivocada: Ubuntu Desktop en vez de Ubuntu Server
**Problema:** todo el hardening inicial se hizo sobre una VM de Ubuntu Desktop por error de selección de ISO al momento de instalar.
**Evidencia:** el script de auditoría mostró servicios de entorno gráfico corriendo (`gdm`, `gnome-shell`, `nautilus`, `avahi-daemon`, `cups`, `docker`, `snapd`), inapropiados para un servidor.
**Solución:** se migró toda la configuración (llave SSH, UFW, fail2ban, Nginx, script de auditoría) a una VM real de Ubuntu Server ya disponible, reconectándola a la red del lab (VMnet2) y repitiendo la secuencia de hardening completa ahí.
**Resultado:** el nuevo servidor pasó de ~36 servicios activos a 25, sin ningún componente de escritorio.

### 2. `PasswordAuthentication` seguía activo pese a configurarlo en `sshd_config`
**Causa raíz:** `cloud-init` crea automáticamente el archivo `/etc/ssh/sshd_config.d/50-cloud-init.conf` con `PasswordAuthentication yes`. Como `sshd_config` incluye los archivos de `sshd_config.d/` casi al inicio del archivo (`Include /etc/ssh/sshd_config.d/*.conf`), y OpenSSH usa la **primera coincidencia** encontrada para directivas simples, ese drop-in prevalecía sobre cualquier cambio hecho en el archivo principal.
**Solución:** modificar directamente `50-cloud-init.conf` en vez de (o además de) `sshd_config`.
**Aprendizaje:** usar `sudo sshd -T | grep passwordauthentication` para ver la configuración **efectiva** antes de asumir un error de sintaxis propio. Cualquier servicio con una carpeta `*.d/` puede tener configuración adicional fuera del archivo principal.

### 3. Conflicto de conectividad entre el PC host y la red del lab (heredado de la Fase 0)
Ver detalle completo en el README de la [Fase 0](../fase0-red-segmentada/README.md) — resumen: al desactivar el adaptador de host en VMnet2 para resolver un conflicto de IP con OPNsense, el PC Windows quedó sin ruta hacia la LAN interna, lo que impedía `ssh-copy-id` desde el host. Se resolvió reactivando el adaptador de host con una IP fija (`192.168.56.2`) fuera del rango DHCP.

### 4. `Connection refused` en el puerto 22 al copiar la llave SSH
**Causa raíz:** OpenSSH Server no estaba instalado en la VM de Ubuntu Server (el servicio simplemente no existía, por lo que ningún tráfico podía ser atendido en ese puerto, aunque la red sí llegara).
**Solución:** `sudo apt install openssh-server -y && sudo systemctl enable --now ssh`.

### 5. Ping bloqueado desde las VMs hacia el PC Windows
**Causa raíz:** el Firewall de Windows Defender bloquea por defecto las peticiones ICMP entrantes (ping) que se originan fuera del propio equipo.
**Solución:** habilitar la regla de entrada "File and Printer Sharing (Echo Request - ICMPv4-In)" en Windows Defender Firewall con Seguridad Avanzada.

### 6. Actualizaciones "atascadas" por *phased updates*
**Observación:** al correr `apt upgrade`, 6 paquetes no se actualizaron pese a aparecer como disponibles, con el mensaje `Not upgrading yet due to phasing`.
**Explicación:** Canonical despliega ciertas actualizaciones de forma gradual (a un porcentaje de máquinas primero) para detectar problemas antes de un despliegue masivo. No es un error del servidor.

### 7. Error transitorio 404 en `unattended-upgrades`
**Observación:** el log de `unattended-upgrades` mostró un error `404 Not Found` al intentar descargar una versión específica del paquete `tar`.
**Explicación:** desincronización temporal entre la lista local de paquetes y el repositorio remoto (la versión exacta ya había sido reemplazada). Se confirmó que en la siguiente ejecución automática el error ya no aparecía y el sistema quedó al día.
**Aprendizaje:** diferenciar un error transitorio de sincronización de un problema real de seguridad/configuración, revisando si persiste en ejecuciones posteriores.

## El script de auditoría (`auditoria.sh`)

Revisa 4 aspectos clave del servidor en una sola ejecución:

1. **Puertos abiertos** (`ss -tulnp`) — qué está escuchando y qué proceso lo abrió.
2. **Usuarios con privilegios sudo** (`getent group sudo`) — detecta cuentas administrativas no reconocidas.
3. **Actualizaciones de seguridad pendientes** (`apt list --upgradable`).
4. **Servicios activos** (`systemctl list-units --type=service --state=running`).

El código completo está en el archivo `auditoria.sh` de esta carpeta.

## Verificación y resultados

- ✅ Acceso SSH exclusivamente por llave — contraseña y login root deshabilitados y verificados en una sesión nueva antes de cerrar la anterior.
- ✅ UFW activo — política `deny incoming` / `allow outgoing`, solo 22/tcp y 80/tcp permitidos explícitamente.
- ✅ fail2ban activo, jail `sshd` habilitado, 0 IPs baneadas (esperado, sin ataques reales).
- ✅ Nginx corriendo y accesible vía HTTP en el puerto 80.
- ✅ Script de auditoría funcional, usado para comparar el estado "antes" (Desktop, ~36 servicios) y "después" (Server, 25 servicios).
- ✅ `unattended-upgrades` confirmado aplicando parches de seguridad automáticamente (evidencia en logs).

### Servicios activos en el servidor final (19 en total)
`chrony`, `cron`, `dbus`, `fail2ban`, `getty@tty1`, `networkd-dispatcher`, `nginx`, `open-vm-tools`, `polkit`, `rsyslog`, `ssh`, `systemd-journald`, `systemd-logind`, `systemd-networkd`, `systemd-resolved`, `systemd-udevd`, `udisks2`, `unattended-upgrades`, `user@1000`, `vgauth`


## Aprendizajes clave

- La diferencia real entre Ubuntu Desktop y Ubuntu Server en términos de superficie de ataque, no solo de interfaz gráfica.
- Cómo migrar una configuración de hardening completa de un servidor a otro.
- El patrón de "drop-in config files" (`*.d/`) presente en muchos servicios de Linux, y por qué puede hacer que un cambio de configuración "no se aplique" aparentemente.
- Uso de `sshd -T` para verificar configuración efectiva en vez de asumir errores de sintaxis.
- Diferenciar errores transitorios de infraestructura (phased updates, 404 temporal) de problemas reales de seguridad.
- El orden correcto y seguro para cambios de acceso remoto: siempre verificar el nuevo método de acceso en una sesión/ventana separada antes de cerrar la sesión/método anterior.

## Próximos pasos

- **Fase 2:** Pentest guiado contra este mismo servidor Ubuntu ya hardenizado, usando Kali Linux (nmap + Metasploit), para evaluar qué tan bien resiste las protecciones aplicadas aquí.

---
*Proyecto de aprendizaje práctico — Leandro Cabrera, Ingeniero en Telecomunicaciones (UCAB)*
