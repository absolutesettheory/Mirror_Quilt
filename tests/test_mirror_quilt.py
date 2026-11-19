import unittest

from src.mirror_quilt import (
    PRIMARY_FUNDING_ADDRESS,
    MirrorQuiltError,
    UniversalBridge,
    boundary_crossing,
    certify_ruleset,
    cell_coordinate,
    is_supported_funding_address,
    neighbors,
    parity,
    tunnel,
)


class MirrorQuiltTests(unittest.TestCase):
    def test_coordinates_are_integer_absolute_cells(self):
        self.assertEqual(cell_coordinate(-1, 0, 2), (-1, 0, 2))
        with self.assertRaises(MirrorQuiltError):
            cell_coordinate(1.5, 0, 0)

    def test_checkerboard_parity(self):
        self.assertEqual(parity((0, 0, 0)), 1)
        self.assertEqual(parity((1, 0, 0)), -1)
        self.assertEqual(parity((-1, 0, 0)), -1)

    def test_face_neighbors_have_opposite_parity(self):
        for neighbor in neighbors((0, 0, 0)):
            self.assertEqual(parity(neighbor), -parity((0, 0, 0)))

    def test_only_one_unit_boundary_crossing_is_allowed(self):
        self.assertEqual(boundary_crossing((0, 0, 0), (1, 0, 0)), -1)
        with self.assertRaises(MirrorQuiltError):
            boundary_crossing((0, 0, 0), (2, 0, 0))

    def test_tunnel_is_deterministic_and_complete(self):
        result = tunnel((0, 0, 0), (1, 0, 0), 7)
        self.assertEqual(result["T_quilt"], 1)
        self.assertEqual(result["closure"], 1)
        self.assertEqual(result["state"], -7)

    def test_bridge_routes_to_single_funding_endpoint(self):
        bridge = UniversalBridge()
        receipt = bridge.funding_receipt(25000, "unit-seal")
        self.assertEqual(receipt.address, PRIMARY_FUNDING_ADDRESS)
        self.assertEqual(receipt.amount_minor_units, 25000)

    def test_funding_address_validation_is_structural(self):
        self.assertTrue(is_supported_funding_address(PRIMARY_FUNDING_ADDRESS))
        self.assertFalse(is_supported_funding_address("1BitcoinAddress"))

    def test_full_certification(self):
        cells = ((i, j, k) for i in range(-1, 2) for j in range(-1, 2) for k in range(-1, 2))
        result = certify_ruleset(cells)
        self.assertTrue(all(result[key] for key in (
            "finite_lattice", "checkerboard_parity", "face_neighbor_opposition",
            "deterministic_tunnel", "universal_bridge",
        )))


if __name__ == "__main__":
    unittest.main()
