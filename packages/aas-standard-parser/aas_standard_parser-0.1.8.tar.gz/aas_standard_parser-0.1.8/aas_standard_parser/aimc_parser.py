"""Parser for Mapping Configurations in AIMC Submodel."""

import json
import logging
from dataclasses import dataclass, field

import basyx.aas.adapter.json
from basyx.aas import model

import aas_standard_parser.collection_helpers as ch

logger = logging.getLogger(__name__)


class SourceSinkRelation:
    """Class representing a source-sink relation in the mapping configuration."""

    aid_submodel_id: str = field(metadata={"description": "Identifier of the AID submodel used by the source reference."})
    source: model.ExternalReference = field(metadata={"description": "Reference to the source property in the AID submodel."})
    sink: model.ExternalReference = field(metadata={"description": "Reference to the sink property in the target submodel."})
    property_name: str = field(metadata={"description": "Name of the mapped property."})
    source_parent_path: list[str] = field(metadata={"description": "List of idShorts representing the parent path of the reference."})

    def source_as_dict(self) -> dict:
        """Convert the source reference to a dictionary.

        :return: The source reference as a dictionary.
        """
        dict_string = json.dumps(self.source, cls=basyx.aas.adapter.json.AASToJsonEncoder)
        dict_string = dict_string.replace("GlobalReference", "Submodel").replace("FragmentReference", "SubmodelElementCollection")
        return json.loads(dict_string)

    def sink_as_dict(self) -> dict:
        """Convert the sink reference to a dictionary.

        :return: The sink reference as a dictionary.
        """
        return json.loads(json.dumps(self.sink, cls=basyx.aas.adapter.json.AASToJsonEncoder))

    def get_source_parent_property_group_name(self) -> str:
        """Get the name of the parent property group from the source. Ignore 'properties' entries from the path."""
        if len(self.source_parent_path) == 0:
            return ""

        return next((n for n in reversed(self.source_parent_path) if n != "properties"), "")


class MappingConfiguration:
    """Class representing a mapping configuration."""

    interface_reference: model.ReferenceElement = field(metadata={"description": "Reference to the interface in the AID submodel."})
    aid_submodel_id: str = field(metadata={"description": "Identifier of the AID submodel used by the interface reference."})
    source_sink_relations: list[SourceSinkRelation] = field(metadata={"description": "List of source-sink relations in the mapping configuration."})


class MappingConfigurations:
    """Class representing mapping configurations from AIMC submodel."""

    configurations: list[MappingConfiguration] = field(metadata={"description": "List of mapping configurations."})
    aid_submodel_ids: list[str] = field(metadata={"description": "List of AID submodel IDs used in the mapping configurations."})


def get_mapping_configuration_root_element(aimc_submodel: model.Submodel) -> model.SubmodelElementCollection | None:
    """Get the mapping configuration root submodel element collection from the AIMC submodel.

    :param aimc_submodel: The AIMC submodel to extract the mapping configuration root from.
    :return: The mapping configuration root submodel element collection or None if not found.
    """
    # check if AIMC submodel is None
    if aimc_submodel is None:
        logger.error("AIMC submodel is None.")
        return None

    # get 'MappingConfigurations' element list by its semantic ID
    mc_element = ch.find_by_in_semantic_id(aimc_submodel.submodel_element, "idta/AssetInterfacesMappingConfiguration/1/0/MappingConfigurations")
    if mc_element is None:
        logger.error("'MappingConfigurations' element list not found in AIMC submodel.")

    return mc_element


def get_mapping_configuration_elements(aimc_submodel: model.Submodel) -> list[model.SubmodelElementCollection] | None:
    """Get all mapping configurations from the AIMC submodel.

    :param aimc_submodel: The AIMC submodel to extract mapping configurations from.
    :return: A dictionary containing all mapping configurations.
    """
    # check if AIMC submodel is None
    if aimc_submodel is None:
        logger.error("AIMC submodel is None.")
        return None

    # get mapping configuration root element
    root_element = get_mapping_configuration_root_element(aimc_submodel)
    if root_element is None:
        return None

    # find all 'MappingConfiguration' elements by their semantic ID
    mapping_configurations = ch.find_all_by_in_semantic_id(root_element.value, "idta/AssetInterfacesMappingConfiguration/1/0/MappingConfiguration")

    logger.debug(f"Found {len(mapping_configurations)} mapping configuration elements in AIMC submodel.")

    return mapping_configurations


def parse_mapping_configurations(aimc_submodel: model.Submodel) -> MappingConfigurations:
    """Parse all mapping configurations in the AIMC submodel.

    :param aimc_submodel: The AIMC submodel to parse mapping configurations from.
    :return: A list of parsed mapping configurations.
    """
    logger.info("Parse mapping configurations from AIMC submodel.")

    mapping_configurations: list[MappingConfiguration] = []

    # get all mapping configuration elements
    mapping_configurations_elements = get_mapping_configuration_elements(aimc_submodel)
    if mapping_configurations_elements is None:
        logger.error("No mapping configuration elements found in AIMC submodel.")
        return mapping_configurations_elements

    # parse each mapping configuration element
    for mc_element in mapping_configurations_elements:
        mc = parse_mapping_configuration_element(mc_element)
        if mc is not None:
            mapping_configurations.append(mc)

    logger.debug(f"Parsed {len(mapping_configurations)} mapping configurations.")

    mcs = MappingConfigurations()
    mcs.configurations = mapping_configurations
    # add all unique AID submodel IDs from all mapping configurations
    mcs.aid_submodel_ids = list({mc.aid_submodel_id for mc in mapping_configurations})

    logger.debug(f"Found {len(mcs.aid_submodel_ids)} unique AID submodel IDs in mapping configurations.")
    logger.debug(f"Found {len(mcs.configurations)} mapping configurations in AIMC submodel.")

    return mcs


