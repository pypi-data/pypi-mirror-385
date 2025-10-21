# This is a Zapf simulated PLC that runs automatically for the demo config.

# pylint: skip-file
# ruff: noqa: PGH004
# ruff: noqa

import time

from zapf.simulator.funcs import adr, memcpy, memset, sizeof
from zapf.simulator.runtime import (
    Globals,
    Struct,
    Var,
    array,
    byte,
    dword,
    program,
    real,
    string,
    word,
)
from zapf.spec import FLOAT32_MAX
from zapf.spec.v_2021_09 import DEVICE_FLAGS, encode_unit

PILS_MAGIC = 2021.09
DESCRIPTOR_SLOT_SIZE = 48
DESCRIPTOR_SLOTS = 4
INDEXER_DATA_SIZE = DESCRIPTOR_SLOTS * DESCRIPTOR_SLOT_SIZE
INDEXER_SIZE = 2 + INDEXER_DATA_SIZE
INDEXER_OFFSET = 6
PARAM_DEFAULTS = [0, 100, 10, 90, 5, 500, 0, 10, 2, 0, 0.125, 0, 10, 1, 0, 0, 0, 0]


class DevicesLayout(Struct):
    # di32, do32  (re-using do32_target as di32_value)
    dx32_value = Var(dword, 0)
    dx32_target = Var(dword, 0)
    dx32_estatus = Var(dword, 0x10000000)
    dx32_padding = Var(dword, 0)

    # pi/po32
    fax32_params = Var(array(real, 0, 17), PARAM_DEFAULTS)
    px32_value = Var(real, 50)
    px32_target = Var(real, 0)
    px32_estatus = Var(dword, 0x10000000)
    px32_nerrid = Var(word, 0)
    px32_pctl = Var(word, 0)
    px32_pvalue = Var(real, 0)

    # table storage: 1d
    table32_act_row = Var(word, 0)
    table32_req_row = Var(word, 0)
    table32_line = Var(array(real, 0, 9))
    # table storage: 2d, direct mapped
    table32 = Var(array(real, 0, 99))


alignment_ok = True
for _n, addr in DevicesLayout.OFFSET.items():
    o = getattr(DevicesLayout, _n)
    try:
        size = o.dtype.INNER.sizeof()
    except AttributeError:
        size = o.dtype.sizeof()
    if addr != (addr // size) * size:
        print(f'{_n} is not correctly aligned! (addr={addr}, size={size})')
        alignment_ok = False
assert alignment_ok


def addrof(n):
    return 200 + DevicesLayout.OFFSET[n]


class PLCDescriptor(Struct):
    dt = Var(word, 0x1010)
    devices = Var(word, 0)
    description = Var(word, 0)
    version = Var(word, 0)
    author = Var(word, 0)
    desc_slot_size = Var(word, DESCRIPTOR_SLOT_SIZE)
    num_devices = Var(word, 0)
    flags = Var(word, (DESCRIPTOR_SLOTS - 1) << 12)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 16 - 1), '')
    # flags, desc_slot_size == const, num_devices -> magic!
    keys = 'dt', 'devices', 'description', 'version', 'author', 'name'


class DeviceDescriptor(Struct):
    dt = Var(word, 0x2014)
    prev = Var(word, 0)
    description = Var(word, 0)
    value_param = Var(word, 0)
    aux = Var(word, 0)
    params = Var(word, 0)
    errid = Var(word, 0)
    typecode = Var(word, 0)
    address = Var(word, 0)
    flags = Var(word, 0)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 20 - 1), '')
    keys = 'dt', 'prev', 'description', 'value_param', 'aux', 'params', \
        'errid', 'typecode', 'address', 'flags', 'name'


class StringDescriptor(Struct):
    dt = Var(word, 0x3004)
    prev = Var(word, 0)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 4 - 1), '')
    keys = 'dt', 'prev', 'name'


