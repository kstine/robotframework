#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Optional base classes for libraries and listeners.

Module contents:

- :class:`DynamicLibrary` for libraries using the `dynamic library API`__.
- :class:`HybridLibrary` for libraries using the `hybrid library API`__.
- `ListenerV2` for `listener interface version 2`__. *TODO*.
- `ListenerV3` for `listener interface version 3`__. *TODO*.
- Type definitions used by the aforementioned classes.

Main benefit of using these base classes is that editors can provide automatic
completion, documentation and type information. Their usage is not required.
Notice also that libraries typically use the static API and do not need any
base class.

.. note:: These classes are not exposed via the top level :mod:`robot.api`
          package. They need to imported via :mod:`robot.api.interfaces`.

New in Robot Framework 6.1.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#dynamic-library-api
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#hybrid-library-api
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-version-2
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-version-3
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


# Type aliases.
Name = str
Documentation = str
ArgumentSpec = List[
    Union[
        str,               # Name with possible default like `arg` or `arg=1`.
        Tuple[str],        # Name without a default like `('arg',)`.
        Tuple[str, Any]    # Name and default like `('arg', 1)`.
    ]
]
TypeSpec = Union[
    Dict[                  # Types by name.
        str,               # Name.
        Union[
            type,          # Actual type.
            str            # Type name or alias.
        ]
    ],
    List[                  # Types by position.
        Union[
            type,          # Actual type.
            str,           # Type name or alias.
            None           # No type info.
        ]
    ]
]
Tags = List[str]
Source = str


