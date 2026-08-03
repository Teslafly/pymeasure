#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PSChannel(Channel):
    """Implementation of a P4KF-80x channel."""

    VOLTAGE_RANGE = [0, 70] ## query this from instrument
    CURRENT_RANGE = [0, 45] # query this from instrument

    get_voltage_range(self):


    output_bleeder_enabled = Instrument.control(
        "SYSTem:BLEEDer?",
        "SYSTem:BLEEDer %d",
        """ Turn the current sink function OFF/ON """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    output_enabled = Instrument.control( #todo: fix for p4k psu
        "SOURCE:OUTP?",
        "SOURCE:OUTP %d",
        """ Control the output state.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage_setpoint = Instrument.control(#todo: fix for p4k psu
        "VOLT?",
        "VOLT %g",
        """ Control output voltage in Volts.""",
        validator=strict_range,
        values=VOLTAGE_RANGE,
    )

    current_limit = Instrument.control( #todo: fix for p4k psu
        "CURR?",
        "CURR %g",
        """ Control output current in Amps.""",
        validator=strict_range,
        values=CURRENT_RANGE,
    )

    current = Instrument.measurement( #todo: fix for p4k psu
        "MEAS:CURR?",
        """ Measure the current in Amps.""",
    )

    voltage = Instrument.measurement( #todo: fix for p4k psu
        "MEAS:VOLT?",
        """ Measure the voltage in Volts.""",
    )

    power = Instrument.measurement( #todo: fix for p4k psu
        "MEAS:POW?",
        """ Measure the power in watts.""",
    )

    voltage_limit = Instrument.control( #todo: fix for p4k psu
        "VOLT:LIM?",
        "VOLT:LIM %g",
        """ Control the maximum voltage that can be set.""",
        validator=strict_range,
        values=VOLTAGE_RANGE,
    )

    voltage_limit_enabled = Instrument.control( #todo: fix for p4k psu
        "VOLT:LIM:STAT?",
        "VOLT:LIM:STAT %d",
        """ Control whether the maximum voltage limit is enabled.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def insert_id(self, command):
        """ Specifies the unit number that should respond to SCPI command.
            Only applicable when multiple supplies chained to master supply 
            using master/slave function """
        return f"INST:NSEL {self.id};{command}"


    # Use SCPIMixin to avoide warning. Instrument does not have full IEEE4882 compliant scpi command support.
    # only *IDN? and *RST are supported.
class MatsusadaP4KF80(SCPIMixin, Instrument):
    """Represents the Matsusada P4KF-80x Power Supply."""

    def __init__(self, adapter, name="P4KF-80", **kwargs):
        super().__init__(adapter, name, **kwargs)

    ch_1 = Instrument.ChannelCreator(PSChannel, 1)

    remote = Instrument.control(
        "SYST?", 
        "SYST:%s",
        """Control the current remote operation of the power supply.

        SYSTem?         Acquires local/remote 
        SYSTem:LOCal    Sets local mode
        SYSTem:REMote   Sets remote mode
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values=["LOC", "REM", "LOCAL", "REMOTE"],
        cast=str
    )

    # SYSTem:MODe? Acquires status 
    # return example: "OFF RM CC OVP LD"
    #                 ([Output status] [Operation status] [Active status] [Error description])
