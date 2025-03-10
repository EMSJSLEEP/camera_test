from mix.tools.util.logfactory import create_null_logger
from mix.driver.modulebase.mixcomponent import MIXComponent
from hashlib import sha1
from glob import glob

class XINFO_FIELD():

    def __init__(self, offset, length):
        self._offset = offset
        self._length = length

    @property
    def offset(self):
        return self._offset

    @property
    def length(self):
        return self._length

    @property
    def slice(self):
        return slice(self._offset, self._offset + self._length)

# See rdar://72450811
XINFO_TABLE = {
    1: {
        'format': XINFO_FIELD(0x00, 1),
        'capacity': XINFO_FIELD(0x01, 2),
        'sn': XINFO_FIELD(0x03, 16),
        'reserved': XINFO_FIELD(0x13, 1),
        'ers': XINFO_FIELD(0x14, 1),
        'config': XINFO_FIELD(0x15, 3),
        'num_cals': XINFO_FIELD(0x18, 1),
        'cal_datasize': XINFO_FIELD(0x19, 4),
        'module_condition': XINFO_FIELD(0x1d, 1),
        'reserved2': XINFO_FIELD(0x1e, 14),
        'checksum': XINFO_FIELD(0x2c, 20),
        'macaddress': XINFO_FIELD(0x40, 6),
        'macaddress_checksum': XINFO_FIELD(0x46, 1),
        'checksum_content': XINFO_FIELD((0x00), 0x2c),  # This is really a block, not a field.
    },
    4: {
        'format': XINFO_FIELD(0x00, 1),
        'capacity': XINFO_FIELD(0x01, 2),
        'sn': XINFO_FIELD(0x03, 17),
        'ers': XINFO_FIELD(0x14, 1),
        'config': XINFO_FIELD(0x15, 3),
        'num_cals': XINFO_FIELD(0x18, 1),
        'cal_datasize': XINFO_FIELD(0x19, 4),
        'module_condition': XINFO_FIELD(0x1d, 1),
        'reserved': XINFO_FIELD(0x1e, 14),
        'checksum': XINFO_FIELD(0x2c, 20),
        'macaddress': XINFO_FIELD(0x40, 6),
        'macaddress_checksum': XINFO_FIELD(0x46, 1),
        'checksum_content': XINFO_FIELD((0x00), 0x2c),  # This is really a block, not a field.
    },
    5: {
        'format': XINFO_FIELD(0x00, 1),
        'capacity': XINFO_FIELD(0x01, 2),
        'sn': XINFO_FIELD(0x03, 18),
        'ers': XINFO_FIELD(0x15, 1),
        'config': XINFO_FIELD(0x16, 3),
        'num_cals': XINFO_FIELD(0x19, 1),
        'cal_datasize': XINFO_FIELD(0x1a, 4),
        'module_condition': XINFO_FIELD(0x1e, 1),
        'reserved': XINFO_FIELD(0x1f, 13),
        'checksum': XINFO_FIELD(0x2c, 20),
        'macaddress': XINFO_FIELD(0x40, 6),
        'macaddress_checksum': XINFO_FIELD(0x46, 1),
        'checksum_content': XINFO_FIELD((0x00), 0x2c),  # This is really a block, not a field.
    },
}


class Xavier(MIXComponent):
    '''
    xavier represents the xavier board, including both the zynq soc
    and the linux environment. However, it's important xaiver itself does
    not rely on the driver pakcage. It should get its zynq object from
    its client
    '''

    rpc_public_api = ["get_system_time",
                      "set_system_time",
                      "read_serial_number",
                      "read_protected_blob",
                      "get_mac_address"]

    def __init__(self, zynq, os_helper):
        self.logger = create_null_logger()
        self.zynq = zynq
        self.os_helper = os_helper
        self._xinfo = None

    def set_ip(self, ip_addr):
        self.os_helper.ip = ip_addr

    def get_ip(self):
        return self.os_helper.ip

    def set_system_time(self, timestamp):
        '''
        Set the system time based on given timestamp.

        Args:
            timestamp: float/int, should be seconds from 1970/1/1.

        Returns:
            Current system time after it has been updated.
        '''
        self.os_helper.time = timestamp
        return self.os_helper.time

    def get_system_time(self):
        '''
        Return the system time in seconds since the epoch as a floating point number.
        '''
        return self.os_helper.time

    def _mtd_for_offset(self, offset):
        '''
        Find the mtd device name that host the given absolute flash offset.
        '''
        mtds = glob('/sys/class/mtd/mtd?')
        for mtd in mtds:
            with open(f'{mtd}/offset') as f:
                mtd_offset  = int(f.read())
            with open(f'{mtd}/size') as f:
                mtd_size = int(f.read())
            if offset >= mtd_offset and offset < (mtd_offset + mtd_size):
                return mtd.split("/")[-1]

    def read_nvmem(self, addr, count):

        # Morocco Region size, including reserve, is 4KB.  Relative address must be 0-0xFFF.
        assert addr >= 0 and addr <= 0xFFF, "Address (addr) out of range"
        assert addr + count <= 0x0FFF, "Address (count) out of range"

        # Morocco Region absolute flash address at 0xE0_0000, rdar://91383632
        mtd = self._mtd_for_offset(0xe00000)

        dev = f'/dev/{mtd}'
        with open(dev, 'rb') as mtd:
            mtd.seek(addr, 0)
            data = mtd.read(count)
        return bytearray(data)

    def verify_xinfo(self):
        if self._xinfo is None:
            raise RuntimeError("Xavier info was not initialized")

        if len(self._xinfo) != 256:
            raise SystemError("Xavier info block lenght is incorrect ({})". format(len(self._xinfo)))

        format = self._xinfo[0]
        if format not in XINFO_TABLE.keys():
            raise SystemError("Xavier info format unknown ({})".format(format))

        checksum_nvm = self._xinfo[XINFO_TABLE[format]['checksum'].slice]
        
        checksum_content = self._xinfo[ XINFO_TABLE[format]['checksum_content'].slice ]
        checksum_cal = sha1(checksum_content).digest()

        if checksum_nvm != checksum_cal:
            raise SystemError("Invalid checksum.  exp({}) cal({})".format(checksum_nvm, checksum_cal))

        return None

    def read_serial_number(self) -> str:
        '''
        Read and return the Xavier's serial number.
        '''

        self.read_protected_blob()

        format = self._xinfo[0]

        if format in XINFO_TABLE.keys():
            start_offset = XINFO_TABLE[format]['sn'].offset
            end_offset = XINFO_TABLE[format]['sn'].offset + XINFO_TABLE[format]['sn'].length
            return self._xinfo[start_offset:end_offset].decode()
        else:
            raise SystemError("Table version {} is not known".format(format))

    def read_protected_blob(self) -> list:
        '''
        Read and return the Xavier's protected blob.

        The protected blob's checksum is verified.  If invalid, an exception is raised.
        '''

        if self._xinfo is None:
            self._xinfo = self.read_nvmem(0, 256)

        self.verify_xinfo()

        return list(self._xinfo)

    def get_mac_address(self) -> str:
        '''
        Read and return the Xavier's ethernet mac address.
        '''
        return self.os_helper.mac_address
