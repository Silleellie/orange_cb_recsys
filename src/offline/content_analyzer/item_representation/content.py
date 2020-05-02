from offline.content_analyzer.item_representation.content_field import ContentField

from typing import List


class Content:
    """
    A Item is a list of his fields, identified by a string id
    Args:
        item_id (str): identifier
        fields (list[ContentField]): list of the fields of an item
    """
    def __init__(self, item_id: str, fields: List[ContentField] = None):
        if fields is None:
            fields = []         # list o dict
        self.__id: str = item_id
        self.__fields: List[ContentField] = fields

    def append(self, field: ContentField):
        """
        append a field to the fields list
        Args:
            field (ContentField): the field to append
        """
        self.__fields.append(field)

    def remove(self, field_name: str):
        """
        remove the field with field_name in the fields list
        Args:
            field_name (str): the name of the field to remove
        """
        self.__fields.pop(self.__fields.index(ContentField(field_name)))

    def serialize(self):
        """
        Serialize an item
        """
        pass


class RepresentedItems:
    """
    Class that collect the Items created and serialize the entire collection.
    Args:
        items (list<Item>): list of Items
        length: number of items
    """
    def __init__(self, length: int = 0, items: List[Content] = None):
        if items is None:
            items = []
        self.__items: List[Content] = items
        self.__length: int = length

    def append(self, item: Content):
        self.__items.append(item)

    def serialize(self):
        """
        Serialize the entire collection
        Returns:

        """
        pass                