# Datos de Atalaya

Versión: 2026-11-08T18:20:15+00:00 · Total: **5696** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 195 (5s)
- **DGT PDF cámaras**: ✅ 252 (2s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (0s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ✅ 3226 (74s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (3s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Câmara Municipal de Lisboa**: ✅ 18 (0s)
- **Ajuntament de Viladecans**: ✅ 24 (1s)
- **Portugal: ANSR (red SINCRO)**: ✅ 121 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Ayto. Pamplona cinemómetros**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1802 (0s)
- **Cámaras de stop y semáforo**: 100 cámaras de stop o semáforo llevadas a su línea de detención (140751 stops y semáforos de OSM)
- **Puntos comprobados**: ⚠️ 103 comprobados sobre el terreno; arreglados: osm:r9933664 (la2, lo2)
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 585 coinciden con los nuestros, 10 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 565/588 → se usa en 319 puntos y en 42 vigila los dos sentidos
- **Sentido de los radares de OSM**: 62 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
- **Sentido de los tramos de la DGT**: 36 de 52 tramos del feed de la DGT venían con la salida primero y se les ha dado la vuelta (comprobado con OSM/PDF: 15 a favor, 1 en contra)
- **Zonas de bajas emisiones**: ✅ 57
- **Situados por PK**: ✅ comprobado con 357 radares del feed (PK y coordenadas): en recta mediana 47 m, p75 93 m, p90 256 m; por la carretera mediana 34 m, p75 76 m, p90 247 m → 294 de 368 situados por PK recolocados por la carretera
- **Zonas de radar móvil por carretera**: 1139 de 1301 que venían en línea recta siguen ya la carretera (162 sin poder trazar)
- **Caminos de aproximación**: ✅ 3903 puntos con camino por su carretera, 317 de 347 tramos con recorrido real (28 sin vía cercana; 80s)
- **Sentido por el lado de la calle**: 285 puntos de calles de doble sentido y 29 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 39/42 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 94/117; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 1/2; dgtpdf ciudad 12-25 m: 3/5; dgtpdf carretera 25-41 m: 1/2; dgtpdf carretera 4-7 m: 1/1; dgtpdf carretera 7-12 m: 1/2; dgtpdf ciudad 7-12 m: 1/1; dgtpdf carretera todas: 4/7; dgtpdf ciudad todas: 4/6; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 94/120; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 154/200; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1. Pistas combinadas: limite 23/32; cruce+lado 1/2; cruce 33/42; lado+limite 8/9
- **Copias de OSM de radares oficiales**: 66 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 41/42 → heredado en 18; 8 radares del PDF de la DGT llevados a la posición de su copia de OSM
- **Radares viejos de OSM repetidos**: 4 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:n5744469677, osm:n7171815050, osm:n14169137330
- **Radares seguidos (mismo sentido, < 300 m)**: 72 pares por revisar: osm:n8281297753→osm:n3269210194 87 m; osm:n8081941155→osm:n8432725880 90 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; ansr:IC17:6.7:S→ansr:IC17:6.2:S 113 m; osm:n5308701907→osm:n245940388 120 m; ansr:IC17:7.4:N→ansr:IC17:6.7:N 121 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; osm:r20130852→osm:n9920942778 128 m; osm:n5764699427→osm:n6561635959 130 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 132 m; osm:n8432725876→osm:n8081941154 135 m; osm:n13170535898b→osm:n13170535897 139 m; osm:n13170535897b→osm:n13170535898 139 m; osm:n3269210194→osm:n8281297753 139 m; madzbe:40.4291,-3.7048→madzbe:40.4291,-3.7037 140 m; osm:n4388458815→osm:n682302418 141 m; osm:n13378565235→osm:n11223504291 142 m; osm:n8081941158→osm:n8158390898 143 m; osm:n8432725879→osm:n8081941158 144 m
- **Límites tomados de su vía**: 154 puestos, 5 quitados por no ser de su vía
- **Revisar**: nada sospechoso
- **Cámaras de semáforo**: comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 10 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 41 llevadas a su línea (7 estaban pasado el cruce); 40 sin ningún semáforo de OSM a 50 m (posición por revisar)
- **Sentido oficial (última comprobación)**: 934 con sentido oficial comprobable; 3 corregidos: dgt:GUID_CABINACINEMOMETRO_120602, dgt:GUID_CABINACINEMOMETRO_120603, dgt:GUID_CABINACINEMOMETRO_120647
- **Revisión final**: 15 movidos a su cámara de OSM (estaban a más de 150 m de su PK y OSM la tiene en él); 29 llevados a su carretera; 16 con el rumbo cruzado corregido; 16 duplicados quitados; 6 con el sentido sacado de los radares vecinos
- **Posición aproximada (solo PK)**: 348 puntos
- **Descartados por paso**: fusión de fuentes (mismo punto en otra fuente más fiable, < 60-300 m): 1646: com:euskadi-andoain-vitoria (comunitario), com:euskadi-egino-madrid (comunitario), com:euskadi-inicio-malmasin-can (comunitario), com:euskadi-inicio-malmasin-ss (comunitario), com:euskadi-tunel-malmasin-ss (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-0 (comunitario), com:leon-2026-11-02-gran-via-de-san-marcos-0 (comunitario), com:leon-2026-11-04-avenida-de-la-magdalena-0 (comunitario), com:leon-2026-11-04-calle-pendon-de-baeza-0 (comunitario), com:leon-2026-11-05-paseo-de-papalaguinda-0 (comunitario), com:leon-2026-11-05-paseo-de-papalaguinda-1 (comunitario), com:leon-2026-11-05-paseo-de-papalaguinda-2 (comunitario), com:leon-2026-11-05-paseo-de-papalaguinda-3 (comunitario), com:murcia-2026-10-26-avenida-miguel-ngel-blanco-santiago-el-mayor-0 (comunitario), com:murcia-2026-10-26-avenida-santa-catalina-santo-ngel-1 (comunitario), com:murcia-2026-10-26-avenida-santa-catalina-santo-ngel-2 (comunitario), com:osm-note-3967049 (comunitario), com:osm-note-3967053 (comunitario), com:sct_remolc-AP-7-129.5-2 (comunitario), com:sct_remolc-AP-7-83.95 (comunitario), dgt:GUID_CABINACINEMOMETRO_120193 (DGT), dgt:GUID_CABINACINEMOMETRO_120282 (DGT), dgt:GUID_CABINACINEMOMETRO_120283 (DGT), dgt:GUID_CABINACINEMOMETRO_120286 (DGT), dgt:GUID_CABINACINEMOMETRO_120301 (DGT), dgt:GUID_CABINACINEMOMETRO_120316 (DGT), dgt:GUID_CABINACINEMOMETRO_120336 (DGT), dgt:GUID_CABINACINEMOMETRO_120474 (DGT), dgt:GUID_CABINACINEMOMETRO_120476 (DGT), dgt:GUID_CABINACINEMOMETRO_120559 (DGT), dgt:GUID_CABINACINEMOMETRO_160988 (DGT), dgt:GUID_CABINACINEMOMETRO_160989 (DGT), dgt:GUID_CABINACINEMOMETRO_161529 (DGT), dgt:GUID_CABINACINEMOMETRO_163710 (DGT), dgt:GUID_CABINACINEMOMETRO_165204 (DGT), dgt:GUID_CABINACINEMOMETRO_165889 (DGT), dgt:GUID_CABINACINEMOMETRO_165891 (DGT), dgt:GUID_CABINACINEMOMETRO_165893 (DGT), dgt:GUID_CABINACINEMOMETRO_169363 (DGT), dgt:GUID_CABINACINEMOMETRO_169365 (DGT), dgt:GUID_CABINACINEMOMETRO_169367 (DGT), dgt:GUID_CABINACINEMOMETRO_169368 (DGT), dgt:GUID_CABINACINEMOMETRO_169369 (DGT), dgtpdf:F:A-6:7.75:D (PDF DGT), dgtpdf:F:A-7:568.028:D (PDF DGT), dgtpdf:F:MU-32:13.1:D (PDF DGT), dgtpdf:F:SE-30:11.114:D (PDF DGT), dgtpdf:T:TF-5:20.66:D (PDF DGT), lis:38.71656,-9.17549 (Lisboa), lis:38.74824,-9.12052 (Lisboa), mad:40.41664,-3.65930 (Madrid), mad:40.42619,-3.66006 (Madrid), mad:40.46715,-3.71445 (Madrid), mad:40.47934,-3.67429 (Madrid), madzbe:40.3486,-3.7040 (Madrid 2), madzbe:40.3621,-3.6938 (Madrid 2), madzbe:40.3662,-3.6048 (Madrid 2), madzbe:40.3662,-3.6049 (Madrid 2), madzbe:40.3664,-3.6047 (Madrid 2), madzbe:40.3739,-3.7705 (Madrid 2) … | correcciones, caducados y situados en otra provincia: 184: com:donostia_movil-2026-10-28-paseo-berio-0 (comunitario), com:donostia_movil-2026-10-28-paseo-berio-1 (comunitario), com:donostia_movil-2026-10-28-paseo-berio-2 (comunitario), com:donostia_movil-2026-10-28-paseo-berio-3 (comunitario), com:donostia_movil-2026-10-28-paseo-de-mons-0 (comunitario), com:donostia_movil-2026-10-28-paseo-de-mons-1 (comunitario), com:donostia_movil-2026-10-28-paseo-de-mons-2 (comunitario), com:donostia_movil-2026-10-28-paseo-doctor-begiristain-0 (comunitario), com:donostia_movil-2026-10-28-paseo-doctor-begiristain-1 (comunitario), com:donostia_movil-2026-10-28-paseo-doctor-begiristain-2 (comunitario), com:donostia_movil-2026-10-28-paseo-doctor-begiristain-3 (comunitario), com:donostia_movil-2026-11-04-avenida-de-ategorrieta-0 (comunitario), com:donostia_movil-2026-11-04-avenida-de-ategorrieta-1 (comunitario), com:donostia_movil-2026-11-04-avenida-de-ategorrieta-2 (comunitario), com:donostia_movil-2026-11-04-calle-peruene-0 (comunitario), com:donostia_movil-2026-11-04-paseo-de-otxoki-0 (comunitario), com:donostia_movil-2026-11-04-paseo-de-otxoki-1 (comunitario), com:donostia_movil-2026-11-04-paseo-de-otxoki-2 (comunitario), com:donostia_movil-2026-11-04-paseo-del-urumea-0 (comunitario), com:donostia_movil-2026-11-04-paseo-del-urumea-1 (comunitario), com:donostia_movil-2026-11-04-paseo-izostegi-0 (comunitario), com:donostia_movil-2026-11-04-paseo-izostegi-1 (comunitario), com:donostia_movil-2026-11-04-paseo-zorroaga-0 (comunitario), com:donostia_movil-2026-11-04-paseo-zorroaga-1 (comunitario), com:leon-2026-10-23-calle-riosol-0 (comunitario), com:leon-2026-10-23-calle-riosol-1 (comunitario), com:leon-2026-10-24-avenida-de-europa-0 (comunitario), com:leon-2026-10-24-avenida-de-europa-1 (comunitario), com:leon-2026-10-24-calle-campos-goticos-0 (comunitario), com:leon-2026-10-24-calle-campos-goticos-1 (comunitario), com:leon-2026-10-24-calle-campos-goticos-2 (comunitario), com:leon-2026-10-24-calle-general-gutierrez-mellado-0 (comunitario), com:leon-2026-10-24-calle-general-gutierrez-mellado-1 (comunitario), com:leon-2026-10-25-paseo-condesa-de-sagasta-0 (comunitario), com:leon-2026-10-25-paseo-condesa-de-sagasta-1 (comunitario), com:leon-2026-10-25-paseo-de-salamanca-0 (comunitario), com:leon-2026-10-25-paseo-de-salamanca-1 (comunitario), com:leon-2026-10-25-paseo-de-salamanca-2 (comunitario), com:leon-2026-10-25-paseo-de-salamanca-3 (comunitario), com:leon-2026-10-25-paseo-de-salamanca-4 (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-1 (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-2 (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-3 (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-4 (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-5 (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-6 (comunitario), com:leon-2026-11-02-avenida-de-los-peregrinos-7 (comunitario), com:leon-2026-11-02-avenida-san-ignacio-de-loyola-0 (comunitario), com:leon-2026-11-02-avenida-san-ignacio-de-loyola-1 (comunitario), com:leon-2026-11-02-calle-la-serna-0 (comunitario), com:leon-2026-11-02-calle-la-serna-1 (comunitario), com:leon-2026-11-02-calle-la-serna-2 (comunitario), com:leon-2026-11-02-calle-la-serna-3 (comunitario), com:leon-2026-11-02-gran-via-de-san-marcos-1 (comunitario), com:leon-2026-11-02-gran-via-de-san-marcos-2 (comunitario), com:leon-2026-11-03-avenida-reyes-leoneses-0 (comunitario), com:leon-2026-11-03-avenida-reyes-leoneses-1 (comunitario), com:leon-2026-11-03-avenida-reyes-leoneses-2 (comunitario), com:leon-2026-11-03-avenida-reyes-leoneses-3 (comunitario), com:leon-2026-11-03-n-601-0 (comunitario) … | copias de OSM de radares oficiales (misma calle y sentido, < 450 m): 66: osm:n10182984432 (OSM), osm:n1039703176 (OSM), osm:n10635057610 (OSM), osm:n10889039647 (OSM), osm:n11056291674 (OSM), osm:n11223504298 (OSM), osm:n1140674451 (OSM), osm:n12380371853 (OSM), osm:n12640711390 (OSM), osm:n12670697283 (OSM), osm:n12697311017 (OSM), osm:n12839568988 (OSM), osm:n13162470760 (OSM), osm:n13287299934 (OSM), osm:n13363143074 (OSM), osm:n13375582777 (OSM), osm:n13378056778 (OSM), osm:n13381607998 (OSM), osm:n13504941198 (OSM), osm:n13514069079 (OSM), osm:n13524206072b (OSM), osm:n13593596480 (OSM), osm:n13620008764 (OSM), osm:n14192164590 (OSM), osm:n1760285628 (OSM), osm:n21473125 (OSM), osm:n2334938812 (OSM), osm:n2334938925b (OSM), osm:n2378266572 (OSM), osm:n2378266977 (OSM), osm:n290930221 (OSM), osm:n3202405846 (OSM), osm:n3368363707 (OSM), osm:n3398522973 (OSM), osm:n3580983610 (OSM), osm:n3714381772 (OSM), osm:n393808999 (OSM), osm:n4139225820 (OSM), osm:n4587398829 (OSM), osm:n4838340298 (OSM), osm:n4913375355 (OSM), osm:n5761837916 (OSM), osm:n6680005633 (OSM), osm:n6926374946 (OSM), osm:n7024118307 (OSM), osm:n7157495257 (OSM), osm:n7541702987 (OSM), osm:n8974875727 (OSM), osm:n8974875728 (OSM), osm:n9015262314 (OSM), osm:n914385003 (OSM), osm:n9212434658 (OSM), osm:n9238909853 (OSM), osm:n992000728 (OSM), osm:n992001543 (OSM), osm:n992001615 (OSM), osm:n992001915 (OSM), osm:n992003532 (OSM), osm:n992004415 (OSM), osm:n992004682 (OSM) … | unir tramos (cámara de entrada o salida de un tramo): 19: ansr:A1:217.4:N (ANSR), ansr:A29:47.3:N (ANSR), ansr:A3:38.1:S (ANSR), dgt:GUID_CABINACINEMOMETRO_120674 (DGT), dgt:GUID_CABINACINEMOMETRO_165910 (DGT), dgt:GUID_CABINACINEMOMETRO_165911 (DGT), dgt:GUID_CABINACINEMOMETRO_169359 (DGT), dgt:GUID_CABINACINEMOMETRO_175020 (DGT), osm:n12066644037 (OSM), osm:n12066644038 (OSM), osm:n2378266603 (OSM), osm:r17488225 (OSM), osm:r17488226 (OSM), vdc:23 (Viladecans), vdc:24 (Viladecans), vdc:25 (Viladecans), vdc:26 (Viladecans), vdc:27 (Viladecans), vdc:28 (Viladecans) | revisión final (duplicados) y comprobados: 16: dgt:GUID_CABINACINEMOMETRO_169360 (DGT), dgt:GUID_CABINACINEMOMETRO_169362 (DGT), dgt:GUID_CABINACINEMOMETRO_169364 (DGT), dgt:GUID_CABINACINEMOMETRO_169366 (DGT), dgt:GUID_CVM_164265 (DGT), dgt:GUID_CVM_165001 (DGT), dgt:GUID_CVM_165415 (DGT), dgt:GUID_CVM_169184 (DGT), osm:n13070637359b (OSM), osm:n13311195241b (OSM), osm:n13512708762 (OSM), osm:n4587378949 (OSM), osm:n7655766543 (OSM), osm:n806985872 (OSM), osm:n992001271 (OSM), vdc:2 (Viladecans) | unir tramos tras orientarlos: 14: osm:r13040121 (OSM), osm:r14170001 (OSM), osm:r15974337 (OSM), osm:r16567705 (OSM), osm:r17135243 (OSM), osm:r1907383 (OSM), osm:r19366197 (OSM), osm:r19947241 (OSM), osm:r20142909 (OSM), osm:r20171243 (OSM), osm:r20181703 (OSM), osm:r20183369 (OSM), osm:r7431334 (OSM), osm:r8812728 (OSM) | radares viejos de OSM repetidos: 4: osm:n1123913886 (OSM), osm:n14169137330 (OSM), osm:n5744469677 (OSM), osm:n7171815050 (OSM)
- **Ministerio: tramos de concentración de accidentes**: ✅ 109 (24s); trazados por la carretera 419 de 528
- **Tramos con muchos accidentes (autonómicas y provinciales, microdatos DGT)**: ✅ 425 (0s)

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil | Accidentes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Andalucía | 294 | 42 | 22 | 0 | 65 | 231 | 65 |
| Aragón | 95 | 5 | 0 | 0 | 17 | 109 | 1 |
| Canarias | 51 | 13 | 2 | 0 | 0 | 68 | 90 |
| Cantabria | 16 | 4 | 2 | 0 | 3 | 27 | 3 |
| Castilla y León | 214 | 54 | 34 | 0 | 32 | 293 | 3 |
| Castilla-La Mancha | 102 | 21 | 12 | 1 | 33 | 152 | 1 |
| Cataluña | 502 | 69 | 68 | 0 | 3 | 66 | 4 |
| Comunidad de Madrid | 153 | 28 | 66 | 1 | 304 | 59 | 80 |
| Comunidad Foral de Navarra | 37 | 2 | 1 | 0 | 2 | 37 | 3 |
| Comunitat Valenciana | 157 | 22 | 8 | 2 | 46 | 80 | 53 |
| Extremadura | 56 | 6 | 2 | 0 | 5 | 86 | 0 |
| Galicia | 127 | 24 | 7 | 0 | 31 | 128 | 20 |
| Illes Balears | 83 | 9 | 0 | 0 | 2 | 38 | 41 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 | 1 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 210 | 2 | 9 | 0 | 0 | 0 | 47 |
| Portugal | 268 | 33 | 8 | 0 | 0 | 0 | 0 |
| Principado de Asturias | 77 | 13 | 8 | 0 | 7 | 32 | 8 |
| Región de Murcia | 20 | 4 | 0 | 0 | 5 | 67 | 5 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 | 109 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2718**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1707
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1140
- ACCIDENTES_DGT: 425
- AYUNTAMIENTO: 422
- SCT: 279
- AUTONOMICA: 209
- MINISTERIO: 109
- POLICIA_LOCAL: 66
- MULTAS: 33

## Registro

```
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
  su vía: dgt:GUID_CABINACINEMOMETRO_120133 N-232 PK 293.875: a 269 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 270 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120140 N-211 PK 228.153: a 213 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 214 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120203 N-330 PK 670.101: a 9999 m de su carretera → a ella (en su PK, 572 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120204 N-330 PK 671.745: a 407 m de su carretera → a ella (en su PK, 486 m)
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_120435 AC-552 rumbo 195.2 y su vía va a [124, 136, 131] → 135.8
  su vía: dgt:GUID_CABINACINEMOMETRO_120601 CV-91 PK 18.888: a 266 m de su carretera → a ella (en su PK, 278 m)
  su vía: dgt:GUID_CABINACINEMOMETRO_120651 MA-19 PK 30.125: a 74 m de su carretera → a ella (en su PK, 76 m)
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_163776 N-6 rumbo 114.5 y su vía va a [206, 205, 206, 205, 206] → None
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_165670 AC-862 rumbo 84.1 y su vía va a [154] → 154.3
  rumbo cruzado: dgt:GUID_CABINACINEMOMETRO_165816 VG-4.4 rumbo 249.8 y su vía va a [306] → 306.4
  su vía: dgt:GUID_CABINACINEMOMETRO_166987 A-68 PK 246.017: a 172 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 276 m)
  rumbo cruzado: dgtpdf:F:CA-141:21.3:C CA-141 rumbo 114.2 y su vía va a [178, 184, 168] → 168.3
  su vía: dgtpdf:F:N-611:194.33:D N-611 PK 194.33: a 138 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 139 m)
  rumbo cruzado: dgtpdf:F:AC-221:2.55:C AC-221 rumbo 116.2 y su vía va a [356, 356] → 176.4
  su vía: dgtpdf:F:H-30:8.502:D H-30 PK 8.502: a 217 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 219 m)
  su vía: dgtpdf:F:A-7052:7.5:C A-7052 PK 7.5: a 141 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 168 m)
  su vía: dgtpdf:F:A-49:0.7:C A-49 PK 0.7: a 120 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 134 m)
  su vía: dgtpdf:F:A-8077:3.18:D A-8077 PK 3.18: a 72 m de su carretera → a ella (en su PK, 72 m)
  su vía: dgtpdf:F:N-234:119.66:D N-234 PK 119.66: a 185 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 185 m)
  su vía: sct:41.25502,1.17357 C-14 PK 20.029: a 63 m de su carretera → a ella (en su PK, 166 m)
  su vía: sct:41.74640,2.63225 C-35 PK 69.887: a 140 m de su carretera → a ella (en su PK, 146 m)
  su vía: sct:40.73027,0.59360 N-340 PK 1084.318: a 224 m de su carretera → a ella (en su PK, 261 m)
  su vía: ansr:EN125:102:O EN125 PK 102.0: a 207 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 208 m)
  su vía: ansr:IC17:19.1:E IC17 PK 19.1: a 62 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 134 m)
  su vía: ansr:IC17:14.1:N IC17 PK 14.1: a 210 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 210 m)
  su vía: dgteq:AI-81:1.9:D:cintur AI-81 PK 1.9: a 62 m de su carretera → a ella (en su PK, 62 m)
  su vía: dgteq:A-492:0.2:C:cintur A-492 PK 0.2: a 171 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 172 m)
  su vía: dgteq:H-30:8.585:D:cintur H-30 PK 8.585: a 183 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 184 m)
  su vía: dgteq:N-550:116.74:D:cintur N-550 PK 116.74: a 81 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 81 m)
  su vía: dgteq:N-552:4.35:C:cintur N-552 PK 4.35: a 83 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 84 m)
  su vía: dgteq:PO-11:1.56:D:cintur PO-11 PK 1.56: a 146 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 146 m)
  su vía: dgteq:N-330:501.3:C:cintur N-330 PK 501.3: a 312 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 315 m)
  rumbo cruzado: com:euskadi-hondarribia-santaengrazi None rumbo 37.2 y su vía va a [153, 150, 156, 147] → None
  rumbo cruzado: osm:n992005494 None rumbo 244.5 y su vía va a [314, 314, 314, 314, 314, 314] → None
  rumbo cruzado: osm:n2334938864 None rumbo 235.6 y su vía va a [321, 142, 142, 140, 322, 140, 319] → None
  su vía: osm:n5435143134 A-26 PK None: a 70 m de su carretera → a ella (al punto más cercano de la calzada de su sentido, 71 m)
  rumbo cruzado: osm:n13070637359 None rumbo 22.2 y su vía va a [273, 92, 92, 273, 273, 92, 93, 144] → None
  rumbo cruzado: osm:n8119271103 None rumbo 293.6 y su vía va a [29, 31, 31, 30, 198] → None
  rumbo cruzado: osm:n13311195241b None rumbo 262.6 y su vía va a [32, 32, 32] → None
  rumbo por los vecinos: dgt:GUID_CABINACINEMOMETRO_120318 A-2 PK 122.0 Decreciente → 234.5
  rumbo por los vecinos: dgt:GUID_CABINACINEMOMETRO_120331 AP-6 PK 53.126 Creciente → 328.4
  rumbo por los vecinos: dgt:GUID_CABINACINEMOMETRO_165908 N-320 PK 264.11 Creciente → 31.0
  rumbo por los vecinos: dgt:GUID_CABINACINEMOMETRO_165909 N-320 PK 263.933 Decreciente → 114.2
  rumbo por los vecinos: dgt:GUID_CABINACINEMOMETRO_174089 N-125 PK 7.771 Decreciente → 284.7
  rumbo por los vecinos: dgteq:A-68:242.23:C:cintur A-68 PK 242.23 Creciente → 348.5
revisión final: 15 movidos a su cámara de OSM (estaban a más de 150 m de su PK y OSM la tiene en él); 29 llevados a su carretera; 16 con el rumbo cruzado corregido; 16 duplicados quitados; 6 con el sentido sacado de los radares vecinos: {'testigo': ['dgt:GUID_CABINACINEMOMETRO_120095', 'dgt:GUID_CABINACINEMOMETRO_120129', 'dgt:GUID_CABINACINEMOMETRO_120233', 'dgt:GUID_CABINACINEMOMETRO_120261', 'dgt:GUID_CABINACINEMOMETRO_120304', 'dgt:GUID_CABINACINEMOMETRO_120311', 'dgt:GUID_CABINACINEMOMETRO_120314', 'dgt:GUID_CABINACINEMOMETRO_120391', 'dgt:GUID_CABINACINEMOMETRO_120667', 'dgt:GUID_CABINACINEMOMETRO_160238', 'dgt:GUID_CABINACINEMOMETRO_165621', 'dgtpdf:F:CL-623:7.11:D', 'dgtpdf:F:M-300:31.325:D', 'dgtpdf:F:TF-66:9.0:D', 'dgtpdf:F:N-332:245.0:C'], 'su_via': ['dgt:GUID_CABINACINEMOMETRO_120010', 'dgt:GUID_CABINACINEMOMETRO_120011', 'dgt:GUID_CABINACINEMOMETRO_120133', 'dgt:GUID_CABINACINEMOMETRO_120140', 'dgt:GUID_CABINACINEMOMETRO_120203', 'dgt:GUID_CABINACINEMOMETRO_120204', 'dgt:GUID_CABINACINEMOMETRO_120601', 'dgt:GUID_CABINACINEMOMETRO_120651', 'dgt:GUID_CABINACINEMOMETRO_166987', 'dgtpdf:F:N-611:194.33:D', 'dgtpdf:F:H-30:8.502:D', 'dgtpdf:F:A-7052:7.5:C', 'dgtpdf:F:A-49:0.7:C', 'dgtpdf:F:A-8077:3.18:D', 'dgtpdf:F:N-234:119.66:D', 'sct:41.25502,1.17357', 'sct:41.74640,2.63225', 'sct:40.73027,0.59360', 'ansr:EN125:102:O', 'ansr:IC17:19.1:E', 'ansr:IC17:14.1:N', 'dgteq:AI-81:1.9:D:cintur', 'dgteq:A-492:0.2:C:cintur', 'dgteq:H-30:8.585:D:cintur', 'dgteq:N-550:116.74:D:cintur', 'dgteq:N-552:4.35:C:cintur', 'dgteq:PO-11:1.56:D:cintur', 'dgteq:N-330:501.3:C:cintur', 'osm:n5435143134'], 'cruzado': ['dgt:GUID_CABINACINEMOMETRO_120009', 'dgt:GUID_CABINACINEMOMETRO_120025', 'dgt:GUID_CABINACINEMOMETRO_120027', 'dgt:GUID_CABINACINEMOMETRO_120037', 'dgt:GUID_CABINACINEMOMETRO_120435', 'dgt:GUID_CABINACINEMOMETRO_163776', 'dgt:GUID_CABINACINEMOMETRO_165670', 'dgt:GUID_CABINACINEMOMETRO_165816', 'dgtpdf:F:CA-141:21.3:C', 'dgtpdf:F:AC-221:2.55:C', 'com:euskadi-hondarribia-santaengrazi', 'osm:n992005494', 'osm:n2334938864', 'osm:n13070637359', 'osm:n8119271103', 'osm:n13311195241b'], 'duplicados': ['dgt:GUID_CABINACINEMOMETRO_169360→dgt:GUID_CVM_161570', 'dgt:GUID_CABINACINEMOMETRO_169362→dgt:GUID_CVM_161588', 'dgt:GUID_CABINACINEMOMETRO_169364→dgt:GUID_CVM_161609', 'dgt:GUID_CABINACINEMOMETRO_169366→dgt:GUID_CVM_161629', 'dgt:GUID_CVM_164265→dgt:GUID_CVM_163929', 'dgt:GUID_CVM_165001→dgt:GUID_CVM_164999', 'dgt:GUID_CVM_165415→dgt:GUID_CVM_165414', 'dgt:GUID_CVM_169184→dgt:GUID_CVM_169183', 'osm:n13512708762→dgt:GUID_CABINACINEMOMETRO_120011', 'osm:n992001271→dgt:GUID_CABINACINEMOMETRO_120204', 'osm:n806985872→dgtpdf:F:A-49:0.7:C', 'osm:n4587378949→sct:41.25502,1.17357', 'osm:n7655766543→sct:41.74640,2.63225', 'vdc:2→vdc:1', 'osm:n13070637359b→osm:n13070637359', 'osm:n13311195241b→osm:n13311195241'], 'vecinos': ['dgt:GUID_CABINACINEMOMETRO_120318', 'dgt:GUID_CABINACINEMOMETRO_120331', 'dgt:GUID_CABINACINEMOMETRO_165908', 'dgt:GUID_CABINACINEMOMETRO_165909', 'dgt:GUID_CABINACINEMOMETRO_174089', 'dgteq:A-68:242.23:C:cintur']}
  caminos: red cargada (71591 vías) en 21s
  caminos: regla del lado probada en 21s
  caminos: regla del cruce probada en 21s
  caminos: 0/68 en 21s (dgt:GUID_CABINACINEMOMETRO_120602)
verificados: 103 comprobados sobre el terreno, todos en su sitio
  TCA: página del Ministerio no disponible (www.transportes.gob.es: HTTP Error 403: Forbidden); se usan los PDF conocidos
  TCA: TCA 130 filas (NOTA-TCA-2024-Para-Publicar-en-WEB%20%28105%29-Def.pdf)
  TCA: TCAM 21 filas (tca-con-implicacion-de-motoristas.pdf)
  CartoCiudad: 295 hitos necesarios, 0 por consultar
  TCA: 11 sin poder situar: ['B-24 9.6-10.7', 'B-40 1.4-2.1', 'GR-30 9.1-10.1', 'GR-30 10.1-10.6', 'N-240 19.0-19.5', 'N-332 216.3-217.3', 'N-340 1144.7-1145.2', 'N-340 1154.3-1154.8', 'N-340 1159.8-1160.3', 'N-349 2.7-3.2', 'N-351 5.9-6.5']
Ministerio: tramos de concentración de accidentes: 109 puntos
  CartoCiudad: 1877 hitos necesarios, 0 por consultar
  accidentes: 461 tramos, 425 situados, 36 sin poder situar
Tramos con muchos accidentes (autonómicas y provinciales, microdatos DGT): 425 puntos
  zonas: red cargada (501709 vías) para 528 zonas en 35s
```

## Auditoría automática

159 avisos (31 graves) en 3669 radares y cámaras; sin_su_carretera 47, pk_lejos 38, tramo_raro 25, duplicado 17, fuera_de_via 16, camino_incoherente 5, rumbo_cruzado 3, salida_otra_via 3, sentido_dudoso 3, contra_direccion 1, salida_fuera_de_via 1. Detalle en AUDITORIA.md
