"""Support code for sensors and sensor configuration"""

# -- Imports ------------------------------------------------------------------

from collections.abc import Iterator, Mapping
from icotronic.can.streaming import StreamingConfiguration

# -- Classes ------------------------------------------------------------------


class SensorConfiguration(Mapping):
    """Used to store the configuration of the three sensor channels

    Args:

        first:
            The sensor number for the first measurement channel

        second:
            The sensor number for the second measurement channel

        third:
            The sensor number for the third measurement channel


    Examples:

        Create an example sensor configuration

        >>> SensorConfiguration(first=0, second=1, third=2)
        M1: None, M2: S1, M3: S2

        Initializing a sensor configuration with incorrect values will fail

        >>> SensorConfiguration(first=256, second=1, third=2)
        Traceback (most recent call last):
        ...
        ValueError: Incorrect value for first channel: “256”

        >>> SensorConfiguration(first=0, second=1, third=-1)
        Traceback (most recent call last):
        ...
        ValueError: Incorrect value for third channel: “-1”

    """

    def __init__(self, first: int = 0, second: int = 0, third: int = 0):

        self.attributes = {
            "first": first,
            "second": second,
            "third": third,
        }

        for name, channel in self.attributes.items():
            if channel < 0 or channel > 255:
                raise ValueError(
                    f"Incorrect value for {name} channel: “{channel}”"
                )

    def __getitem__(self, item: str) -> int:
        """Return values of the mapping provided by this class

        Note:

            This method allow access to the object via the splat operators (*,
            **)

        Args:

            item:
                The attribute for which we want to retrieve the value

        Returns:

            The value of the attribute

        Examples:

            Create an “empty” example sensor configuration

            >>> dict(**SensorConfiguration()) # doctest:+NORMALIZE_WHITESPACE
            {'first': 0,
             'second': 0,
             'third': 0}

            Create an example sensor configuration using init values

            >>> dict(**SensorConfiguration(first=1, second=2, third=3)
            ...     ) # doctest:+NORMALIZE_WHITESPACE
            {'first': 1,
             'second': 2,
             'third': 3}

        """

        return self.attributes[item]

    def __iter__(self) -> Iterator:
        """Return an iterator over the mapping provided by this class

        Note:

            This method allow access to the object via the splat operators (*,
            **)

        Returns:

            The names of the “important” properties of the sensor
            configuration:

            - first
            - second
            - third

        Examples:

            Get the important sensor config attributes

            >>> for attribute in SensorConfiguration():
            ...     print(attribute)
            first
            second
            third

        """

        return iter(self.attributes)

    def __len__(self) -> int:
        """Return the length of the mapping provided by this class

        Note:

            This method allow access to the object via the splat operators (*,
            **)

        Returns:

            The number of “important” properties of the sensor configuration:

            - first
            - second
            - third

        Examples:

            Get the static length of some example sensor configurations

            >>> len(SensorConfiguration())
            3

            >>> len(SensorConfiguration(second=10))
            3

        """

        return len(self.attributes)

    def __str__(self) -> str:
        """The string representation of the sensor configuration

        Returns:

            A textual representation of the sensor configuration

        Examples:


            Get the string representation of some example sensor configs

            >>> str(SensorConfiguration(first=1, second=3, third=2))
            'M1: S1, M2: S3, M3: S2'

            >>> str(SensorConfiguration())
            ''

            >>> str(SensorConfiguration(second=1))
            'M2: S1'

        """

        return ", ".join((
            f"M{sensor}: S{value}"
            for sensor, value in enumerate(self.attributes.values(), start=1)
            if value != 0
        ))

    def __repr__(self) -> str:
        """The textual representation of the sensor configuration

        Returns:

            A textual representation of the sensor configuration

        Examples:

            Get the textual representation of some example sensor configs

            >>> repr(SensorConfiguration(first=1, second=3, third=2))
            'M1: S1, M2: S3, M3: S2'

            >>> repr(SensorConfiguration())
            'M1: None, M2: None, M3: None'

        """

        return ", ".join((
            f"M{sensor}: {f'S{value}' if value != 0 else 'None'}"
            for sensor, value in enumerate(self.attributes.values(), start=1)
        ))

    @property
    def first(self) -> int:
        """Get the sensor for the first channel

        Returns:

            The sensor number of the first channel

        Examples:

            Get the sensor number for the first channel of a sensor config

            >>> SensorConfiguration(first=1, second=3, third=2).first
            1

        """

        first = self.attributes["first"]

        return 0 if first is None else first

    @property
    def second(self) -> int:
        """Get the sensor for the second channel

        Returns:

            The sensor number of the second channel


        Examples:

            Get the sensor number for the second channel of a sensor config

            >>> SensorConfiguration(first=1, second=3, third=2).second
            3

        """

        second = self.attributes["second"]

        return 0 if second is None else second

    @property
    def third(self) -> int:
        """Get the sensor for the third channel

        Returns:

            The sensor number of the third channel

        Examples:

            Get the sensor number for the third channel of a sensor config

            >>> SensorConfiguration(first=1, second=3, third=2).third
            2

        """

        third = self.attributes["third"]

        return 0 if third is None else third

    def disable_channel(
        self, first: bool = False, second: bool = False, third: bool = False
    ) -> None:
        """Disable certain (measurement) channels

        Args:

            first:
                Specifies if the first measurement channel should be disabled
                or not

            second:
                Specifies if the second measurement channel should be disabled
                or not

            third:
                Specifies if the third measurement channel should be disabled
                or not

        """

        if first:
            self.attributes["first"] = 0
        if second:
            self.attributes["second"] = 0
        if third:
            self.attributes["third"] = 0

    def requires_channel_configuration_support(self) -> bool:
        """Check if the sensor configuration requires channel config support

        Returns:

            - ``True``, if the configuration requires hardware that has
              support for changing the channel configuration
            - ``False``, otherwise

        Examples:

            Check if example sensor configs require channel config support

            >>> SensorConfiguration(first=1, second=3, third=2
            ...     ).requires_channel_configuration_support()
            True

            >>> SensorConfiguration(first=1, second=0, third=1
            ...     ).requires_channel_configuration_support()
            True

            >>> SensorConfiguration(first=1, second=2, third=3
            ...     ).requires_channel_configuration_support()
            False

            >>> SensorConfiguration().requires_channel_configuration_support()
            False

        """

        for measurement_channel, sensor_channel in enumerate(
            self.attributes.values(), start=1
        ):
            if sensor_channel not in {0, measurement_channel}:
                return True
        return False

    def empty(self) -> bool:
        """Check if the sensor configuration is empty

        In an empty sensor configuration all of the channels are disabled.

        Returns:

            ``True``, if all channels are disabled, ``False`` otherwise

        Examples:

            Check if some example configurations are empty or not

            >>> SensorConfiguration(first=3).empty()
            False
            >>> SensorConfiguration().empty()
            True
            >>> SensorConfiguration(third=0).empty()
            True

        """

        return self.first == 0 and self.second == 0 and self.third == 0

    def check(self):
        """Check that at least one measurement channel is enabled

        Raises:

            ValueError:
                if none of the measurement channels is enabled

        Examples:

            >>> SensorConfiguration(second=1).check()
            >>> SensorConfiguration().check()
            Traceback (most recent call last):
                ...
            ValueError: At least one measurement channel has to be enabled

        """

        if self.empty():
            raise ValueError(
                "At least one measurement channel has to be enabled"
            )

    def streaming_configuration(self) -> StreamingConfiguration:
        """Get a streaming configuration that represents this config

        Returns:

            A stream configuration where

            - every channel that is enabled in the sensor configuration is
              enabled, and
            - every channel that is disables in the sensor configuration is
              disabled.

        Examples:

            Get the streaming configuration for some example channel configs

            >>> SensorConfiguration(second=1).streaming_configuration()
            Channel 1 disabled, Channel 2 enabled, Channel 3 disabled

            >>> SensorConfiguration(first=10, third=2
            ...                    ).streaming_configuration()
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled

        """

        return StreamingConfiguration(**{
            channel: bool(value) for channel, value in self.attributes.items()
        })
