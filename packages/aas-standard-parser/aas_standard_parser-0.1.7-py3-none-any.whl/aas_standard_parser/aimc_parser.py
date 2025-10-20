import json
import logging

import basyx.aas.adapter.json
from basyx.aas import model

logger = logging.getLogger(__name__)


class SourceSinkRelation:
    """Class representing a source-sink relation in the mapping configuration."""

    aid_submodel_id: str
    source: model.ExternalReference
    sink: model.ExternalReference
    property_name: str

    def source_as_dict(self) -> dict:
        """Convert the source reference to a dictionary.

        :return: The source reference as a dictionary.
        """
        dict_string = json.dumps(
            self.source, cls=basyx.aas.adapter.json.AASToJsonEncoder
        )
        dict_string = dict_string.replace("GlobalReference", "Submodel").replace(
            "FragmentReference", "SubmodelElementCollection"
        )
        return json.loads(dict_string)

    def sink_as_dict(self) -> dict:
        """Convert the sink reference to a dictionary.

        :return: The sink reference as a dictionary.
        """
        return json.loads(
            json.dumps(self.sink, cls=basyx.aas.adapter.json.AASToJsonEncoder)
        )


class MappingConfiguration:
    """Class representing a mapping configuration."""

    interface_reference: model.ReferenceElement
    aid_submodel_id: str
    source_sink_relations: list[SourceSinkRelation]


class MappingConfigurations:
    """Class representing mapping configurations from AIMC submodel."""

    configurations: list[MappingConfiguration]
    aid_submodel_ids: list[str]


