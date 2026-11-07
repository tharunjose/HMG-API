"""Run freestanding lpatch under Unicorn ARM with an in-memory EABI filesystem.

Host validation only; this does not model Android, dexopt, or vehicle behavior.
Requires unicorn==2.1.4. No emulated syscall accesses the host filesystem.
"""
import io
import struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_INTR
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R7, UC_ARM_REG_SP


def run(binary, args, files):
    assert binary[:7] == b'\x7fELF\x01\x01\x01'
    assert struct.unpack_from('<H', binary, 18)[0] == 40
    entry, phoff = struct.unpack_from('<II', binary, 24)
    phsize, phnum = struct.unpack_from('<HH', binary, 42)
    segments = [struct.unpack_from('<8I', binary, phoff+i*phsize) for i in range(phnum)]
    segments = [s for s in segments if s[0] == 1]
    low = min(s[2] for s in segments) & ~4095
    high = (max(s[2]+s[5] for s in segments)+4095) & ~4095
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    mu.mem_map(low, high-low)
    for _, offset, address, _, size, _, _, _ in segments:
        mu.mem_write(address, binary[offset:offset+size])
    stack = 0x70000000
    mu.mem_map(stack, 2 << 20)
    cursor = stack + (1 << 20)
    pointers = []
    for text in ['lpatch', *args]:
        data = text.encode() + b'\0'
        mu.mem_write(cursor, data)
        pointers.append(cursor)
        cursor += len(data)
    sp = stack + (512 << 10)
    words = [len(pointers), *pointers, 0, 0]
    mu.mem_write(sp, struct.pack('<'+'I'*len(words), *words))
    mu.reg_write(UC_ARM_REG_SP, sp)
    output = {1: bytearray(), 2: bytearray()}
    handles, writes = {}, {}
    result = {'code': None}
    def string(address):
        data = bytearray()
        for i in range(4096):
            b = mu.mem_read(address+i, 1)[0]
            if b == 0:
                return data.decode()
            data.append(b)
        raise ValueError('Unterminated path')
    def interrupt(cpu, number, _):
        if number != 2:
            raise ValueError('Unexpected ARM exception: ' + str(number))
        call = cpu.reg_read(UC_ARM_REG_R7)
        a, b, c = [cpu.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2)]
        if call == 1:
            result['code'] = a
            cpu.emu_stop()
            return
        elif call == 5:
            path = string(a)
            if b == 0 and path not in files:
                value = -2
            elif b not in (0, 0x241):
                raise ValueError('Unexpected open flags')
            else:
                value = max([2, *handles])+1
                handles[value] = io.BytesIO(files[path] if b == 0 else b'')
                if b:
                    writes[value] = path
        elif call == 3:
            data = handles[a].read(c)
            if data:
                cpu.mem_write(b, data)
            value = len(data)
        elif call == 4:
            data = bytes(cpu.mem_read(b, c))
            if a in output:
                output[a].extend(data)
                value = len(data)
            else:
                value = handles[a].write(data)
        elif call == 6:
            if a in writes:
                files[writes.pop(a)] = handles[a].getvalue()
            handles.pop(a)
            value = 0
        else:
            raise ValueError('Unexpected EABI syscall: '+str(call))
        cpu.reg_write(UC_ARM_REG_R0, value & 0xffffffff)
    mu.hook_add(UC_HOOK_INTR, interrupt)
    mu.emu_start(entry, 0xffffffff, timeout=60_000_000)
    assert result['code'] is not None, 'ARM execution timed out'
    return result['code'], bytes(output[1]), bytes(output[2]), files
