"""NewerType: Runtime type checking for the NewType pattern.

This module provides a wrapper that allows runtime type checking while
maintaining the transparency of the wrapped type for most operations.
"""

from typing import Any, Dict, Generic, List, Type, TypeVar

__all__ = ["NewerType"]

T = TypeVar("T")


class NewerTypeType(type):
    """Metaclass for creating NewerType instances with method forwarding.

    This metaclass handles the dynamic creation of types that wrap existing
    types while maintaining runtime type safety. It automatically forwards
    specified methods from the wrapped type to the wrapper.

    Attributes:
        METHODS_TO_FORWARD: List of magic method names to forward by default.
    """

    METHODS_TO_FORWARD: List[str] = [
        "__len__",
        "__length_hint__",
        "__getitem__",
        "__setitem__",
        "__delitem__",
        "__missing__",
        "__iter__",
        "__reversed__",
        "__contains__",
        "__add__",
        "__sub__",
        "__mul__",
        "__matmul__",
        "__truediv__",
        "__floordiv__",
        "__mod__",
        "__divmod__",
        "__pow__",
        "__lshift__",
        "__rshift__",
        "__and__",
        "__xor__",
        "__or__",
        "__radd__",
        "__rsub__",
        "__rmul__",
        "__rmatmul__",
        "__rtruediv__",
        "__rfloordiv__",
        "__rmod__",
        "__rdivmod__",
        "__rpow__",
        "__rlshift__",
        "__rrshift__",
        "__rand__",
        "__rxor__",
        "__ror__",
        "__iadd__",
        "__isub__",
        "__imul__",
        "__imatmul__",
        "__itruediv__",
        "__ifloordiv__",
        "__imod__",
        "__ipow__",
        "__ilshift__",
        "__irshift__",
        "__iand__",
        "__ixor__",
        "__ior__",
        "__neg__",
        "__pos__",
        "__abs__",
        "__invert__",
        "__complex__",
        "__int__",
        "__float__",
        "__index__",
        "__round__",
        "__trunc__",
        "__floor__",
        "__ceil__",
        "__enter__",
        "__exit__",
        "__eq__",
        "__le__",
        "__lt__",
        "__gt__",
        "__ge__",
    ]

    def __new__(mcs, _name, bases, namespace, **kwargs):
        """Create a new NewerType class.

        Args:
            _name: Internal name for the class.
            bases: Base classes.
            namespace: Class namespace dictionary.
            **kwargs: Additional arguments including 'the_contained_type' and 'class_name'.

        Returns:
            A new class with the specified name and contained type.
        """
        contained_type = kwargs.get("the_contained_type", Any)
        namespace["contained_type"] = contained_type
        name = kwargs.get("class_name", _name)
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        """Initialize a NewerType class with method forwarding.

        Args:
            name: Class name.
            bases: Base classes.
            namespace: Class namespace dictionary.
            **kwargs: Additional arguments including:
                - extra_forwards: List of additional method names to forward.
                - no_def_forwards: If True, don't forward default methods.
        """
        extra_forwards: List[str] = kwargs.get("extra_forwards", list())
        no_def_forwards: bool = kwargs.get("no_def_forwards", False)
        methods_to_forward: List[str] = (
            list() if no_def_forwards else NewerTypeType.METHODS_TO_FORWARD
        )
        if extra_forwards:
            methods_to_forward.extend(extra_forwards)
        NewerTypeType._forward_methods(cls, namespace, methods_to_forward)
        super().__init__(name, bases, namespace)

    @staticmethod
    def _collect_forwardable_methods(
        contained_type: type, methods_to_forward: List[str]
    ) -> List[str]:
        """Collect methods that exist on the contained type and should be forwarded.

        Args:
            contained_type: The type being wrapped.
            methods_to_forward: List of method names to potentially forward.

        Returns:
            List of method names that exist on the contained type.
        """
        contained_dict = contained_type.__dict__
        to_forward = [k for k in contained_dict if k in methods_to_forward]
        return to_forward

    @staticmethod
    def _forward(cls, method_name, namespace):
        """Forward a method from the wrapped type to the wrapper class.

        Args:
            cls: The wrapper class.
            method_name: Name of the method to forward.
            namespace: Class namespace dictionary.
        """

        def forwarded(self, *args, **kwargs):
            cooked_args = [
                arg.inner if isinstance(arg, type(self)) else arg for arg in args
            ]
            method = getattr(self._contents, method_name)
            value = method(*cooked_args, **kwargs)
            return value

        setattr(cls, method_name, forwarded)

    @staticmethod
    def _forward_methods(
        cls, namespace: Dict[str, Any], methods_to_forward: List[str]
    ) -> None:
        """Forward all specified methods from the contained type to the wrapper.

        Args:
            cls: The wrapper class.
            namespace: Class namespace dictionary.
            methods_to_forward: List of method names to forward.
        """
        contained_type: type = namespace["contained_type"]
        to_forward = NewerTypeType._collect_forwardable_methods(
            contained_type, methods_to_forward
        )
        for method in to_forward:
            NewerTypeType._forward(cls, method, namespace)