class EnumDescriptor(Struct):
    dt = Var(word, 0x4006)
    prev = Var(word, 0)
    # don't name a field 'value' or 'addr' or the simulator may ignore writes to it...
    val = Var(word, 0)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 6 - 1), '')
    keys = 'dt', 'prev', 'val', 'name'


class BitfieldDescriptor(Struct):
    dt = Var(word, 0x5008)
    prev = Var(word, 0)
    enum_id = Var(word, 0)
    lsb = Var(byte, 0)
    width = Var(byte, 1)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 8 - 1), '')
    keys = 'dt', 'prev', 'enum_id', 'lsb', 'width', 'name'


class FlagDescriptor(Struct):
    dt = Var(word, 0x5105)
    prev = Var(word, 0)
    lsb = Var(byte, 0)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 5 - 1), '')
    keys = 'dt', 'prev', 'lsb', 'name'


class NumericParameterDescriptor(Struct):
    dt = Var(word, 0x6114)
    prev = Var(word, 0)
    description = Var(word, 0)
    paramidx = Var(word, 0)
    paramtype = Var(word, 0)
    unit = Var(word, 0)
    minval = Var(real, -FLOAT32_MAX)
    maxval = Var(real, FLOAT32_MAX)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 20 - 1), '')
    keys = 'dt', 'prev', 'description', 'paramidx', 'paramtype', 'unit', \
        'minval', 'maxval', 'name'


class EnumParameterDescriptor(Struct):
    dt = Var(word, 0x620E)
    prev = Var(word, 0)
    description = Var(word, 0)
    read_enum_id = Var(word, 0)
    write_enum_id = Var(word, 0)
    paramidx = Var(word, 0)
    paramtype = Var(word, 0)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 14 - 1), '')
    keys = 'dt', 'prev', 'description', 'read_enum_id', 'write_enum_id', \
        'paramidx', 'paramtype', 'name'


class SpecialFuncDescriptor(Struct):
    dt = Var(word, 0x680E)
    prev = Var(word, 0)
    description = Var(word, 0)
    arg_id = Var(word, 0)
    res_id = Var(word, 0)
    paramidx = Var(word, 0)
    paramtype = Var(word, 0)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 14 - 1), '')
    keys = 'dt', 'prev', 'description', 'arg_id', 'res_id', 'paramidx', \
        'paramtype', 'name'


class TableDescriptor(Struct):
    dt = Var(word, 0x6C10)
    prev = Var(word, 0)
    description = Var(word, 0)
    columns = Var(word, 0)
    base = Var(word, 0)
    flags = Var(word, 0)
    last_row = Var(word, 0)
    last_column = Var(word, 0)
    name = Var(string(DESCRIPTOR_SLOT_SIZE - 16 - 1), '')
    keys = 'dt', 'prev', 'description', 'columns', 'base', 'flags', \
        'last_row', 'last_column', 'name'


class DebugDescriptor(Struct):
    dt = Var(word, 0xFF06)
    cycle = Var(word, 0)
    indexer_size = Var(word, 0)
    text = Var(string(INDEXER_DATA_SIZE - 6 - 1), '')  # Yes: this is BIG
    keys = 'dt', 'cycle', 'text'


class ST_Indexer(Struct):
    Request = Var(word, 0)
    #    Data = Var(array(U_Descriptor, 0, DESCRIPTOR_SLOTS-1))
    Data = Var(array(array(byte, 0, DESCRIPTOR_SLOT_SIZE - 1), 0, DESCRIPTOR_SLOTS - 1))


# singletons


PLC_DESCRIPTOR = PLCDescriptor(name='testplc_2021_09.py').alloc_self()
DEBUG_DESCRIPTOR = DebugDescriptor(text='PLC_Problem 42, please call 137',
                                   indexer_size=INDEXER_DATA_SIZE).alloc_self()


