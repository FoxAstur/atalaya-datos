# Política de privacidad de Atalaya

*Última actualización: 14 de noviembre de 2026*

Atalaya es una aplicación para Android que avisa de radares, cámaras e incidencias de tráfico y hace de navegador.
La desarrolla una persona particular (Carlos López-Escobar, «FoxAstur»). Contacto: abre una incidencia en
<https://github.com/FoxAstur/atalaya-datos/issues>.

## Resumen

- **No hay cuentas ni registro.** Atalaya no pide nombre, correo ni teléfono.
- **No hay servidores propios, publicidad ni analítica.** El desarrollador no recibe ni guarda ningún dato tuyo.
- **Tu posición se usa en el propio teléfono** para saber qué radares e incidencias tienes delante. No se envía a
  ningún servidor del desarrollador, porque no existe.
- Algunas funciones consultan servicios de terceros y, para dar la respuesta, necesitan saber un lugar (ver abajo).

## Qué datos usa y para qué

| Dato | Para qué | Dónde se queda |
|---|---|---|
| Ubicación precisa, también con la app en segundo plano mientras conduces | Avisar de radares, cámaras, tramos, zonas de bajas emisiones e incidencias; guiarte por la ruta | En el teléfono |
| Micrófono (solo cuando pulsas el botón de voz) | Órdenes de voz («llévame a casa», «marca un radar») | Lo procesa el reconocimiento de voz de tu teléfono (el de Android/Google), según su propia política |
| Dispositivos Bluetooth emparejados (solo su conexión/desconexión) | Arrancar sola al conectar con el coche y parar al desconectar | En el teléfono |
| Notificación de navegación de Google Maps (si das el permiso de acceso a notificaciones) | Saber tu próxima maniobra para no avisar de radares que no están en tu ruta | En el teléfono; no se lee ninguna otra notificación |
| Radares que marcas tú, favoritos, casa/trabajo, historial de viajes y ajustes | Tus avisos y tus lugares | En el teléfono, y en la copia de seguridad de Android de tu cuenta de Google si la tienes activada |

## Servicios de terceros a los que se conecta

Para funcionar, la app descarga datos públicos y hace consultas a estos servicios. Reciben tu dirección IP (como
cualquier web) y, cuando se indica, un lugar:

- **GitHub** (github.com, raw.githubusercontent.com): descarga de la base de radares y de las actualizaciones. No se envía tu posición.
- **DGT – Punto de Acceso Nacional** (nap.dgt.es): incidencias y paneles en tiempo real de toda España. Se descarga el fichero completo; no se envía tu posición.
- **TomTom** (api.tomtom.com), solo si pones tu propia clave: cálculo de rutas y tráfico. Se envían el origen, el destino y la ruta.
- **Valhalla de FOSSGIS** (valhalla1.openstreetmap.de): cálculo de rutas cuando no hay clave de TomTom. Se envían el origen y el destino.
- **Photon de Komoot** (photon.komoot.io): buscador de direcciones y sitios. Se envían el texto buscado y una posición aproximada para ordenar los resultados.
- **Overpass / OpenStreetMap** (overpass-api.de, overpass.kumi.systems): gasolineras, aparcamientos y otros sitios cerca de un punto o de la ruta. Se envía la zona consultada.
- **OpenFreeMap** (tiles.openfreemap.org): las teselas del mapa de la zona que estás viendo.
- **Open-Meteo** (api.open-meteo.com): el tiempo en puntos de tu ruta.
- **adsb.lol y OpenSky Network**: posición de los helicópteros de la DGT. Se envía la zona consultada.
- **Portales de datos abiertos** (Ayuntamientos de Madrid, Pamplona y Santa Cruz de Tenerife, Generalitat de Catalunya, IGN): descarga de listados públicos; no se envía tu posición.

## Lo que no hace

- No vende ni comparte datos con nadie.
- No sigue tu actividad en otras aplicaciones.
- No sube tus viajes, tus radares marcados ni tu posición a ningún servidor del desarrollador.

## Borrar tus datos

Todo está en tu teléfono: se borra desinstalando la app o desde Ajustes de Android › Aplicaciones › Atalaya ›
Almacenamiento › Borrar datos. Dentro de la app puedes borrar tus radares marcados y tus favoritos uno a uno.

## Menores

Atalaya es una aplicación para conductores y no está dirigida a menores de edad.

## Cambios

Si esta política cambia, la nueva versión se publicará en esta misma página con su fecha.
