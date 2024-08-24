# %%
from abc import abstractmethod
from collections import UserList


class ValidateMeta(type):
    def __new__(cls, name, bases, dct):
        # List of methods from list that should be wrapped
        list_methods = [
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__iter__",
            "__len__",
            "append",
            "extend",
            "insert",
            "remove",
            "pop",
            "clear",
            "index",
            "count",
            "sort",
            "reverse",
            "__add__",
            "__radd__",
            "__iadd__",
            "__mul__",
            "__rmul__",
            "__imul__",
        ]

        # Wrap list methods with validation
        for method_name in list_methods:
            if method_name in dct:
                continue  # Skip if the method is already defined in the class

            def make_method_wrapper(method_name):
                def method_wrapper(self, *args, **kwargs):
                    # Validate all data before performing the method
                    self._validate_all()
                    result = getattr(self.data, method_name)(*args, **kwargs)
                    print(f"Method: {method_name}{args}, Result: {type(result)} {result}")
                    if method_name in ["__getitem__"]:
                        return result
                    elif isinstance(result, str):
                        return result
                    elif isinstance(result, (int, float)):
                        return result
                    self._validate_all()
                    print(f"Data: {self.data}")
                    return self

                return method_wrapper

            dct[method_name] = make_method_wrapper(method_name)

        return super().__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        # Create an instance of the class
        instance = super().__call__(*args, **kwargs)

        # Validate all elements in the instance's list
        instance._validate_all()

        return instance


# class CmdOptions(metaclass=ValidateMeta):
#     def __init__(self, **kwargs):

#         self.data = [f"--{k}={v}" for k, v in kwargs.items()]
#         # super().__init__([f"--{k}={v}" for k, v in kwargs.items()])

#         self._validate_all()

#     @staticmethod
#     def validate(x):
#         assert isinstance(x, str), f"Expected string, got {type(x)}"
#         assert x.count("=") == 1, f"Expected string to contain one '=', got {x}"
#         assert x.startswith("--"), f"Expected string to start with '--', got {x}"

#     def _validate_all(self):
#         for x in self.data:
#             self.validate(x)

#     # def __add__(self, other):
#     #     # Return a regular list instead of CmdOptions
#     #     return self.data + other

#     # def __radd__(self, other):
#     #     # Return a regular list instead of CmdOptions
#     #     return other + self.data

#     def __iter__(self):
#         # Make the class iterable
#         return iter(self.data)

#     def __repr__(self) -> str:
#         return repr(self.data)


class ValidatedList(UserList):
    @abstractmethod
    def validate(self, x):
        pass

    def _validate_all(self):
        for x in self.data:
            self.validate(x)

    def append(self, item):
        self.validate(item)
        super().append(item)
        return self

    def extend(self, other):
        for item in other:
            self.validate(item)
        super().extend(other)
        return self

    def insert(self, index, item):
        self.validate(item)
        super().insert(index, item)
        return self

    def reverse(self) -> None:
        super().reverse()
        return self

    def __getitem__(self, index):
        if isinstance(index, slice):
            # Return a new instance of CmdOptions with the sliced data
            return CmdOptions(
                **{k: v for item in self.data[index] for k, v in [item[2:].split("=")]}
            )
        else:
            return super().__getitem__(index)

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            for i in item:
                self.validate(i)
        else:
            self.validate(item)
        super().__setitem__(index, item)
        return self

    def __add__(self, other):
        new_list = super().__add__(other)
        self._validate_all()
        return new_list

    def __radd__(self, other):
        new_list = super().__radd__(other)
        self._validate_all()
        return new_list

    def __iadd__(self, other):
        for item in other:
            self.validate(item)
        return super().__iadd__(other)

    def __delitem__(self, index):
        super().__delitem__(index)
        return self


class CmdOptions(ValidatedList):
    def __init__(self, lst=None, **kwargs):
        lst = lst or []
        initial_data = lst + [f"--{k}={v}" for k, v in kwargs.items()]
        super().__init__(initial_data)
        self._validate_all()

    @staticmethod
    def validate(x):
        assert isinstance(x, str), f"Expected string, got {type(x)}"
        assert x.count("=") == 1, f"Expected string to contain one '=', got {x}"
        assert x.startswith("--"), f"Expected string to start with '--', got {x}"


if __name__ == "__main__":
    say_options = CmdOptions(voice="Daniel", sound=10, beaver="ten more minutes")

    for s in ["--voice=Daniel", "--sound=10", "--beaver=ten more minutes"]:
        assert s in say_options

    tests = [
        ("say_options[0]", "--voice=Daniel"),
        ("say_options[1:] #1", ["--sound=10", "--beaver=ten more minutes"]),
        ("say_options[1:] #2", ["--sound=10", "--beaver=ten more minutes"]),
        (
            "say_options.__setitem__(0, '--voice=gary')",
            [
                "--voice=gary",
                "--sound=10",
                "--beaver=ten more minutes",
            ],
        ),
        ("say_options[1]", "--sound=10"),
        (
            "say_options.reverse()",
            ["--beaver=ten more minutes", "--sound=10", "--voice=gary"],
        ),
        ("len(say_options)", 3),
        (
            "list(i for i in say_options)",
            ["--beaver=ten more minutes", "--sound=10", "--voice=gary"],
        ),
        ("say_options.__delitem__(-1)", ["--beaver=ten more minutes", "--sound=10"]),
        (
            "say_options.append('--extra=more options')",
            ["--beaver=ten more minutes", "--sound=10", "--extra=more options"],
        ),
        (
            "say_options.extend(['--another=extra option', '--one=more'])",
            [
                "--beaver=ten more minutes",
                "--sound=10",
                "--extra=more options",
                "--another=extra option",
                "--one=more",
            ],
        ),
    ]

    test_failures = []
    for i, test in enumerate(tests, start=1):
        result = eval(test[0])
        expected = test[1]

        if isinstance(result, CmdOptions):
            result = list(result)

        try:
            assert type(result) is type(
                expected
            ), f"Test {i}: {test[0]}, Expected {type(test[1])}, got {type(result)}"
        except AssertionError as e:
            test_failures.append(e)
        try:
            assert result == expected, f"Test {i}: {test[0]}, Expected {test[1]}, got {result}\n"
        except AssertionError as e:
            test_failures.append(e)

    if len(test_failures) > 0:
        for failure in test_failures:
            print(failure)
    else:
        print("CmdOptions passed")

# %%
