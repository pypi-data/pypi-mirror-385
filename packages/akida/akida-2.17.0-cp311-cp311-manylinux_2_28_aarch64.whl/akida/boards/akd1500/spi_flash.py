import akida
import struct


def _command(command, address=None):
    if address is not None:
        return bytearray([command,  address >> 16 & 0xff, address >> 8 & 0xff, address & 0xff])
    else:
        return bytearray([command])


class Flash:
    """
    Class used to manage AKD1500 spi flash (Micron MT25QU128ABB, but should work with
    other capacities as well). It uses FTDI via SPI Slave to Master to interact with flash, and
    needs access to PCIe device (char file '/dev/akd1500_#') to configure SPI Slave to Master.

    FTDI is connected to AKD1500 SPI Slave,
    """
    # Registers operations
    CMD_READ_STATUS_REG = 0x5
    CMD_READ_FLAG_STATUS_REG = 0x70
    CMD_CLEAR_FLAG_STATUS_REG = 0x50

    # Write operations
    CMD_WRITE_ENABLE = 0x6
    CMD_PROGRAM_PAGE = 0x02

    # Erase operations
    CMD_ERASE_BULK = 0xC7
    CMD_ERASE_64K = 0xD8
    CMD_ERASE_32K = 0x52
    CMD_ERASE_4K = 0x20

    # Read operations
    CMD_READ = 0x03

    # Device operations
    CMD_READ_ID = 0x9F

    # Define block sizes
    BLOCK_SIZE_64K = 64 * 1024
    BLOCK_SIZE_32K = 32 * 1024
    BLOCK_SIZE_4K = 4 * 1024

    def _read_flash_size_MB(self):
        # read device id to get flash size
        device_id = self._spi.exchange(_command(self.CMD_READ_ID), 3)

        raw_size = device_id[2]  # size is on the 3rd byte
        if raw_size == 0x17:
            return 8
        if raw_size == 0x18:
            return 16
        if raw_size == 0x19:
            return 32
        if raw_size == 0x20:
            return 64
        if raw_size == 0x21:
            return 128
        if raw_size == 0x22:
            return 256
        raise RuntimeError(f"Unexpected flash size value: 0x{raw_size:02x}")

    def _clear_flag_status(self):
        self._spi.exchange(_command(self.CMD_CLEAR_FLAG_STATUS_REG))

    def _check_address(self, address):
        if address >= self._max_addr:
            raise ValueError(f"Address 0x{address:08x} is out of range [0; 0x{self._max_addr:08x}[")

    def _check_size(self, address, byte_size):
        if address + byte_size >= self._max_addr:
            raise ValueError(
                f"Size {byte_size} is too big (max allowed={self._max_addr - address - 1})")

    def _enable_spi_slave_to_master(self, enable):
        with open(self._pcie_device, 'w+b') as pcie:
            pcie.seek(0xfce0_0018)
            cfg_reg = struct.unpack("I", pcie.read(4))[0]
            if enable:
                cfg_reg |= 0x0001_0000
            else:
                cfg_reg &= 0xfffe_ffff
            pcie.seek(0xfce0_0018)
            pcie.write(struct.pack("I", cfg_reg))

    def __init__(self, ftdi_device='ftdi://ftdi:ft2232h/2', pcie_device='/dev/akd1500_0'):
        try:
            import pyftdi.spi
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f"class '{__class__.__name__}' requires pyftdi dependency, please install it.")

        # init FTDI Spi controller
        spi_controller = pyftdi.spi.SpiController(cs_count=2)
        spi_controller.configure(ftdi_device)

        # Spi flash is on 2nd port
        slave = spi_controller.get_port(cs=1, freq=10_000_000)

        self._spi = slave

        # Force akida drivers instantiation, that will initialize spi master controller for AKD1500
        _ = akida.devices()

        # Enable spi slave to master
        self._pcie_device = pcie_device
        self._enable_spi_slave_to_master(True)

        self.flash_size = self._read_flash_size_MB()
        self._max_addr = self.flash_size * 1024 * 1024

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # disable spi slave to master
        self._enable_spi_slave_to_master(False)

    def _wait_for_write_completion(self):
        while True:
            status = self._spi.exchange(_command(self.CMD_READ_STATUS_REG), 1)[0]
            if (status & 1) == 0:  # bit 0 is write in progress bit. 1 = busy, 0 = ready
                break

    def erase(self, address, erase_cmd=CMD_ERASE_4K):
        # Check command is valid
        if erase_cmd not in [self.CMD_ERASE_4K, self.CMD_ERASE_32K, self.CMD_ERASE_64K]:
            raise ValueError("Invalid erase value")

        # Check address is valid
        self._check_address(address)

        # Clear flag status before performing operation
        self._clear_flag_status()

        # Erase needs to enable write 1st
        self._spi.exchange(_command(self.CMD_WRITE_ENABLE))

        # Send erase command
        self._spi.exchange(_command(erase_cmd, address))

        # Wait for completion
        self._wait_for_write_completion()

        # Check for errors
        flag = self._spi.exchange(_command(self.CMD_READ_FLAG_STATUS_REG), 1)[0]
        if flag & 0x20:
            raise RuntimeError(f"Erase operation at address 0x{address:06x} failed")

    def write(self, address, data):
        # Check address & size
        self._check_address(address)
        self._check_size(address, len(data))

        # Clear flag status before performing operation
        self._clear_flag_status()

        # Program command can take up to 256 bytes, so we split data in 256 bytes chunks
        CHUNK_SIZE = 256
        for i in range(0, len(data), CHUNK_SIZE):
            # Enable write
            self._spi.exchange(_command(self.CMD_WRITE_ENABLE))

            # Write chunk
            self._spi.exchange(
                _command(
                    self.CMD_PROGRAM_PAGE, address) + data[i:i+CHUNK_SIZE])
            # Wait for write completion
            self._wait_for_write_completion()

            # Check for errors
            flag = self._spi.exchange(_command(self.CMD_READ_FLAG_STATUS_REG), 1)[0]
            if flag & 0x10:
                raise RuntimeError(f"Write operation at address {address:08x} failed")

            address += CHUNK_SIZE

    def read(self, address, byte_size):
        # Check address and size
        self._check_address(address)
        self._check_size(address, byte_size)
        # Clear flag status before performing operation
        self._clear_flag_status()

        return self._spi.exchange(_command(self.CMD_READ, address), byte_size)


