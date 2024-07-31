# python-type-customizer
An initial attempt to customize behavior in python built-in call type(). This method leverages meta_class to transparently customize the type() behavior. 

Here, the extended functionality is to check if the object (x) in type(x) is "proxied" using the is_proxied function.
If x is proxied, it calls the parent class's __call__ method with x._obj.
If x is not proxied, it calls the parent class's __call__ method with x.

## Customization Approach

A metaclass in Python is a class of a class that defines how a class behaves. A class is an instance of a metaclass. Metaclasses allow you to customize class creation, modify class attributes, and control class instantiation. They are powerful tools for metaprogramming, enabling you to enforce certain patterns or behaviors across multiple classes.

The customization is done through a metaclass that modifies the behavior of class instantiation and method calls. Here's a breakdown of the customization:

- Class Creation Customization:

The __init__ method of the metaclass is overridden to customize the class creation process.

- Class Instantiation Customization:

The __call__ method of the metaclass is overridden to customize the instantiation process of the class.
The code checks if the argument x is proxied using the is_proxied function.
Depending on whether x is proxied, it calls the superclass's __call__ method with either x._obj or x.

- Other utilities, e.g. `isinstance` check and `issubclass` check are wrapped transparently.

## Problem with the Metaclass approach
The metaclass "conflict" occurs when an object is created with another metaclass other than default type construction. This would result in the class cannot find its original metaclass.  For example, in numpy's numpy/_typing/_dtype_like.py  we have a class:
```python
# Mandatory + optional keys
class _DTypeDict(_DTypeDictBase, total=False):
    # Only `str` elements are usable as indexing aliases,
    # but `titles` can in principle accept any object
    offsets: Sequence[int]
    titles: Sequence[Any]
    itemsize: int
    aligned: bool
This class inherits from _DTypeDictBase -> TypedDict, which is a dynamic namespace in python's typing.py . (i.e. the class is constructed by invoking the function):

```python
def TypedDict(typename, fields=None, /, *, total=True, **kwargs):
    """A simple typed namespace. At runtime it is equivalent to a plain dict.
    ...
    return _TypedDictMeta(typename, (), ns, total=total)
```

which invokes the metaclass _TypedDictMeta to construct the class object. When we create a CommonMeta metaclass to do the wrapping, the original way to invoke _TypedDictMeta  seems to be broken. The class constructor here would try to establish the class using the CommonMeta metaclass here and thus invokes the default type metaclass which does not support the total=False argument as a parameter here.