# map descriptorid/descriptortuple to descriptor
DESCRIPTOR_ARRAY = [PLC_DESCRIPTOR]
descriptors = {}


def add_descr(t, Descr):
    # pylint: disable=global-statement
    if t in descriptors:
        return descriptors[t]
    next_descriptor = len(DESCRIPTOR_ARRAY)
    kwds = dict(zip(Descr.keys, t))
    d = Descr(**kwds).alloc_self()
    descriptors[t] = next_descriptor
    DESCRIPTOR_ARRAY.append(d)
    return next_descriptor


def add_Device(name, typecode, address, description='', value_param=None,
               aux=0, params=0, errid=0, flags=0, unit=''):
    if value_param is None:
        # provide some sensible default for most devices
        if typecode in (0x1201, 0x1401, 0x1602, 0x1A02, 0x1E03, 0x1E04):
            value_param = add_IntParam(0, '', 'rw', 0, -32768, 32767)
        elif typecode in (0x1202, 0x1402, 0x1604, 0x1A04, 0x1E06):
            value_param = add_IntParam(0, '', 'rw', 0, -(2 ** 31), 2 ** 31 - 1)
        elif typecode in (0x1204, 0x1404, 0x1608, 0x1A08, 0x1E0C):
            value_param = add_IntParam(0, '', 'rw', 0, -(2 ** 63), 2 ** 63 - 1)
        elif typecode >> 8 != 5:  # not for MSGIO !
            value_param = add_FloatParam(0, '', 'rw', 0, -FLOAT32_MAX, FLOAT32_MAX,
                                         encode_unit(unit) if isinstance(unit, str) else unit)
        else:
            value_param = 0
    if isinstance(flags, str):
        flags = [flags]
    try:
        int(flags)
    except TypeError:
        f = 0
        for bit, fn in DEVICE_FLAGS.items():
            if fn in flags:
                fn |= 1 << bit
        flags = f
    t = (
        0x2014,
        PLC_DESCRIPTOR.devices,
        add_String(description),
        value_param,
        aux,
        params,
        errid,
        typecode,
        address,
        flags,
        name,
    )
    PLC_DESCRIPTOR.devices = add_descr(t, DeviceDescriptor)
    PLC_DESCRIPTOR.num_devices += 1
    # no return....


def add_String(s):
    prev = 0
    while s:
        part, s = s[: DESCRIPTOR_SLOT_SIZE - 4 - 1], s[DESCRIPTOR_SLOT_SIZE - 4 - 1:]
        t = (0x3004, prev, part)
        prev = add_descr(t, StringDescriptor)
    return prev


def add_Enum(prev, val, name):
    t = (0x4006, prev, val, name)
    return add_descr(t, EnumDescriptor)


def add_Enums(prev, enumdict):
    # add all values of a dict to the given chain.
    # XXX: also remove duplicates aready in prev? How?
    for v, n in sorted(enumdict.items()):
        prev = add_Enum(prev, v, n)
    return prev


def add_Bitfield(prev, name, lsb, width, enum):
    if isinstance(enum, dict):
        enum = add_Enums(0, enum)
    t = (0x5008, prev, enum, lsb, width, name)
    return add_descr(t, BitfieldDescriptor)


def add_Flag(prev, lsb, name):
    t = (0x5105, prev, lsb, name)
    return add_descr(t, FlagDescriptor)


def add_BfFChain(prev, chain):
    # chain is an iterable of 2/4 tuples for flags/bitfields
    # flags: (bit, name)
    # bitfield: (name, lsb, width, enumdict)
    for e in chain:
        if len(e) == 2:
            prev = add_Flag(prev, *e)
        elif len(e) == 4:
            prev = add_Bitfield(prev, *e)
        else:
            raise RuntimeError(f'bad Element {e} in Bitfield/Flag Chain: {chain}')
    return prev


WRO_MAP = {'rw': 1, 'ro': 2, 'obs': 3}  # writeable, readonly, observable


