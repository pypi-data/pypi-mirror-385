"""Entities generation plugin to configure tasks in workflows."""

from collections.abc import Sequence

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
from cmem_plugin_base.dataintegration.parameter.code import YamlCode
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from yaml import YAMLError, safe_load

DESCRIPTION = """Connect this task to a config port of another task in order to set
or overwrite the parameter values of this task."""

YAML_EXAMPLE = """url: http://example.org
method: GET
query: |
    SELECT ?s
    WHERE {{
      ?s ?p ?o
    }}
execute_once: True
limit: 5
"""

DOCUMENTATION = f"""{DESCRIPTION}

To configure this task, add one `key: value` pair per line to the Parameter
Configuration multiline field (YAML syntax). `key` is the ID of the parameter
you want to set or update, `value` is the new value to set.

You can also use multiline values with `|`
(be aware of the correct indentation with spaces, not tabs).

Example parameter configuration:

```
{YAML_EXAMPLE}
```
"""

DESC_PARAMETERS = f"""Your parameter configuration in YAML Syntax.
One 'parameter: value' pair per line.

{YAML_EXAMPLE}
"""


@Plugin(
    label="Set or Overwrite parameters",
    plugin_id="cmem_plugin_parameters-ParametersPlugin",
    icon=Icon(file_name="custom.svg", package=__package__),
    description=DESCRIPTION,
    documentation=DOCUMENTATION,
    parameters=[
        PluginParameter(
            name="parameters",
            label="Parameter Configuration",
            description=DESC_PARAMETERS,
        )
    ],
)
class ParametersPlugin(WorkflowPlugin):
    """Entities generation plugin to configure tasks in workflows."""

    def __init__(self, parameters: YamlCode = YamlCode(YAML_EXAMPLE)) -> None:  # noqa: B008
        try:
            self.process_yaml(str(parameters))
        except YAMLError as error:
            raise ValueError(f"Error in parameter input: {error!s}") from error

        # Input and output ports
        self.input_ports = FixedNumberOfInputs([])
        self.output_port = FixedSchemaPort(self.schema)

    def process_yaml(self, yaml_string: str) -> None:
        """Generate entities from the yaml string."""
        parameters = safe_load(yaml_string)
        if not isinstance(parameters, dict):
            raise TypeError("We need at least one line 'key: value' here.")
        value_counter = 0
        values = []
        paths = []
        type_uri = "urn:x-eccenca:Parameter"
        for key, value in parameters.items():
            if type(value) in (str, int, float, bool):
                paths.append(EntityPath(path=key))
                values.append([str(value)])
                value_counter += 1
        entities = [Entity(uri=type_uri, values=values)]

        self.schema = EntitySchema(type_uri=type_uri, paths=paths)
        self.entities = Entities(entities=entities, schema=self.schema)
        self.total_params = value_counter

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
        """Execute the workflow."""
        _ = inputs
        context.report.update(
            ExecutionReport(
                entity_count=self.total_params,
                operation="write",
                operation_desc="parameters written",
            )
        )
        return self.entities
