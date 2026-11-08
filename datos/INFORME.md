# Datos de Atalaya

Versión: 2026-11-08T06:55:35+00:00 · Total: **5683** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 190 (8s)
- **DGT PDF cámaras**: ✅ 252 (1s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ✅ 3217 (82s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (1s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Câmara Municipal de Lisboa**: ✅ 18 (0s)
- **Ajuntament de Viladecans**: ✅ 24 (2s)
- **Portugal: ANSR (red SINCRO)**: ✅ 121 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Ayto. Pamplona cinemómetros**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1802 (0s)
- **Cámaras de stop y semáforo**: 100 cámaras de stop o semáforo llevadas a su línea de detención (140751 stops y semáforos de OSM)
- **Puntos comprobados**: ⚠️ 96 comprobados sobre el terreno; arreglados: osm:r9933664 (la2, lo2)
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 584 coinciden con los nuestros, 10 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 565/588 → se usa en 317 puntos y en 42 vigila los dos sentidos
- **Sentido de los radares de OSM**: 61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
- **Sentido de los tramos de la DGT**: 36 de 52 tramos del feed de la DGT venían con la salida primero y se les ha dado la vuelta (comprobado con OSM/PDF: 15 a favor, 1 en contra)
- **Zonas de bajas emisiones**: ✅ 57
- **Situados por PK**: ✅ comprobado con 357 radares del feed (PK y coordenadas): en recta mediana 47 m, p75 93 m, p90 256 m; por la carretera mediana 34 m, p75 76 m, p90 247 m → 295 de 364 situados por PK recolocados por la carretera
- **Zonas de radar móvil por carretera**: 1139 de 1301 que venían en línea recta siguen ya la carretera (162 sin poder trazar)
- **Caminos de aproximación**: ✅ 3888 puntos con camino por su carretera, 317 de 346 tramos con recorrido real (27 sin vía cercana; 123s)
- **Sentido por el lado de la calle**: 281 puntos de calles de doble sentido y 29 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 39/42 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 94/117; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 1/2; dgtpdf ciudad 12-25 m: 3/5; dgtpdf carretera 25-41 m: 1/2; dgtpdf carretera 4-7 m: 1/1; dgtpdf carretera 7-12 m: 0/1; dgtpdf ciudad 7-12 m: 1/1; dgtpdf carretera todas: 3/6; dgtpdf ciudad todas: 4/6; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 94/120; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 154/200; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1. Pistas combinadas: limite 23/32; cruce+lado 1/2; cruce 33/42; lado+limite 8/9
- **Copias de OSM de radares oficiales**: 67 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 42/43 → heredado en 18; 9 radares del PDF de la DGT llevados a la posición de su copia de OSM
- **Radares viejos de OSM repetidos**: 4 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:n5744469677, osm:n7171815050, osm:n14169137330
- **Radares seguidos (mismo sentido, < 300 m)**: 70 pares por revisar: osm:n8281297753→osm:n3269210194 87 m; osm:n8081941155→osm:n8432725880 90 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n5308701907→osm:n245940388 120 m; ansr:IC17:7.4:N→ansr:IC17:6.7:N 121 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; osm:r20130852→osm:n9920942778 128 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 132 m; osm:n8432725876→osm:n8081941154 135 m; osm:n13170535898b→osm:n13170535897 139 m; osm:n13170535897b→osm:n13170535898 139 m; osm:n3269210194→osm:n8281297753 139 m; madzbe:40.4291,-3.7048→madzbe:40.4291,-3.7037 140 m; osm:n4388458815→osm:n682302418 141 m; osm:n13378565235→osm:n11223504291 142 m; osm:n8081941158→osm:n8158390898 143 m; osm:n8432725879→osm:n8081941158 144 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.3998,-3.6687→madzbe:40.3986,-3.6695 154 m
- **Límites tomados de su vía**: 151 puestos, 5 quitados por no ser de su vía
- **Revisar**: nada sospechoso
- **Cámaras de semáforo**: comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 10 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 41 llevadas a su línea (7 estaban pasado el cruce); 40 sin ningún semáforo de OSM a 50 m (posición por revisar)
- **Sentido oficial (última comprobación)**: 940 con sentido oficial comprobable; 3 corregidos: dgt:GUID_CABINACINEMOMETRO_120602, dgt:GUID_CABINACINEMOMETRO_120603, dgt:GUID_CABINACINEMOMETRO_120647
- **Revisión final**: 15 movidos a su cámara de OSM (estaban a más de 150 m de su PK y OSM la tiene en él); 29 llevados a su carretera; 16 con el rumbo cruzado corregido; 13 duplicados quitados
- **Posición aproximada (solo PK)**: 343 puntos
- **Ministerio: tramos de concentración de accidentes**: ✅ 109 (22s); trazados por la carretera 419 de 529
- **Tramos con muchos accidentes (autonómicas y provinciales, microdatos DGT)**: ✅ 426 (0s)

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil | Accidentes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Andalucía | 293 | 41 | 22 | 0 | 65 | 231 | 65 |
| Aragón | 95 | 5 | 0 | 0 | 17 | 109 | 1 |
| Canarias | 51 | 13 | 2 | 0 | 0 | 68 | 90 |
| Cantabria | 16 | 4 | 2 | 0 | 3 | 27 | 3 |
| Castilla y León | 214 | 54 | 34 | 0 | 32 | 293 | 3 |
| Castilla-La Mancha | 102 | 20 | 12 | 1 | 33 | 152 | 1 |
| Cataluña | 502 | 69 | 68 | 0 | 3 | 66 | 4 |
| Comunidad de Madrid | 153 | 28 | 66 | 1 | 304 | 59 | 80 |
| Comunidad Foral de Navarra | 37 | 2 | 1 | 0 | 2 | 37 | 3 |
| Comunitat Valenciana | 156 | 22 | 8 | 2 | 46 | 80 | 53 |
| Extremadura | 56 | 6 | 2 | 0 | 5 | 86 | 0 |
| Galicia | 127 | 24 | 7 | 0 | 31 | 128 | 20 |
| Illes Balears | 83 | 9 | 0 | 0 | 2 | 38 | 42 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 | 1 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 210 | 2 | 9 | 0 | 0 | 0 | 47 |
| Portugal | 258 | 33 | 8 | 0 | 0 | 0 | 0 |
| Principado de Asturias | 77 | 13 | 8 | 0 | 7 | 32 | 8 |
| Región de Murcia | 20 | 4 | 0 | 0 | 5 | 67 | 5 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 | 109 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2706**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1702
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1134
- ACCIDENTES_DGT: 426
- AYUNTAMIENTO: 422
- SCT: 277
- AUTONOMICA: 208
- MINISTERIO: 109
- POLICIA_LOCAL: 66
- MULTAS: 33

## Registro

```
  CartoCiudad: 3795 hitos necesarios, 0 por consultar
  sentido oficial: dgt:GUID_CABINACINEMOMETRO_120602 N-332 PK 203.2 Creciente: rumbo 113.1 → 306.4
  sentido oficial: dgt:GUID_CABINACINEMOMETRO_120603 N-332 PK 204.45 Decreciente: rumbo 293.1 → 124.5
  sentido oficial: dgt:GUID_CABINACINEMOMETRO_120647 EI-600 PK 9.635 Creciente: rumbo 99.0 → 286.2
  testigo: dgt:GUID_CABINACINEMOMETRO_120095 A-92N PK 9.25 a 430 m de su PK; la cámara de OSM, a 89 m → se mueve 368 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120129 A-220 PK 9.366 a 244 m de su PK; la cámara de OSM, a 18 m → se mueve 227 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120233 N-432 PK 111.654 a 347 m de su PK; la cámara de OSM, a 8 m → se mueve 355 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120261 A-4 PK 40.406 a 411 m de su PK; la cámara de OSM, a 20 m → se mueve 401 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120304 A-2 PK 53.559 a 210 m de su PK; la cámara de OSM, a 19 m → se mueve 214 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120311 A-31 PK 11.635 a 366 m de su PK; la cámara de OSM, a 32 m → se mueve 391 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120314 A-40 PK 299.452 a 445 m de su PK; la cámara de OSM, a 20 m → se mueve 442 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120391 A-6050 PK 0.95 a 392 m de su PK; la cámara de OSM, a 29 m → se mueve 417 m
  testigo: dgt:GUID_CABINACINEMOMETRO_120667 N-122 PK 142.26 a 263 m de su PK; la cámara de OSM, a 47 m → se mueve 310 m
  testigo: dgt:GUID_CABINACINEMOMETRO_160238 CA-34 PK 0.71 a 185 m de su PK; la cámara de OSM, a 94 m → se mueve 279 m
  testigo: dgt:GUID_CABINACINEMOMETRO_165621 M-40 PK 20.265 a 465 m de su PK; la cámara de OSM, a 64 m → se mueve 445 m
  testigo: dgtpdf:F:CL-623:7.11:D CL-623 PK 7.11 a 161 m de su PK; la cámara de OSM, a 12 m → se mueve 160 m
  testigo: dgtpdf:F:M-300:31.325:D M-300 PK 31.325 a 266 m de su PK; la cámara de OSM, a 54 m → se mueve 256 m
  testigo: dgtpdf:F:TF-66:9.0:D TF-66 PK 9.0 a 171 m de su PK; la cámara de OSM, a 20 m → se mueve 184 m
  testigo: dgtpdf:F:N-332:245.0:C N-332 PK 245.0 a 152 m de su PK; la cámara de OSM, a 33 m → se mueve 120 m
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_120009 N-240 rumbo 274.5 y su vía va a [157, 153] → 333.1
  su vía: dgt:GUID_CABINACINEMOMETRO_120010 N-330 PK 668.655: a 9999 m de su carretera → a ella (en su PK, 571 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120011 N-330 PK 667.435: a 135 m de su carretera → a ella (en su PK, 321 m)
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_120025 N-234 rumbo 117.0 y su vía va a [192, 12, 12, 190, 9, 12] → 189.0
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_120027 A-12 rumbo 262.3 y su vía va a [343, 343, 345, 343, 341, 347, 341] → None
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_120037 A-4 rumbo 2.9 y su vía va a [286, 286, 105, 106] → None
  su vía: dgt:GUID_CABINACINEMOMETRO_120133 N-232 PK 293.875: a 269 m de su carretera → a ella (al punto más cercano, 270 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120140 N-211 PK 228.153: a 213 m de su carretera → a ella (al punto más cercano, 214 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120203 N-330 PK 670.101: a 9999 m de su carretera → a ella (en su PK, 572 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120204 N-330 PK 671.745: a 407 m de su carretera → a ella (en su PK, 486 m)
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_120435 AC-552 rumbo 195.2 y su vía va a [124, 136, 131] → 135.8
  su vía: dgt:GUID_CABINACINEMOMETRO_120601 CV-91 PK 18.888: a 266 m de su carretera → a ella (en su PK, 278 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120651 MA-19 PK 30.125: a 74 m de su carretera → a ella (en su PK, 76 m)
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_163776 N-6 rumbo 114.5 y su vía va a [206, 205, 206, 205, 206] → None
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_165670 AC-862 rumbo 84.1 y su vía va a [154] → 154.3
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_165816 VG-4.4 rumbo 249.8 y su vía va a [306] → 306.4
  su vía: dgt:GUID_CABINACINEMOMETRO_166987 A-68 PK 246.017: a 172 m de su carretera → a ella (al punto más cercano, 172 m)
  rumbo cruzado: dgtpdf:F:CA-141:21.3:C CA-141 rumbo 114.2 y su vía va a [178, 184, 168] → 168.3
  su vía: dgtpdf:F:N-611:194.33:D N-611 PK 194.33: a 138 m de su carretera → a ella (al punto más cercano, 139 m)
  rumbo cruzado: dgtpdf:F:AC-221:2.55:C AC-221 rumbo 116.2 y su vía va a [356, 356] → 176.4
  su vía: dgtpdf:F:H-30:8.502:D H-30 PK 8.502: a 217 m de su carretera → a ella (al punto más cercano, 219 m)
  su vía: dgtpdf:F:A-7052:7.5:C A-7052 PK 7.5: a 141 m de su carretera → a ella (al punto más cercano, 142 m)
  su vía: dgtpdf:F:A-49:0.7:C A-49 PK 0.7: a 120 m de su carretera → a ella (al punto más cercano, 119 m)
  su vía: dgtpdf:F:A-8077:3.18:D A-8077 PK 3.18: a 72 m de su carretera → a ella (en su PK, 72 m)
  su vía: dgtpdf:F:N-234:119.66:D N-234 PK 119.66: a 185 m de su carretera → a ella (al punto más cercano, 185 m)
  su vía: sct:41.25502,1.17357 C-14 PK None: a 63 m de su carretera → a ella (al punto más cercano, 63 m)
  su vía: sct:41.74640,2.63225 C-35 PK None: a 140 m de su carretera → a ella (al punto más cercano, 141 m)
  su vía: sct:40.73027,0.59360 N-340 PK None: a 224 m de su carretera → a ella (al punto más cercano, 224 m)
  su vía: ansr:EN125:102:O EN125 PK 102.0: a 207 m de su carretera → a ella (al punto más cercano, 208 m)
  su vía: ansr:IC17:19.1:E IC17 PK 19.1: a 62 m de su carretera → a ella (al punto más cercano, 62 m)
  su vía: ansr:IC17:14.1:N IC17 PK 14.1: a 210 m de su carretera → a ella (al punto más cercano, 210 m)
  su vía: dgteq:AI-81:1.9:D:cintur AI-81 PK 1.9: a 62 m de su carretera → a ella (en su PK, 79 m)
  su vía: dgteq:A-492:0.2:C:cintur A-492 PK 0.2: a 171 m de su carretera → a ella (al punto más cercano, 172 m)
  su vía: dgteq:H-30:8.585:D:cintur H-30 PK 8.585: a 183 m de su carretera → a ella (al punto más cercano, 184 m)
  su vía: dgteq:N-550:116.74:D:cintur N-550 PK 116.74: a 81 m de su carretera → a ella (al punto más cercano, 81 m)
  su vía: dgteq:N-552:4.35:C:cintur N-552 PK 4.35: a 83 m de su carretera → a ella (al punto más cercano, 84 m)
  su vía: dgteq:PO-11:1.56:D:cintur PO-11 PK 1.56: a 146 m de su carretera → a ella (al punto más cercano, 146 m)
  su vía: dgteq:N-330:501.3:C:cintur N-330 PK 501.3: a 312 m de su carretera → a ella (al punto más cercano, 314 m)
  rumbo cruzado: com:euskadi-hondarribia-santaengrazi None rumbo 37.2 y su vía va a [153, 150, 156, 147] → None
  rumbo cruzado: osm:n992005494 None rumbo 244.5 y su vía va a [314, 314, 314, 314, 314, 314] → None
  rumbo cruzado: osm:n2334938864 None rumbo 235.6 y su vía va a [321, 142, 142, 140, 322, 140, 319] → None
  su vía: osm:n5435143134 A-26 PK None: a 70 m de su carretera → a ella (al punto más cercano, 71 m)
  rumbo cruzado: osm:n13070637359 None rumbo 22.2 y su vía va a [273, 92, 92, 273, 273, 92, 93, 144] → None
  rumbo cruzado: osm:n8119271103 None rumbo 293.6 y su vía va a [29, 31, 31, 30, 198] → None
  rumbo cruzado: osm:n13311195241b None rumbo 262.6 y su vía va a [32, 32, 32] → None
revisión final: 15 movidos a su cámara de OSM (estaban a más de 150 m de su PK y OSM la tiene en él); 29 llevados a su carretera; 16 con el rumbo cruzado corregido; 13 duplicados quitados: {'testigo': ['dgt:GUID_CABINACINEMOMETRO_120095', 'dgt:GUID_CABINACINEMOMETRO_120129', 'dgt:GUID_CABINACINEMOMETRO_120233', 'dgt:GUID_CABINACINEMOMETRO_120261', 'dgt:GUID_CABINACINEMOMETRO_120304', 'dgt:GUID_CABINACINEMOMETRO_120311', 'dgt:GUID_CABINACINEMOMETRO_120314', 'dgt:GUID_CABINACINEMOMETRO_120391', 'dgt:GUID_CABINACINEMOMETRO_120667', 'dgt:GUID_CABINACINEMOMETRO_160238', 'dgt:GUID_CABINACINEMOMETRO_165621', 'dgtpdf:F:CL-623:7.11:D', 'dgtpdf:F:M-300:31.325:D', 'dgtpdf:F:TF-66:9.0:D', 'dgtpdf:F:N-332:245.0:C'], 'su_via': ['dgt:GUID_CABINACINEMOMETRO_120010', 'dgt:GUID_CABINACINEMOMETRO_120011', 'dgt:GUID_CABINACINEMOMETRO_120133', 'dgt:GUID_CABINACINEMOMETRO_120140', 'dgt:GUID_CABINACINEMOMETRO_120203', 'dgt:GUID_CABINACINEMOMETRO_120204', 'dgt:GUID_CABINACINEMOMETRO_120601', 'dgt:GUID_CABINACINEMOMETRO_120651', 'dgt:GUID_CABINACINEMOMETRO_166987', 'dgtpdf:F:N-611:194.33:D', 'dgtpdf:F:H-30:8.502:D', 'dgtpdf:F:A-7052:7.5:C', 'dgtpdf:F:A-49:0.7:C', 'dgtpdf:F:A-8077:3.18:D', 'dgtpdf:F:N-234:119.66:D', 'sct:41.25502,1.17357', 'sct:41.74640,2.63225', 'sct:40.73027,0.59360', 'ansr:EN125:102:O', 'ansr:IC17:19.1:E', 'ansr:IC17:14.1:N', 'dgteq:AI-81:1.9:D:cintur', 'dgteq:A-492:0.2:C:cintur', 'dgteq:H-30:8.585:D:cintur', 'dgteq:N-550:116.74:D:cintur', 'dgteq:N-552:4.35:C:cintur', 'dgteq:PO-11:1.56:D:cintur', 'dgteq:N-330:501.3:C:cintur', 'osm:n5435143134'], 'cruzado': ['dgt:GUID_CABINACINEMOMETRO_120009', 'dgt:GUID_CABINACINEMOMETRO_120025', 'dgt:GUID_CABINACINEMOMETRO_120027', 'dgt:GUID_CABINACINEMOMETRO_120037', 'dgt:GUID_CABINACINEMOMETRO_120435', 'dgt:GUID_CABINACINEMOMETRO_163776', 'dgt:GUID_CABINACINEMOMETRO_165670', 'dgt:GUID_CABINACINEMOMETRO_165816', 'dgtpdf:F:CA-141:21.3:C', 'dgtpdf:F:AC-221:2.55:C', 'com:euskadi-hondarribia-santaengrazi', 'osm:n992005494', 'osm:n2334938864', 'osm:n13070637359', 'osm:n8119271103', 'osm:n13311195241b'], 'duplicados': ['dgt:GUID_CABINACINEMOMETRO_169360→dgt:GUID_CVM_161570', 'dgt:GUID_CABINACINEMOMETRO_169362→dgt:GUID_CVM_161588', 'dgt:GUID_CABINACINEMOMETRO_169364→dgt:GUID_CVM_161609', 'dgt:GUID_CABINACINEMOMETRO_169366→dgt:GUID_CVM_161629', 'dgt:GUID_CVM_164265→dgt:GUID_CVM_163929', 'dgt:GUID_CVM_165001→dgt:GUID_CVM_164999', 'dgt:GUID_CVM_165415→dgt:GUID_CVM_165414', 'dgt:GUID_CVM_169184→dgt:GUID_CVM_169183', 'osm:n13512708762→dgt:GUID_CABINACINEMOMETRO_120011', 'osm:n992001271→dgt:GUID_CABINACINEMOMETRO_120204', 'vdc:2→vdc:1', 'osm:n13070637359b→osm:n13070637359', 'osm:n13311195241b→osm:n13311195241']}
  caminos: red cargada (69993 vías) en 37s
  caminos: regla del lado probada en 37s
  caminos: regla del cruce probada en 37s
  caminos: 0/62 en 37s (dgt:GUID_CABINACINEMOMETRO_120602)
verificados: 96 comprobados sobre el terreno, todos en su sitio
  TCA: página del Ministerio no disponible (www.transportes.gob.es: HTTP Error 403: Forbidden); se usan los PDF conocidos
  TCA: TCA 130 filas (NOTA-TCA-2024-Para-Publicar-en-WEB%20%28105%29-Def.pdf)
  TCA: TCAM 21 filas (tca-con-implicacion-de-motoristas.pdf)
  CartoCiudad: 295 hitos necesarios, 0 por consultar
  TCA: 11 sin poder situar: ['B-24 9.6-10.7', 'B-40 1.4-2.1', 'GR-30 9.1-10.1', 'GR-30 10.1-10.6', 'N-240 19.0-19.5', 'N-332 216.3-217.3', 'N-340 1144.7-1145.2', 'N-340 1154.3-1154.8', 'N-340 1159.8-1160.3', 'N-349 2.7-3.2', 'N-351 5.9-6.5']
Ministerio: tramos de concentración de accidentes: 109 puntos
  CartoCiudad: 1877 hitos necesarios, 0 por consultar
  accidentes: 461 tramos, 426 situados, 35 sin poder situar
Tramos con muchos accidentes (autonómicas y provinciales, microdatos DGT): 426 puntos
  zonas: red cargada (501783 vías) para 529 zonas en 59s
```