def add_IntParam(prev, name, wro, idx, minval, maxval, unit=0, description=''):
    if isinstance(description, str):
        description = add_String(description)
    wro = WRO_MAP.get(wro, wro) & 3
    if isinstance(unit, str):
        unit = encode_unit(unit)
    t = (0x6114, prev, description, idx, (0xC + wro) << 12, unit, minval, maxval, name)
    return add_descr(t, NumericParameterDescriptor)


def add_FloatParam(prev, name, wro, idx, minval, maxval, unit='', description=''):
    if isinstance(description, str):
        description = add_String(description)
    wro = WRO_MAP.get(wro, wro) & 3
    if isinstance(unit, str):
        unit = encode_unit(unit)
    t = (0x6114, prev, description, idx, (0x4 + wro) << 12, unit, minval, maxval, name)
    return add_descr(t, NumericParameterDescriptor)


def add_EnumParam(prev, name, wro, idx, read_enum, write_enum=0, description=''):
    if isinstance(description, str):
        description = add_String(description)
    wro = WRO_MAP.get(wro, wro) & 3
    if read_enum == 0:
        read_enum = write_enum
    if isinstance(read_enum, dict):
        if isinstance(write_enum, dict):
            read_enum.update(write_enum)
        read_enum = add_Enums(0, read_enum)
    if isinstance(write_enum, dict):
        write_enum = add_Enums(0, write_enum)
    t = (0x620E, prev, description, read_enum, write_enum, idx, (0x8 + wro) << 12, name)
    return add_descr(t, EnumParameterDescriptor)


def add_SFunc(prev, name, idx, arg_id, res_id, description=''):
    if isinstance(description, str):
        description = add_String(description)
    t = (0x680E, prev, description, arg_id, res_id, idx, 0, name)
    return add_descr(t, SpecialFuncDescriptor)


def add_Table(prev, name, base, typ, columns, last_row, last_column, description=''):
    if isinstance(description, str):
        description = add_String(description)
    t = (0x6C10, prev, description, columns, base, (typ & 3) << 14, last_row, last_column, name)
    return add_descr(t, TableDescriptor)


# prepare some chains to be used later

AUX8 = add_BfFChain(0, [(d, f'AUX{d}') for d in range(6)] +
                    [('Minion', 6, 2, {1: 'Ape', 2: 'Banana', 3: 'Dragon'})])

AUX24 = add_BfFChain(AUX8, [(d, f'AUX{d}') for d in range(8, 20)] +
                     [('Minion', 6, 3, {4: 'Hamster', 2:''})] +
                     [(d, f'AUX{d}') for d in range(20, 24)] +
                     [('', 21, 1, {1:'aux22', 0:'nix'})]+
                     [('X', 18, 3, {})] +
                     [('', 22, 2, {0:'', 1:'Under voltage', 2:'Over voltage', 3:'no Power'})])

ERRID = add_BfFChain(
    0, [('lowerByte', 0, 8, 0), ('topmost 7 Bit', 9, 7, 0), (8, 'a Flag')]
)

