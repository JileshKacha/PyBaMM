#
# Tests for the base model class
#
import pybamm
import unittest


class TestGeometry1DMacro(unittest.TestCase):
    def test_add_custom_geometry(self):
        geometry = pybamm.Geometry1DMacro()
        whole_cell = ["negative electrode", "separator", "positive electrode"]
        x = pybamm.SpatialVariable("x", whole_cell)
        custom_geometry = {
            "negative electrode": {
                x: {"min": pybamm.Scalar(1), "max": pybamm.Scalar(2)}
            }
        }
        geometry.update(custom_geometry)
        self.assertEqual(
            geometry["negative electrode"], custom_geometry["negative electrode"]
        )

    def test_geometry_keys(self):
        geometry = pybamm.Geometry1DMacro()
        for prim_sec_vars in geometry.values():
            spatial_vars = prim_sec_vars["primary"]
            all(
                self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                for spatial_var in spatial_vars.keys()
            )


class TestGeometry1DMicro(unittest.TestCase):
    def test_add_custom_geometry(self):
        geometry = pybamm.Geometry1DMicro()
        whole_cell = ["negative electrode", "separator", "positive electrode"]
        x = pybamm.SpatialVariable("x", whole_cell)
        custom_geometry = {}
        custom_geometry["negative electrode"] = {
            "primary": {x: {"min": pybamm.Scalar(1), "max": pybamm.Scalar(2)}}
        }
        geometry.update(custom_geometry)

        self.assertEqual(
            geometry["negative electrode"], custom_geometry["negative electrode"]
        )

    def test_geometry_keys(self):
        geometry = pybamm.Geometry1DMicro()
        for prim_sec_vars in geometry.values():
            for spatial_vars in prim_sec_vars.values():
                all(
                    self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                    for spatial_var in spatial_vars.keys()
                )


class TestGeometry3DMacro(unittest.TestCase):
    def test_add_custom_geometry(self):
        geometry = pybamm.Geometry3DMacro()
        whole_cell = ["negative electrode", "separator", "positive electrode"]
        x = pybamm.SpatialVariable("x", whole_cell)
        custom_geometry = {
            "negative electrode": {
                "primary": {x: {"min": pybamm.Scalar(1), "max": pybamm.Scalar(2)}}
            }
        }

        geometry.update(custom_geometry)
        self.assertEqual(
            geometry["negative electrode"], custom_geometry["negative electrode"]
        )

    def test_geometry_keys(self):
        geometry = pybamm.Geometry3DMacro()
        for prim_sec_vars in geometry.values():
            for spatial_vars in prim_sec_vars.values():
                all(
                    self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                    for spatial_var in spatial_vars.keys()
                )


class TestGeometry1p1DMacro(unittest.TestCase):
    def test_geometry_keys(self):
        geometry = pybamm.Geometryxp1DMacro(cc_dimension=1)
        for key, prim_sec_vars in geometry.items():
            self.assertIn("primary", prim_sec_vars.keys())
            if key != "current collector":
                self.assertIn("secondary", prim_sec_vars.keys())
                var = pybamm.standard_spatial_vars
                self.assertEqual(
                    list(prim_sec_vars["secondary"].keys())[0].id, var.z.id
                )
            for spatial_vars in prim_sec_vars.values():
                all(
                    self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                    for spatial_var in spatial_vars.keys()
                    if spatial_var not in ["negative", "positive"]
                )


class TestGeometry2p1DMacro(unittest.TestCase):
    def test_geometry_keys(self):
        geometry = pybamm.Geometryxp1DMacro(cc_dimension=2)
        for key, prim_sec_vars in geometry.items():
            self.assertIn("primary", prim_sec_vars.keys())
            if key != "current collector":
                self.assertIn("secondary", prim_sec_vars.keys())
                var = pybamm.standard_spatial_vars
                self.assertIn(var.y, prim_sec_vars["secondary"].keys())
                self.assertIn(var.z, prim_sec_vars["secondary"].keys())

            for spatial_vars in prim_sec_vars.values():
                all(
                    self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                    for spatial_var in spatial_vars.keys()
                    if spatial_var not in ["negative", "positive"]
                )

        def test_init_failure(self):
            with self.assertRaises(pybamm.GeometryError):
                pybamm.Geometryxp1DMacro(cc_dimension=3)


class TestGeometry1p1DMicro(unittest.TestCase):
    def test_geometry_keys(self):
        geometry = pybamm.Geometry1p1DMicro()
        for prim_sec_vars in geometry.values():
            for spatial_vars in prim_sec_vars.values():
                all(
                    self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                    for spatial_var in spatial_vars.keys()
                )