def NewerType(name: str, the_contained_type: Type[T], **kwargs) -> type:  # noqa: N802
    """Create a new type that wraps an existing type with runtime type checking.

    This function creates a new type that wraps the specified type, allowing
    runtime type checking while maintaining transparency for most operations.
    Instances of different NewerTypes are not compatible even if they wrap
    the same underlying type.

    Args:
        name: The name for the new type.
        the_contained_type: The type to wrap.
        **kwargs: Optional arguments:
            - extra_forwards: List of additional method names to forward
              from the wrapped type.
            - no_def_forwards: If True, don't forward the default set of
              magic methods.

    Returns:
        A new type class that wraps the specified type.

    Example:
        >>> UserId = NewerType("UserId", int)
        >>> user_id = UserId(42)
        >>> isinstance(user_id, UserId)
        True
        >>> isinstance(user_id, int)
        False
    """
    extra_forwards: List[str] = kwargs.get("extra_forwards", list())
    no_def_forwards: bool = kwargs.get("no_def_forwards", False)

    class NewerTypeInstance(
        Generic[T],
        metaclass=NewerTypeType,
        class_name=name,
        the_contained_type=the_contained_type,
        extra_forwards=extra_forwards,
        no_def_forwards=no_def_forwards,
    ):
        """Instance class for NewerType wrappers.

        This class is dynamically created for each NewerType and wraps
        the actual contained value.
        """

        _contents: T

        def __init__(self, *args, **kwargs) -> None:
            """Initialize a NewerType instance.

            Args:
                *args: Positional arguments to pass to the wrapped type constructor.
                **kwargs: Keyword arguments to pass to the wrapped type constructor.
            """
            self._contents = the_contained_type(*args, **kwargs)
            super().__init__()

        def __str__(self):
            """Return string representation showing the type name and value."""
            return f"{self.__class__.__name__}({str(self._contents)})"

        def __repr__(self):
            """Return representation (same as __str__)."""
            return str(self)

        def __bool__(self):
            """Return truthiness of the wrapped value."""
            return bool(self._contents)

        def __bytes__(self, *args):
            """Convert to bytes.

            For strings, uses UTF-8 encoding by default.
            For other types, delegates to the wrapped type's bytes conversion.
            """
            encoding = ["utf-8"] if isinstance(self._contents, str) else []
            return bytes(self._contents, *encoding)

        @property
        def inner(self) -> T:
            """Get the wrapped value.

            Returns:
                The wrapped value of type T.
            """
            return self._contents

        @inner.setter
        def inner(self, value: T) -> None:
            """Set the wrapped value.

            Args:
                value: New value to wrap.
            """
            self._contents = value

    return NewerTypeInstance