PARS_1 = add_FloatParam(0, 'UserMin', 'rw', 0, 0, 100, '#', 'lower user settable limit')
PARS_2 = add_FloatParam(PARS_1, 'UserMax', 'rw', 1, 0, 100, '#', 'upper user settable limit')
PARS_3 = add_FloatParam(PARS_2, 'WarnMin', 'rw', 2, 0, 100, '#', 'lower warn limit')
PARS_4 = add_FloatParam(PARS_3, 'WarnMax', 'rw', 3, 0, 100, '#', 'upper warn limit')
PARS_5 = add_FloatParam(PARS_4, 'Timeout', 'rw', 4, 0, 900, 's', 'timeout for movement in s')
PARS_6 = add_FloatParam(PARS_5, 'MaxTravelDist', 'rw', 5, 0, 500, '#', 'maximum travel distance')
PARS_7 = add_FloatParam(PARS_6, 'Offset', 'ro', 6, 0, 100, '#', 'internal offset')
PARS_8 = add_FloatParam(PARS_7, 'P', 'rw', 7, 0, 100, '%/(#)', 'P constant for regulation')
PARS_9 = add_FloatParam(PARS_8, 'I', 'rw', 8, 0, 100, 's', 'I constant for regulation')
PARS_10 = add_FloatParam(PARS_9, 'D', 'rw', 9, 0, 100, '1/s', 'D constant for regulation')
PARS_11 = add_FloatParam(PARS_10, 'Hysteresis', 'rw', 10, 0, 100, '#', 'Hysteresis for regulation')
PARS_12 = add_FloatParam(PARS_11, 'Holdback', 'rw', 11, 0, 100, '#', 'max difference between actual temp and setpoint')
PARS_13 = add_FloatParam(PARS_12, 'Speed', 'rw', 12, 0.1, 100, '#/s', 'max speed of movement')
PARS_14 = add_FloatParam(PARS_13, 'Accel', 'rw', 13, 0, 100, '#/s^2', 'acceleration of movement')
PARS_15 = add_FloatParam(PARS_14, 'Home', 'rw', 14, 0, 100, '#', 'Home Position')
PARS_16 = add_FloatParam(PARS_15, 'Setpoint', 'obs', 15, 0, 100, '#', 'actual setpoint')
PARS_17 = add_EnumParam(PARS_16, 'microsteps', 'rw', 16, 0, {s:f'{2**s} steps' for s in range(9)}, 'microstepping selection')
PARS_18 = add_IntParam(PARS_17, 'numbits', 'rw', 17, 1, 32, 'bit', 'number of bits per ssi transfer')

TCOL_ = add_EnumParam(PARS_10, 'enable', 'rw', 0, {2:'enabled', 1:'updating', 0:'ignored'}, {2:'enabled', 0:'ignored'},
                      'en/disable this table row')
TCOL = add_EnumParam(TCOL_, 'microsteps', 'rw', 9, 0, {s:f'{2**s} steps' for s in range(9)}, 'microstepping selection')

SFUNC_1 = add_SFunc(PARS_18, 'reset_to_factory_default', 128,
                    add_IntParam(0, 'unlock_value', 'rw', 0, -2**31, 2**31-1, '', 'Unlock value'),
                    0,
                    'resets everything to factory defaults'
                    )
SFUNC_2 = add_SFunc(SFUNC_1, 'home', 133, 0, 0, 'starts a homing cycle')
SFUNC_3 = add_SFunc(SFUNC_2, 'SetPosition', 137, PARS_15, 0, 'sets a new current position')
SFUNC_4 = add_SFunc(SFUNC_3, 'ContMove', 142, PARS_13, 0, 'Starts a continuous movement')
SFUNC_5 = add_SFunc(SFUNC_4, 'SetBits', 240, PARS_18, PARS_18, 'set and read-back current number of bits')
SFUNC_6 = add_SFunc(SFUNC_5, 'GetBits', 241, 0, PARS_18, 'read-back current number of bits')

TABLE_2 = add_Table(SFUNC_6, 'table2', addrof('table32'), 2, TCOL, 9, 9,
                    '32 bit extra simple 10x10 table, direct mapped')
TABLE_1 = add_Table(TABLE_2, 'table1', addrof('table32_act_row'), 1, TCOL, 9, 9,
                    '32 bit extra simple 10x10 table, with line select')
TABLE32 = add_Table(TABLE_1, 'table0', 1000, 0, TCOL, 9, 9,
                    '32 bit extra simple 10x10 table, via paramctlif')

ENUM_1 = add_Enums(0, {0: 'On', 1: 'Off'})
ENUM_2 = add_Enum(ENUM_1, 2, 'Moving')

