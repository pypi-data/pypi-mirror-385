import inspect
import os
import re
from typing import NamedTuple

from qtpy.QtCore import QObject

from bec_widgets.utils.name_utils import pascal_to_snake

EXCLUDED_PLUGINS = ["BECConnector", "BECDock"]
_PARENT_ARG_REGEX = r".__init__\(\s*(?:parent\)|parent=parent,?|parent,?)"
_SELF_PARENT_ARG_REGEX = r".__init__\(\s*self,\s*(?:parent\)|parent=parent,?|parent,?)"
SUPER_INIT_REGEX = re.compile(r"super\(\)" + _PARENT_ARG_REGEX, re.MULTILINE)


class PluginFilenames(NamedTuple):
    register: str
    plugin: str
    pyproj: str


def plugin_filenames(name: str) -> PluginFilenames:
    return PluginFilenames(f"register_{name}.py", f"{name}_plugin.py", f"{name}.pyproject")


class DesignerPluginInfo:
    def __init__(self, plugin_class):
        self.plugin_class = plugin_class
        self.plugin_name_pascal = plugin_class.__name__
        self.plugin_name_snake = pascal_to_snake(self.plugin_name_pascal)
        self.widget_import = f"from {plugin_class.__module__} import {self.plugin_name_pascal}"
        plugin_module = (
            ".".join(plugin_class.__module__.split(".")[:-1]) + f".{self.plugin_name_snake}_plugin"
        )
        self.plugin_import = f"from {plugin_module} import {self.plugin_name_pascal}Plugin"

        # first sentence / line of the docstring is used as tooltip
        self.plugin_tooltip = (
            plugin_class.__doc__.split("\n")[0].strip().replace('"', "'")
            if plugin_class.__doc__
            else self.plugin_name_pascal
        )

        self.base_path = os.path.dirname(inspect.getfile(plugin_class))


class DesignerPluginGenerator:
    def __init__(self, widget: type):
        self._excluded = False
        self.widget = widget
        self.info = DesignerPluginInfo(widget)
        if widget.__name__ in EXCLUDED_PLUGINS:

            self._excluded = True
            return

        self.templates: dict[str, str] = {}
        self.template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "plugin_templates"
        )

    @property
    def filenames(self):
        return plugin_filenames(self.info.plugin_name_snake)

    def run(self, validate=True):
        if self._excluded:
            print(f"Plugin {self.widget.__name__} is excluded from generation.")
            return
        if validate:
            self._check_class_validity()
        self._load_templates()
        self._write_templates()

    def _check_class_validity(self):

        # Check if the widget is a QWidget subclass
        if not issubclass(self.widget, QObject):
            return

        # Check if the widget class has parent as the first argument. This is a strict requirement of Qt!
        signature = list(inspect.signature(self.widget.__init__).parameters.values())
        if len(signature) == 1 or signature[1].name != "parent":
            raise ValueError(
                f"Widget class {self.widget.__name__} must have parent as the first argument."
            )

        base_cls = [val for val in self.widget.__bases__ if issubclass(val, QObject)]
        if not base_cls:
            raise ValueError(
                f"Widget class {self.widget.__name__} must inherit from a QObject subclass."
            )

        # Check if the widget class calls the super constructor with parent argument
        init_source = inspect.getsource(self.widget.__init__)
        class_re = re.compile(base_cls[0].__name__ + _SELF_PARENT_ARG_REGEX, re.MULTILINE)
        cls_init_found = class_re.search(init_source) is not None
        super_self_re = re.compile(
            rf"super\({base_cls[0].__name__}, self\)" + _PARENT_ARG_REGEX, re.MULTILINE
        )
        super_init_found = super_self_re.search(init_source) is not None
        if issubclass(self.widget.__bases__[0], QObject) and not super_init_found:
            super_init_found = SUPER_INIT_REGEX.search(init_source) is not None

        # for the new style classes, we only have one super call. We can therefore check if the
        # number of __init__ calls is 2 (the class itself and the super class)
        num_inits = re.findall(r"__init__", init_source)
        if len(num_inits) == 2 and not super_init_found:
            super_init_found = SUPER_INIT_REGEX.search(init_source) is not None

        if not cls_init_found and not super_init_found:
            raise ValueError(
                f"Widget class {self.widget.__name__} must call the super constructor with parent."
            )

    def _write_file(self, name: str, contents: str):
        with open(os.path.join(self.info.base_path, name), "w", encoding="utf-8") as f:
            f.write(contents)

    def _format(self, name: str):
        return self.templates[name].format(**self.info.__dict__)

    def _write_templates(self):
        self._write_file(self.filenames.register, self._format("register"))
        self._write_file(self.filenames.plugin, self._format("plugin"))
        pyproj = str({"files": [f"{self.info.plugin_class.__module__.split('.')[-1]}.py"]})
        self._write_file(self.filenames.pyproj, pyproj)

    def _load_templates(self):
        for file in os.listdir(self.template_path):
            if not file.endswith(".template"):
                continue
            with open(os.path.join(self.template_path, file), "r", encoding="utf-8") as f:
                self.templates[file.split(".")[0]] = f.read()


if __name__ == "__main__":  # pragma: no cover
    # from bec_widgets.widgets.bec_queue.bec_queue import BECQueue
    from bec_widgets.widgets.utility.spinner import SpinnerWidget

    generator = DesignerPluginGenerator(SpinnerWidget)
    generator.run(validate=False)
