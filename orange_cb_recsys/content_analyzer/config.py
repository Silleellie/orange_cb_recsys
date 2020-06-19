import time
from typing import List, Dict, Set

from orange_cb_recsys.content_analyzer.field_content_production_techniques.field_content_production_technique import \
    FieldContentProductionTechnique, CollectionBasedTechnique
from orange_cb_recsys.content_analyzer.information_processor.information_processor import InformationProcessor
from orange_cb_recsys.content_analyzer.lod_properties_retrieval import LODPropertiesRetrieval
from orange_cb_recsys.content_analyzer.memory_interfaces.memory_interfaces import InformationInterface
from orange_cb_recsys.content_analyzer.raw_information_source import RawInformationSource


class FieldRepresentationPipeline:
    """
    Pipeline which specifies how to produce one of the representations of a field.

    Args:
        content_technique (FieldContentProductionTechnique):
            used to produce complex representation of the field given pre-processed information
        preprocessor_list (InformationProcessor):
            list of information processors that will be applied to the original text, in a pipeline way
    """

    instance_counter: int = 0

    def __init__(self, content_technique: FieldContentProductionTechnique,
                 preprocessor_list: List[InformationProcessor] = None):
        if preprocessor_list is None:
            preprocessor_list = []
        self.__preprocessor_list: List[InformationProcessor] = preprocessor_list
        self.__content_technique: FieldContentProductionTechnique = content_technique
        self.__id: str = str(FieldRepresentationPipeline.instance_counter)
        FieldRepresentationPipeline.instance_counter += 1

    def append_preprocessor(self, preprocessor: InformationProcessor):
        """
        Add a new preprocessor to the preprocessor list
        Args:
            preprocessor (InformationProcessor): The preprocessor to add
        """
        self.__preprocessor_list.append(preprocessor)

    def set_content_technique(self, content_technique: FieldContentProductionTechnique):
        self.__content_technique = content_technique

    def get_preprocessor_list(self) -> List[InformationProcessor]:
        for preprocessor in self.__preprocessor_list:
            yield preprocessor

    def get_content_technique(self) -> FieldContentProductionTechnique:
        return self.__content_technique

    def set_lang(self, lang: str):
        for preprocessor in self.__preprocessor_list:
            preprocessor.set_lang(lang)

        try:
            self.__content_technique.set_lang(lang)
        except AttributeError:
            pass

    def __str__(self):
        return self.__id

    def __repr__(self):
        msg = "< " + "FieldRepresentationPipeline: " + "" \
            "preprocessor_list = " + str(self.__preprocessor_list) + "; " \
            "content_technique = " + str(self.__content_technique) + ">"
        return msg


class FieldConfig:
    """
    Class that represents the configuration of a single field.
    Args:
        pipelines_list (List<FieldRepresentationPipeline>):
            list of the pipelines that will be used to produce different field's representations,
            one pipeline for each representation
    """

    def __init__(self, lang: str = "EN",
                 memory_interface: InformationInterface = None,
                 pipelines_list: List[FieldRepresentationPipeline] = None):
        if pipelines_list is None:
            pipelines_list = []

        self.__lang = lang
        self.__memory_interface: InformationInterface = memory_interface
        self.__pipelines_list: List[FieldRepresentationPipeline] = pipelines_list

    def get_lang(self):
        return self.__lang

    def get_memory_interface(self) -> InformationInterface:
        return self.__memory_interface

    def set_memory_interface(self, memory_interface: InformationInterface):
        self.__memory_interface = memory_interface

    def append_pipeline(self, pipeline: FieldRepresentationPipeline):
        pipeline.set_lang(self.__lang)
        self.__pipelines_list.append(pipeline)

    def get_pipeline_list(self) -> List[FieldRepresentationPipeline]:
        for pipeline in self.__pipelines_list:
            yield pipeline

    def __str__(self):
        return "FieldConfig"

    def __repr__(self):
        return "< " + "FieldConfig: " + "" \
                "pipelines_list = " + str(self.__pipelines_list) + " >"


class ContentAnalyzerConfig:
    """
    Class that represents the Configuration for the content analyzer.
    Args:
        source (RawInformationSource):
            raw data source to iterate on for extracting the contents
        id_field_name (str): list of the fields names containing the content's id,
            it's a list instead of single value for handling complex id
            composed of multiple fields
        field_config_dict (Dict<str, FieldConfig>):
            store the config for each field_name
    """

    def __init__(self, content_type: str,
                 source: RawInformationSource,
                 id_field_name,
                 output_directory: str,
                 search_index=False,
                 field_config_dict: Dict[str, FieldConfig] = None,
                 lod_properties_retrieval: LODPropertiesRetrieval = None):
        if field_config_dict is None:
            field_config_dict = {}

        if type(search_index) is str:
            self.__search_index = search_index.lower() == 'true'
        else:
            self.__search_index = search_index

        self.__output_directory: str = output_directory + str(time.time())
        self.__content_type = content_type.lower()
        self.__field_config_dict: Dict[str, FieldConfig] = field_config_dict
        self.__source: RawInformationSource = source
        self.__id_field_name: str = id_field_name
        self.__lod_properties_retrieval: LODPropertiesRetrieval = lod_properties_retrieval

        FieldRepresentationPipeline.instance_counter = 0

    def set_lod_properties_retrieval(self, lod_properties_retrieval: LODPropertiesRetrieval):
        self.__lod_properties_retrieval = lod_properties_retrieval

    def get_lod_properties_retrieval(self):
        return self.__lod_properties_retrieval

    def get_search_index(self):
        return self.__search_index

    def get_output_directory(self):
        return self.__output_directory

    def get_content_type(self):
        return self.__content_type

    def get_id_field_name(self):
        return self.__id_field_name

    def get_source(self) -> RawInformationSource:
        return self.__source

    def get_field_config(self, field_name: str):
        return self.__field_config_dict[field_name]

    def get_memory_interface(self, field_name: str) -> InformationInterface:
        return self.__field_config_dict[field_name].get_memory_interface()

    def get_pipeline_list(self, field_name: str) -> List[FieldRepresentationPipeline]:
        """
        Get the list of the pipelines specified for the input field
        Args:
            field_name (str): name of the field

        Returns:
            List<FieldRepresentationPipeline>:
                the list of pipelines specified for the input field
        """
        for pipeline in self.__field_config_dict[field_name].get_pipeline_list():
            yield pipeline

    def get_field_name_list(self) -> List[str]:
        """
        Get the list of the field names
        Returns:
            List<str>: list of config dictionary keys
        """
        return self.__field_config_dict.keys()

    def get_interfaces(self) -> Set[InformationInterface]:
        """
        get the list of field interfaces

        Returns:
            List<InformationInterface>: list of config dict values
        """
        interfaces = set()
        for key in self.__field_config_dict.keys():
            if self.__field_config_dict[key].get_memory_interface() is not None:
                interfaces.add(self.__field_config_dict[key].get_memory_interface())
        return interfaces

    def append_field_config(self, field_name: str, field_config: FieldConfig):
        self.__field_config_dict[field_name] = field_config

    def __str__(self):
        return str(self.__id_field_name)

    def __repr__(self):
        msg = "< " + "ContentAnalyzerConfig: " + "" \
                                                 "id_field_name = " + str(self.__id_field_name) + "; " \
                                                                                                  "source = " + str(
            self.__source) + "; " \
                             "field_config_dict = " + str(self.__field_config_dict) + "; " \
                                                                                      "content_type = " + str(
            self.__content_type) + ">"
        return msg
