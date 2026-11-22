// Pinta el estilo de Atalaya sobre el mapa propio (espana.pmtiles servido en local por «pmtiles serve») en varios
// sitios, para revisarlo sin el móvil. Salida: vista_mapa/salida/*.png
import { chromium } from "playwright";
import { readFileSync, mkdirSync } from "fs";
const salida = "vista_mapa/salida"; mkdirSync(salida, { recursive: true });
const SITIOS = [
  ["espana", [-3.7, 40.2], 5.2, 0], ["valencia", [-0.376, 39.47], 14.5, 0], ["oviedo", [-5.845, 43.362], 13, 0],
  ["huerna", [-5.84, 43.02], 12, 0], ["palma", [2.65, 39.57], 13, 0], ["tenerife", [-16.55, 28.3], 9.5, 0],
  ["a7-3d", [-0.33, 39.61], 16.5, 60], ["ceuta", [-5.31, 35.888], 14, 0],
  ["ruzafa-limites", [-0.3745, 39.4625], 16.5, 0], ["gijon", [-5.665, 43.538], 15, 0], ["picos-europa", [-4.85, 43.19], 11.5, 0],
  ["aeropuerto-vlc", [-0.4815, 39.4893], 12.5, 0], ["pirineo", [0.65, 42.65], 11, 0], ["barcelona", [2.17, 41.39], 13, 0],
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
  if (estilo.sources.atalaya) estilo.sources.atalaya = { type: "vector", tiles: ["http://localhost:8080/extras/{z}/{x}/{y}.mvt"], maxzoom: 14 };
  await pagina.evaluate(async (e) => {
    if (window.mapa) window.mapa.remove();
    window.mapa = new maplibregl.Map({ container: "m", style: e, center: [-3.7, 40.2], zoom: 5, preserveDrawingBuffer: true, attributionControl: false });
    // las señales de límite (en la app las dibuja Kotlin): círculo blanco con borde rojo y el número
    window.mapa.on("styleimagemissing", (ev) => {
      const m = /^lim-(\d+)$/.exec(ev.id); if (!m) return;
      const t = 64, cv = document.createElement("canvas"); cv.width = t; cv.height = t; const g = cv.getContext("2d");
      g.beginPath(); g.arc(t / 2, t / 2, t / 2 - 1, 0, 7); g.fillStyle = "#fff"; g.fill();
      g.lineWidth = t * 0.11; g.strokeStyle = "#C8102E"; g.beginPath(); g.arc(t / 2, t / 2, t / 2 - t * 0.09, 0, 7); g.stroke();
      g.fillStyle = "#111"; g.font = `bold ${m[1].length > 2 ? t * 0.34 : t * 0.42}px sans-serif`; g.textAlign = "center"; g.textBaseline = "middle";
      g.fillText(m[1], t / 2, t / 2 + 2);
      window.mapa.addImage(ev.id, g.getImageData(0, 0, t, t), { pixelRatio: 2 });
    });
    await new Promise((r) => window.mapa.once("load", r));
  }, estilo);
  for (const [nombre, centro, zoom, pitch] of SITIOS) {
    if (modo === "noche" && !["valencia", "a7-3d", "huerna", "ruzafa-limites"].includes(nombre)) continue;
    await pagina.evaluate(async ([c, z, p]) => { window.mapa.jumpTo({ center: c, zoom: z, pitch: p, bearing: p ? 20 : 0 });
      await new Promise((r) => window.mapa.once("idle", () => r(true))); }, [centro, zoom, pitch]);
    await pagina.waitForTimeout(800);
    await pagina.screenshot({ path: `${salida}/${nombre}-${modo}.png` });
    console.log("hecho", nombre, modo);
  }
}
await navegador.close();
