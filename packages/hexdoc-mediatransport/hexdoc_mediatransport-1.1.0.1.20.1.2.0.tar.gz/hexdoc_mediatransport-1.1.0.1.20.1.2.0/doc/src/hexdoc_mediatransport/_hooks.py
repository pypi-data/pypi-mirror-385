from importlib.resources import Package
from typing import Any

from hexdoc.plugin import (
    HookReturn,
    ModPlugin,
    ModPluginImpl,
    ModPluginWithBook,
    hookimpl,
)
from typing_extensions import override

import hexdoc_mediatransport

from . import diagrams
from .__gradle_version__ import FULL_VERSION, MINECRAFT_VERSION, MOD_ID, MOD_VERSION
from .__version__ import PY_VERSION
from .api import ExtensionSection
from .book import pages
from .plugins import MediaTransportPlugins
from .prettylog import info


class MediaTransportContext:
    diagrams = diagrams
    extensions: list[ExtensionSection] | None = None

    @staticmethod
    def filter_extensions(ids: list[str]):
        if MediaTransportContext.extensions is None:
            raise ValueError("Too early, somehow")
        return [x for x in MediaTransportContext.extensions if x.id in ids]


class MediaTransportPlugin(ModPluginImpl):
    @staticmethod
    @hookimpl
    def hexdoc_mod_plugin(branch: str) -> ModPlugin:
        plugin_loader = MediaTransportPlugins()

        MediaTransportContext.extensions = plugin_loader.get_sections()
        diagrams.symbols = plugin_loader.get_symbols()
        diagrams.plurals = plugin_loader.get_plurals()
        return MediaTransportModPlugin(branch=branch)

    @staticmethod
    @hookimpl
    def hexdoc_load_tagged_unions() -> HookReturn[Package]:
        return [pages]

    @staticmethod
    @hookimpl
    def hexdoc_update_template_args(template_args: dict[str, Any]) -> None:
        template_args["mediatransport"] = MediaTransportContext


class MediaTransportModPlugin(ModPluginWithBook):
    @property
    @override
    def modid(self) -> str:
        return MOD_ID

    @property
    @override
    def full_version(self) -> str:
        return FULL_VERSION

    @property
    @override
    def mod_version(self) -> str:
        return f"{MOD_VERSION}+{MINECRAFT_VERSION}"

    @property
    @override
    def plugin_version(self) -> str:
        return PY_VERSION

    @override
    def resource_dirs(self) -> HookReturn[Package]:
        # lazy import because generated may not exist when this file is loaded
        # eg. when generating the contents of generated
        # so we only want to import it if we actually need it
        from ._export import generated

        return generated

    @override
    def jinja_template_root(self) -> tuple[Package, str]:
        return hexdoc_mediatransport, "_templates"
