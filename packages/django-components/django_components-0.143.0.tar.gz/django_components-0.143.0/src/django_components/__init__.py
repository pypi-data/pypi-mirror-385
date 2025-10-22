"""Main package for Django Components."""

# Public API
# NOTE: Some of the documentation is generated based on these exports
# isort: off
from django_components.app_settings import ContextBehavior, ComponentsSettings
from django_components.attributes import format_attributes, merge_attributes
from django_components.autodiscovery import autodiscover, import_libraries
from django_components.util.command import (
    CommandArg,
    CommandArgGroup,
    CommandHandler,
    CommandLiteralAction,
    CommandParserInput,
    CommandSubcommand,
    ComponentCommand,
)
from django_components.component import (
    Component,
    ComponentInput,
    ComponentNode,
    ComponentVars,
    OnRenderGenerator,
    all_components,
    get_component_by_class_id,
)
from django_components.component_media import ComponentMediaInput, ComponentMediaInputPath
from django_components.component_registry import (
    AlreadyRegistered,
    ComponentRegistry,
    NotRegistered,
    RegistrySettings,
    register,
    registry,
    all_registries,
)
from django_components.dependencies import DependenciesStrategy, render_dependencies
from django_components.extension import (
    ComponentExtension,
    ExtensionComponentConfig,
    OnComponentRegisteredContext,
    OnComponentUnregisteredContext,
    OnRegistryCreatedContext,
    OnRegistryDeletedContext,
    OnComponentClassCreatedContext,
    OnComponentClassDeletedContext,
    OnComponentInputContext,
    OnComponentDataContext,
    OnComponentRenderedContext,
    OnSlotRenderedContext,
    OnTemplateCompiledContext,
    OnTemplateLoadedContext,
)
from django_components.extensions.cache import ComponentCache
from django_components.extensions.defaults import ComponentDefaults, Default, get_component_defaults
from django_components.extensions.debug_highlight import ComponentDebugHighlight
from django_components.extensions.view import ComponentView, get_component_url
from django_components.library import TagProtectedError
from django_components.node import BaseNode, template_tag
from django_components.provide import ProvideNode
from django_components.slots import (
    FillNode,
    Slot,
    SlotContent,
    SlotContext,
    SlotFallback,
    SlotFunc,
    SlotInput,
    SlotNode,
    SlotRef,
    SlotResult,
)
from django_components.tag_formatter import (
    ComponentFormatter,
    ShorthandComponentFormatter,
    TagFormatterABC,
    TagResult,
    component_formatter,
    component_shorthand_formatter,
)
from django_components.template import cached_template
import django_components.types as types  # noqa: PLR0402
from django_components.util.loader import ComponentFileEntry, get_component_dirs, get_component_files
from django_components.util.routing import URLRoute, URLRouteHandler
from django_components.util.types import Empty

# NOTE: Import built-in components last to avoid circular imports
from django_components.components import DynamicComponent, ErrorFallback

# isort: on


__all__ = [
    "AlreadyRegistered",
    "BaseNode",
    "CommandArg",
    "CommandArgGroup",
    "CommandHandler",
    "CommandLiteralAction",
    "CommandParserInput",
    "CommandSubcommand",
    "Component",
    "ComponentCache",
    "ComponentCommand",
    "ComponentDebugHighlight",
    "ComponentDefaults",
    "ComponentExtension",
    "ComponentFileEntry",
    "ComponentFormatter",
    "ComponentInput",
    "ComponentMediaInput",
    "ComponentMediaInputPath",
    "ComponentNode",
    "ComponentRegistry",
    "ComponentVars",
    "ComponentView",
    "ComponentsSettings",
    "ContextBehavior",
    "Default",
    "DependenciesStrategy",
    "DynamicComponent",
    "Empty",
    "ErrorFallback",
    "ExtensionComponentConfig",
    "FillNode",
    "NotRegistered",
    "OnComponentClassCreatedContext",
    "OnComponentClassDeletedContext",
    "OnComponentDataContext",
    "OnComponentInputContext",
    "OnComponentRegisteredContext",
    "OnComponentRenderedContext",
    "OnComponentUnregisteredContext",
    "OnRegistryCreatedContext",
    "OnRegistryDeletedContext",
    "OnRenderGenerator",
    "OnSlotRenderedContext",
    "OnTemplateCompiledContext",
    "OnTemplateLoadedContext",
    "ProvideNode",
    "RegistrySettings",
    "ShorthandComponentFormatter",
    "Slot",
    "SlotContent",
    "SlotContext",
    "SlotFallback",
    "SlotFunc",
    "SlotInput",
    "SlotNode",
    "SlotRef",
    "SlotResult",
    "TagFormatterABC",
    "TagProtectedError",
    "TagResult",
    "URLRoute",
    "URLRouteHandler",
    "all_components",
    "all_registries",
    "autodiscover",
    "cached_template",
    "component_formatter",
    "component_shorthand_formatter",
    "format_attributes",
    "get_component_by_class_id",
    "get_component_defaults",
    "get_component_dirs",
    "get_component_files",
    "get_component_url",
    "import_libraries",
    "merge_attributes",
    "register",
    "registry",
    "render_dependencies",
    "template_tag",
    "types",
]