VT_UINT32 = add_IntParam(0, 'ignored pname', 'rw', -1, 0, 2**32-1, '', 'unsigned 32 bit integer')

add_Device('di32', 0x1a04, addrof('dx32_target'), value_param=VT_UINT32, description='discrete input, 32 bit',
           aux=AUX24)
add_Device('pi32', 0x4008, addrof('px32_target'), unit='%', description='parameter output, 32 bit',
           aux=AUX24, params=TABLE32, errid=ERRID)
add_Device('po32', 0x500a, addrof('px32_value'), unit='%', description='parameter output, 32 bit',
           aux=AUX24, errid=ERRID, params=TABLE32)


PLC_DESCRIPTOR.description = add_String('simulation for testing zapf')
PLC_DESCRIPTOR.version = add_String('https://forge.frm2.tum.de/review/mlz/pils/zapf:v2.1-alpha')
PLC_DESCRIPTOR.author = add_String('anonymous\nauthor')


class Global(Globals):
    fMagic = Var(real, PILS_MAGIC, at='%MB0')
    iOffset = Var(word, INDEXER_OFFSET, at='%MB4')

    stIndexer = Var(ST_Indexer, at=f'%MB{INDEXER_OFFSET}')

    data = Var(DevicesLayout, at='%MB200')

    iCycle = Var(word, 0)


g = Global()

@program(
    nDevices = Var(word),
    devnum = Var(word),
    infotype = Var(word),
    itemp = Var(byte),
    tempofs = Var(word),
)
def Indexer(v):
    if g.fMagic != PILS_MAGIC:
        g.fMagic = PILS_MAGIC
    if g.iOffset != INDEXER_OFFSET:
        g.iOffset = INDEXER_OFFSET

    g.iCycle += 1

    if g.stIndexer.Request[[15]]:
        return

    req_num = g.stIndexer.Request & 0x7FFF

    data = g.stIndexer.Data
    memset(adr(data), 0, sizeof(data))

    if req_num == 32767:
        DEBUG_DESCRIPTOR.cycle = g.iCycle
        memcpy(adr(data), adr(DEBUG_DESCRIPTOR), sizeof(DEBUG_DESCRIPTOR))
    else:
        for i in range(DESCRIPTOR_SLOTS):
            if req_num + i < len(DESCRIPTOR_ARRAY):
                memcpy(adr(data) + i*DESCRIPTOR_SLOT_SIZE,
                       adr(DESCRIPTOR_ARRAY[req_num + i]),
                       DESCRIPTOR_SLOT_SIZE)

    g.stIndexer.Request[[15]] = 1


# helper
def advance32(value, target, status, usermin=0.0, usermax=100.0,
              warnmin=10.0, warnmax=90.0, speed=10.0):
    state = status >> 12
    reason = 0
    if state == 0:
        state = 1
    elif state in [1, 3, 7]:
        state = 1 if warnmin <= value <= warnmax else 3
    elif state == 5:
        state, reason = (6, 0) if usermin <= target <= usermax else (8, 1)
    elif state == 6:
        if value == target:
            state, reason = 1, 0
        value += max(min((target - value), speed / 20), -speed / 20)
    target = max(min(usermax, target), usermin)
    if value < warnmin:
        reason |= 4
    if value > warnmax:
        reason |= 8

    return value, target, (state << 12) | (reason << 8) | (1 << ((g.iCycle >> 9) & 7))


# same as above but for 32 bit status fields
def advance64(value, target, status, *args, **kwds):
    v, t, s = advance32(value, target, max(status >> 16, status & 0xFFFF), *args, **kwds)
    return v, t, s << 16 | s


