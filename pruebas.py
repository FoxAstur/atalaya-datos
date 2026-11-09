"""
Pruebas del recolector que no necesitan internet: la unión de radares de tramo de distintas fuentes, que es donde se
perdían (V-30, A-3, CL-613, LZ-67, N-320...). Se pasan antes de cada recogida:  python -m unittest pruebas -v
"""
import unittest

import recolector as r


def tramo(id_, f, la, lo, la2, lo2, **k):
    return {"id": id_, "t": "RADAR_TRAMO", "f": f, "la": la, "lo": lo, "la2": la2, "lo2": lo2, **k}


class Fusion(unittest.TestCase):
    def setUp(self):
        r.FUSION["absorbidos"].clear()

    def test_pdf_por_pk_toma_los_extremos_de_osm(self):
        # A-3 hacia Valencia: la salida situada por PK caía a 880 m de la cámara real
        pdf = tramo("dgtpdf:T:A-3:349.15:C", "PDF DGT", 39.479167, -0.470308, 39.474984, -0.439235, s="Creciente", c="A-3")
        osm = tramo("osm:r18845490", "OSM", 39.47886, -0.47176, 39.47841, -0.44830)
        out = r.fusionar([[pdf], [osm]])
        self.assertEqual(1, len(out))
        self.assertAlmostEqual(39.47841, out[0]["la2"], places=5)
        self.assertAlmostEqual(-0.44830, out[0]["lo2"], places=5)
        self.assertTrue(out[0]["_pos_osm"])

    def test_dos_tramos_de_osm_con_la_misma_entrada_y_distinta_salida_no_se_funden(self):
        a = tramo("osm:r1", "OSM", 29.01138, -13.73335, 28.99111, -13.74144)
        b = tramo("osm:r2", "OSM", 29.01138, -13.73335, 28.96000, -13.75600)
        self.assertEqual(2, len(r.fusionar([[b], [a]])))

    def test_calzadas_contrarias_no_se_funden(self):
        ida = tramo("dgt:GUID_CVM_1", "DGT", 42.2148, -4.8474, 42.1409, -4.6731)
        vuelta = tramo("osm:r3", "OSM", 42.2150, -4.8470, 42.3000, -5.0000)
        self.assertTrue(r.tramos_distintos(vuelta, ida))
        self.assertEqual(2, len(r.fusionar([[ida], [vuelta]])))

    def test_el_mismo_tramo_en_dos_fuentes_se_funde(self):
        of = tramo("dgt:GUID_CVM_2", "DGT", 42.54148, -5.73327, 42.55351, -5.71403)
        osm = tramo("osm:r4", "OSM", 42.54150, -5.73330, 42.55350, -5.71400)
        out = r.fusionar([[of], [osm]])
        self.assertEqual(1, len(out))
        self.assertTrue(r.osm_confirma(out[0]))

    def test_osm_no_confirma_un_tramo_al_reves(self):
        of = tramo("dgt:GUID_CVM_5", "DGT", 42.54148, -5.73327, 42.55351, -5.71403)
        of["_osm_tramos"] = [(42.55351, -5.71403, 42.54148, -5.73327, "osm:r9", {})]
        self.assertFalse(r.osm_confirma(of))


class Comprobacion(unittest.TestCase):
    def test_tramo_de_osm_cubierto_solo_en_su_sentido(self):
        r.TRAMOS_OSM_VISTOS.clear()
        r.TRAMOS_OSM_VISTOS["osm:r5"] = (40.57306, -3.05298, 40.58213, -3.08533)
        al_reves = [tramo("dgt:x", "DGT", 40.58213, -3.08533, 40.57306, -3.05298)]
        bien = [tramo("dgt:y", "DGT", 40.5731, -3.0531, 40.5820, -3.0850)]
        self.assertEqual(["osm:r5"], r.tramos_osm_sin_cubrir(al_reves))
        self.assertEqual([], r.tramos_osm_sin_cubrir(bien))
        r.TRAMOS_OSM_VISTOS.clear()


if __name__ == "__main__":
    unittest.main()
