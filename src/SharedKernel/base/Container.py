import inspect
import sys
from abc import ABC
from typing import get_type_hints
_component_registry = []
_configuration_registry = []

def Component(cls):
    _component_registry.append((cls, "transient"))
    return cls

def Service(cls):
    _component_registry.append((cls, "singleton"))
    return cls

def Repository(cls):
    _component_registry.append((cls, "transient"))
    return cls

def Singleton(cls):
    _component_registry.append((cls, "singleton"))
    return cls

def Transient(cls):
    _component_registry.append((cls, "transient"))
    return cls

def Configuration(cls):
    _component_registry.append((cls, "singleton"))
    return cls

class Container:
    def __init__(self) -> None:
        self._registrations = {}

    # ========================
    # Registration methods
    # ========================

    def add_transient(self, interface, implementation):
        self._registrations[interface] = {
            "provider": lambda: self._create(implementation)
        }

    def add_singleton(self, interface, implementation):
        instance = None

        def provider():
            nonlocal instance 
            if instance is None:
                instance = self._create(implementation)
            return instance
        
        self._registrations[interface] = {
            "provider": provider
        }

    def add_instance(self, interface, instance):
        self._registrations[interface] = {
            "provider": lambda: instance
        }

    def add_factory(self, interface, factory_func):
        self._registrations[interface] = {
            "provider": factory_func
        }

    def try_add(self, interface, implementation):
        if interface not in self._registrations:
            self.add_transient(interface, implementation)

    # ========================
    # Scan components
    # ========================
    def scan_components(self):
        # Scan all modules in sys.modules to find concrete implementations of abstract classes
        for module_name, module in sys.modules.items():
            if module is None or not hasattr(module, '__dict__'):
                continue

            for name, obj in module.__dict__.items():
                if inspect.isclass(obj) and not inspect.isabstract(obj):
                    # Check if this class inherits from any abstract base class
                    for base in obj.__bases__:
                        if inspect.isabstract(base):
                            # Register this concrete class as implementation of the abstract base
                            if base not in self._registrations:
                                self.add_singleton(base, obj)

        # Also scan from decorator registry for backward compatibility
        for cls, lifecycle in _component_registry:
            if lifecycle == "singleton":
                for base in cls.__bases__:
                    if inspect.isabstract(base):
                        self.add_singleton(base, cls)
            else:
                for base in cls.__bases__:
                    if inspect.isabstract(base):
                        self.add_transient(base, cls)
        
    # ========================
    # Resolve
    # ========================
    def resolve(self, cls):
        return self._build(cls)

    def _build(self, cls):
        if cls in self._registrations:
            return self._registrations[cls]["provider"]()
        return self._create(cls)

    def _create(self, cls):
        params = [
            p for p in inspect.signature(cls.__init__).parameters.values()
            if p.name != 'self' 
            and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            and p.default == inspect.Parameter.empty
        ]

        # Resolve forward references
        type_hints = get_type_hints(cls.__init__)

        deps = []
        for p in params:
            if p.name not in type_hints:
                raise Exception(f"Missing type hint: {cls}.{p.name}")
            deps.append(self._build(type_hints[p.name]))

        return cls(*deps)