# pylint: disable=too-many-return-statements
def handle_pctl(pctl, pvalue, valuestore, tablestore):
    pnum = pctl & 8191
    cmd = pctl >> 13
    if pctl & 0x8000:
        # nothing to do
        return pctl, pvalue
    elif not cmd:
        return 0x2000, pvalue
    if pnum in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                17, 128, 133, 137, 142, 240, 241] or 1000 <= pnum <= 1099:
        # param exists, can at least be read
        if cmd == 1:  # DO_READ
            if 0 <= pnum <= 17:
                # return DONE and value
                return 0x8000 | pnum, valuestore[pnum]
            elif pnum == 240:
                return 0x8000 | pnum, valuestore[17]
            elif pnum == 241:
                return 0x8000 | pnum, valuestore[17]
            elif 1000 <= pnum <= 1099:
                # table access
                # return DONE and value
                return 0x8000 | pnum, float(tablestore[pnum - 1000])
            # invent value and DONE
            return 0x8000 | pnum, 0
        if cmd == 2:  # DO_WRITE
            if 0 <= pnum <= 17:
                valuestore[pnum] = pvalue
                return 0x2000 | pnum, pvalue  # -> read
            elif pnum == 240:
                valuestore[17] = pvalue
                return 0x8000 | pnum, valuestore[17]
            elif pnum == 241:
                return 0x8000 | pnum, valuestore[17]
            elif 128 <= pnum <= 239:
                # go to BUSY for some and ERR_RETRY for others
                if pnum in (128, 133):
                    return 0x6000 | pnum, pvalue
                return 0xE000 | pnum, pvalue  # ERR_RETRY
            elif 1000 <= pnum <= 1099:
                tablestore[pnum - 1000] = float(pvalue)
                return 0x2000 | pnum, pvalue  # -> read
            # no function, no storage -> ERR_READ_ONLY
            return 0xC000 | pnum, pvalue
        if cmd == 3:  # BUSY
            return 0x2000 | pnum, pvalue
        raise RuntimeError(f'handle_pctl({pctl}, {pvalue}, {valuestore}): '
                           'This should never happen!')
    else:
        # non exisiting param -> ERR_NO_IDX
        return 0xA000 | pnum, pvalue


def handle_dx16(value, target, status):
    if status >> 12 == 5:
        return target, 0x6000
    return value, 0x1000


def handle_dx32(value, target, status):
    v, s = handle_dx16(value, target, max(status >> 16, status & 0xFFFF))
    return v, s << 16 | s


@program(msg=Var(array(byte, 0, 80)), msglen=Var(byte, 0))
def Implementation(v):
    d = g.data

    d.dx32_target &= 0xFFFFFF
    d.dx32_value, d.dx32_estatus = handle_dx32(
        d.dx32_value, d.dx32_target, d.dx32_estatus
    )

    d.px32_value, d.px32_target, d.px32_estatus = advance64(
        d.px32_value, d.px32_target, d.px32_estatus,
        usermin = d.fax32_params[0], usermax = d.fax32_params[1],
        warnmin = d.fax32_params[2], warnmax = d.fax32_params[3],
        speed = d.fax32_params[12],
    )
    d.px32_nerrid = d.px32_estatus >> 15 if d.px32_estatus[[31]] else 0
    d.px32_pctl, d.px32_pvalue = handle_pctl(
        d.px32_pctl, d.px32_pvalue, d.fax32_params, d.table32
    )

    # handle table lines
    if d.table32_req_row != d.table32_act_row:
        # write back
        memcpy(
            adr(d.table32) + 40 * d.table32_act_row,
            adr(d.table32_line),
            sizeof(d.table32_line),
        )
        # avoid illegal values for req_row
        if not 0 <= d.table32_req_row <= 9:
            d.table32_req_row = d.table32_act_row
        # read from table
        memcpy(
            adr(d.table32_line),
            adr(d.table32) + 40 * d.table32_req_row,
            sizeof(d.table32_line),
        )
        d.table32_act_row = d.table32_req_row


@program()
def Main(v):
    # slow down simulation; this is both good for CPU load and for
    # simulating a slow connection for Zapf
    time.sleep(0.01)
    Indexer()
    Implementation()
