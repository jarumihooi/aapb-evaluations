"""
Unit test for NamedEntityLink class
"""

from unittest import TestCase
from nel import NamedEntityLink

# define some toy NEL data
united_nations = {"doc_id": "d1", "begin_offset": 50688, "end_offset": 50702, "entity_type": "location",
                  "surface_form": "United Nations", "uris": ["http://www.wikidata.org/entity/Q1065"]}
un = {"doc_id": "d1", "begin_offset": 50786, "end_offset": 50788, "entity_type": "location",
      "surface_form": "UN", "uris": ["http://www.wikidata.org/entity/Q1065"]}
terence_smith = {"doc_id": "d1", "begin_offset": 52886, "end_offset": 52899, "entity_type": "person",
                 "surface_form": "TERENCE SMITH", "uris": ["http://www.wikidata.org/entity/Q7702012"]}
jim_lehrer = {"doc_id": "d1", "begin_offset": 52966, "end_offset": 52976, "entity_type": "person",
              "surface_form": "JIM LEHRER", "uris": ["https://www.wikidata.org/wiki/Q931148"]}
# the first is constructed from system output data, the second is constructed from gold labeled data
cambodia_1 = {"doc_id": "d1", "begin_offset": 52511, "end_offset": 52519, "entity_type": "location",
              "surface_form": "Cambodia", "uris": ["http://www.wikidata.org/entity/Q1054184",
                                                   "http://www.wikidata.org/entity/Q2387250",
                                                   "http://www.wikidata.org/entity/Q424",
                                                   "http://www.wikidata.org/entity/Q867778"]}
cambodia_2 = {"doc_id": "d1", "begin_offset": 52511, "end_offset": 52519, "entity_type": "location",
              "surface_form": "Cambodia", "uris": "https://www.wikidata.org/wiki/Q424"}


class TestNEL(TestCase):
    def test_init(self):
        """Test constructor."""
        nel_terence_smith = NamedEntityLink(**terence_smith)
        self.assertEqual(nel_terence_smith.span, "d1: 52886 - 52899")
        self.assertEqual(nel_terence_smith.surface_form, "TERENCE SMITH")
        self.assertEqual(nel_terence_smith.entity_type, "person")
        self.assertEqual(nel_terence_smith.kbid, frozenset(["Q7702012"]))

    def test_equal(self):
        """Test whether two distinct NEL instances are equal.
        Span, entity_type, and kbid are compared.
        kbid's are treated as sets and equivalence is based on whether the intersection is not empty.
        """
        nel_cambodia_1 = NamedEntityLink(**cambodia_1)
        nel_cambodia_2 = NamedEntityLink(**cambodia_2)
        self.assertEqual(nel_cambodia_1, nel_cambodia_2)

    def test_not_equal(self):
        """Test whether two distinct NEL instances are not equal."""
        nel_united_nations = NamedEntityLink(**united_nations)
        nel_un = NamedEntityLink(**un)
        self.assertNotEqual(nel_united_nations, nel_un)

    def test_intersection(self):
        """Test whether set intersection captures distinct NEL instances that are equivalent."""
        nel_jim_lehrer = NamedEntityLink(**jim_lehrer)
        nel_cambodia_1 = NamedEntityLink(**cambodia_1)
        sys_instances = frozenset([nel_jim_lehrer, nel_cambodia_1])

        nel_cambodia_2 = NamedEntityLink(**cambodia_2)
        nel_un = NamedEntityLink(**un)
        gold_instances = frozenset([nel_cambodia_2, nel_un])

        intersection = gold_instances.intersection(sys_instances)
        self.assertIn(nel_cambodia_2, intersection)
        self.assertTrue(len(intersection) == 1)