class AIMCParser:
    """Parser for the AIMC submodel.

    :return: The parsed AIMC submodel.
    """

    aimc_submodel: model.Submodel | None = None
    mapping_configuration_element: model.SubmodelElementCollection | None = None

    def __init__(self, aimc_submodel: model.Submodel):
        """Initialize the AIMC parser.

        :param aimc_submodel: The AIMC submodel to parse.
        """
        if aimc_submodel is None:
            raise ValueError("AIMC submodel cannot be None.")

        self.aimc_submodel = aimc_submodel

    def get_mapping_configuration_root_element(
        self,
    ) -> model.SubmodelElementCollection | None:
        """Get the mapping configuration root submodel element collection from the AIMC submodel.

        :return: The mapping configuration root submodel element collection or None if not found.
        """
        self.mapping_configuration_element = next(
            (
                elem
                for elem in self.aimc_submodel.submodel_element
                if elem.id_short == "MappingConfigurations"
            ),
            None,
        )

        if self.mapping_configuration_element is None:
            logger.error(
                "'MappingConfigurations' element list not found in AIMC submodel."
            )
            return None

        return self.mapping_configuration_element

    def get_mapping_configuration_elements(
        self,
    ) -> list[model.SubmodelElementCollection] | None:
        """Get all mapping configurations elements from the AIMC submodel.

        :return: A dictionary containing all mapping configurations elements.
        """
        if self.mapping_configuration_element is None:
            self.mapping_configuration_element = (
                self.get_mapping_configuration_root_element()
            )

        if self.mapping_configuration_element is None:
            return None

        mapping_configurations: list[model.SubmodelElementCollection] = [
            element
            for element in self.mapping_configuration_element.value
            if isinstance(element, model.SubmodelElementCollection)
        ]

        logger.debug(
            f"Found {len(mapping_configurations)} mapping configuration elements in AIMC submodel."
        )

        return mapping_configurations

    def parse_mapping_configurations(self) -> MappingConfigurations:
        """Parse all mapping configurations in the AIMC submodel.

        :return: A list of parsed mapping configurations.
        """
        logger.info("Parse mapping configurations from AIMC submodel.")

        mapping_configurations: list[MappingConfiguration] = []

        mc_elements = self.get_mapping_configuration_elements()

        if mc_elements is None:
            logger.error("No mapping configuration elements found in AIMC submodel.")
            return mapping_configurations

        for mc_element in mc_elements:
            mc = self.parse_mapping_configuration(mc_element)
            if mc is not None:
                mapping_configurations.append(mc)

        logger.debug(f"Parsed {len(mapping_configurations)} mapping configurations.")

        mcs = MappingConfigurations()
        mcs.configurations = mapping_configurations
        # add all unique AID submodel IDs from all mapping configurations
        mcs.aid_submodel_ids = list(
            {mc.aid_submodel_id for mc in mapping_configurations}
        )

        logger.debug(
            f"Found {len(mcs.aid_submodel_ids)} unique AID submodel IDs in mapping configurations."
        )
        logger.debug(
            f"Found {len(mcs.configurations)} mapping configurations in AIMC submodel."
        )

        return mcs

    def parse_mapping_configuration(
        self, mapping_configuration_element: model.SubmodelElementCollection
    ) -> MappingConfiguration | None:
        """Parse a mapping configuration element.

        :param mapping_configuration_element: The mapping configuration element to parse.
        :return: The parsed mapping configuration or None if parsing failed.
        """
        if mapping_configuration_element is None:
            logger.error("Mapping configuration element is None.")
            return None

        logger.debug(f"Parse mapping configuration '{mapping_configuration_element}'")

        interface_reference = self._get_interface_reference(
            mapping_configuration_element
        )

        if interface_reference is None:
            return None

        source_sink_relations = self._generate_source_sink_relations(
            mapping_configuration_element
        )

        if len(source_sink_relations) == 0:
            logger.error(
                f"No source-sink relations found in mapping configuration '{mapping_configuration_element.id_short}'."
            )
            return None

        # check if all relations have the same AID submodel
        aid_submodel_ids = list(
            {
                source_sink_relation.aid_submodel_id
                for source_sink_relation in source_sink_relations
            }
        )

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

    def _get_interface_reference(
        self, mapping_configuration_element: model.SubmodelElementCollection
    ) -> model.ReferenceElement | None:
        """Get the interface reference ID from the mapping configuration element.

        :param mapping_configuration_element: The mapping configuration element to extract the interface reference ID from.
        :return: The interface reference ID or None if not found.
        """
        logger.debug(
            f"Get 'InterfaceReference' from mapping configuration '{mapping_configuration_element}'."
        )

        interface_ref: model.ReferenceElement = next(
            (
                elem
                for elem in mapping_configuration_element.value
                if elem.id_short == "InterfaceReference"
            ),
            None,
        )

        if interface_ref is None or not isinstance(
            interface_ref, model.ReferenceElement
        ):
            logger.error(
                f"'InterfaceReference' not found in mapping configuration '{mapping_configuration_element.id_short}'."
            )
            return None

        if interface_ref.value is None or len(interface_ref.value.key) == 0:
            logger.error(
                f"'InterfaceReference' has no value in mapping configuration '{mapping_configuration_element.id_short}'."
            )
            return None

        return interface_ref

    def _generate_source_sink_relations(
        self, mapping_configuration_element: model.SubmodelElementCollection
    ) -> list[SourceSinkRelation]:
        source_sink_relations: list[SourceSinkRelation] = []

        logger.debug(
            f"Get 'MappingSourceSinkRelations' from mapping configuration '{mapping_configuration_element}'."
        )

        relations_list: model.SubmodelElementList = next(
            (
                elem
                for elem in mapping_configuration_element.value
                if elem.id_short == "MappingSourceSinkRelations"
            ),
            None,
        )

        if relations_list is None or not isinstance(
            relations_list, model.SubmodelElementList
        ):
            logger.error(
                f"'MappingSourceSinkRelations' not found in mapping configuration '{mapping_configuration_element.id_short}'."
            )
            return source_sink_relations

        for source_sink_relation in relations_list.value:
            logger.debug(f"Parse source-sink relation '{source_sink_relation}'.")

            if not isinstance(source_sink_relation, model.RelationshipElement):
                logger.warning(
                    f"'{source_sink_relation.id_short}' is not a RelationshipElement"
                )
                continue

            if (
                source_sink_relation.first is None
                or len(source_sink_relation.first.key) == 0
            ):
                logger.warning(
                    f"'first' reference is missing in RelationshipElement '{source_sink_relation.id_short}'"
                )
                continue

            if (
                source_sink_relation.second is None
                or len(source_sink_relation.second.key) == 0
            ):
                logger.warning(
                    f"'second' reference is missing in RelationshipElement '{source_sink_relation.id_short}'"
                )
                continue

            global_ref = next(
                (
                    key
                    for key in source_sink_relation.first.key
                    if key.type == model.KeyTypes.GLOBAL_REFERENCE
                ),
                None,
            )

            if global_ref is None:
                logger.warning(
                    f"No GLOBAL_REFERENCE key found in 'first' reference of RelationshipElement '{source_sink_relation.id_short}'"
                )
                continue

            last_fragment_ref = next(
                (
                    key
                    for key in reversed(source_sink_relation.first.key)
                    if key.type == model.KeyTypes.FRAGMENT_REFERENCE
                ),
                None,
            )

            if last_fragment_ref is None:
                logger.warning(
                    f"No FRAGMENT_REFERENCE key found in 'first' reference of RelationshipElement '{source_sink_relation.id_short}'"
                )
                continue

            relation = SourceSinkRelation()
            relation.source = source_sink_relation.first
            relation.sink = source_sink_relation.second
            relation.aid_submodel_id = global_ref.value
            relation.property_name = last_fragment_ref.value

            source_sink_relations.append(relation)

        return source_sink_relations
