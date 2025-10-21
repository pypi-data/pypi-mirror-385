from typing import TypeVar, Protocol, runtime_checkable, Iterable

from ...core.hooks.hook_aliases import Hook, ReadOnlyHook


T = TypeVar("T")

@runtime_checkable
class XListProtocol(Protocol[T]):

    #-------------------------------- list value --------------------------------

    @property
    def list_hook(self) -> Hook[Iterable[T]]:
        """
        Get the hook for the list - it can contain any iterable as long as it can be converted to a list.
        """
        ...

    @property
    def list(self) -> list[T]:
        """
        Get the current list value.
        """
        ...
    
    @list.setter
    def list(self, value: Iterable[T]) -> None:
        """
        Set the list value (accepts any iterable).
        """
        self.change_list(value)

    def change_list(self, value: Iterable[T]) -> None:
        """
        Change the list value.
        """
        ...

    #-------------------------------- length --------------------------------

    @property
    def length(self) -> int:
        """
        Get the current length of the list.
        """
        ...

    @property
    def length_hook(self) -> ReadOnlyHook[int]:
        """
        Get the hook for the list length.
        """
        ...