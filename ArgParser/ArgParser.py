"""
File: ArgParser.py
Purpose: Provides a custom argument parser class to validate and parse command-line arguments.
"""
import logging

logger = logging.getLogger(__name__)

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
            message = f"Type check failed for '{name}': expected {self.dtype}, got {type(value)}"
            logger.error(message)
            raise TypeError(message)

        if self.hasSubClass and not issubclass(type(value), self.subClass):
            message = f"Subclass check failed for '{name}': expected subclass of {self.subClass}"
            logger.error(message)
            raise SubClassError(message)
    
        if self.hasMin and value < self.min:
            message = f"Min check failed for '{name}': value {value} < min {self.min}"
            logger.error(message)
            raise MinError(message)
        
        if self.hasMax and value > self.max:
            message = f"Max check failed for '{name}': value {value} > max {self.max}"
            logger.error(message)
            raise MaxError(message)
        
        if self.hasMinLength and len(value) < self.minLength:
            message = f"MinLength check failed for '{name}': len {len(value)} < minLength {self.minLength}"
            logger.error(message)
            raise MinLengthError(message)
        
        if self.hasMaxLength and len(value) > self.maxLength:
            message = f"MaxLength check failed for '{name}': len {len(value)} > maxLength {self.maxLength}"
            logger.error(message)
            raise MaxLengthError(message)

        if self.hasPossibleValues and value not in self.possibleValues:
            message = f"Invalid argument for '{name}': {value} not in {self.possibleValues}"
            logger.error(message)
            raise InvalidArgument(message)

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
        if self.hasPossibleValues:
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
        if self.hasPossibleValues:
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
        logger.info("Created ArgParser instance")

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
        logger.debug(f"Parsing constraints for argument '{name}': {kwargs}")
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
                message = f"Type check failed for '{name}': expected {dtype}, got {type(value)}"
                logger.debug(message)
                raise TypeError(message)

            if subClass is not _sentinel and not issubclass(type(value), subClass):
                message = f"Subclass check failed for '{name}': expected subclass of {subClass}"
                logger.error(message)
                raise SubClassError(message)

            if min_val is not _sentinel and value < min_val:
                message = f"Min check failed for '{name}': value {value} < min {min_val}"
                logger.error(message)
                raise MinError(message)

            if max_val is not _sentinel and value > max_val:
                message = f"Max check failed for '{name}': value {value} > max {max_val}"
                logger.error(message)
                raise MaxError(message)

            if minLength is not _sentinel and len(value) < minLength:
                message = f"MinLength check failed for '{name}': len {len(value)} < minLength {minLength}"
                logger.error(message)
                raise MinLengthError(message)

            if maxLength is not _sentinel and len(value) > maxLength:
                message = f"MaxLength check failed for '{name}': len {len(value)} > maxLength {maxLength}"
                logger.error(message)
                raise MaxLengthError(message)
            
            if possibleVals and possibleVals is not _sentinel and value not in possibleValues:
                message = f"Invalid argument for '{name}': {value} not in {possibleValues}"
                logger.error(message)
                raise InvalidArgument(message)

        # Check for unsupported constraint keys
        for k in kwargs:
            if k not in ("dtype", "subClass", "min", "max", "minLength", "maxLength", "default", "optional", "possibleValues"):
                message = f"Unsupported constraint key '{k}' for argument '{name}'"
                logger.error(message)
                raise NotImplementedError(message)

        dtype = kwargs.get("dtype", _sentinel)
        # dtype must be a type or tuple of types
        if dtype is not _sentinel:
            if not isinstance(dtype, (type, tuple)) or (
                isinstance(dtype, tuple) and not all(isinstance(t, type) for t in dtype)
            ):
                message = f"dtype constraint for '{name}' is invalid: must be type or tuple of types, got {dtype!r}"
                logger.error(message)
                raise TypeError(message)
            else:
                logger.debug(f"dtype constraint for '{name}' validated as {dtype}")

        subClass = kwargs.get("subClass", _sentinel)
        # subClass must be a type if specified
        if subClass is not _sentinel:
            if not isinstance(subClass, type):
                message = f"subClass constraint for '{name}' is invalid: must be of type 'type', got {subClass!r}"
                logger.error(message)
                raise TypeError(message)
            else:
                logger.debug(f"subClass constraint for '{name}' validated as {subClass}")

        min_val = kwargs.get("min", _sentinel)
        # min must be an int if specified
        
        if min_val is not _sentinel:
            if not isinstance(min_val, (int, float)):
                message = f"min constraint for '{name}' is invalid: must be int or float, got {min_val!r}"
                logger.error(message)
                raise TypeError(f"min for {name} must be of type 'int' or 'float'")
            else:
                logger.debug(f"min constraint for '{name}' validated as {min_val}")

        max_val = kwargs.get("max", _sentinel)
        # max must be an int if specified
        if max_val is not _sentinel:
            if not isinstance(max_val, (int, float)):
                message = f"max constraint for '{name}' is invalid: must be int or float, got {max_val!r}"
                logger.error(message)
                raise TypeError(f"max for {name} must be of type 'int' or 'float'")
            else:
                logger.debug(f"max constraint for '{name}' validated as {max_val}")

        minLength = kwargs.get("minLength", _sentinel)
        # minLength must be an int if specified
        if minLength is not _sentinel:
            if not isinstance(minLength, int):
                message = f"minLength constraint for '{name}' is invalid: must be int, got {minLength!r}"
                logger.error(message)
                raise TypeError(message)
            else:
                logger.debug(f"minLength constraint for '{name}' validated as {minLength}")

        maxLength = kwargs.get("maxLength", _sentinel)
        # maxLength must be an int if specified
        if maxLength is not _sentinel:
            if not isinstance(maxLength, int):
                message = f"maxLength constraint for '{name}' is invalid: must be int, got {maxLength!r}"
                logger.error(message)
                raise TypeError(message)
            else:
                logger.debug(f"maxLength constraint for '{name}' validated as {maxLength}")

        optional = kwargs.get("optional", False)
        # optional must be a bool if specified
        if not isinstance(optional, bool):
            message = f"optional constraint for '{name}' is invalid: must be bool, got {optional!r}"
            logger.error(message)
            raise TypeError(message)
        else:
            logger.debug(f"optional constraint for '{name}' set to {optional}")

        possibleValues = kwargs.get("possibleValues", _sentinel)
        # possibleValues must be a list or tuple if present
        if possibleValues is not _sentinel:
            if not isinstance(possibleValues, (list, tuple)):
                message = f"possibleValues constraint for '{name}' invalid: must be list or tuple, got {possibleValues!r}"
                logger.error(message)
                raise TypeError(message)
            else:
                logger.debug(f"possibleValues constraint for '{name}' validated as {possibleValues}")
                # Values in possibleValues must pass other conditions provided
                for i, value in enumerate(possibleValues):
                        localValidate(f"possibleValues[{i}]", value)

        default = kwargs.get("default", _sentinel)
        # default must pass other conditions provided if present
        if default is not _sentinel:
            localValidate("default", default)
            logger.debug(f"default constraint for '{name}' validated as {default}")

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

        logger.debug(f"Constructed ArgConstraint for '{name}': {constraint}")
        return constraint

    def addKeywordArg(self, name: str, **kwargs: dict) -> None:
        """
        Adds a keyword argument along with its constraints.

        Args:
            name (str): Name of the keyword argument.
            kwargs: Constraint specifications like dtype, min, max, default, etc.
        """
        logger.debug(f"Adding keyword argument '{name}' with constraints {kwargs}")
        constraint = self._parseConstraint(name, **kwargs)
        self._kwargs[name] = constraint 
        logger.debug(f"Keyword argument '{name}' added.")

    def addPositionalArg(self, name: str, **kwargs: dict) -> None:
        """
        Adds a positional argument along with its constraints.

        Args:
            name (str): Name of the positional argument.
            kwargs: Constraint specifications like dtype, min, max, default, etc.
        """
        logger.debug(f"Adding positional argument '{name}' with constraints {kwargs}")
        if self._hasDefaultPositionalArg:
            logger.error("If a default is set on a positional arg only one positional arg may be used")
            raise ValueError("If a default is set on a positional arg only one positional arg may be used")

        constraint = self._parseConstraint(name, **kwargs)

        if constraint.hasDefault:
            if len(self._args) != 0:
                logger.error("Multiple positional arguments with defaults are not allowed.")
                raise ValueError("Multiple positional arguments with defaults are not allowed.")
            else:
                self._hasDefaultPositionalArg = True
                logger.debug(f"Positional argument '{name}' has default value set.")

        self._args[name] = constraint 
        logger.debug(f"Positional argument '{name}' added.")

    def _parseKeywordArgs(self, **kwargs: dict) -> None:
        """
        Parses and validates keyword arguments against stored constraints.

        Args:
            kwargs: The keyword arguments to parse.

        Raises:
            TypeError: If a required keyword argument is missing or an unexpected argument is provided.
        """
        logger.debug(f"Parsing keyword arguments: {kwargs!s}")
        # Validate and set stored keyword arguments
        for name, constraint in list(self._kwargs.items()):
            if name in kwargs:
                value = kwargs[name]
                logger.debug(f"Validating keyword argument '{name}' with value {value!s}")
                try:
                    constraint.validate(name, value)
                except Exception as e:
                    logger.error(f"Validation failed for keyword argument '{name}': {e}")
                    raise
                setattr(self, name, value)
                del kwargs[name]
            elif constraint.hasDefault:
                setattr(self, name, constraint.default)
                logger.debug(f"Using default value for missing keyword argument '{name}'")
            elif constraint.optional:
                setattr(self, name, None)
                logger.debug(f"Setting None for optional missing keyword argument '{name}'")
            else:
                message = f"Missing required keyword argument '{name}'"
                logger.error(message)
                raise TypeError(message)
            # Remove arg onced parsed
            del self._kwargs[name]

        # Handle unexpected keyword arguments
        if len(kwargs) > 0:
            if kwargs == 1:
                raise TypeError(f"ArgParser: got an unexpected keyword argument '{kwargs.popitem()[0]}'")
            else:
                raise TypeError(f"ArgParser: got unexpected keyword arguments {", ".join(f"'{name}'" for name in kwargs.keys())}")

        logger.info("Parsed keyword arguments.")

    def _parsePositionalArgs(self, *args: tuple, **kwargs: dict) -> dict:
        """
        Parses and validates positional arguments against stored constraints.

        Args:
            *args: The positional arguments to parse.

        Raises:
            TypeError: If too many positional arguments are passed or a required argument is missing.
        """
        logger.debug(f"Parsing positional arguments: {args}")
        keywordlessKWARGS = False
        if len(args) > len(self._args):
            if len(self._kwargs) == 0:
                message = f"Too many positional arguments: expected {len(self._args)}, got {len(args)}"
                logger.error(message)
                raise TypeError(message)
            elif len(self._kwargs) + len(self._args) < len(args):
                message = f"Too many positional arguments considering keyword args: expected from {len(self._args)} to {len(self._args) + len(self._kwargs)}, got {len(args)}"
                logger.error(message)
                raise TypeError(message)
            else:
                keywordlessKWARGS = True
                logger.warning("Extra positional arguments may overflow into keyword arguments")

        if self._hasDefaultPositionalArg and len(args) == 0:
            name, constraint = list(self._args.items())[0]
            setattr(self, name, constraint.default)
            logger.debug(f"Using default value for positional argument '{name}'")
            del self._args[name]
        else:
            args = list(args)
            for i, (arg, (name, constraint)) in enumerate(zip(args, list(self._args.items()))):
                logger.debug(f"Validating positional argument '{name}' with value {arg}")
                try:
                    constraint.validate(name, arg)
                except Exception as e:
                    logger.error(f"Validation failed for positional argument '{name}': {e}")
                    raise
                setattr(self, name, arg)
                del args[i]
                del self._args[name]
            
            # Handle missing positional arguments
            if len(self._args) > 0:
                missing = list(self._args.keys())
                if len(self._args) == 1:
                    logger.error(f"Missing positional argument '{missing[0]}'")
                    raise TypeError(f"ArgParser: missing positional argument '{missing[0]}'")
                else:
                    logger.error(f"Missing positional arguments {missing}")
                    raise TypeError(f"ArgParser: missing positional arguments {missing}")

        # Handle overflow into kwargs    
        if keywordlessKWARGS:
            kwargNames = list(self._kwargs.keys())
            for i, arg in enumerate(args):
                kwargs[kwargNames[i]] = arg
                logger.debug(f"Assigning overflow positional argument '{arg}' to keyword argument '{kwargNames[i]}'")

        logger.info("Parsed positional arguments.")

        return kwargs
            
    def parseArgs(self, *args: tuple, **kwargs: dict) -> None:
        """
        Parses and validates both positional and keyword arguments.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        logger.debug(f"Starting parseArgs with positional args {args!s} and keyword args {kwargs!s}")
        kwargs = self._parsePositionalArgs(*args, **kwargs)
        self._parseKeywordArgs(**kwargs)
        logger.info("Arguments parsed successfully")