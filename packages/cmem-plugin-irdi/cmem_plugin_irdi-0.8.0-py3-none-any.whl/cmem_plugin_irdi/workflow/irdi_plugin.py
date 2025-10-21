"""IRDI creation Plugin"""

import re
from typing import Sequence  # noqa: UP035

import rfc3987
from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
)
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.parameter.graph import GraphParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import (
    FixedNumberOfInputs,
    FixedSchemaPort,
)
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access

from cmem_plugin_irdi.components import components
from cmem_plugin_irdi.item_code import generate_item_code, init_counter

# Version Identifier
VI = "001"

DOCUMENTATION = """Create unique
[ECLASS](https://eclass.eu/support/technical-specification/structure-and-elements/irdi) IRDIs.

IRDIs are unique for each combination of (non-advanced) parameters.
If no input path is configured, values are read from the URIs of the input (Transformation Input).

- All fields of the IRDI are configurable, except `Item Code`, which is created by the plugin.
  - Created IRDIs are unique per configuration.
- Specify a graph that stores the state of Item Codes.
- Input and output paths are configurable.
  - if no input path is configured, values are read from the URIs of the input
    (transformation input).
"""

PARAMETERS = [
    PluginParameter(
        name="graph",
        label="Counter graph",
        description="Graph in which the Item Code (IC) counter is stored",
        param_type=GraphParameterType(allow_only_autocompleted_values=False),
    ),
    PluginParameter(
        name="output_schema_path",
        label="Output path / property",
        description="Path or property that will connect input values and their generated IRDIs",
    ),
    PluginParameter(
        name="counted_object",
        label="Counted object",
        description="The class of objects that are counted. (IRI)",
        default_value="",
        advanced=True,
    ),
    PluginParameter(
        name="input_schema_path",
        label="Input Schema Path / Property",
        description="Path from which input values are taken. "
        "If empty, values are read from the URIs of the input",
        advanced=True,
        default_value="",
    ),
] + [parameter["parameter"] for parameter in components.values()]


@Plugin(
    label="Generate base36 IRDIs",
    description="Create unique ECLASS IRDIs.",
    documentation=DOCUMENTATION,
    parameters=PARAMETERS,
    icon=Icon(file_name="logo.svg", package=__package__),
)
class IrdiPlugin(WorkflowPlugin):
    """IRDI Plugin"""

    def __init__(  # noqa: PLR0913
        self,
        graph: str,
        icd: str,
        oi: str,
        opi: str,
        opis: str,
        ai: str,
        csi: str,
        counted_object: str,
        input_schema_path: str,
        output_schema_path: str,
    ):
        self.input_schema_path = input_schema_path
        self.graph = graph
        self.output_schema_path = output_schema_path
        self.icd = icd
        self.oi = oi
        self.opi = opi.upper()
        self.opis = opis
        self.ai = ai
        self.csi = csi.upper() if csi else ""
        self.counted_object = counted_object

        # validate inputs
        for component, definition in components.items():
            value = self.__dict__.get(component)
            if value and (re.match(definition["regex"], value) is None):
                raise ValueError(component + ": wrong format")

        if self.counted_object and (rfc3987.match(self.counted_object, rule="IRI") is None):
            raise ValueError(f"Counted object: {self.counted_object} is not a valid URI")

        # define input ports if path was provided
        if self.input_schema_path:
            self.input_ports = FixedNumberOfInputs(
                [
                    FixedSchemaPort(
                        schema=EntitySchema(
                            type_uri="",
                            paths=[EntityPath(path=self.input_schema_path)],
                        )
                    )
                ]
            )
        # define
        else:
            self.input_ports = FixedNumberOfInputs(
                [
                    FixedSchemaPort(
                        schema=EntitySchema(
                            type_uri="",
                            paths=[],
                        )
                    )
                ]
            )

        # define output port
        self.output_port = FixedSchemaPort(
            schema=EntitySchema(type_uri="", paths=[EntityPath(path=self.output_schema_path)])
        )

        # construct counter identifier
        self.counter = f"{self.icd}-{self.oi}-{self.opi}-{self.opis}-{self.ai}#{self.csi}"

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities | None:
        """Execute Workflow plugin"""
        setup_cmempy_user_access(context.user)

        init_counter(self.graph, self.counter, self.counted_object)

        output = []

        try:
            first_input: Entities = inputs[0]
        except IndexError as error:
            raise ValueError("Input port not connected.") from error

        schema = EntitySchema(
            type_uri=first_input.schema.type_uri, paths=[EntityPath(self.output_schema_path)]
        )

        if self.input_schema_path:
            uris = self._get_input_path(first_input, self.input_schema_path)
        else:
            uris = self._get_input_uri(first_input)

        for uri in uris:
            item_code = generate_item_code(self.graph, self.counter)
            irdi = (
                f"{self.icd}-{self.oi}-{self.opi}-{self.opis}-{self.ai}#{self.csi}-{item_code}#{VI}"
            )
            output.append(Entity(uri=uri, values=[[irdi]]))

        # write execution report
        context.report.update(
            ExecutionReport(
                entity_count=len(output),
                operation_desc="IRDIs created",
                sample_entities=Entities(entities=output[:10], schema=schema),
            )
        )

        return Entities(entities=output, schema=schema)

    def _get_input_uri(self, entities: Entities) -> list[str]:
        """Get URIs to be processed from URIs of input entities"""
        return [entity.uri for entity in entities.entities]

    def _get_input_path(self, entities: Entities, input_path: str) -> list[str]:
        """Get URIS to be processed from values of input entities

        :param input_path: path for which values are returned
        :raises ValueError: if input_path is not in input schema of entities
        """
        paths = entities.schema.paths
        try:
            index = next(index for index, path in enumerate(paths) if path.path == input_path)
        except StopIteration as error:
            raise ValueError(f"Input does not contain path {input_path}") from error

        return [entity.values[index][0] for entity in entities.entities]
