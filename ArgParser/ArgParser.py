"""
File: ArgParser.py
Purpose: Provides a custom argument parser class to validate and parse command-line arguments.
"""

# Sentinel object used to detect unspecified argument constraints
_sentinel = object()

class SubClassError(TypeError):
    """Error raised when subclass check fails"""

class MinError(ValueError):
    """Error raised when min check fails"""

class MaxError(ValueError):
    """Error raised when max check fails"""

class MinLengthError(ValueError):
    """Error raised when minlength check fails"""

class MaxLengthError(ValueError):
    """Error raised when maxlength check fails"""

class InvalidArgument(ValueError):
    """Error raised when possibleValues check fails"""

class ArgConstraint:
    """
    Represents constraints for a single argument, such as type, subclass, range, and default value.
    """
    def __init__(
        self,
        dtype=_sentinel,
        subClass=_sentinel,
        min=_sentinel,
        max=_sentinel,
        minLength=_sentinel,
        maxLength=_sentinel,
        default=_sentinel,
        possibleValues=_sentinel,
        optional=False
    ):
        # Flags indicating whether each constraint was specified
        self.hasDtype = dtype is not _sentinel
        self.dtype = dtype if self.hasDtype else None

        self.hasSubClass = subClass is not _sentinel
        self.subClass = subClass if self.hasSubClass else None

        self.hasMin = min is not _sentinel
        self.min = min if self.hasMin else None

        self.hasMax = max is not _sentinel
        self.max = max if self.hasMax else None

        self.hasMinLength = minLength is not _sentinel
        self.minLength = minLength if self.hasMinLength else None

        self.hasMaxLength = maxLength is not _sentinel
        self.maxLength = maxLength if self.hasMaxLength else None

        self.hasDefault = default is not _sentinel
        self.default = default if self.hasDefault else None

        self.hasPossibleValues = possibleValues is not _sentinel
        self.possibleValues = possibleValues if self.hasPossibleValues else None

        self.optional = optional
    
    def validate(self, name: str, value: object) -> None:
        """
        Validates a given value against the stored constraints.

        Args:
            name (str): The name of the argument being validated.
            value: The value to validate.

        Raises:
            TypeError: If the type or subclass constraint is violated.
            ValueError: If the min, max, minLength or maxLength constraint is violated.
        """
        if self.hasDtype and not isinstance(value, self.dtype):
            raise TypeError(f"{name} must be of type {self.dtype}, not {type(value)}")

        if self.hasSubClass and not issubclass(type(value), self.subClass):
            raise SubClassError(f"{name} must be a subclass of {self.subClass}")

        if self.hasMin and value < self.min:
            raise MinError(f"{name} must be ≥ {self.min}")

        if self.hasMax and value > self.max:
            raise MaxError(f"{name} must be ≤ {self.max}")

        if self.hasMinLength and len(value) < self.minLength:
            raise MinLengthError(f"{name} length must be ≥ {self.minLength}")

        if self.hasMaxLength and len(value) > self.maxLength:
            raise MaxLengthError(f"{name} length must be ≤ {self.maxLength}")

        if self.hasPossibleValues and value not in self.possibleValues:
            raise InvalidArgument(f"{name} must be one of ({', '.join(f"{val!r}" for val in self.possibleValues)})")

    def __repr__(self):
        parts = []
        if self.hasDtype:
            parts.append(f"dtype={self.dtype!r}")
        if self.hasSubClass:
            parts.append(f"subClass={self.subClass!r}")
        if self.hasMax:
            parts.append(f"min={self.min!r}")
        if self.hasMax:
            parts.append(f"max={self.max!r}")
        if self.hasMinLength:
            parts.append(f"minLength={self.minLength!r}")
        if self.hasMaxLength:
            parts.append(f"maxLength={self.maxLength!r}")
        if self.hasDefault:
            parts.append(f"default={self.default!r}")
        if self.hasPossibleValuese:
            parts.append(f"possibleValues={self.possibleValues!r}")
        parts.append(f"optional={self.optional!r}")
        return f"ArgConstraint({', '.join(parts)})"


    def __str__(self):
        parts = []
        if self.hasDtype:
            parts.append(f"dtype={self.dtype}")
        if self.hasSubClass:
            parts.append(f"subClass={self.subClass}")
        if self.hasMax:
            parts.append(f"min={self.min}")
        if self.hasMax:
            parts.append(f"max={self.max}")
        if self.hasMinLength:
            parts.append(f"minLength={self.minLength}")
        if self.hasMaxLength:
            parts.append(f"maxLength={self.maxLength}")
        if self.hasDefault:
            parts.append(f"default={self.default!r}")
        if self.hasPossibleValuese:
            parts.append(f"possibleValues={self.possibleValues!r}")
        parts.append(f"optional={self.optional}")
        return f"ArgConstraint({', '.join(parts)})"