class DynamicLibrary(ABC):
    """Optional base class for libraries using the dynamic library API.

    The dynamic library API makes it possible to dynamically specify
    what keywords a library implements and run them by using
    :meth:`get_keyword_names` and :meth:`run_keyword` methods, respectively.
    In addition to that it has various optional methods for returning more
    information about the implemented keywords to Robot Framework.
    """

    @abstractmethod
    def get_keyword_names(self) -> List[Name]:
        """Return names of the keywords this library implements.

        :return: Keyword names as a list of strings.

        ``name`` passed to other methods is always in the same format as
        returned by this method.
        """
        raise NotImplementedError

    @abstractmethod
    def run_keywords(self, name: Name, args: List[Any], named: Dict[str, Any]) -> Any:
        """Execute the specified keyword using the given arguments.

        :param name: Keyword name as a string.
        :param args: Positional arguments as a list.
        :param named: Named arguments as a dictionary.
        :raises: Reporting FAIL or SKIP status.
        :return: Keyword's return value.

        Reporting status, logging, returning values, etc. is handled the same
        way as with the normal static library API.
        """
        raise NotImplementedError

    def get_keyword_documentation(self, name: Name) -> Optional[Documentation]:
        """Optional method to return keyword documentation.

        The first logical line of keyword documentation is shown in
        the execution log under the executed keyword. The whole
        documentation is shown in documentation generated by Libdoc.

        :param name: Keyword name as a string.
        :return: Documentation as a string oras ``None`` if there is no
            documentation.

        This method is also used to get the overall library documentation as
        well as documentation related to importing the library. They are
        got by calling this method with special names ``__intro__`` and
        ``__init__``, respectively.
        """
        return None

    def get_keyword_arguments(self, name: Name) -> Optional[ArgumentSpec]:
        """Optional method to return keyword's argument specification.

        Returned information is used during execution for argument validation.
        In addition to that, arguments are shown in documentation generated
        by Libdoc.

        :param name: Keyword name as a string.
        :return: Argument specification using format explained below.

        Argument specification defines what arguments the keyword accepts.
        Returning ``None`` means that the keywords accepts any arguments.
        Accepted arguments are returned as a list using these rules:

        - Normal arguments are specified as a list of strings like
          ``['arg1', 'arg2']``. An empty list denotes that the keyword
          accepts no arguments.
        - Varargs must have a ``*`` prefix like ``['*numbers']``. There can
          be only one varargs, and it must follow normal arguments.
        - Arguments after varargs like ``['*items', 'arg']`` are considered
          named-only arguments.
        - If keyword does not accept varargs, a lone ``*`` can be used
          a separator between normal and named-only arguments like
          ``['normal', '*', 'named']``.
        - Kwargs must have a ``**``  prefix like [``**config``]. There can
          be only one kwargs, and it must be last.

        Both normal arguments and named-only arguments can have default values:

        - Default values can be embedded to argument names so that they are
          separated with the equal sign like ``name=default``. In this case
          the default value type is always a string.
        - Alternatively arguments and their default values can be represented
          as two-tuples like ``('name', 'default')``. This allows non-string
          default values and automatic argument conversion based on them.
        - Arguments without default values can also be specified as tuples
          containing just the name like ``('name',)``.
        - With normal arguments, arguments with default values must follow
          arguments without them. There is no such restriction with named-only
          arguments.
        """
        return None

    def get_keyword_types(self, name: Name) -> Optional[TypeSpec]:
        """Optional method to return keyword's type specification.

        Type information is used for automatic argument conversion during
        execution. It is also shown in documentation generated by Libdoc.

        :param name: Keyword name as a string.
        :return: Type specification as a dictionary, as a list, or as ``None``
            if type information is not known.

        Type information can be mapped to arguments returned by
        :meth:`get_keyword_names` either by names using a dictionary or
        by position using a list. For example, if a keyword has argument
        specification ``['arg', 'second']``, it would be possible to return
        types both like ``{'arg': str, 'second': int}`` and ``[str, int]``.

        Regardless of the approach that is used, it is not necessarily to
        specify types for all arguments. When using a dictionary, some
        arguments can be omitted altogether. When using a list, it is possible
        to use ``None`` to mark that a certain argument does not have type
        information and arguments at the end can be omitted altogether.

        If is possible to specify that an argument has multiple possible types
        by using unions like ``{'arg': Union[int, float]}`` or tuples like
        ``{'arg': (int, float)}``.

        In addition to specifying types using classes, it is also possible
        to use names or aliases like ``{'a': 'int', 'b': 'boolean'}``.
        For an up-to-date list of supported types, names and aliases see
        the User Guide.
        """
        return None

    def get_keyword_tags(self, name: Name) -> Optional[Tags]:
        """Optional method to return keyword's tags.

        Tags are shown in the execution log and in documentation generated by
        Libdoc. Tags can also be used with various command line options.

        :param name: Keyword name as a string.
        :return: Tags as a list of strings or ``None`` if there are no tags.
        """
        return None

    def get_keyword_source(self, name: Name) -> Optional[Source]:
        """Optional method to return keyword's source path and line number.

        Source information is used by IDEs to provide navigation from
        keyword usage to implementation.

        :param name: Keyword name as a string.
        :return: Source as a string in format ``path:lineno`` or ``None``
            if source is not known.

        The general format to return the source is ``path:lineno`` like
        ``/example/Lib.py:42``. If the line number is not known, it is
        possible to return only the path. If the keyword is in the same
        file as the main library class, the path can be omitted and only
        the line number returned like ``:42``.

        The source information of the library itself is got automatically from
        the imported library class. The library source path is used with all
        keywords that do not return their own path.
        """
        return None


class HybridLibrary(ABC):
    """Optional base class for libraries using the hybrid library API.

    Hybrid library API makes it easy to specify what keywords a library
    implements by using the :meth:`get_keyword_names` method. After getting
    keyword names, Robot Framework uses ``getattr`` to get the actual keyword
    methods exactly like it does when using the normal static library API.
    Keyword name, arguments, documentation, tags, and so on are got directly
    from the keyword method.

    It is possible to implement keywords also outside the main library class.
    In such cases the library needs to have a ``__getattr__`` method that
    returns desired keyword methods.
    """

    @abstractmethod
    def get_keyword_names(self) -> List[Name]:
        """Return names of the implemented keyword methods as a list or strings.

        Returned names must match names of the implemented keyword methods.
        """
        raise NotImplementedError
