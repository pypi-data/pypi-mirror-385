import re
import builtins
# import numpy as np
import math
import sys
import logging
import warnings
from abc import ABC
from typing import Tuple, List, Any, Literal, Dict, Type, TypeVar, get_origin, Union, get_type_hints
from enum import Enum

# log
logger = logging.getLogger('mobject')

# Regular expressions to match type annotations for List and Dict from typing module
list_pattern = re.compile(r'typing\.List\[(.+)\]', re.IGNORECASE)
dict_pattern = re.compile(r'typing\.Dict\[(.+),\s*(.+)\]', re.IGNORECASE)
typing_pattern = re.compile(r'typing\.(.*)')


# full static function to set nested properties by . notation


MOBJECT = TypeVar("MOBJECT", bound='MObject')
ENUM = TypeVar("ENUM", bound=Enum)

class MObject(ABC):
    """
    Abstract base class providing utilities for handling nested properties
    and setting up keys, types, and translation mechanisms for subclasses.
    """
    
    # Define tuples to store keys of different types
    __keys__: Tuple[str, ...] = ()
    _config_keys_k: Tuple[str, ...] = ()

    # can be set if a specific build order is required
    _build_order: Tuple[str, ...] | None = None

    # Class Mapper for potentional None init Properties
    # _class_mapper: dict = {} # deprecrated use _key_mapper
    _key_mapper: Dict[str, Tuple[Literal['_k', '_i', '_r'], Type[Any]]] = {}

    # exclusion list for properties
    _exclusion_list: List[str] = ['json', '__dict__', 'dict']
    
    # include properties to keys
    _inlcude_properties: bool = False

    # properties
    _input_keys: Tuple[str, ...] = ()
    @property
    def InputKeys(self):
        return [self._translate_output_key(key) for key in self._input_keys]
    
    _result_keys: Tuple[str, ...] = ()
    @property
    def ResultKeys(self):
        return [self._translate_output_key(key) for key in self._result_keys]
    
    _class_name_k: str = ""
    @property
    def ClassName(self):
        return self.__class__.__name__
    
    @property
    def dict(self):
        return self.to_dict()

    @property
    def json(self):
        return self.to_dict(serializable=True)

    def get_nested_property(self, props: List[str], serializable: bool = False):
        """        
        Args:
            props: List of property names, ordered by depth.
        
        Returns:
            The value of the nested property.
        """
        attribute = getattr(self, props[0])
        if len(props) == 1:
            if not serializable:
                return attribute
            return self._get_property(attribute, serializable=serializable)
        else:
            if hasattr(attribute, 'get_nested_property'):
                return getattr(attribute, 'get_nested_property')(props[1:], serializable=serializable)
            return self._get_property(attribute, serializable=serializable)

    def set_nested_property(self, props: List[str], val: Any, translate: bool = False): # type: ignore
        """
        Recursively set a nested property on an object using a list of property names.
        
        Args:
            obj: The object to set the property on.
            props: List of property names, ordered by depth.
            val: The value to assign to the property.
        """
        if len(props) == 1:
            if hasattr(self, props[0]):
                self._set_property(props[0], val)
        else:
            new_obj = getattr(self, props[0], None)
            if new_obj is not None:
                setter = getattr(new_obj, 'set_nested_property', None)
                if setter is not None:
                    setter(props[1:], val)
                else:
                    setattr(new_obj, props[1], val)
        
    @staticmethod
    def set_enum(val: int | str | Enum, enum: Type[ENUM]) -> ENUM:
        if isinstance(val, enum):
            return val
        elif isinstance(val, int):
            return enum(val)
        else:
            try:
                return enum[str(val).upper()]
            except (KeyError, ValueError) as e:
                logger.warning(f"Cannot convert {val} to {enum.__name__} with {str(e)}! Using first enum Entry!")
                return next(iter(enum))

    @classmethod
    def set(cls: Type[MOBJECT], val: Dict[str, Any] | MOBJECT) -> MOBJECT:
        instance = None
        if isinstance(val, dict):
            instance = cls(**val)
        else:
            instance = val
        return instance

    @classmethod
    def collect_annotations(cls: Type[Any]) -> Dict[str, Any]:
        annotations: Dict[str, Any] = {}
        if hasattr(cls, '__annotations__'):
            annotations.update(cls.__annotations__)
        if hasattr(cls, '__bases__'):
            for base in cls.__bases__:
                if hasattr(base, 'collect_annotations'):
                    annotations.update(getattr(base, 'collect_annotations')())

        return annotations

    @classmethod
    def collect_properties(cls: Type['MObject']) -> List[str]:
        """
        Collects all properties of a given class, including inherited properties.

        Args:
            cls (Type): The class to inspect.

        Returns:
            List[str]: A list of property names.
        """
        properties: list[str] = []
        for base in cls.__mro__:  # Check the entire method resolution order (MRO)
            for name, attr in base.__dict__.items():
                if isinstance(attr, property):
                    properties.append(name)
        return properties
    
    def _translate_input_key(self, inp_key: str, suffix: Literal['_k', '_i', '_r']):
        """
        Translate a camel-case input key into snake_case format, appending the given prefix.
        
        Args:
            inp_key: The camel-case key to translate.
            prefix: The suffix to append after translation ('_k', '_i', or '_r').

        Returns:
            The translated snake_case key.
        """
        result: list[str] = []
        for char in inp_key:
            if char.isupper():
                result.extend(['_', char.lower()])
            else:
                result.append(char)
        result.append(suffix)
        return ''.join(result)

    def _translate_output_key(self, out_key: str):
        """
        Translate a snake_case key back into camel-case format by splitting on underscores.
        
        Args:
            out_key: The snake_case key to translate.
        
        Returns:
            The translated camel-case key.
        """
        out = out_key[1:-2].split("_")
        out = [k.capitalize() for k in out]
        return ''.join(out)

    def _setup(self):
        """
        Set up keys, categorize them into input, config, and result keys, 
        and map class types for key translation and property setting.
        """
        keys: set[str] = set()
        input_keys: set[str] = set()
        config_keys: set[str] = set()
        result_keys: set[str] = set()

        # Maps the last character of the key (e.g., _i, _k, _r) to corresponding sets
        prefix_mapper = {
            'i': input_keys,
            'k': config_keys,
            'r': result_keys
        }

        key_mapper = {}

        annotations = self.collect_annotations()
       
        for key, type_annotation in annotations.items():
            out_key = self._translate_output_key(key)
            if out_key in key_mapper:
                continue
            if key[-2:] in ['_i', '_k', '_r']:
                keys.add(key)
                prefix_mapper[key[-1]].add(key)
                if key[-1] == 'r':
                    continue    # skip result keys
                attr = getattr(self, key, None)
                if attr is not None:
                    key_mapper[self._translate_output_key(key)] = ('_' + key[-1], type(attr)) # type: ignore
                else:
                    if hasattr(type_annotation, '__args__'):
                        classes = getattr(type_annotation, '__args__')
                        classes = [class_ for class_ in classes if hasattr(class_, '__name__') and class_.__name__ != 'NoneType']
                    
                    else:
                        classes = [self._get_class(type_annotation)]
                    key_mapper[self._translate_output_key(key)] = ('_' + key[-1], self._get_class(classes[0])) # type: ignore

        # Assign collected keys and mappings to instance attributes
        self.__keys__ = tuple(keys)
        self._input_keys = tuple(input_keys)
        self._config_keys_k = tuple(config_keys)
        self._result_keys = tuple(result_keys)
        self._key_mapper = key_mapper

    def _get_class(self, class_: Type[Any]):
        """
        Resolve a class object from a type annotation string or from built-in types.
        
        Args:
            class_: The class type or string representation of the type.
        
        Returns:
            The resolved class object.
        """
        if isinstance(class_, type): # type: ignore
            return class_
        typing_match = typing_pattern.match(str(class_))
        if typing_match:
            if hasattr(class_, '_name'):
                # Handle List types
                match = list_pattern.match(str(class_))
                if match:
                    return getattr(builtins, match.group(1))
                # Handle Dict types
                match = dict_pattern.match(str(class_))
                if match:
                    return self._get_class(match.group(1)), self._get_class(match.group(2))
            else:
                return class_
        else:
            if hasattr(builtins, str(class_)):
                return getattr(builtins, str(class_))

    def _set_property(self, key: str, val: Any):
        """
        Set a property based on the key, translating it to the internal format and validating the type.
        
        Args:
            key: The external key used for setting the value. It is the CamelCase Variant
            val: The value to assign to the property.
        """
        suffix, class_ = self._key_mapper.get(key, (None, None))
        class_prop = getattr(self.__class__, key, None)
        if class_prop:
            has_setter = isinstance(class_prop, property) and class_prop.fset is not None
            if has_setter and val is not None:
                try:
                    setattr(self, key, val)
                except Exception as ex:
                    logger.warning(f"Failed to set property {key} with {self.ClassName} using value {val} with {str(ex)}")
                finally:
                    return
        if suffix is not None and class_ is not None:
            key_property = self._translate_input_key(key, suffix)
            if val is None:
                if self._is_optional_type(key_property):
                    setattr(self, key_property, val)
                    return
                try:
                    cls_prp = getattr(self, key_property)
                    if cls_prp is None:
                        setattr(self, key_property, class_())
                except Exception:
                    logger.warning(f"Failed to set property {key_property} with {class_} using default constructor ()")
                finally:
                    return
            try:
                setattr(self, key_property, class_(val))
            except TypeError as ex:
                logger.warning(f"Failed to set attribute {key_property} with {class_} using value {val} with {str(ex)}")

    def _get_property(self, val: Any, serializable: bool = True) -> Any:
        
        if val is None:
            return None

        if hasattr(val, 'to_dict'):
            return getattr(val, 'to_dict')()
        else:
            if serializable:
                # float handling
                if isinstance(val, float):
                    if math.isinf(val):
                        return sys.float_info.max if val > 0 else -sys.float_info.max
                    elif math.isnan(val):
                        return None
                    return val
                
                # array-like handling (numpy, pandas, etc.) usually implement tolist()
                if hasattr(val, 'tolist') and callable(getattr(val, 'list')):
                    try:
                        return val.tolist()
                    except Exception:
                        pass
                
                # enum handler --> readable output using the name
                if isinstance(val, (Enum)):
                    return val.name 
                
                # handling generic sized 1ds: lists / tuples
                if isinstance(val, (list, tuple)):
                    list_out: list[Any] = []
                    for item in val: # type: ignore
                        list_out.append(self._get_property(item, serializable=serializable))
                    return list_out
                
                # handling key <-> value objects: dict
                if isinstance(val, dict):
                    dict_out: Dict[str, Any] = {}
                    for dkey, item in val.items(): # type: ignore
                        dict_out[dkey] = self._get_property(item, serializable=serializable)
                    return dict_out
                
                # simple generics w/o strings, chars
                if isinstance(val, (int, float, bool)):
                    return val
                
                # all others including strings
                return str(val)
            
            else:
                return val

    def _is_optional_type(self, key_property: str) -> bool:
        type_hints = get_type_hints(self.__class__)[key_property]
        if get_origin(type_hints) == Union:
            return True
        return False

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        Initialize the object, setting up key mappings and assigning properties
        based on keyword arguments passed in.

        Args:
            **kwargs: Property values to assign during initialization.
        """
        self._exclusion_list = ['json', '__dict__', 'dict']
        
        super().__init__()
        self._setup()

        if self._build_order is None:
            for key, value in kwargs.items():
                self._set_property(key, value)
        else:
            for prp in self._build_order:
                key = self._translate_output_key(prp)
                self._set_property(key, kwargs.get(key, None))
     
    def to_dict(
            self, 
            serializable: bool = True, 
            exclude: List[str] = [],
        ) -> Dict[str, Any]:
        warnings.warn(
            "to_dict is deprecrated and is supposed to be private"
            "Use Properties 'json' or 'dict'",
            category=DeprecationWarning,
            stacklevel=2
        )
        self._exclusion_list.extend(exclude)
        keys: set[str] = set()
        out: Dict[str, Any] = dict()
        for key in self.__keys__:
            keys.add(self._translate_output_key(key))
        if self._inlcude_properties:
            for key in self.collect_properties():
                keys.add(key)

        for key in keys:
            if key in self._exclusion_list:
                continue
            inp_val = getattr(self, key, None)
            value: Any = self._get_property(inp_val, serializable=serializable)
            if value is not None:
                out[key] = value
        return out
    
    def cast(self, cls: Type[Any]) -> 'MObject':
        if issubclass(cls, MObject):
            return cls(**self.to_dict(serializable=False))
        else:
            raise TypeError(f"{cls.__class__.__name__} is not a derived class of MOBJECT")