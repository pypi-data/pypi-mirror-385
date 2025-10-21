
import warnings
import pyvisa
from functools import wraps

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
pyvisa_logger = logging.getLogger('pyvisa')
pyvisa_logger.setLevel(logging.INFO)

VALID_INSTRUMENT_IDS = ['GPP-4323']


class CBGwiGpp():
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def print_instrument_list(self):
        # Ignore UserWarnings from pyvisa about resource discovery features
        warnings.simplefilter('ignore', category=UserWarning)

        rm = pyvisa.ResourceManager('@py')
        resources = rm.list_resources()

        log.info('Available instruments:')

        for resource in resources:
            instr = rm.open_resource(resource)

            instr = rm.open_resource(
                resource,
                baud_rate=115200, timeout=1,
                read_termination='\n', write_termination='\n')

            inst_id = instr.query('*IDN?', delay=0.1).strip()

            log.info(f' - {resource:<30} ID: {inst_id}')

        return resources

    def open_required(func):
        """Decorator to ensure the instrument interface is open
        before executing a method."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'instr') or self.instr is None:
                raise RuntimeError(
                    f'Interface is not open. Call open() method \
                        first before using {func.__name__}.')
            try:
                # Test if the interface is still alive by checking the session
                self.instr.session
                return func(self, *args, **kwargs)
            except (AttributeError, pyvisa.errors.InvalidSession):
                raise RuntimeError(
                    f'Interface connection lost. Please reopen the \
                        connection before using {func.__name__}.')
        return wrapper

    def open(self, instrument: str = 'ASRL/dev/ttyUSB0::INSTR'):
        self.rm = pyvisa.ResourceManager()
        self.instr = self.rm.open_resource(
            instrument,
            baud_rate=115200, timeout=1,
            read_termination='\n', write_termination='\n')

        if self.instr is None:
            raise ValueError(f'Could not open instrument at {instrument}')

        inst_id = self.instr.query('*IDN?', delay=0.1).strip()
        if self.verbose:
            log.info(f'Instrument ID: {inst_id}')

        self.check_instrument()

        return inst_id

    @open_required
    def check_instrument(self):
        # Verify that the connected instrument is a valid GWI GPP-x model
        # by checking the IDN string
        # Basicly all other GWI GPP-x models should be compatible,
        # but we limit it here to the GPP-4323 for safety reasons
        # in case there are differences in the command set.

        inst_id = self.instr.query('*IDN?', delay=0.1).strip()
        if not any(valid_id in inst_id for valid_id in VALID_INSTRUMENT_IDS):
            raise ValueError(
                f'Connected instrument is not supported: {inst_id}')
        return inst_id

    @open_required
    def close(self):
        self.instr.close()

    @open_required
    def set_channel(self,
                    channel: int = 1,
                    voltage: float = None,
                    current: float = None):

        if channel not in [1, 2, 3, 4]:
            raise ValueError(
                f'Invalid channel number: {channel}. Valid channels are 1-4.')

        self.instr.write(f':SOUR{channel}:VOLT {voltage}')
        self.instr.write(f':SOUR{channel}:CURR {current}')

    @open_required
    def output_on(self):
        self.instr.write('OUT1')

    @open_required
    def output_off(self):
        self.instr.write('OUT0')

    @open_required
    def get_measurements(self):
        voltage = self.instr.query('MEAS:VOLT:ALL?', delay=0.1)
        current = self.instr.query('MEAS:CURR:ALL?', delay=0.1)

        voltage = voltage.split(',')
        current = current.split(',')

        voltage = [float(i) for i in voltage]
        current = [float(i) for i in current]

        return voltage, current

    @open_required
    def print_measurements(self):

        voltage, current = self.get_measurements()

        for i, (v, c) in enumerate(zip(voltage, current), start=1):
            print(f'CH:{i}: '
                  f'{v:7.3f} V / '
                  f'{c:5.3f} A    ',
                  end='')

        print()
