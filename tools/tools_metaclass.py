from typing import Any, List, Callable, Dict, Set

class FunctionProperty:
    # utility dataclass for function properties
    def __init__(self, name: str, type: str, description: str, required=False):
        self.name = name
        self.type = type
        self.description = description
        self.required = required

class EnvironmentProperty:
    # dataclass for properties that are passed through from the global environment
    def __init__(self, name: str, default=None):
        self.name = name
        self.default = default

class ToolReq:
    def __init__(self, *values):
        self.values = values

    def validate(self, roles: Set[str]):
        return all(sub_tool_req in roles if isinstance(sub_tool_req, str) else sub_tool_req.validate(roles) for sub_tool_req in self.values)

class ToolReqAny:
    def __init__(self, *values):
        self.values = values

    def validate(self, roles: Set[str]):
        return any(sub_tool_req in roles if isinstance(sub_tool_req, str) else sub_tool_req.validate(roles) for sub_tool_req in self.values)

class Tool:
    NAME: str # must be alphanumeric or '-' or '_' and len < 64
    DESCRIPTION: str
    ENV_PARAMETERS: List[EnvironmentProperty] = []
    PARAMETERS: List[FunctionProperty] = []
    REQS: ToolReq | ToolReqAny = ToolReq()

    def __call__(cls, *args, **kwargs) -> str | None:
        pass

class ToolMeta(type):
    tools: List[Dict] = []
    tool_reqs: List[ToolReq] = []
    functions: Dict[str, Callable] = {}
    function_properties: Dict[str, List[EnvironmentProperty]] = {}

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        cls: Tool

        tool_entry = {
            "type": "function",
            "function": {
                "name": cls.NAME,
                "description": cls.DESCRIPTION,
            }
        }

        if hasattr(cls, 'PARAMETERS') and cls.PARAMETERS:
            properties = {
                prop.name: {
                    "type": prop.type,
                    "description": prop.description,
                } for prop in cls.PARAMETERS if isinstance(prop, FunctionProperty)
            }

            required = [
                prop.name for prop in cls.PARAMETERS if getattr(prop, 'required', False)
            ]

            tool_entry["function"]["parameters"] = {
                "type": "object",
                "properties": properties,
                "required": required
            }

        ToolMeta.tools.append(tool_entry)
        ToolMeta.tool_reqs.append(cls.REQS)
        ToolMeta.functions[cls.NAME] = cls()
        ToolMeta.function_properties[cls.NAME] = cls.ENV_PARAMETERS

        return cls

    def available_tools(roles: Set[str]):
        return [tool for tool, tool_req in zip(ToolMeta.tools, ToolMeta.tool_reqs) if tool_req.validate(roles)]