class ArgParser:
    """
    A parser for handling and validating positional and keyword arguments with constraints.
    """
    def __init__(self):
        """
        Initializes the ArgParser.
        """
        self._hasDefaultPositionalArg = False
        # Storage for constraints and argument names
        self._kwargs = {}
        self._args = {}

    def _parseConstraint(self, name: str, **kwargs: dict) -> ArgConstraint:
        """
        Parses keyword argument constraints into an ArgConstraint object.

        Args:
            name (str): The name of the argument.
            kwargs (dict): The constraint keyword arguments.

        Returns:
            ArgConstraint: The constructed constraint object.

        Raises:
            NotImplementedError: If an unknown constraint keyword is used.
            TypeError: If dtype or subClass constraints are incorrectly specified.
        """
        def localValidate(name: str, value: object, possibleVals = False) -> None:
            """
            Helper func that validates a given value against the provided constraints.

            Args:
                name (str): The name of the argument being validated.
                value: The value to validate.

            Raises:
                TypeError: If the type or subclass constraint is violated.
                ValueError: If the min, max, minLength or maxLength constraint is violated.
            """
            if dtype is not _sentinel and not isinstance(value, dtype):
                raise TypeError(f"{name} must be of type {dtype}, not {type(value)}")

            if subClass is not _sentinel and not issubclass(type(value), subClass):
                raise SubClassError(f"{name} must be a subclass of {subClass}")

            if min_val is not _sentinel and value < min_val:
                raise MinError(f"{name} must be ≥ {min_val}")

            if max_val is not _sentinel and value > max_val:
                raise MaxError(f"{name} must be ≤ {max_val}")

            if minLength is not _sentinel and len(value) < minLength:
                raise MinLengthError(f"{name} length must be ≥ {minLength}")

            if maxLength is not _sentinel and len(value) > maxLength:
                raise MaxLengthError(f"{name} length must be ≤ {maxLength}")
            
            if possibleVals and possibleVals is not _sentinel and value not in possibleValues:
                raise InvalidArgument(f"{name} must be one of ({', '.join(f"{val!r}" for val in possibleValues)})")

        # Check for unsupported constraint keys
        for k in kwargs:
            if k not in ("dtype", "subClass", "min", "max", "minLength", "maxLength", "default", "optional", "possibleValues"):
                raise NotImplementedError(f"{k} condition not implemented")

        dtype = kwargs.get("dtype", _sentinel)
        # dtype must be a type or tuple of types
        if dtype is not _sentinel:
            if not isinstance(dtype, (type, tuple)) or (
                isinstance(dtype, tuple) and not all(isinstance(t, type) for t in dtype)
            ):
                raise TypeError(f"dtype for {name} must be type or tuple of types")

        subClass = kwargs.get("subClass", _sentinel)
        # subClass must be a type if specified
        if subClass is not _sentinel and not isinstance(subClass, type):
            raise TypeError(f"subClass for {name} must be of type 'type'")

        min_val = kwargs.get("min", _sentinel)
        # min must be an int if specified
        if min_val is not _sentinel and not isinstance(min_val, (int, float)):
            raise TypeError(f"min for {name} must be of type 'int' or 'float'")

        max_val = kwargs.get("max", _sentinel)
        # max must be an int if specified
        if max_val is not _sentinel and not isinstance(max_val, (int, float)):
            raise TypeError(f"max for {name} must be of type 'int' or 'float'")

        minLength = kwargs.get("minLength", _sentinel)
        # minLength must be an int if specified
        if minLength is not _sentinel and not isinstance(minLength, int):
            raise TypeError(f"minLength for {name} must be of type 'int'")

        maxLength = kwargs.get("maxLength", _sentinel)
        # maxLength must be an int if specified
        if maxLength is not _sentinel and not isinstance(maxLength, int):
            raise TypeError(f"maxLength for {name} must be of type 'int'")

        optional = kwargs.get("optional", False)
        # optional must be a bool if specified
        if not isinstance(optional, bool):
            raise TypeError(f"optional for {name} must be of type 'bool'")

        possibleValues = kwargs.get("possibleValues", _sentinel)
        # possibleValues must be a list or tuple if present
        if possibleValues is not _sentinel:
            if not isinstance(possibleValues, (list, tuple)):
                raise TypeError(f"possibleValues for {name} must be of types 'list' or 'tuple'")
            else:
                # Values in possibleValues must pass other conditions provided
                for i, value in enumerate(possibleValues):
                        localValidate(f"possibleValues[{i}]", value)

        default = kwargs.get("default", _sentinel)
        # default must pass other conditions provided if present
        if default is not _sentinel:
            localValidate("default", default)

        # Construct and return ArgConstraint object with all constraints and no default
        constraint =  ArgConstraint(
            dtype=dtype,
            subClass=subClass,
            min=min_val,
            max=max_val,
            minLength=minLength,
            maxLength=maxLength,
            optional=optional,
            possibleValues=possibleValues,
            default=default
        )

        return constraint

    def addKeywordArg(self, name: str, **kwargs: dict) -> None:
        """
        Adds a keyword argument along with its constraints.

        Args:
            name (str): Name of the keyword argument.
            kwargs: Constraint specifications like dtype, min, max, default, etc.
        """
        constraint = self._parseConstraint(name, **kwargs)
        self._kwargs[name] = constraint 

    def addPositionalArg(self, name: str, **kwargs: dict) -> None:
        """
        Adds a positional argument along with its constraints.

        Args:
            name (str): Name of the positional argument.
            kwargs: Constraint specifications like dtype, min, max, default, etc.
        """
        if self._hasDefaultPositionalArg:
            raise ValueError("ArgParser: If a default is set on a positional arg only one positional arg may be used")

        constraint = self._parseConstraint(name, **kwargs)

        if constraint.hasDefault:
            if len(self._args) != 0:
                raise ValueError("ArgParser: If a default is set on a positional arg only one positional arg may be used")
            else:
                self._hasDefaultPositionalArg = True

        self._args[name] = constraint 

    def _parseKeywordArgs(self, **kwargs: dict) -> None:
        """
        Parses and validates keyword arguments against stored constraints.

        Args:
            kwargs: The keyword arguments to parse.

        Raises:
            TypeError: If a required keyword argument is missing or an unexpected argument is provided.
        """
        
        # Validate and set stored keyword arguments
        for name, constraint in list(self._kwargs.items()):
            if name in kwargs:
                value = kwargs[name]
                constraint.validate(name, value)
                setattr(self, name, value)
                del kwargs[name]
            elif constraint.hasDefault:
                setattr(self, name, constraint.default)
            elif constraint.optional:
                setattr(self, name, None)
            else:
                raise TypeError(f"ArgParser: missing required keyword argument: '{name}'")
            # Remove arg onced parsed
            del self._kwargs[name]

        # Handle unexpected keyword arguments
        if len(kwargs) > 0:
            if kwargs == 1:
                raise TypeError(f"ArgParser: got an unexpected keyword argument '{kwargs.popitem()[0]}'")
            else:
                raise TypeError(f"ArgParser: got unexpected keyword arguments {", ".join(f"'{name}'" for name in kwargs.keys())}")

    def _parsePositionalArgs(self, *args: tuple, **kwargs: dict) -> dict:
        """
        Parses and validates positional arguments against stored constraints.

        Args:
            *args: The positional arguments to parse.

        Raises:
            TypeError: If too many positional arguments are passed or a required argument is missing.
        """
        keywordlessKWARGS = False
        if len(args) > len(self._args):
            if len(self._kwargs) == 0:
                raise TypeError(f"ArgParser: takes {len(self._args)} positional arguments but {len(args)} were given")
            elif len(self._kwargs) + len(self._args) < len(args):
                raise TypeError(f"ArgParser: takes from {len(self._args)} to {len(self._args) + len(self._kwargs)} positional arguments but {len(args)} were given")
            else:
                keywordlessKWARGS = True

        if self._hasDefaultPositionalArg and len(args) == 0:
            name, constraint = list(self._args.items())[0]
            setattr(self, name, constraint.default)
            del self._args[name]
        else:
            args = list(args)
            for i, (arg, (name, constraint)) in enumerate(zip(args, list(self._args.items()))):
                constraint.validate(name, arg)
                setattr(self, name, arg)
                del args[i]
                del self._args[name]
            
            # Handle missing positional arguments
            if len(self._args) > 0:
                if len(self._args) == 1:
                    raise TypeError(f"ArgParser: missing positional argument '{self._args.popitem()[0]}'")
                else:
                    raise TypeError(f"ArgParser: missing positional arguments {", ".join(f"'{name}'" for name in self._args.keys())}")

        # Handle overflow into kwargs    
        if keywordlessKWARGS:
            kwargNames = list(self._kwargs.keys())
            for i, arg in enumerate(args):
                kwargs[kwargNames[i]] = arg
        
        return kwargs

                
    def parseArgs(self, *args: tuple, **kwargs: dict) -> None:
        """
        Parses and validates both positional and keyword arguments.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        kwargs = self._parsePositionalArgs(*args, **kwargs)
        self._parseKeywordArgs(**kwargs)