from __future__ import annotations
from typing import Optional, List, Type, Any
from pydantic import BaseModel, Field


class ToolAgentOutput(BaseModel):
    """Standard output for all tool agents"""
    output: str
    sources: list[str] = Field(default_factory=list)


class Profile(BaseModel):
    instructions: str = Field(description="The agent's system prompt/instructions that define its behavior")
    runtime_template: str = Field(description="The runtime template for the agent's behavior")
    model: Optional[str] = Field(default=None, description="Model override for this profile (e.g., 'gpt-4', 'claude-3-5-sonnet')")
    output_schema: Optional[Type[BaseModel]] = Field(default=None, description="Pydantic model class for structured output validation")
    tools: Optional[List[Any]] = Field(default=None, description="List of tool objects (e.g., FunctionTool instances) to use for this profile")
    description: Optional[str] = Field(default=None, description="Optional one-sentence description for agent capabilities (auto-extracted from instructions if not provided)")

    class Config:
        arbitrary_types_allowed = True

    def get_description(self) -> str:
        """Get description for this profile.

        Returns explicit description if set, otherwise auto-extracts from instructions.
        Auto-extraction takes the first sentence and removes 'You are a/an ' prefix.

        Returns:
            Description string
        """
        if self.description:
            return self.description

        # Auto-extract from first sentence of instructions
        first_line = self.instructions.split('\n')[0].strip()

        # Remove "You are a " or "You are an " prefix
        if first_line.startswith("You are a "):
            desc = first_line[10:].strip()  # len("You are a ") = 10
        elif first_line.startswith("You are an "):
            desc = first_line[11:].strip()  # len("You are an ") = 11
        else:
            desc = first_line

        # Remove trailing period
        if desc.endswith('.'):
            desc = desc[:-1]

        return desc

    def render(self, **kwargs) -> str:
        """Render the runtime template with provided keyword arguments.

        Args:
            **kwargs: Values to substitute for placeholders in the template.
                     Keys are matched case-insensitively with {placeholder} patterns.

        Returns:
            Rendered template string with all placeholders replaced.

        Examples:
            profile.render(task="What is AI?", query="Previous context...")
        """
        # Convert all keys to lowercase and use .format() for substitution
        kwargs_lower = {k.lower(): str(v) for k, v in kwargs.items()}
        return self.runtime_template.format(**kwargs_lower)


def load_all_profiles():
    """Load all Profile instances from the profiles package.

    Returns:
        Dict with shortened keys (e.g., "observe" instead of "observe_profile")
        Each profile has a _key attribute added for automatic name derivation
    """
    import importlib
    import inspect
    from pathlib import Path

    profiles = {}
    package_path = Path(__file__).parent

    # Recursively find all .py files in the profiles directory
    for py_file in package_path.rglob('*.py'):
        if py_file.name == 'base.py' or py_file.name.startswith('_'):
            continue

        # Convert file path to module name (need to find 'contextagent' root)
        # Go up from current file: profiles/base.py -> profiles -> contextagent
        contextagent_root = package_path.parent
        relative_path = py_file.relative_to(contextagent_root)
        module_name = 'contextagent.' + str(relative_path.with_suffix('')).replace('/', '.')

        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, Profile) and not name.startswith('_'):
                    # Strip "_profile" suffix from key for cleaner access
                    key = name.replace('_profile', '') if name.endswith('_profile') else name
                    # Add _key attribute to profile for automatic name derivation
                    obj._key = key
                    profiles[key] = obj
        except Exception as e:
            print(f"Error loading profile: {module_name}")
            raise e

    return profiles


