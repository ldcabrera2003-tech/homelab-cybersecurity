# Homelab de Redes y Ciberseguridad

Laboratorio de práctica construido y documentado progresivamente mientras aprendo Redes, Ciberseguridad, IT y Automatización. Cada carpeta representa una fase del proyecto, con su propio README detallando objetivos, arquitectura, comandos usados y problemas resueltos durante la construcción.

## Sobre este proyecto

Soy Ingeniero en Telecomunicaciones (UCAB) y estoy construyendo experiencia práctica más allá de los cursos formales y certificaciones. Este repositorio documenta un homelab virtual que voy expandiendo por fases: desde la infraestructura de red base, pasando por hardening de sistemas, pruebas de penetración controladas, automatización con Python, hasta un entorno integrado de detección tipo SOC.

## Stack utilizado

- **Virtualización:** VMware Workstation Pro
- **Firewall/Router:** OPNsense
- **Sistemas:** Kali Linux, Ubuntu Server LTS
- **Lenguajes/Herramientas:** Python, Bash, Docker
- **Documentación:** Markdown, draw.io

## Fases del proyecto

| Fase | Descripción | Estado |
|---|---|---|
| [Fase 0 — Red segmentada](./fase0-red-segmentada/README.md) | Laboratorio virtual con firewall OPNsense y red interna aislada | ✅ Completa |
| [Fase 1 — Hardening de Linux] (./fase1-hardening-linux/README.md) | Endurecimiento de un servidor Ubuntu (UFW/iptables, SSH, fail2ban) | ✅ Completa |
| [Fase 2 — Pentest guiado] (./fase2-pentest-metasploitable/README.md) | Reconocimiento y explotación controlada sobre una máquina vulnerable | ✅ Completa |
| [Fase 3 — Automatización con Python] (./fase3-automatizacion-python/README.md) | Scripts propios de escaneo, análisis de logs e inventario de red | ✅ Completa |
| Fase 4 — Automatización de redes | Configuración de dispositivos de red vía Python/Ansible | ⏳ Pendiente |
| Fase 5 — Proyecto integrador | Mini-SOC casero uniendo todas las fases anteriores | ⏳ Pendiente |

## Contacto

Leandro Daniel Cabrera Lobo — ld.cabrera2003@gmail.com