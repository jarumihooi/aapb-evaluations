"""
Represents an instance of a Named Entity Link (NEL)
"""

from typing import List, Union


class NamedEntityLink:
    def __init__(self, doc_id: str, begin_offset: int, end_offset: int, entity_type: str,
                 surface_form: str, uris: Union[List[str], str]) -> None:
        """
        Initializes NEL instance. Gold data provides the URI as a string, whereas system output MMIFs provide
        the URI(s) in a list format.
        :param doc_id: the ID of the context document.
        :param begin_offset: position of the first character in the span.
        :param end_offset: position of the last character in the span.
        :param entity_type: the category of the entity.
        :param surface_form: the text corresponding to the entity.
        :param uris: the Wikidata URI(s) grounding the entity.
        """
        self.doc_id = doc_id
        self.begin_offset = begin_offset
        self.end_offset = end_offset
        self.entity_type = entity_type
        self.span = f"{self.doc_id}: {self.begin_offset} - {self.end_offset}"
        self.surface_form = surface_form
        self.kbid = frozenset() # knowledge base ID
        if isinstance(uris, str):
            if uris != '':
                self.kbid = frozenset([uris.rsplit("/", 1)[1]]) # get QID from URI
        elif isinstance(uris, list):
            # multiple wikidata URIs
            self.kbid = frozenset([uri.rsplit("/", 1)[1] for uri in uris])
        else:
            raise TypeError(f"Argument uris must be of type List[str] or str, not {type(uris)}")

    def __str__(self) -> str:
        """Returns a printable string representation of the NEL instance."""
        return f"{self.span} (QID: {self.kbid})"

    def __eq__(self, other) -> bool:
        """Returns True if another object is an NEL instance with the same span (doc id and offsets), entity type,
        and a QID matching this one. Returns False otherwise."""
        if isinstance(other, NamedEntityLink):
            return self.span == other.span and self.entity_type == other.entity_type \
                   and self.kbid.intersection(other.kbid)
        return False

    def __ne__(self, other) -> bool:
        """Returns True if another object is not an NEL instance or if it is an NEL instance not equal to this one.
        Returns False if another object is an NEL instance equal to this one."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Returns the hash value for the NEL object."""
        return hash((self.span, self.entity_type))
