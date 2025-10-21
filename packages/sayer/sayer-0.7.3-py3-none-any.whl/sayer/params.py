from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    import click


class BaseParam:
    """
    Base class for command-line parameter definitions.

    This class is not intended to be instantiated directly but serves as a base
    for more specific parameter types like Option, Argument, and Env.
    """

    def __init__(self, **options: Any):
        """
        Initializes a new BaseParam instance.

        Args:
            options: Additional options for the parameter.
        """
        self.type: Any = options.pop("type", None)
        self.options: dict[str, Any] = options if options is not None else {}


class Option(BaseParam):
    """
    Represents a command-line option parameter definition.

    Stores configuration like default value, help text, environment variable name,
    prompting behavior, and required status.
    """

    def __init__(
        self,
        default: Any = ...,
        *param_decls: str,
        help: str | None = None,
        envvar: str | None = None,
        prompt: bool | str = False,
        confirmation_prompt: bool = False,
        hide_input: bool = False,
        show_default: bool = True,
        required: Optional[bool] = None,
        callback: Optional[Callable[[click.Context, click.Parameter, Any], Any]] = None,
        default_factory: Callable[[], Any] | None = None,
        is_flag: bool = False,
        expose_value: bool = True,
        **options: Any,
    ) -> None:
        """
        Initializes a new Option instance.

        Args:
            default: The default value for the option. Defaults to `...`.
            help: Help text for the option.
            envvar: The name of the environment variable to read the value from.
            prompt: Whether to prompt the user for the value. Can be a boolean
                    or a string to use as the prompt message.
            confirmation_prompt: Whether to ask for confirmation when prompting.
            hide_input: Whether to hide input when prompting (e.g., for passwords).
            show_default: Whether to show the default value in the help text.
            required: An optional boolean to explicitly set whether the option is
                      required. If None, being required is determined by the default value.
            callback: A function to call to process the value after parsing.
        """
        super().__init__(**options)
        self.help = help
        self.envvar = envvar
        self.prompt = prompt
        self.confirmation_prompt = confirmation_prompt
        self.hide_input = hide_input
        self.show_default = show_default
        self.param_decls = param_decls
        self.is_flag = is_flag
        self.expose_value = expose_value

        # ✅ Preserve explicit None (do NOT coerce to "None" string)
        self.default = default

        has_static = default is not ... and default is not None
        has_factory = default_factory is not None

        # ✅ Required logic: if default is None, option is not required
        if default is None and required is None:
            self.required = False
        else:
            self.required = required if required is not None else not (has_static or has_factory)

        self.callback = callback
        self.default_factory = default_factory


class Argument(BaseParam):
    """
    Represents a command-line argument parameter definition.

    Stores configuration like default value, help text, and required status.
    """

    def __init__(
        self,
        default: Any = ...,
        *param_decls: str,
        help: str | None = None,
        required: Optional[bool] = None,
        callback: Optional[Callable[[click.Context, click.Parameter, Any], Any]] = None,
        default_factory: Callable[[], Any] | None = None,
        is_flag: bool = False,
        expose_value: bool = True,
        **options: Any,
    ) -> None:
        """
        Initializes a new Argument instance.

        Args:
            default: The default value for the argument. Defaults to `...`.
            help: Help text for the argument.
            required: An optional boolean to explicitly set whether the argument is
                      required. If None, being required is determined by the default value.
            callback: A function to call to process the value after parsing.
        """
        super().__init__(**options)
        self.default = default
        self.help = help
        self.is_flag = is_flag
        self.expose_value = expose_value

        has_static = default is not ...
        has_factory = default_factory is not None
        self.required = required if required is not None else not (has_static or has_factory)

        self.callback = callback
        self.default_factory = default_factory
        self.param_decls = param_decls


class Env(BaseParam):
    """
    Represents an environment variable parameter definition.

    Stores the environment variable name, default value, and required status.
    """

    def __init__(
        self,
        envvar: str,
        default: Any = ...,
        required: Optional[bool] = None,
        default_factory: Callable[[], Any] | None = None,
        is_flag: bool = False,
        expose_value: bool = True,
        **options: Any,
    ) -> None:
        """
        Initializes a new Env instance.

        Args:
            envvar: The name of the environment variable.
            default: The default value for the environment variable if not set.
                     Defaults to `...`.
            required: An optional boolean to explicitly set whether the environment
                      variable is required. If None, being required is determined
                      by the default value.
        """
        super().__init__(**options)
        self.envvar = envvar
        self.default = default
        self.is_flag = is_flag
        self.expose_value = expose_value

        has_static = default is not ...
        has_factory = default_factory is not None
        self.required = required if required is not None else not (has_static or has_factory)

        self.default_factory = default_factory


class Param(BaseParam):
    """
    Represents a flexible parameter definition with various configuration options.

    Can be used to define parameters that can later be converted into
    specific types like command-line options.
    """

    def __init__(
        self,
        default: Any = ...,
        *param_decls: str,
        help: str | None = None,
        envvar: str | None = None,
        prompt: bool | str = False,
        confirmation_prompt: bool = False,
        hide_input: bool = False,
        show_default: bool = True,
        required: bool | None = None,
        callback: Callable[[click.Context, click.Parameter, Any], Any] | None = None,
        default_factory: Callable[[], Any] | None = None,
        is_flag: bool = False,
        expose_value: bool = True,
        **options: Any,
    ) -> None:
        """
        Initializes a new Param instance.

        Args:
            default: The default value for the parameter. Defaults to `...`.
            help: Help text for the parameter.
            envvar: The name of the environment variable to read the value from.
            prompt: Whether to prompt the user for the value. Can be a boolean
                    or a string to use as the prompt message.
            confirmation_prompt: Whether to ask for confirmation when prompting.
            hide_input: Whether to hide input when prompting (e.g., for passwords).
            show_default: Whether to show the default value in the help text.
            required: An optional boolean to explicitly set whether the parameter is
                      required. If None, being required is determined by the default value.
            callback: A function to call to process the value after parsing.
        """
        super().__init__(**options)
        self.default = default
        self.help = help
        self.envvar = envvar
        self.prompt = prompt
        self.confirmation_prompt = confirmation_prompt
        self.hide_input = hide_input
        self.show_default = show_default
        self.param_decls = param_decls
        self.is_flag = is_flag
        self.expose_value = expose_value

        has_static = default is not ...
        has_factory = default_factory is not None
        self.required = required if required is not None else not (has_static or has_factory)

        self.callback = callback
        self.default_factory = default_factory

    def as_option(self) -> "Option":
        """
        Converts this Param instance into an Option instance.

        Transfers all relevant configuration properties from the Param
        to a new Option object.

        Returns:
            An instance of the Option class configured with this Param's settings.
        """
        return Option(
            default=self.default,
            *self.param_decls,
            help=self.help,
            envvar=self.envvar,
            prompt=self.prompt,
            confirmation_prompt=self.confirmation_prompt,
            hide_input=self.hide_input,
            show_default=self.show_default,
            required=self.required,
            callback=self.callback,
            default_factory=self.default_factory,
            options=self.options,
            is_flag=self.is_flag,
            expose_value=self.expose_value,
        )


class JsonParam(Param):
    """
    Marks a parameter as JSON‐encoded.
    The CLI will accept a JSON string and decode it into your target type
    via the global encoders (dataclass, attrs, pydantic, msgspec, etc.).
    """

    default: Optional[str] = None
    required: bool = True
