// Pinta el estilo de Atalaya sobre el mapa propio (espana.pmtiles servido en local por «pmtiles serve») en varios
// sitios, para revisarlo sin el móvil. Salida: vista_mapa/salida/*.png
import { chromium } from "playwright";
import { readFileSync, mkdirSync } from "fs";
const salida = "vista_mapa/salida"; mkdirSync(salida, { recursive: true });
const SITIOS = [
  ["espana", [-3.7, 40.2], 5.2, 0], ["valencia", [-0.376, 39.47], 14.5, 0], ["oviedo", [-5.845, 43.362], 13, 0],
  ["huerna", [-5.84, 43.02], 12, 0], ["palma", [2.65, 39.57], 13, 0], ["tenerife", [-16.55, 28.3], 9.5, 0],
  ["a7-3d", [-0.33, 39.61], 16.5, 60], ["ceuta", [-5.31, 35.888], 14, 0],
];
const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
pagina.on("console", (m) => console.log("consola:", m.text()));
await pagina.setContent(`<!doctype html><html><head>
<link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<style>html,body,#m{margin:0;height:100%}</style></head><body><div id="m"></div></body></html>`);
await pagina.waitForFunction(() => window.maplibregl);
for (const modo of ["dia", "noche"]) {
  const estilo = JSON.parse(readFileSync(`vista_mapa/atalaya-${modo}.json`, "utf8"));
  estilo.sources.openmaptiles = { type: "vector", tiles: ["http://localhost:8080/espana/{z}/{x}/{y}.mvt"], maxzoom: 14,
    attribution: "© OpenStreetMap" };
  delete estilo.sources.relieve; estilo.layers = estilo.layers.filter((l) => l.source !== "relieve");
  await pagina.evaluate(async (e) => {
    if (window.mapa) window.mapa.remove();
    window.mapa = new maplibregl.Map({ container: "m", style: e, center: [-3.7, 40.2], zoom: 5, preserveDrawingBuffer: true, attributionControl: false });
    await new Promise((r) => window.mapa.once("load", r));
  }, estilo);
  for (const [nombre, centro, zoom, pitch] of SITIOS) {
    if (modo === "noche" && !["valencia", "a7-3d", "huerna"].includes(nombre)) continue;
    await pagina.evaluate(async ([c, z, p]) => { window.mapa.jumpTo({ center: c, zoom: z, pitch: p, bearing: p ? 20 : 0 });
      await new Promise((r) => window.mapa.once("idle", () => r(true))); }, [centro, zoom, pitch]);
    await pagina.waitForTimeout(800);
    await pagina.screenshot({ path: `${salida}/${nombre}-${modo}.png` });
    console.log("hecho", nombre, modo);
  }
}
await navegador.close();