def parse_mapping_configuration_element(
    mapping_configuration_element: model.SubmodelElementCollection,
) -> MappingConfiguration | None:
    """Parse a mapping configuration element.

    :param mapping_configuration_element: The mapping configuration element to parse.
    :return: The parsed mapping configuration or None if parsing failed.
    """
    if mapping_configuration_element is None:
        logger.error("Mapping configuration element is None.")
        return None

    logger.debug(f"Parse mapping configuration '{mapping_configuration_element}'")

    # get interface reference element
    interface_reference = _get_interface_reference_element(mapping_configuration_element)
    if interface_reference is None:
        return None

    source_sink_relations = _generate_source_sink_relations(mapping_configuration_element)

    if len(source_sink_relations) == 0:
        logger.error(f"No source-sink relations found in mapping configuration '{mapping_configuration_element.id_short}'.")
        return None

    # check if all relations have the same AID submodel
    aid_submodel_ids = list({source_sink_relation.aid_submodel_id for source_sink_relation in source_sink_relations})

    if len(aid_submodel_ids) != 1:
        logger.error(
            f"Multiple AID submodel IDs found in mapping configuration '{mapping_configuration_element.id_short}': {aid_submodel_ids}. Expected exactly one AID submodel ID."
        )
        return None

    mc = MappingConfiguration()
    mc.interface_reference = interface_reference
    mc.source_sink_relations = source_sink_relations
    # add all unique AID submodel IDs from source-sink relations
    mc.aid_submodel_id = aid_submodel_ids[0]
    return mc


def _get_interface_reference_element(
    mapping_configuration_element: model.SubmodelElementCollection,
) -> model.ReferenceElement | None:
    """Get the interface reference ID from the mapping configuration element.

    :param mapping_configuration_element: The mapping configuration element to extract the interface reference ID from.
    :return: The interface reference ID or None if not found.
    """
    logger.debug(f"Get 'InterfaceReference' from mapping configuration '{mapping_configuration_element}'.")

    interface_ref: model.ReferenceElement = ch.find_by_in_semantic_id(
        mapping_configuration_element, "idta/AssetInterfacesMappingConfiguration/1/0/InterfaceReference"
    )

    if interface_ref is None or not isinstance(interface_ref, model.ReferenceElement):
        logger.error(f"'InterfaceReference' not found in mapping configuration '{mapping_configuration_element.id_short}'.")
        return None

    if interface_ref.value is None or len(interface_ref.value.key) == 0:
        logger.error(f"'InterfaceReference' has no value in mapping configuration '{mapping_configuration_element.id_short}'.")
        return None

    return interface_ref


def _generate_source_sink_relations(mapping_configuration_element: model.SubmodelElementCollection) -> list[SourceSinkRelation]:
    source_sink_relations: list[SourceSinkRelation] = []

    logger.debug(f"Get 'MappingSourceSinkRelations' from mapping configuration '{mapping_configuration_element}'.")

    relations_list: model.SubmodelElementList = ch.find_by_in_semantic_id(
        mapping_configuration_element, "/idta/AssetInterfacesMappingConfiguration/1/0/MappingSourceSinkRelations"
    )

    if relations_list is None or not isinstance(relations_list, model.SubmodelElementList):
        logger.error(f"'MappingSourceSinkRelations' not found in mapping configuration '{mapping_configuration_element.id_short}'.")
        return source_sink_relations

    for source_sink_relation in relations_list.value:
        logger.debug(f"Parse source-sink relation '{source_sink_relation}'.")

        if not isinstance(source_sink_relation, model.RelationshipElement):
            logger.warning(f"'{source_sink_relation}' is not a RelationshipElement")
            continue

        if source_sink_relation.first is None or len(source_sink_relation.first.key) == 0:
            logger.warning(f"'first' reference is missing in RelationshipElement '{source_sink_relation.id_short}'")
            continue

        if source_sink_relation.second is None or len(source_sink_relation.second.key) == 0:
            logger.warning(f"'second' reference is missing in RelationshipElement '{source_sink_relation.id_short}'")
            continue

        source_ref = source_sink_relation.first

        global_ref = next((key for key in source_ref.key if key.type == model.KeyTypes.GLOBAL_REFERENCE), None)

        if global_ref is None:
            logger.warning(f"No GLOBAL_REFERENCE key found in 'first' reference of RelationshipElement '{source_sink_relation.id_short}'")
            continue

        last_fragment_ref = next(
            (key for key in reversed(source_ref.key) if key.type == model.KeyTypes.FRAGMENT_REFERENCE),
            None,
        )

        if last_fragment_ref is None:
            logger.warning(f"No FRAGMENT_REFERENCE key found in 'first' reference of RelationshipElement '{source_sink_relation.id_short}'")
            continue

        relation = SourceSinkRelation()
        relation.source = source_sink_relation.first
        relation.sink = source_sink_relation.second
        relation.aid_submodel_id = global_ref.value
        relation.property_name = last_fragment_ref.value
        relation.source_parent_path = _get_reference_parent_path(source_ref)

        source_sink_relations.append(relation)

    return source_sink_relations


def _get_reference_parent_path(reference: model.ExternalReference) -> list[str]:
    """Get the parent path of a reference as a list of idShorts.

    :param reference: The reference to extract the parent path from.
    :return: A list of idShorts representing the parent path.
    """
    # Exclude the last key which is the actual element
    return [key.value for key in reference.key[:-1] if key.type == model.KeyTypes.FRAGMENT_REFERENCE]
