import pandas as pd
from typing import List, Any, Union, Iterator, Dict


class RepresentationContainer:
    """
    Class that stores a generic representation. This is used in the project for storing the representations and
    ids for both the field and exogenous representations of the contents. In order to store the data, the class handles
    a dataframe with 1 column ('representation') and 2 indexes ('internal_id' and 'external_id').
    The dataframe is in the following form

                                            representation
                    internal_id external_id
                    0           'test'      FieldRepresentation instance
                    1           NaN         FieldRepresentation instance
                    2           'test2'     FieldRepresentation instance


    The index 'internal_id' is used to store the id automatically assigned by the framework to the representation.
    This default id is an integer and the column will always be in the form: [0, 1, 2, 3, ...]

    The index 'external_id' is used to store the optional id that the user can assign to the representation.
    If the user didn't define an external_id for the representation it will be set to NaN and it will be
    accessible using the internal_id only.
    The 'external_id' is a string and the column will always be in the form: ['test', NaN, 'test2', 'test3', ...]

    Both 'internal_id' and 'external_id' contain unique values, meaning that there can't be duplicates in the
    columns (except for NaN)

    The column 'representation' is used to store the instances of the representations for the content,
    It can store both instances of FieldRepresentation or ExogenousRepresentation (not both at the same time obviously,
    the column has to contain FieldRepresentation or ExogenousRepresentation only)
    By using an index value either integer (referring to 'internal_id') or string (referring to 'external_id') it's
    possible to access the corresponding representation

    Args:
        external_id_list (Union[List[Union[str, None]], Union[str, None]]): list containing the user defined ids for the
            representations, the None value is used for representations the user didn't assign an id to. It's also
            possible to pass a single value instead of a list.
        representation_list (Union[List[Any], Any]): list containing the representations instances (so eiter
            FieldRepresentation or ExogenousRepresentation). It's also possible to pass a single value instead of a
            list.

    internal_id_list is not required as an argument because it will be automatically created by the class
    """

    def __init__(self, representation_list: Union[List[Any], Any] = None,
                 external_id_list: Union[List[Union[str, None]], Union[str, None]] = None):
        if external_id_list is None:
            external_id_list = []
        if representation_list is None:
            representation_list = []

        if not isinstance(external_id_list, list):
            external_id_list = [external_id_list]
        if not isinstance(representation_list, list):
            representation_list = [representation_list]

        if len(representation_list) != len(external_id_list):
            raise ValueError("Representation and external_id lists must have the same length")
        if len(external_id_list) != len(set(external_id_list)):
            raise ValueError("Custom IDs must be unique!")

        self.__dataframe = pd.DataFrame({'external_id': external_id_list, 'representation': representation_list})
        self.__dataframe['internal_id'] = self.__dataframe.index
        self.__alias_dict = {k: v for k, v in zip(external_id_list, self.__dataframe.index.values) if k is not None}
        self.__dataframe.set_index(['internal_id', 'external_id'], inplace=True)

    def get_internal_index(self) -> List[int]:
        """
        Returns a list containing the values in the 'internal_id' index
        """
        return list(self.__dataframe.index.get_level_values('internal_id'))

    def get_external_index(self) -> List[Union[str, None]]:
        """
        Returns a list containing the values in the 'external_id' index
        """
        return list(self.__dataframe.index.get_level_values('external_id'))

    def get_representations(self) -> List[Any]:
        """
        Returns a list containing the values in the 'representations' column
        """
        return list(self.__dataframe['representation'])

    def append(self, representation: Union[List[Any], Any],
               external_id: Union[List[Union[str, None]], Union[str, None]]):
        """
        Method used to append a list of representations (or a single representation) and their list of
        external_ids (or a single external_id) to the main dataframe. In order to do so, a new dataframe is created
        for the arguments passed by the user and it will be appended to the original dataframe. The logic behind the
        creation of the dataframe is the same as the constructor, with only one difference: the internal_id index is
        generated from the original dataframe one (so that the internal_ids are consecutive).

        Args:
            external_id (Union[List[Union[str, None]], Union[str, None]]): list containing the user defined ids for the
                representations, the None value is used for representations the user didn't assign an id to. It's also
                possible to pass a single value instead of a list.
            representation (Union[List[Any], Any]): list containing the representations instances (so eiter
                FieldRepresentation or ExogenousRepresentation). It's also possible to pass a single value instead of a
                list.
        """
        if not isinstance(external_id, list):
            external_id = [external_id]
        if not isinstance(representation, list):
            representation = [representation]

        if len(representation) != len(external_id):
            raise ValueError("Representation and external_id lists must have the same length")
        if len(external_id) != len(set(external_id)):
            raise ValueError("Custom IDs must be unique!")

        if len(self.get_internal_index()) == 0:
            next_internal_id = 0
        else:
            next_internal_id = self.__dataframe.index.get_level_values('internal_id')[-1] + 1
        new_dataframe = pd.DataFrame({'external_id': external_id, 'representation': representation})
        new_dataframe['internal_id'] = list(range(next_internal_id, len(representation) + next_internal_id))
        self.__alias_dict.update({k: v for k, v in zip(external_id, new_dataframe['internal_id'].values)
                                  if k is not None})
        new_dataframe.set_index(['internal_id', 'external_id'], inplace=True)
        self.__dataframe = self.__dataframe.append(new_dataframe)

    def pop(self, id: Union[str, int]):
        """
        Remove a specific row from the dataframe identified by the external or internal id passed as an argument.
        The representation corresponding to the selected row is also returned (in case it's needed).

        Args:
            id(Union[str, int]): used to access the row to remove from the dataframe. If it is an integer, it means
                it refers to the internal_id index, if it is a string, it means that it refers to the external_id index

        Returns:
            removed_representation (Any): representation corresponding to the removed row
        """
        removed_representation = self[id]
        try:
            # id is int
            self.__dataframe = self.__dataframe.drop(id, level=0)
        except KeyError:
            # id is string
            del self.__alias_dict[id]
            self.__dataframe = self.__dataframe.drop(id, level=1)
        return removed_representation

    def __getitem__(self, item: Union[str, int]):
        """
        Access a specific representation using an index value. The index value can be either string or integer,
        if it is an integer, it means that it is referring to the 'internal_id' index, otherwise if it is a string,
        it means that it is referring to the 'external_id' index.

        Args:
            item (Union[str, int]): value used to refer to a specific representation by accessing the index columns
        """
        try:
            # the index is an integer
            return self.__dataframe.iloc[item]['representation']
        except TypeError as e:
            # the index is a string
            integer_ind = self.__alias_dict[item]
            return self.__dataframe.iloc[integer_ind]['representation']

    def __iter__(self) -> Iterator[Dict]:
        for internal_index, external_index, representation in \
                zip(self.get_internal_index(), self.get_external_index(), self.get_representations()):
            yield {'internal_id': internal_index, 'external_id': external_index, 'representation': representation}

    def __len__(self):
        return len(self.get_internal_index())

    def __eq__(self, other):
        return self.__dataframe.equals(other.__dataframe)

    def __str__(self):
        return str(self.__dataframe)

    def __repr__(self):
        return str(self)
