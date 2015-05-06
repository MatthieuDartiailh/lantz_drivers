# -*- coding: utf-8 -*-
"""
    lantz_drivers.standards.ieee488
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base classes for instruments supporting standards
    command such *IDN?.

    A lot of those class are heavily insopired from the Slave package.

    The standards specifies that if one command of a group is implmented all
    commends should be implemented. However this is not always enforced. The
    base classes subdivide a bit more the commands to take this fact into
    account.

    Reporting Commands
     * `*CLS` - Clears the data status structure [#]_ .
     * `*ESE` - Write the event status enable register [#]_ .
     * `*ESE?` - Query the event status enable register [#]_ .
     * `*ESR?` - Query the standard event status register [#]_ .
     * `*SRE` - Write the status enable register [#]_ .
     * `*SRE?` - Query the status enable register [#]_ .
     * `*STB` - Query the status register [#]_ .

    Internal operation commands
     * `*IDN?` - Identification query [#]_ .
     * `*RST` -  Perform a device reset [#]_ .
     * `*TST?` - Perform internal self-test [#]_ .

    Synchronization commands
     * `*OPC` - Set operation complete flag high [#]_ .
     * `*OPC?` -  Query operation complete flag [#]_ .
     * `*WAI` - Wait to continue [#]_ .

    Power on common commands
     * `*PSC` - Set the power-on status clear bit [#]_ .
     * `*PSC?` - Query the power-on status clear bit [#]_ .

    Parallel poll common commands NOT IMPLEMENTED
     * `*IST?` - Query the individual status message bit [#]_ .
     * `*PRE` - Set the parallel poll enable register [#]_ .
     * `*PRE?` - Query the parallel poll enable register [#]_ .

    Resource description common commands
     * `*RDT` - Store the resource description in the device [#]_ .
     * `*RDT?` - Query the stored resource description [#]_ .

    Protected user data commands
     * `*PUD` - Store protected user data in the device [#]_ .
     * `*PUD?` - Query the protected user data [#]_ .

    Calibration command
     * `*CAL?` - Perform internal self calibration [#]_ .

    Trigger command
     * `*TRG` - Execute trigger command [#]_ .

    Trigger macro commands
     * `*DDT` - Define device trigger [#]_ .
     * `*DDT?` - Define device trigger query [#]_ .

    Macro Commands NOT IMPLEMENTED
     * `*DMC` - Define device trigger [#]_ .
     * `*EMC` - Define device trigger query [#]_ .
     * `*EMC?` - Define device trigger [#]_ .
     * `*GMC?` - Define device trigger query [#]_ .
     * `*LMC?` - Define device trigger [#]_ .
     * `*PMC` - Define device trigger query [#]_ .

    Option Identification command
     * `*OPT?` - Option identification query [#]_ .

    Stored settings commands
     * `*RCL` - Restore device settings from local memory [#]_ .
     * `*SAV` - Store current settings of the device in local memory [#]_ .

    Learn command NOT IMPLEMENTED
     * `*LRN?` - Learn device setup query [#]_ .

    System configuration commands NOT IMPLEMENTED
     * `*AAD` - Accept address command [#]_ .
     * `*DLF` - Disable listener function command [#]_ .

    Passing control command NOT IMPLEMENTED
     * `*PCB` - Pass control back [#]_ .

    Reference:

    .. [#] IEC 60488-2:2004(E) section 10.3
    .. [#] IEC 60488-2:2004(E) section 10.10
    .. [#] IEC 60488-2:2004(E) section 10.11
    .. [#] IEC 60488-2:2004(E) section 10.12
    .. [#] IEC 60488-2:2004(E) section 10.34
    .. [#] IEC 60488-2:2004(E) section 10.35
    .. [#] IEC 60488-2:2004(E) section 10.36
    .. [#] IEC 60488-2:2004(E) section 10.14
    .. [#] IEC 60488-2:2004(E) section 10.32
    .. [#] IEC 60488-2:2004(E) section 10.38
    .. [#] IEC 60488-2:2004(E) section 10.18
    .. [#] IEC 60488-2:2004(E) section 10.19
    .. [#] IEC 60488-2:2004(E) section 10.39
    .. [#] IEC 60488-2:2004(E) section 10.25
    .. [#] IEC 60488-2:2004(E) section 10.26
    .. [#] IEC 60488-2:2004(E) section 10.15
    .. [#] IEC 60488-2:2004(E) section 10.23
    .. [#] IEC 60488-2:2004(E) section 10.24
    .. [#] IEC 60488-2:2004(E) section 10.30
    .. [#] IEC 60488-2:2004(E) section 10.31
    .. [#] IEC 60488-2:2004(E) section 10.27
    .. [#] IEC 60488-2:2004(E) section 10.28
    .. [#] IEC 60488-2:2004(E) section 10.2
    .. [#] IEC 60488-2:2004(E) section 10.37
    .. [#] IEC 60488-2:2004(E) section 10.4
    .. [#] IEC 60488-2:2004(E) section 10.5
    .. [#] IEC 60488-2:2004(E) section 10.7
    .. [#] IEC 60488-2:2004(E) section 10.8
    .. [#] IEC 60488-2:2004(E) section 10.9
    .. [#] IEC 60488-2:2004(E) section 10.13
    .. [#] IEC 60488-2:2004(E) section 10.16
    .. [#] IEC 60488-2:2004(E) section 10.22
    .. [#] IEC 60488-2:2004(E) section 10.20
    .. [#] IEC 60488-2:2004(E) section 10.29
    .. [#] IEC 60488-2:2004(E) section 10.33
    .. [#] IEC 60488-2:2004(E) section 10.17
    .. [#] IEC 60488-2:2004(E) section 10.1
    .. [#] IEC 60488-2:2004(E) section 10.6
    .. [#] IEC 60488-2:2004(E) section 10.21

    .. _IEC 60488-2: http://dx.doi.org/10.1109/IEEESTD.2004.95390

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core.features import Bool, Register, Unicode
from lantz_core.action import Action
from lantz_core.utils import byte_to_dict
from lantz_core.backends.visa import VisaMessageDriver


# =============================================================================
# --- Status reporting --------------------------------------------------------
# =============================================================================

class StatusReporting(VisaMessageDriver):
    """Class implementing the status reporting commands.

    * `*CLS` - See IEC 60488-2:2004(E) section 10.3
    * `*ESE` - See IEC 60488-2:2004(E) section 10.10
    * `*ESE?` - See IEC 60488-2:2004(E) section 10.11
    * `*ESR?` - See IEC 60488-2:2004(E) section 10.12
    * `*SRE` - See IEC 60488-2:2004(E) section 10.34
    * `*SRE?` - See IEC 60488-2:2004(E) section 10.35
    * `*STB?` - See IEC 60488-2:2004(E) section 10.36

    """
    #: Meaning of the event register.
    EVENT_STATUS_REGISTER = (
        'operation complete',
        'request control',
        'query error',
        'device dependent error',
        'execution error',
        'command error',
        'user request',
        'power on',
    )

    #: Define which bits of the status byte cause a service request.
    service_request_enabled = Register('*SRE?', '*SRE {}')

    #: Define which bits contribute to the event status in the status byte.
    event_status_enabled = Register('*ESE?', '*ESE {}', )

    @Action()
    def read_event_status_register(self):
        """Read and clear the event register.

        """
        return byte_to_dict(int(self.query('*ESR?')),
                            self.EVENT_STATUS_REGISTER)


# =============================================================================
# --- Internal operations -----------------------------------------------------
# =============================================================================

class Identify(VisaMessageDriver):
    """Class implementing the identification command.

    """
    @Action()
    def read_idn(self):
        """Read the instrument id.

        """
        return self.query('*IDN')


class SelfTest(VisaMessageDriver):
    """Class implementing the self-test command.

    """
    #: Meaning of the self test result.
    SELF_TEST = {0: 'Normal completion'}

    @Action()
    def perform_self_test(self):
        """Run the self test routine.

        """
        return self.SELF_TEST.get(int(self.query('*TST?')), 'Unknown error')


class Reset(VisaMessageDriver):
    """Class implemnting the reset command.

    """
    @Action()
    def reset(self):
        """Initialize the instrument settings.

        After running this you might need to wait a bit before sending new
        commands to the instrument.

        """
        self.write('*RST')


class InternalOperations(Reset, SelfTest, Identify):
    """Class implementing all the internal operations.

    """
    pass


# =============================================================================
# --- Synchronisation ---------------------------------------------------------
# =============================================================================

class OperationComplete(VisaMessageDriver):
    """A mixin class implementing the operation complete commands.

    * `*OPC` - See IEC 60488-2:2004(E) section 10.18
    * `*OPC?` - See IEC 60488-2:2004(E) section 10.19

    """

    @Action()
    def complete_operation(self):
        """Sets the operation complete bit high of the event status byte.

        """
        self.write('*OPC')

    @Action()
    def is_operation_completed(self):
        """Check whether or not the instrument has completed all pending
        operations.

        """
        return bool(int(self.query('*OPC?')))


class WaitToContinue(VisaMessageDriver):
    """A mixin class implementing the wait command.

    * `*WAI` - See IEC 60488-2:2004(E) section 10.39

    """
    @Action()
    def wait_to_continue(self):
        """Prevents the device from executing any further commands or queries
        until the no operation flag is `True`.

       Notes
       -----
       In devices implementing only sequential commands, the no-operation
       flag is always True.

        """
        self.write('*WAI')


class Synchronisation(WaitToContinue, OperationComplete):
    """A mixin class implementing all synchronisation methods.

    """
    pass


# =============================================================================
# --- Power on ----------------------------------------------------------------
# =============================================================================

class PowerOn(VisaMessageDriver):
    """A mixin class, implementing the optional power-on common commands.

    The IEC 60488-2:2004(E) defines the following optional power-on common
    commands:

    * `*PSC` - See IEC 60488-2:2004(E) section 10.25
    * `*PSC?` - See IEC 60488-2:2004(E) section 10.26

    """
    #: Represents the power-on status clear flag. If it is `False` the event
    #: status enable, service request enable and serial poll enable registers
    #: will retain their status when power is restored to the device and will
    #: be cleared if it is set to `True`.
    poweron_status_clear = Bool('*PSC?', '*PSC {}',
                                mapping={True: '1', False: '0'})


# =============================================================================
# --- Resource description ----------------------------------------------------
# =============================================================================

class ResourceDescription(VisaMessageDriver):
    """A class implementing the resource description common commands.

    * `*RDT` - See IEC 60488-2:2004(E) section 10.30
    * `*RDT?` - See IEC 60488-2:2004(E) section 10.31

    """
    #: Descrption of the resource. The formatting is not checked.
    resource_description = Unicode('*RDT?', '*RDT {}')


# =============================================================================
# --- Protected user data -----------------------------------------------------
# =============================================================================

class ProtectedUserData(VisaMessageDriver):
    """A class implementing the protected user data common commands.

    * `*RDT` - See IEC 60488-2:2004(E) section 10.30
    * `*RDT?` - See IEC 60488-2:2004(E) section 10.31

    """
    #: Protected user data. The validaty of the passed string is not checked.
    protected_user_data = Unicode('*PUD?', '*PUD {}')


# =============================================================================
# --- Calibration -------------------------------------------------------------
# =============================================================================

class Calibration(object):
    """A class implementing the optional calibration command.

    * `*CAL?` - See IEC 60488-2:2004(E) section 10.2

    """
    CALIBRATION = {0: 'Calibration completed'}

    def calibrate(self):
        """Performs a internal self-calibration.

        """
        return self.CALIBRATION.get(int(self.query('*CAL?')), 'Unknown error')


# =============================================================================
# --- Triggering --------------------------------------------------------------
# =============================================================================

class Trigger(VisaMessageDriver):
    """A class implementing the optional trigger command.

    * `*TRG` - See IEC 60488-2:2004(E) section 10.37

    It is mandatory for devices implementing the DT1 subset.

    """
    def __init__(self, *args, **kw):
        super(Trigger, self).__init__(*args, **kw)

    def trigger(self):
        """Creates a trigger event.

        """
        self.write('*TRG')


# =============================================================================
# --- Macro trigger -----------------------------------------------------------
# =============================================================================

class TriggerMacro(Trigger):
    """A class implementing the optional trigger macro commands.

    * `*DDT` - See IEC 60488-2:2004(E) section 10.4
    * `*DDT?` - See IEC 60488-2:2004(E) section 10.5

    """
    #: Sequence of commands to execute when receiving a trigger.
    trigger_macro = Unicode('*DDT?', 'DDT {}')


# =============================================================================
# --- Option identification ---------------------------------------------------
# =============================================================================

class OptionsIdentification(VisaMessageDriver):
    """A class implementing the option identification command.

    * `*OPT?` - See IEC 60488-2:2004(E) section 10.20

    """
    instr_options = Unicode('*OPT?')


# =============================================================================
# --- Stored settings ---------------------------------------------------------
# =============================================================================

class StoredSettings(VisaMessageDriver):
    """A class implementing the stored setting commands.

    * `*RCL` - See IEC 60488-2:2004(E) section 10.29
    * `*SAV` - See IEC 60488-2:2004(E) section 10.33

    """
    @Action()
    def recall(self, idx):
        """Restores the current settings from a copy stored in local memory.

        Paremters
        ---------
        idx : int
            Specifies the memory slot.

        """
        self.write('*RCL {}'.format(idx))

    @Action()
    def save(self, idx):
        """Stores the current settings of a device in local memory.

        Parameters
        ----------
        idx : int
            Specifies the memory slot.

        """
        self.write('*SAV {}'.format(idx))
