# Datos de Atalaya

Versión: 2026-10-27T10:59:01+00:00 · Total: **4641** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 175 (10s)
- **DGT PDF cámaras**: ✅ 249 (3s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (0s)
- **Ayto. València**: ✅ 6 (0s)
- **OpenStreetMap**: ✅ 2621 (63s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (1s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ⚠️ falló (www.santacruzdetenerife.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Ayto. Pamplona cinemómetros**: ⚠️ falló (sig.pamplona.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1637 (1s)
- **Sentido de los radares de OSM**: direction de OSM frente a radares oficiales: 4 igual, 0 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Caminos de aproximación**: ✅ 3252 puntos con camino por su carretera, 268 de 325 tramos con recorrido real (81 sin vía cercana; 67s)
- **Sentido por el lado de la calle**: 226 puntos siguen en ambos sentidos; comprobación con radares de sentido conocido: 325 de 465 aciertos (69 %)
- **Límites tomados de su vía**: 114 puestos, 2 quitados por no ser de su vía
- **Revisar**: 88 radares de autovía con límite < 60: dgt:GUID_CABINACINEMOMETRO_120012 N-232 El Villar de Arnedo límite 50; dgt:GUID_CABINACINEMOMETRO_120062 N-634 O Pino límite 50; dgt:GUID_CABINACINEMOMETRO_120100 AC-12 Oleiros límite 50; dgt:GUID_CABINACINEMOMETRO_120101 FE-14 Fene límite 50; dgt:GUID_CABINACINEMOMETRO_120115 N-550 Redondela límite 50; dgt:GUID_CABINACINEMOMETRO_120467 N-2 Alfajarín límite 50; dgt:GUID_CABINACINEMOMETRO_120546 VA-20 Valladolid límite 50; dgt:GUID_CABINACINEMOMETRO_120608 N-340 Torreblanca límite 50; dgt:GUID_CABINACINEMOMETRO_161447 N-357 Algeciras límite 50; dgt:GUID_CABINACINEMOMETRO_163774 N-6 Guadarrama límite 50; dgt:GUID_CABINACINEMOMETRO_163775 N-6  límite 50; dgt:GUID_CABINACINEMOMETRO_163776 N-6 El Espinar límite 50

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 279 | 48 | 19 | 0 | 68 | 230 |
| Aragón | 92 | 6 | 0 | 0 | 18 | 102 |
| Canarias | 48 | 12 | 2 | 0 | 0 | 68 |
| Cantabria | 15 | 6 | 2 | 0 | 6 | 27 |
| Castilla y León | 181 | 57 | 32 | 0 | 35 | 265 |
| Castilla-La Mancha | 109 | 20 | 9 | 1 | 34 | 150 |
| Cataluña | 490 | 69 | 59 | 0 | 4 | 60 |
| Comunidad de Madrid | 147 | 28 | 60 | 1 | 307 | 59 |
| Comunidad Foral de Navarra | 27 | 2 | 1 | 0 | 2 | 35 |
| Comunitat Valenciana | 149 | 28 | 6 | 0 | 44 | 69 |
| Extremadura | 54 | 7 | 2 | 0 | 5 | 86 |
| Galicia | 120 | 33 | 7 | 0 | 30 | 128 |
| Illes Balears | 67 | 11 | 0 | 0 | 2 | 34 |
| La Rioja | 29 | 0 | 0 | 0 | 7 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 176 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 68 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 63 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **1984**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1413
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1100
- AYUNTAMIENTO: 386
- SCT: 277
- AUTONOMICA: 91
- POLICIA_LOCAL: 35
- MULTAS: 33

## Registro

```
DGT feed: 737 puntos
PDFs DGT: {'equipos': 'https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/conoce-el-estado-del-trafico/informacion-e-incidencias-de-trafico/EQUIPOS.pdf', 'cinemometros': 'https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/conoce-el-estado-del-trafico/informacion-e-incidencias-de-trafico/INFORME_CINEMOMETROS_WEB_OK_20260803_extra.pdf'}
  cinemómetros: 2158 filas (707 fijos, 126 tramos, 1325 móviles)
  CartoCiudad: 672 hitos necesarios, 0 por consultar
  cinemómetros: 642 ya estaban en el feed, 175 añadidos, 8 sin poder situar
DGT PDF radares: 175 puntos
  equipos: 260 filas; tipos: ['Cinturón', 'Foto Rojo', 'Línea Contínua', 'Video Stop']
  CartoCiudad: 496 hitos necesarios, 0 por consultar
  equipos: 249 situados, 11 sin poder situar
DGT PDF cámaras: 249 puntos
  SCT JSON: analisi.transparenciacatalunya.cat: HTTP Error 403: Forbidden; pruebo CSV y TXT
  SCT https://analisi.transparenciacatalunya.cat/api/views/re3y-fftf/rows.csv?accessType=DOWNLOAD: analisi.transparenciacatalunya.cat: HTTP Error 400: Bad Request
  SCT muestra: '(ETRS89)' | 'Via         PK          Velocitat   X           Y           ' | 'A-2         445,35      120         288075,4643 4601625,063 '
  SCT radars.txt: 230 radares
Cataluña (SCT): 230 puntos
  Madrid columnas: ['Nº RADAR', 'Ubicacion', 'Carretara o vial', 'UBICACIÓN Calle 30', 'PK', 'Sentido', 'Tipo', 'Carril', 'Longitud inicio tramo', 'Latitud inicio tramo', 'X (WGS84)', 'Y (WGS84)', 'Longitud', 'Latitud', 'Velocidad límite', 'Responsable']
Ayto. Madrid: 23 puntos
Ayto. València: 6 puntos
OpenStreetMap: 2621 puntos
Tramos radar móvil: 1152 puntos
Ayto. Madrid foto-rojo y ZBE: 454 puntos
Ayto. Málaga foto-rojo: 7 puntos
Ayto. Salamanca: 24 puntos
Ayto. Donostia: 12 puntos
Ayto. Santa Cruz de Tenerife foto-rojo: ERROR www.santacruzdetenerife.es: <urlopen error timed out>
Ayto. Pamplona cinemómetros: ERROR sig.pamplona.es: <urlopen error timed out>
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1637 puntos
feed comunitario tras quitar tramos ya situados: 466
tramos: 2 puntos sueltos unidos a su tramo, 5 cámaras de entrada/salida absorbidas
  límites: 186 sin límite, 0 por consultar
límites deducidos de OSM: 108
  regiones: 0 celdas nuevas que consultar
  CartoCiudad: 1993 hitos necesarios, 0 por consultar
rumbos por sentido: 1020
direction de OSM frente a radares oficiales: 4 igual, 0 al revés → no se usa
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
caminos: {'con_camino': 3252, 'sin_via': 81, 'tramos_con_recorrido': 268, 'tramos': 325, 'lado_ok': 325, 'lado_mal': 140, 'caminos_alternativos': 8, 'en_enlace': 36, 'sospechosos': ['dgt:GUID_CABINACINEMOMETRO_120012 N-232 El Villar de Arnedo límite 50', 'dgt:GUID_CABINACINEMOMETRO_120062 N-634 O Pino límite 50', 'dgt:GUID_CABINACINEMOMETRO_120100 AC-12 Oleiros límite 50', 'dgt:GUID_CABINACINEMOMETRO_120101 FE-14 Fene límite 50', 'dgt:GUID_CABINACINEMOMETRO_120115 N-550 Redondela límite 50', 'dgt:GUID_CABINACINEMOMETRO_120467 N-2 Alfajarín límite 50', 'dgt:GUID_CABINACINEMOMETRO_120546 VA-20 Valladolid límite 50', 'dgt:GUID_CABINACINEMOMETRO_120608 N-340 Torreblanca límite 50', 'dgt:GUID_CABINACINEMOMETRO_161447 N-357 Algeciras límite 50', 'dgt:GUID_CABINACINEMOMETRO_163774 N-6 Guadarrama límite 50', 'dgt:GUID_CABINACINEMOMETRO_163775 N-6  límite 50', 'dgt:GUID_CABINACINEMOMETRO_163776 N-6 El Espinar límite 50', 'dgt:GUID_CABINACINEMOMETRO_166114 N-433 El Garrobo límite 50', 'dgtpdf:F:N-320:309.935:C N-320 Torrejón del Rey límite 50', 'mad:40.48048,-3.68543 PASEO DE LA CASTELLANA Nº 300, SALIDA Madrid límite 50', 'slm:40.95233,-5.67013  Salamanca límite 50', 'slm:40.95223,-5.65938  Salamanca límite 50', 'slm:40.95505,-5.67865  Salamanca límite 30', 'slm:40.95995,-5.65963  Salamanca límite 30', 'slm:40.96599,-5.65766  Salamanca límite 30', 'osm:n60022423  Alcobendas límite 50', 'osm:n254459894  Toledo límite 40', 'osm:n269563920  Arroyo de la Encomienda límite 50', 'osm:n297102149  Getaria límite 50', 'osm:n913996684  Santiago de Compostela límite 50', 'osm:n986339533  Oviedo límite 30', 'osm:n992000532  Zaragoza límite 50', 'osm:n992001590  Bilbao límite 50', 'osm:n992001758  Zaragoza límite 50', 'osm:n992002037 39 Valladolid límite 50', 'osm:n992004492  Zaragoza límite 50', 'osm:n992005295  Madrid límite 50', 'osm:n1123913886  Badajoz límite 50', 'osm:n1324141870  Santiago de Compostela límite 50', 'osm:n2310925029  Badajoz límite 50', 'osm:n2334938841  Zaragoza límite 50', 'osm:n2334938842  Zaragoza límite 50', 'osm:n2334938845  Zaragoza límite 50', 'osm:n2334938848  Zaragoza límite 50', 'osm:n2334938854  Arroyo de la Encomienda límite 50', 'osm:n2334938864  Barcelona límite 50', 'osm:n2334938896  Arroyo de la Encomienda límite 50', 'osm:n2334938943  Gijón límite 50', 'osm:n2334938954  Oviedo límite 50', 'osm:n2378267329  Oviedo límite 50', 'osm:n3368363707  Madrid límite 50', 'osm:n4483769673  Huesca límite 40', 'osm:n6450367493 41 Valladolid límite 50', 'osm:n6578570920 46 Valladolid límite 50', 'osm:n6790287179  Badajoz límite 50', 'osm:n6831769280  Ferrol límite 50', 'osm:n6865072280  La Bañeza límite 50', 'osm:n6865072283  La Bañeza límite 40', 'osm:n7185167104  Santiago de Compostela límite 50', 'osm:n9212434658  Ultzama límite 50', 'osm:n10101245045  Herrera del Duque límite 50', 'osm:n10182509613  Leioa límite 30', 'osm:n10182984432  Leioa límite 30', 'osm:n11026473819  A Coruña límite 50', 'osm:n11026473821  A Coruña límite 50', 'osm:n11203254732  Gijón límite 50', 'osm:n11359435759 43 Valladolid límite 50', 'osm:n11422372005   límite 50', 'osm:n12292478909  Ourense límite 50', 'osm:n12640711390  Tarifa límite 50', 'osm:n13098388072  Llinars del Vallès límite 30', 'osm:n13171328938  Oviedo límite 50', 'osm:n13171708760  Oviedo límite 30', 'osm:n13171708761  Oviedo límite 30', 'osm:n13183426531  Oviedo límite 50', 'osm:n13183466667  Oviedo límite 50', 'osm:n13305042666  Mérida límite 50', 'osm:n13305061599  Mérida límite 50', 'osm:n13305138029  Talavera la Real límite 50', 'osm:n13330585898  Alcobendas límite 50', 'osm:n13348131857  Badajoz límite 50', 'osm:n13426513493  Zafra límite 50', 'osm:n13503585321  Trabazos límite 50', 'osm:n13512109619  Monzón límite 50', 'osm:n13512145216  Monzón límite 50', 'osm:n13577412657  Palma límite 50', 'osm:n13577417988  Palma límite 50', 'osm:n13577425546  Palma límite 50', 'osm:n13655273294  Llinars del Vallès límite 30', 'osm:n13730592761  Algeciras límite 30', 'osm:n13730609393  Algeciras límite 30', 'osm:n13745794143  Mérida límite 50', 'osm:n13754691491  La Bañeza límite 50'], 'dos_sentidos': 226, 'limites_via': 114, 'limites_quitados': 2, 'segundos': 67}
```
