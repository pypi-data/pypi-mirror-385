"""
MIT License

Copyright (c) 2022 QQ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Callable, Iterable, List, Sequence, Union

from .utils import deprecated


class qDict(dict):
    """
    qq: access python dict values through a property manner
    """

    def __init__(
        self,
        d: Union[dict, Any] = None,
        default_function: Callable = None,
        allow_notexist: bool = True,
        recursive: bool = True,
    ):
        """__init__ _summary_

        Args:
            d (dict-like, optional): dict-like input. Defaults to None.
            default_function (Callable, optional): the function to generate a default value if access to non-existing keys or attributes, by default None. Defaults to None.
            allow_notexist (bool, optional): if true, access to non-existing keys or attributes would not trigger error alert. Only take effect when default_function is None. Defaults to True.
            recursive (bool, optional): whether to convert dict-type values to qDict recursively. Defaults to False.
        """

        super().__init__()
        if isinstance(d, dict):
            for k, v in d.items():
                if recursive and isinstance(v, dict):
                    v = qDict(
                        v,
                        default_function=default_function,
                        allow_notexist=allow_notexist,
                        recursive=True,
                    )
                self.__setitem__(k, v)
        else:
            try:
                import argparse

                if isinstance(d, argparse.Namespace):
                    for k, v in d.__dict__.items():
                        self.__setitem__(k, v)
            except Exception:
                pass

        # be compatible with `getattr(qDict, key, defaultVal)`
        self.__dict__["_allow_notexist"] = allow_notexist
        self.__dict__["_default_function"] = default_function if default_function is not None else None

    @property
    def allow_notexist(self):
        return self.__dict__["_allow_notexist"]

    @property
    def default_function(self):
        return self.__dict__["_default_function"]

    @allow_notexist.setter
    def allow_notexist(self, allow_notexist):
        self.__dict__["_allow_notexist"] = allow_notexist

    @default_function.setter
    def default_function(self, default_function):
        print("default_function.setter", default_function)
        if default_function is None:
            del self.__dict__["_default_function"]
        else:
            self.__dict__["_default_function"] = default_function

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except Exception:
            if "_default_function" in self.__dict__ and self.__dict__["_default_function"] is not None:
                self.__setitem__(key, self.__dict__["_default_function"]())
                return self.__getitem__(key)
            elif "_allow_notexist" in self.__dict__ and self.__dict__["_allow_notexist"]:
                return None
            else:
                raise AttributeError(str(key))

    def __getitem__(self, key):
        if key == "_default_function":
            return self.__dict__["_default_function"]
        try:
            return super().__getitem__(key)
        except Exception:
            if "_default_function" in self.__dict__ and self.__dict__["_default_function"] is not None:
                self.__setitem__(key, self.__dict__["_default_function"]())
                return self.__getitem__(key)
            elif "_allow_notexist" in self.__dict__ and self.__dict__["_allow_notexist"]:
                return None
            else:
                raise KeyError(str(key))

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def fetch(self, keys: List[str]):
        return [self.__getitem__(k) for k in keys]

    @deprecated("since its not implemented", None, ".copy()")
    def __deepcopy__(self, memo):
        """not implemented yet"""
        if id(self) in memo:
            return memo[id(self)]
        return self.__copy__()

    def __copy__(self):
        """return new instance"""
        _d = self.__class__.__new__(self.__class__)
        _d.__init__(self, self.allow_notexist, self.allow_notexist)
        return _d

    def copy(self):
        return self.__copy__()

    def to_dict(self):
        _d = dict()
        for k, v in self.items():
            if isinstance(v, qDict):
                v = v.to_dict()
            _d[k] = v
        return _d

    def lazy_update(self, d: dict, neccessary_keys=[]):
        """only absort keys not been contained, except for neccessary_keys."""
        assert isinstance(d, dict), TypeError("only accept dict")
        for k, v in d.items():
            if (k not in self) or (k in neccessary_keys):
                self.__setitem__(k, v)
        return self

    def recursive_update(self, d: dict, exclude_keys: Sequence = []):
        """recursive_update

        Args:
            d (dict): the source dict.
            exclude_keys (Sequence, optional): keys to ignore. Defaults to [].
        """
        for k, v in d.items():
            if k in exclude_keys:
                continue
            if isinstance(v, dict):
                if k in self and isinstance(self.__getitem__(k), dict):
                    _old = self.__getitem__(k)
                    v = qDict(_old).recursive_update(v)
                    v = _old.__class__(v)
                else:
                    v = qDict(v)
            self.__setitem__(k, v)
        return self

    def safe_pop(self, key):
        if key in self:
            return self.pop(key)
        else:
            return None

    def remove(self, key):
        del self[key]
        return self

    @classmethod
    def from_list(cls, k: Iterable, v: Union[Iterable, Callable]):
        """Accept keys as list.
        v can be either a list or a callable function,
        if a function is given, v() will be used as the default value."""
        assert len(k) == len(v)
        d_ = cls()
        if callable(v):
            for k_ in k:
                d_.__setitem__(k_, v())
        else:
            for k_, v_ in zip(k, v):
                d_.__setitem__(k_, v_)
        return d_

    @classmethod
    def from_namespace(cls, namespace):
        """convert from argparse.Namespace"""
        d_ = cls()
        for k, v in namespace.__dict__.items():
            d_.__setitem__(k, v)
        return d_

    @classmethod
    def from_args(cls, **kwargs):
        return cls(kwargs)

    def __repr__(self):
        if len(self) < 5:
            return super().__repr__()

        s_ = "qDict{\n"
        for k, v in self.items():
            s_ += f"\t'{k}':{v}\n"

        s_ += "}"
        return s_


if __name__ == "__main__":
    d = qDict.from_args(a=1, b=2)
    print(d)

    d0 = qDict({"a": {"aval": 1, "b": 2}, "c": 3}, recursive=True)
    d1 = qDict({"a": {"aval": 1, "b": 2}, "c": 3}, recursive=False)
    print(type(d0.a), type(d1.a))  # qDict, dict
    d0_ = d0.recursive_update({"a": {"new_k": 5}})
    d1_ = d1.recursive_update({"a": {"new_k": 5}})
    print(type(d0_.a), type(d1_.a))  # qDict, dict