class TestGeometryxp0p1DMicro(unittest.TestCase):
    def test_geometry_keys(self):
        for cc_dimension in [1, 2]:
            geometry = pybamm.Geometryxp0p1DMicro(cc_dimension=cc_dimension)
            for prim_sec_vars in geometry.values():
                for spatial_vars in prim_sec_vars.values():
                    all(
                        self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                        for spatial_var in spatial_vars.keys()
                    )

    def test_init_failure(self):
        with self.assertRaises(pybamm.GeometryError):
            pybamm.Geometryxp0p1DMicro(cc_dimension=3)


class TestGeometryxp1p1DMicro(unittest.TestCase):
    def test_geometry_keys(self):
        for cc_dimension in [1, 2]:
            geometry = pybamm.Geometryxp1p1DMicro(cc_dimension=cc_dimension)
            for prim_sec_vars in geometry.values():
                for spatial_vars in prim_sec_vars.values():
                    all(
                        self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                        for spatial_var in spatial_vars.keys()
                    )

    def test_init_failure(self):
        with self.assertRaises(pybamm.GeometryError):
            pybamm.Geometryxp0p1DMicro(cc_dimension=3)


class TestGeometry(unittest.TestCase):
    def test_combine_geometries(self):
        geometry1Dmacro = pybamm.Geometry1DMacro()
        geometry1Dmicro = pybamm.Geometry1DMicro()
        geometry = pybamm.Geometry(geometry1Dmacro, geometry1Dmicro)
        self.assertEqual(
            set(geometry.keys()),
            set(
                [
                    "negative electrode",
                    "separator",
                    "positive electrode",
                    "negative particle",
                    "positive particle",
                ]
            ),
        )

        # update with custom geometry
        whole_cell = ["negative electrode", "separator", "positive electrode"]
        x = pybamm.SpatialVariable("x", whole_cell)
        custom_geometry = {
            "negative electrode": {
                "primary": {x: {"min": pybamm.Scalar(1), "max": pybamm.Scalar(2)}}
            }
        }
        geometry = pybamm.Geometry(
            geometry1Dmacro, geometry1Dmicro, custom_geometry=custom_geometry
        )
        self.assertEqual(
            geometry["negative electrode"], custom_geometry["negative electrode"]
        )

    def test_combine_geometries_3D(self):
        geometry3Dmacro = pybamm.Geometry3DMacro()
        geometry1Dmicro = pybamm.Geometry1DMicro()
        geometry = pybamm.Geometry(geometry3Dmacro, geometry1Dmicro)
        self.assertEqual(
            set(geometry.keys()),
            set(
                [
                    "negative electrode",
                    "separator",
                    "positive electrode",
                    "negative particle",
                    "positive particle",
                ]
            ),
        )

        with self.assertRaises(ValueError):
            geometry1Dmacro = pybamm.Geometry1DMacro()
            geometry = pybamm.Geometry(geometry3Dmacro, geometry1Dmacro)

    def test_combine_geometries_strings(self):
        geometry = pybamm.Geometry("1D macro", "1D micro")
        self.assertEqual(
            set(geometry.keys()),
            set(
                [
                    "negative electrode",
                    "separator",
                    "positive electrode",
                    "negative particle",
                    "positive particle",
                ]
            ),
        )
        geometry = pybamm.Geometry("3D macro", "1D micro")
        self.assertEqual(
            set(geometry.keys()),
            set(
                [
                    "negative electrode",
                    "separator",
                    "positive electrode",
                    "negative particle",
                    "positive particle",
                ]
            ),
        )


class TestGeometry2DCurrentCollector(unittest.TestCase):
    def test_add_custom_geometry(self):
        geometry = pybamm.Geometry2DCurrentCollector()
        whole_cell = ["negative electrode", "separator", "positive electrode"]
        x = pybamm.SpatialVariable("x", whole_cell)
        custom_geometry = {
            "negative electrode": {
                "primary": {x: {"min": pybamm.Scalar(1), "max": pybamm.Scalar(2)}}
            }
        }

        geometry.update(custom_geometry)
        self.assertEqual(
            geometry["negative electrode"], custom_geometry["negative electrode"]
        )

    def test_geometry_keys(self):
        geometry = pybamm.Geometry2DCurrentCollector()
        for prim_sec_vars in geometry.values():
            for spatial_vars in prim_sec_vars.values():
                all(
                    self.assertIsInstance(spatial_var, pybamm.SpatialVariable)
                    for spatial_var in spatial_vars.keys()
                    if spatial_var not in ["negative", "positive"]
                )


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    pybamm.settings.debug_mode = True
    unittest.main()
