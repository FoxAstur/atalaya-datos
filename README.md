# atalaya-datos

Radares y cámaras de control de tráfico de España en un único fichero, regenerado cada día por GitHub Actions
para la app [Atalaya](https://github.com/FoxAstur/atalaya).

- `datos/radares.json`: todos los puntos (formato compacto que lee la app).
- `datos/INFORME.md`: recuento por comunidad y tipo, estado de cada fuente y registro de la última ejecución.

## Fuentes

| Fuente | Qué aporta |
|---|---|
| DGT, feed DATEX II (Punto de Acceso Nacional) | Radares fijos y de tramo con coordenadas oficiales |
| DGT, PDF "Puntos y tramos de control de velocidad" | Fijos y tramos que falten en el feed, longitud de los tramos |
| DGT, PDF "Equipos automáticos de detección de infracciones" | Cámaras de cinturón/móvil, línea continua, foto-rojo, video-stop |
| CartoCiudad (IGN/CNIG, CC BY 4.0) | Posición por carretera + punto kilométrico; municipio y provincia |
| Servei Català de Trànsit | Radares fijos de Cataluña |
| Ayuntamiento de Madrid | Radares municipales de Madrid |
| Ayuntamiento de València | Cabinas de radar anunciadas |
| OpenStreetMap (© colaboradores, ODbL) | Radares municipales, País Vasco, semáforos, stop/ceda, tramos, límites de velocidad |
| [radares-datos](https://github.com/secretariacyas-crypto/radares-datos) | Tramos de vigilancia con radar móvil geolocalizados |
| Ayuntamiento de Madrid | Foto-rojo y cámaras de acceso a la ZBE y a la ZBEDEP Distrito Centro |
| Ayuntamiento de Málaga | Foto-rojo (CC BY 4.0) |
| Ayuntamiento de Salamanca | Radares fijos y de tramo municipales |
| Ayuntamiento de Donostia / San Sebastián | Radares fijos municipales |
| ANSR, portal «Radares à vista» (Portugal) | Radares SINCRO oficiales de Portugal: coordenadas, carretera, PK, límite y sentido |
| Câmara Municipal de Lisboa (dados.gov.pt) | Radares municipales de Lisboa |
| Ajuntament de Viladecans (geoportal) | Cabinas de radar y fotorrojos municipales |
| Prensa y avisos municipales (`correcciones.json`, a mano) | Foto-stop de Burjassot y Vinalesa y otras cámaras que no publica nadie en datos abiertos |
| Ayuntamientos de Santa Cruz de Tenerife y Pamplona | Foto-rojo y cinemómetros (cuando responden desde fuera de España) |
| [radares-anunciados](https://github.com/GeiserX/radares-anunciados-ha) (ODbL) | Gobierno Vasco (cabinas y tramos), Navarra, radares móviles anunciados por las Policías Locales de Murcia, León y Donostia, puntos habituales de radar móvil deducidos de las multas de Madrid y Barcelona, remolques del SCT y tramos INVIVE de la DGT |

Los datos derivados de OpenStreetMap se distribuyen bajo ODbL.
