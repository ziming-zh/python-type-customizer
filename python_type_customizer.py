import builtins
from typing import Any, Sequence

original_type = builtins.type
debug_mode = True


def print_debug(*args, **kwargs):
    if debug_mode:
        print(*args, **kwargs)


def is_proxied(obj):
    try:
        if obj is not None and "is_ml_daikon_proxied_obj" in obj.__dict__:
            return True
    except Exception:
        return False
    return False


class CustomTypeMeta(original_type):
    def __init__(self, *args, **kwargs):
        print_debug(f"<Creating> CustomType with args {args} and kwargs {kwargs}")
        super().__init__(*args, **kwargs)
        # # copy attributes from original type to CustomType
        # for attr_name, attr_value in original_type.__dict__.items():
        #     if attr_name not in CustomType.__dict__:
        #         try:
        #             setattr(CustomType, attr_name, attr_value)
        #         except Exception as e:
        #             print(f"Failed to copy attribute {attr_name} to CustomType: {e}")
        #             # handle the read-only attributes
        print_debug(f"<Finished> creating CustomType")

    def __call__(cls, *args, **kwargs):
        try:
            print_debug(f"<Calling> class {cls} with args {args} and kwargs {kwargs}")
            print_debug(f"super: {super()}")
            if len(args) == 1:
                x = args[0]
                print_debug(f"Checking if {x} is proxied")
                if is_proxied(x):
                    result = super().__call__(x._obj)
                    return result
                else:
                    result = super().__call__(x)
                    return result
            else:
                # Call the original type function with all arguments
                print_debug(
                    f"Calling original type with args {args} and kwargs {kwargs}"
                )
                result = super().__call__(*args, **kwargs)
                return result
        finally:
            print_debug(f"<Finished> calling class with result {result}")

    # __bases__ = original_type.__bases__
    # __module__ = original_type.__module__

    @property
    def __mro__(self):
        return original_type.__mro__

    @property
    def __name__(self):
        return original_type.__name__

    @property
    def __dict__(self):
        return original_type.__dict__

    @property
    def __annotations__(self):
        return original_type.__annotations__

    def __getitem__(cls, key):
        print_debug(f"Getting item {key} from class {cls}")
        return original_type[key]

    def __instancecheck__(self, instance: Any) -> builtins.bool:
        print_debug(f"Checking instance {instance} with class {self}")
        # print(original_type.__instancecheck__)
        return original_type.__instancecheck__(original_type, instance)

    def __subclasscheck__(self, subclass: Any) -> builtins.bool:
        return original_type.__subclasscheck__(original_type, subclass)

    def __subclasses__(self):
        print_debug(f"Getting subclasses of {self}")
        return original_type.__subclasses__(original_type)


# Create a common metaclass if original_type has a different metaclass
class CommonMeta(CustomTypeMeta, original_type):
    pass


class CustomType(original_type, metaclass=CommonMeta):
    def __new__(cls, *args, **kwargs):
        try:
            print_debug(f"<Creating> CustomType with args {args} and kwargs {kwargs}")
            if len(args) == 1 and isinstance(args[0], object):
                print_debug(f"args: {args}")
                # Handle the case: __new__(cls, o: object)
                print_debug(f"Creating type from object: {args[0]}")
                print_debug(f"Type of object: {args[0].__class__}")
                return args[0].__class__
            elif (
                len(args) >= 3
                and isinstance(args[0], str)
                and isinstance(args[1], tuple)
                and isinstance(args[2], dict)
            ):
                # Handle the case: __new__(cls, name: str, bases: tuple, namespace: dict)
                print_debug(
                    f"Creating class {args[0]} with bases {args[1]} and namespace {args[2]}"
                )
                print_debug(original_type, cls)
                return original_type.__new__(
                    original_type, args[0], args[1], args[2], **kwargs
                )
            else:
                raise TypeError("Invalid arguments for CustomType.__new__")
        finally:
            print_debug(f"<Finished> creating CustomType")


# # Copy attributes from builtins.type to CustomType
for attr_name, attr_value in original_type.__dict__.items():
    if attr_name not in CustomType.__dict__:
        try:
            print_debug(f"Copying attribute {attr_name} to CustomType")
            setattr(CustomType, attr_name, attr_value)
        except Exception as e:
            print_debug(f"Failed to copy attribute {attr_name} to CustomType: {e}")


def test_type_aliasing():

    print("Any", type[Any]) # Outputs: <class 'type'>
    # builtins.type = CustomType
    print("Any", CustomType[Any]) # Outputs: <class 'type'>
    print(type[int]) # Outputs: <class 'type'>

class MyClass:
    def __init__(self):
        self.value = 42

    # def __init_subclass__(cls, **kwargs):
    #     print(super().__init_subclass__)
    #     print(original_type.__init_subclass__)
    #     original_type.__init_subclass__(**kwargs)
    #     print(f"Subclass created: {cls}")


class _ABC(type):
    # meta class for abstract base classes
    pass


class MySubclass(MyClass, metaclass=_ABC):
    # subclass of MyClass
    def __init__(self):
        super().__init__()
        self.value = 43

    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)

def test_type_creation():
    from typing import Any, TypeVar
    # Now CustomType should be subscriptable
    T = TypeVar("T")


    def create_instance(cls: type[T]) -> T:
        return cls()
    
    return True


    # This should work with the custom type
    instance = create_instance(MyClass)
    print(instance.value)  # Outputs: 42
    
    return instance.value == 42
    

def test_subscripting_with_type_hints():
    # Test subscripting with type hints
    def example_function(cls: type[Any]) -> Any:
        return cls()
    print(example_function(MyClass))  # Outputs: <class '__main__.MyClass'>
    
    return True


def test_instance_identity():
    a = MySubclass()


    print(type(a))  # Outputs: <class '__main__.MySubclass'>
    print(type(MySubclass))  # Outputs: <'type'>

    print(original_type(a))
    print(original_type(MySubclass))
    # # Get the source code of MySubclass
    # source_code = inspect.getsource(MySubclass)
    return (isinstance(MySubclass, type)) == True \
        and (isinstance(MySubclass, original_type)) == True \
        and issubclass(MySubclass, type) == False \
        and issubclass(MySubclass, original_type)== False

# # Dump the AST node
# print(ast.dump(ast_node, indent=4))
# class MySubSubClass(MySubclass, keyword=42):
#     offsets: Sequence[int]
#     titles: Sequence[Any]
#     itemsize: int
#     aligned: bool
def test_from_import():
    import ast
    import inspect
    import ast
    import typing
    import numpy

if __name__ == "__main__":
    if test_type_aliasing():
        print("test type aliasing passed")
    else:
        print("test type aliasing failed")
    
    if test_type_creation():
        print("test type creation passed")
    else:
        print("test type creation failed")
        
    if test_subscripting_with_type_hints():
        print("test subscripting with type hints passed")
    else:
        print("test subscripting with type hints failed")
    
    if test_instance_identity():
        print("test instance identity passed")
    else:
        print("test instance identity failed")
    
    if test_from_import():
        print("test from import passed")
    else:
        print("test from import failed")