if __name__ == '__main__':
    import argparse

    def _parse_address(address):
        return int(address, 0)  # auto guess base so it can handle values like "0xAA"

    parser = argparse.ArgumentParser(description="Manage AKD1500 spi flash")
    action_parser = parser.add_subparsers(dest="action",
                                          required=True,
                                          help="Perform action on AKD1500 spi flash")
    erase_parser = action_parser.add_parser("erase")
    erase_parser.add_argument("-a", "--address",
                              type=int,
                              default=0,
                              help="Address of data to erase")
    erase_parser.add_argument("-b", "--block-size",
                              type=str,
                              default="64K",
                              choices=["4K", "32K", "64K"],
                              help="Block size to erase")
    erase_parser.add_argument("-c", "--count",
                              type=_parse_address,
                              required=True,
                              help="Number of blocks to erase")

    write_parser = action_parser.add_parser("write")
    write_parser.add_argument("-f", "--file",
                              type=argparse.FileType('rb'),
                              required=True,
                              help="The file that will be written to flash")
    write_parser.add_argument("-a", "--address",
                              type=_parse_address,
                              default=0,
                              help="Address where data will be written")

    read_parser = action_parser.add_parser("read")
    read_parser.add_argument("-f", "--file",
                             type=argparse.FileType('wb'),
                             default=None,
                             help="The file to write the read data")
    read_parser.add_argument("-a", "--address",
                             type=_parse_address,
                             default=0,
                             help="Address to read from")
    read_parser.add_argument("-c", "--count",
                             type=int,
                             required=True,
                             help="The number of bytes to read from flash")
    args = parser.parse_args()

    with Flash() as flash:
        if args.action == "erase":
            if args.block_size == "4K":
                erase_cmd = Flash.CMD_ERASE_4K
                increment = 4*1024
            elif args.block_size == "32K":
                erase_cmd = Flash.CMD_ERASE_32K
                increment = 32*1024
            elif args.block_size == "64K":
                erase_cmd = Flash.CMD_ERASE_64K
                increment = 64*1024
            else:
                raise ValueError("Unexpected block size")

            address = args.address
            for i in range(args.count):
                flash.erase(address, erase_cmd)
                address += increment
            print(f"Successfuly erased {args.count * increment} bytes"
                  f" ({args.count} blocks of {args.block_size})")

        elif args.action == "write":
            flash.write(args.address, args.file.read())
            print(f"Successfuly wrote '{args.file.name}' to flash at address 0x{args.address:08x}")

        elif args.action == "read":
            data = flash.read(args.address, args.count)
            if args.file is None:
                for i in data:
                    print(f"{i:02x}", end='')
                print("\n")
            else:
                args.file.write(data)
                print(f"Successfuly read {args.count} bytes from flash to '{args.file.name}'")
