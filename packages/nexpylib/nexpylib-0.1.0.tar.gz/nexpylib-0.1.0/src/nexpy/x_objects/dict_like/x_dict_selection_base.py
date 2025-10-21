from typing import Iterable, Literal, TypeVar, Generic, Optional, Mapping, Any, Callable
from logging import Logger
from abc import ABC, abstractmethod

from ...core.hooks.hook_aliases import Hook, ReadOnlyHook
from ...core.hooks.hook_protocols.managed_hook_protocol import ManagedHookProtocol
from ...x_objects_base.x_complex_base import XComplexBase
from .protocols import XDictProtocol
from ...core.auxiliary.listening_base import ListeningBase
from ...core.nexus_system.update_function_values import UpdateFunctionValues
from ...core.nexus_system.nexus_manager import NexusManager
from ...core.nexus_system.default_nexus_manager import DEFAULT_NEXUS_MANAGER
from ...core.nexus_system.submission_error import SubmissionError

K = TypeVar("K")
V = TypeVar("V")
KT = TypeVar("KT")  # Key type (can be Optional[K] for optional variants)
VT = TypeVar("VT")  # Value type (can be Optional[V] for optional variants)

class XDictSelectionBase(
    XComplexBase[
        Literal["dict", "key", "value"], 
        Literal["keys", "values", "length"], 
        Any, 
        set[K]|list[V]|int, 
        "XDictSelectionBase[K, V, KT, VT]"
    ], 
    XDictProtocol[K, V],
    ListeningBase, 
    Generic[K, V, KT, VT], 
    ABC
):
    """
    Four Variants (see their specific docs for behavior matrices):
    ┌────────────────────────────────────┬───────────────┬────────────────────┐
    │ Variant                            │ if key is None│ if key not in dict │
    ├────────────────────────────────────┼───────────────┼────────────────────┤
    │ XSelectionDict                     │     error     │       error        │
    │ XOptionalSelectionDict             │     None      │       error        │
    │ XSelectionDictWithDefault          │     error     │      default       │
    │ XOptionalSelectionDictWithDefault  │     None      │      default       │
    └────────────────────────────────────┴───────────────┴────────────────────┘
    
    Type Parameters:
        K: Dictionary key type
        V: Dictionary value type
        KT: Actual key type (K or Optional[K] for optional variants)
        VT: Actual value type (V or Optional[V] for optional variants)
    
    Subclasses must implement:
        - _create_add_values_callback(): Creates the add_values_to_be_updated_callback
        - _create_validation_callback(): Creates the validate_complete_values_in_isolation_callback
        - _compute_initial_value(): Computes the initial value from dict and key
    """

    def __init__(
        self,
        dict_hook: Mapping[K, V] | Hook[Mapping[K, V]] | ReadOnlyHook[Mapping[K, V]] | XDictProtocol[K, V],
        key_hook: KT | Hook[KT] | ReadOnlyHook[KT],
        value_hook: Optional[Hook[VT]] | ReadOnlyHook[VT] = None,
        *,
        invalidate_callback: Optional[Callable[[], None]] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER
    ):
        """
        Initialize the XDictSelectionBase.
        
        Args:
            dict_hook: The mapping or hook containing the mapping
            key_hook: The initial key or hook
            value_hook: Optional hook for the value (if None, will be computed)
            logger: Optional logger for debugging
            invalidate_callback: Optional callback called after value changes
        """
        
        if isinstance(dict_hook, (Hook, ReadOnlyHook)):
            _initial_dict_value: Mapping[K, V] = dict_hook.value
        elif isinstance(dict_hook, Mapping):
            _initial_dict_value = dict_hook
        else:
            raise ValueError("dict_hook must be a Hook, ReadOnlyHook, or Mapping")

        if isinstance(key_hook, ManagedHookProtocol):
            _initial_key_value: KT = key_hook.value  # type: ignore
        else:
            _initial_key_value = key_hook

        # Compute initial value if not provided
        if value_hook is None:
            _initial_value_value: VT = self._compute_initial_value(
                _initial_dict_value,
                _initial_key_value  # type: ignore
            )
        else:
            if not isinstance(value_hook, ManagedHookProtocol):  # type: ignore
                raise ValueError("value_hook must be a Hook or ReadOnlyHook or None")
            _initial_value_value = value_hook.value

        # Initialize ListeningBase
        ListeningBase.__init__(self, logger)
        
        # Initialize XComplexBase
        XComplexBase.__init__(  # type: ignore
            self,
            initial_hook_values={
                "dict": dict_hook if isinstance(dict_hook, ManagedHookProtocol) else _initial_dict_value,
                "key": key_hook if not (key_hook is None or (isinstance(key_hook, type(None)))) else _initial_key_value,
                "value": value_hook if value_hook is not None else _initial_value_value
            },
            secondary_hook_callbacks={
                "keys": lambda values: set(values["dict"].keys()) if values["dict"] is not None else set(),  # type: ignore
                "values": lambda values: list(values["dict"].values()) if values["dict"] is not None else list(),  # type: ignore
                "length": lambda values: len(values["dict"]) if values["dict"] is not None else 0  # type: ignore
            },
            verification_method=self._create_validation_callback(),
            add_values_to_be_updated_callback=self._create_add_values_callback(),
            invalidate_callback=invalidate_callback,
            output_value_wrapper={
                "dict": lambda x: dict(x) # type: ignore
            },
            logger=logger,
            nexus_manager=nexus_manager
        )

    @abstractmethod
    def _create_add_values_callback(self) -> Callable[
        [Any, UpdateFunctionValues[Literal["dict", "key", "value"], Any]], 
        Mapping[Literal["dict", "key", "value"], Any]
    ]:
        """
        Create the add_values_to_be_updated_callback for this X object.
        
        This callback is responsible for completing partial value submissions.
        Each subclass implements its own logic for handling different combinations
        of dict/key/value submissions.
        
        Returns:
            A callback function that takes (self, current_values, submitted_values)
            and returns additional values to be updated.
        """
        ...

    @abstractmethod
    def _create_validation_callback(self) -> Callable[
        [Mapping[Literal["dict", "key", "value"], Any]], 
        tuple[bool, str]
    ]:
        """
        Create the validate_complete_values_in_isolation_callback for this X object.
        
        This callback validates that a complete set of values (dict, key, value)
        represents a valid state. Each subclass can implement its own validation logic.
        
        Returns:
            A callback function that takes (values) and returns (is_valid, message).
        """
        ...

    @abstractmethod
    def _compute_initial_value(self, initial_dict: Mapping[K, V], initial_key: KT) -> VT:
        """
        Compute the initial value from the dict and key.
        
        Args:
            initial_dict: The initial dictionary
            initial_key: The initial key
            
        Returns:
            The computed initial value
        """
        ...

    ########################################################
    # Common properties
    ########################################################

    @property
    def dict_hook(self) -> Hook[Mapping[K, V]]:
        """
        Get the dictionary hook.
        
        Returns:
            The hook managing the dictionary value as Map (immutable).
            
        Note:
            Returns Map to enforce immutability. Attempting to mutate
            the returned dict will raise TypeError. All modifications should go
            through change_dict() or submit_values().
        """
        return self._primary_hooks["dict"]

    @property
    def dict(self) -> dict[K, V]:
        """
        Get the dictionary value.
        """
        return self._value_wrapped("dict") # type: ignore

    @dict.setter
    def dict(self, value: Mapping[K, V]) -> None:
        """
        Set the dictionary value.
        """
        self.change_dict(value)

    def change_dict(self, value: Mapping[K, V], *, logger: Optional[Logger] = None, raise_submission_error_flag: bool = True) -> None:
        """
        Change the dictionary behind this hook.
        
        Args:
            value: The new mapping
        """
        success, msg = self._submit_value("dict", value, logger=logger)
        if not success and raise_submission_error_flag:
            raise SubmissionError(msg, value, "dict")

    @property
    def key_hook(self) -> Hook[KT]:
        """
        Get the key hook.
        
        Returns:
            The hook managing the dictionary key.
        """
        return self._primary_hooks["key"]

    @property
    def key(self) -> KT:
        """
        Get the key behind this hook.
        """
        return self._value_wrapped("key") # type: ignore
    
    @key.setter
    def key(self, value: KT) -> None:
        """
        Set the key behind this hook.
        """
        self.change_key(value)

    def change_key(self, value: KT, *, logger: Optional[Logger] = None, raise_submission_error_flag: bool = True) -> None:
        """
        Change the key behind this hook.
        """
        success, msg = self._submit_value("key", value, logger=logger)
        if not success and raise_submission_error_flag:
            raise SubmissionError(msg, value, "key")

    @property
    def value_hook(self) -> Hook[VT]:
        """
        Get the value hook.
        
        Returns:
            The hook managing the retrieved value.
        """
        return self._primary_hooks["value"]

    @property
    def value(self) -> VT:
        """
        Get the value behind this hook.
        """
        return self._value_wrapped("value") # type: ignore

    @value.setter
    def value(self, value: VT) -> None:
        """
        Set the value behind this hook.
        """
        self.change_value(value)

    def change_value(self, value: VT, *, logger: Optional[Logger] = None, raise_submission_error_flag: bool = True) -> None:
        """
        Change the value behind this hook.
        """
        success, msg = self._submit_value("value", value, logger=logger)
        if not success and raise_submission_error_flag:
            raise SubmissionError(msg, value, "value")

    # ------------------------- length -------------------------

    @property
    def length_hook(self) -> ReadOnlyHook[int]:
        """
        Get the length hook (read-only).
        """
        return self._secondary_hooks["length"] # type: ignore

    @property
    def length(self) -> int:
        """
        Get the length behind this hook.
        """
        return self._value_wrapped("length") # type: ignore

    # ------------------------- keys -------------------------

    @property
    def keys_hook(self) -> ReadOnlyHook[Iterable[K]]:
        """
        Get the keys hook (read-only).
        
        Returns:
            A read-only hook containing an iterable of dictionary keys.
        """
        return self._secondary_hooks["keys"] # type: ignore

    @property
    def keys(self) -> set[K]:
        """
        Get the keys behind this hook as an immutable set.
        
        Returns:
            A set of all keys in the dictionary.
        """
        return self._value_wrapped("keys") # type: ignore

    # ------------------------- values -------------------------

    @property
    def values_hook(self) -> ReadOnlyHook[Iterable[V]]:
        """
        Get the values hook (read-only).
        """
        return self._secondary_hooks["values"] # type: ignore

    @property
    def values(self) -> list[V]:
        """
        Get the values behind this hook.
        """
        return self._value_wrapped("values") # type: ignore