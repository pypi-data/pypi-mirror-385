from typing import Generic, TypeVar, Optional, Mapping
from pathlib import Path
from logging import Logger

from ...x_objects_base.carries_some_hooks_base import CarriesSomeHooksBase
from ...x_objects_base.x_object_serializable_mixin import XObjectSerializableMixin
from ...core.hooks.owned_hook import OwnedHook
from ...core.hooks.hook_protocols.owned_full_hook_protocol import OwnedFullHookProtocol
from ...core.nexus_system.nexus import Nexus
from ...core.nexus_system.update_function_values import UpdateFunctionValues
from ...core.nexus_system.nexus_manager import NexusManager
from ...core.nexus_system.default_nexus_manager import DEFAULT_NEXUS_MANAGER

EK = TypeVar("EK", bound=str)

ROOT_PATH_KEY: str = "root_path"

class XRootedPaths(CarriesSomeHooksBase[str, str|Path|None, "XRootedPaths"], XObjectSerializableMixin[str, str|Path|None], Generic[EK]):
    """
    Manages a root directory with associated elements (files or directories) and provides
    X object hooks for path management.

    This class maintains a root directory path and a set of elements that are relative
    to this root. It automatically computes absolute paths for each element based on the
    root directory and the element's relative path. All paths are exposed through
    X object hooks that can be linked to UI components or other systems.

    The class provides three types of hooks:
    1. Root directory hook: Exposes the root directory path (Path or None)
    2. Relative path hooks: Expose the relative path of each element (str or None)
    3. Absolute path hooks: Expose the computed absolute path of each element (Path or None)

    When the root directory changes, all absolute path hooks are automatically updated
    to reflect the new absolute paths. When a relative path changes, the corresponding
    absolute path is recalculated.

    Args:
        root_path_initial_value: Initial root directory path (Path or None)
        rooted_elements_initial_relative_path_values: Dictionary mapping element keys to their initial relative paths
        logger: Optional logger for debugging and error reporting.

    Example:
        >>> manager = XRootedPaths(Path("/project"), {"data": "data/", "config": "config/"})
        >>> manager.get_relative_path_hook("data").submit_single_value("data/")
        >>> # Absolute path for "data" will automatically be "/project/data/"

    Attributes:
        root_path: The root directory path (Path or None)
    """

    def element_key_to_absolute_path_key(self, key: EK) -> str:
        return f"{key}_absolute_path"
    def element_key_to_relative_path_key(self, key: EK) -> str:
        return f"{key}_relative_path"

    def __init__(
        self,
        root_path_initial_value: Optional[Path] = None,
        rooted_elements_initial_relative_path_values: dict[EK, str|None] = {},
        *,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER
    ):

        self._rooted_element_keys: set[EK] = set(rooted_elements_initial_relative_path_values.keys())
        self._rooted_element_path_hooks: dict[str, OwnedFullHookProtocol[Optional[str|Path]]] = {}

        # Initialize the hooks

        # root
        self._root_path_hook = OwnedHook[Optional[Path]](
            self,
            root_path_initial_value,
            logger=logger,
        )
        
        # elements paths
        for key in self._rooted_element_keys:

            # relative paths
            relative_path_key: str = self.element_key_to_relative_path_key(key)
            relative_path_initial_value: Optional[str] = rooted_elements_initial_relative_path_values[key]
            relative_path_hook = OwnedHook[Optional[str]](
                self,
                relative_path_initial_value,
                logger=logger,
            )
            self._rooted_element_path_hooks[relative_path_key] = relative_path_hook # type: ignore

            # absolute paths
            absolute_path_key: str = self.element_key_to_absolute_path_key(key)
            absolute_path_initial_value: Optional[Path] = root_path_initial_value / relative_path_initial_value if root_path_initial_value is not None and relative_path_initial_value is not None else None
            absolute_path_hook = OwnedHook[Optional[Path]](
                self,
                absolute_path_initial_value,
                logger=logger,
            )
            self._rooted_element_path_hooks[absolute_path_key] = absolute_path_hook # type: ignore

        def validate_complete_values_in_isolation_callback(
            self_ref: "XRootedPaths[EK]",
            values: Mapping[str, Path|str|None]) -> tuple[bool, str]:
            """
            Check if the values are valid as part of the owner.
            
            Values are provided for all hooks according to get_hook_keys().
            """

            root_path: Optional[Path] = values[ROOT_PATH_KEY] # type: ignore
            if root_path is not None and not isinstance(root_path, Path): # type: ignore
                return False, "Value must be a path"

            for key in self._rooted_element_keys:

                # Check the relative path
                relative_path: Optional[str] = values[self.element_key_to_relative_path_key(key)] # type: ignore
                if relative_path is not None and not isinstance(relative_path, str): # type: ignore
                    return False, "Value must be a string"
                
                # Check the absolute path
                absolute_path: Optional[Path] = values[self.element_key_to_absolute_path_key(key)] # type: ignore
                if root_path is not None:
                    if absolute_path is None:
                        return False, "The root path is set, so the absolute path must be set"
                    # Check if the absolute path is a subpath of the root path
                    if not absolute_path.is_relative_to(root_path):
                        return False, "Absolute path must be a subpath of the root path"
                    # Check if the root + relative path gives the absolute path
                    assert isinstance(relative_path, str)
                    if absolute_path != root_path / relative_path:
                        return False, "The root + relative path must give the absolute path"
                else:
                    if absolute_path is not None:
                        return False, "The root path is not set, so the absolute path must be None"
            return True, "Valid"

        def add_values_to_be_updated_callback(
            self_ref: "XRootedPaths[EK]",
            update_values: UpdateFunctionValues[str, Path|str|None]
        ) -> Mapping[str, Path|str|None]:
            """
            Add values to be updated.
            """

            additional_values: Mapping[str, Path|str|None] = {}
            if ROOT_PATH_KEY in update_values.submitted:
                root_path: Optional[Path] = update_values.submitted[ROOT_PATH_KEY] # type: ignore
            else:
                root_path = update_values.current.get(ROOT_PATH_KEY) # type: ignore
                additional_values[ROOT_PATH_KEY] = root_path

            for key in self._rooted_element_keys:

                # Take care of the relative path
                relative_path_key: str = self.element_key_to_relative_path_key(key)
                if relative_path_key in update_values.submitted:
                    relative_path: Optional[str] = update_values.submitted[relative_path_key] # type: ignore
                else:
                    relative_path = update_values.current.get(relative_path_key) # type: ignore
                    additional_values[relative_path_key] = relative_path

                # Take care of the absolute path
                absolute_path_key: str = self.element_key_to_absolute_path_key(key)
                if absolute_path_key not in update_values.submitted:
                    if root_path is not None and relative_path is not None:
                        # Ensure root_path is a Path object
                        if isinstance(root_path, str):
                            root_path = Path(root_path)
                        absolute_path: Optional[Path] = root_path / relative_path
                    else:
                        absolute_path = None
                    additional_values[absolute_path_key] = absolute_path

            return additional_values

        CarriesSomeHooksBase.__init__( # type: ignore
            self,
            validate_complete_values_in_isolation_callback=validate_complete_values_in_isolation_callback,
            add_values_to_be_updated_callback=add_values_to_be_updated_callback,
            logger=logger)

    ##########################################
    # Conversion methods
    ##########################################

    @property
    def root_path(self) -> Optional[Path]:
        return self._root_path_hook.value

    @root_path.setter
    def root_path(self, path: Optional[Path]) -> None:
        success, msg = self._root_path_hook.change_value(path)
        if not success:
            raise ValueError(msg)

    def get_relative_path_hook(self, key: EK) -> OwnedFullHookProtocol[Optional[str]]:
        return self._get_hook_by_key(self.element_key_to_relative_path_key(key)) # type: ignore

    def get_absolute_path_hook(self, key: EK) -> OwnedFullHookProtocol[Optional[Path]]:
        return self._get_hook_by_key(self.element_key_to_absolute_path_key(key)) # type: ignore

    def set_root_path(self, path: Optional[Path]) -> tuple[bool, str]:
        """Set the root path value."""
        return self._root_path_hook.change_value(path, raise_submission_error_flag=False)

    def set_relative_path(self, key: EK, path: Optional[str]) -> tuple[bool, str]:
        """Set the relative path for a specific element."""
        return self.get_relative_path_hook(key).change_value(path, raise_submission_error_flag=False)

    def set_absolute_path(self, key: EK, path: Optional[Path]) -> tuple[bool, str]:
        """Set the absolute path for a specific element (usually not recommended)."""
        return self.get_absolute_path_hook(key).change_value(path, raise_submission_error_flag=False)

    @property
    def rooted_element_keys(self) -> set[EK]:
        return self._rooted_element_keys

    @property
    def rooted_element_relative_path_hooks(self) -> dict[str, OwnedFullHookProtocol[Optional[str]]]:
        relative_path_hooks: dict[str, OwnedFullHookProtocol[Optional[str]]] = {}
        for key in self._rooted_element_keys:
            if key not in self._rooted_element_path_hooks:
                raise ValueError(f"Key {key} not found in rooted_element_relative_path_hooks")
            relative_path_hooks[key] = self._rooted_element_path_hooks[key] # type: ignore
        return relative_path_hooks

    @property
    def rooted_element_absolute_path_hooks(self) -> dict[str, OwnedFullHookProtocol[Optional[Path]]]:
        absolute_path_hooks: dict[str, OwnedFullHookProtocol[Optional[Path]]] = {}
        for key in self._rooted_element_keys:
            if key not in self._rooted_element_path_hooks:
                raise ValueError(f"Key {key} not found in rooted_element_absolute_path_hooks")
            absolute_path_hooks[key] = self._rooted_element_path_hooks[key] # type: ignore
        return absolute_path_hooks

    ##########################################
    # CarriesHooks interface implementation
    ##########################################

    def _get_hook_by_key(self, key: str) -> OwnedFullHookProtocol[Path|str|None]:
        """
        Get a hook by its key.
        """
        if key == ROOT_PATH_KEY:
            return self._root_path_hook # type: ignore
        elif key in self._rooted_element_path_hooks:
            return self._rooted_element_path_hooks[key] # type: ignore
        else:
            raise ValueError(f"Key {key} not found in hooks")

    def _get_hook_keys(self) -> set[str]:
        """
        Get all keys of the hooks.
        """
        keys = {ROOT_PATH_KEY}
        for key in self._rooted_element_keys:
            keys.add(self.element_key_to_relative_path_key(key))
            keys.add(self.element_key_to_absolute_path_key(key))
        return keys

    def _get_value_by_key(self, key: str) -> Path|str|None:
        """
        Get the value of a hook by its key.
        """
        if key == ROOT_PATH_KEY:
            return self._root_path_hook.value
        elif key in self._rooted_element_path_hooks:
            return self._rooted_element_path_hooks[key].value # type: ignore
        else:
            raise ValueError(f"Key {key} not found in hooks")

    def _get_key_by_hook_or_nexus(self, hook_or_nexus: OwnedFullHookProtocol[Path|str|None]|Nexus[Path|str|None]) -> EK:
        """
        Get the key of a hook or nexus.
        """
        
        if isinstance(hook_or_nexus, OwnedFullHookProtocol):
            if hook_or_nexus is self._root_path_hook:
                return ROOT_PATH_KEY # type: ignore
            else:
                for hook_key, hook in self._rooted_element_path_hooks.items():
                    if hook == hook_or_nexus:
                        return hook_key # type: ignore
                raise ValueError(f"Key {hook_or_nexus} not found in _rooted_element_path_hooks")
        elif isinstance(hook_or_nexus, Nexus): # type: ignore
            if hook_or_nexus is self._root_path_hook._get_nexus(): # type: ignore
                return ROOT_PATH_KEY # type: ignore
            else:
                for hook_key, hook in self._rooted_element_path_hooks.items():
                    if hook._get_nexus() is hook_or_nexus: # type: ignore
                        return hook_key # type: ignore
            raise ValueError(f"Key {hook_or_nexus} not found in _rooted_element_path_hooks")
        else:
            raise ValueError(f"Expected HookWithOwnerProtocol or HookNexus, got {type(hook_or_nexus)}")

    #### ObservableSerializable implementation ####
    
    def get_values_for_serialization(self) -> Mapping[str, Path|str|None]:
        root_path: Optional[Path] = self._root_path_hook.value
        if root_path is not None and not isinstance(root_path, Path): # type: ignore
            raise ValueError("Root path must be a path")
        rooted_elements_initial_relative_path_values: dict[EK, str|None] = {}
        for key in self._rooted_element_keys:
            relative_path_key: str = self.element_key_to_relative_path_key(key)
            relative_path: Optional[str] = self._rooted_element_path_hooks[relative_path_key].value # type: ignore
            if relative_path is not None and not isinstance(relative_path, str): # type: ignore
                raise ValueError("Relative path must be a string")
            rooted_elements_initial_relative_path_values[key] = relative_path
        return {ROOT_PATH_KEY: root_path, **rooted_elements_initial_relative_path_values}
    
    def set_values_from_serialization(self, values: Mapping[str, Path|str|None]) -> None:
        root_path: Optional[Path] = values[ROOT_PATH_KEY] # type: ignore
        if root_path is not None and not isinstance(root_path, Path): # type: ignore
            raise ValueError("Root path must be a path")
        
        # Build the values dict for submission
        values_to_submit: dict[str, Path|str|None] = {ROOT_PATH_KEY: root_path}
        
        for key in self._rooted_element_keys:
            # Get the relative path from the serialized data (without _relative_path suffix)
            relative_path: Optional[str] = values[key] # type: ignore
            if relative_path is not None and not isinstance(relative_path, str): # type: ignore
                raise ValueError("Relative path must be a string")
            
            # Add it to submission dict with the correct key (with _relative_path suffix)
            relative_path_key: str = self.element_key_to_relative_path_key(key)
            values_to_submit[relative_path_key] = relative_path

        # Submit all values at once using BaseCarriesHooks.submit_values
        success, msg = self._submit_values(values_to_submit) # type: ignore
        if not success:
            raise ValueError(f"Failed to set values from serialization: {msg}")