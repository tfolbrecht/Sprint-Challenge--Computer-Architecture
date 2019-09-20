"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.registers = [0] * 8
        self.running = False
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 7
        self.flag = 0b00000000

    def ram_read(self, MAR):
        """Read the RAM. MAR = memory address register"""
        try:
            return self.ram[MAR]
        except IndexError:
            print("index out of range for RAM read")

    def ram_write(self, MDR, MAR):
        """write to the RAM. MDR = Memory Data Register"""
        try:
            self.ram[MAR] = MDR
        except IndexError:
            print("index out of range for RAM write")

    def increment_pc(self, op_code):
        add_to_pc = (op_code >> 6) + 1
        self.pc += add_to_pc

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    # split before and after any comment symbols
                    comment_split = line.split('#')
                    # convert the pre-comment portion to a value
                    number = comment_split[0].strip()  # trim whitespace

                    if number == "":
                        continue  # ignore blank lines

                    val = int(number, 2)
                    self.ram_write(val, address)

                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.registers[reg_a] = self.registers[reg_a] * \
                self.registers[reg_b]
        elif op == "CMP":
            if self.registers[reg_a] == self.registers[reg_b]:
                self.flag = 0b00000001
            elif self.registers[reg_a] > self.registers[reg_b]:
                self.flag = 0b00000010
            else:
                self.flag = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        # self.trace()
        while self.running:
            op_code = self.ram_read(self.pc)
            if op_code == 0b00000001:  # HLT
                self.running = False
                sys.exit(0)  # 0 exit = success

            elif op_code == 0b10100000:  # ADD
                address_a = self.ram_read(self.pc + 1)
                address_b = self.ram_read(self.pc + 2)
                self.alu('ADD', address_a, address_b)
                self.increment_pc(op_code)

            elif op_code == 0b10000010:  # LDI
                address = self.ram_read(self.pc + 1)
                data = self.ram_read(self.pc + 2)
                self.registers[address] = data
                self.increment_pc(op_code)

            elif op_code == 0b01000111:  # PRN
                address_a = self.ram_read(self.pc + 1)
                print(self.registers[address_a])
                self.increment_pc(op_code)

            elif op_code == 0b10100010:  # MUL
                address_a = self.ram_read(self.pc + 1)
                address_b = self.ram_read(self.pc + 2)
                self.alu('MUL', address_a, address_b)
                self.increment_pc(op_code)

            elif op_code == 0b01000101:  # PUSH
                register_address = self.ram_read(self.pc + 1)
                val = self.registers[register_address]
                self.registers[self.sp] -= 1  # decrement the stack pointer
                self.ram[self.registers[self.sp]] = val
                self.increment_pc(op_code)

            elif op_code == 0b01000110:  # POP
                register_address = self.ram_read(self.pc + 1)
                val = self.ram[self.registers[self.sp]]
                self.registers[register_address] = val
                self.registers[self.sp] += 1
                self.increment_pc(op_code)

            elif op_code == 0b01010000:  # CALL
                self.registers[self.sp] -= 1
                self.ram[self.registers[self.sp]] = self.pc + 2
                address_of_subroutine = self.ram[self.pc + 1]
                self.pc = self.registers[address_of_subroutine]

            elif op_code == 0b00010001:  # RET
                self.pc = self.ram[self.registers[self.sp]]
                self.registers[self.sp] += 1

            else:
                print(bin(op_code))
                sys.exit("I don't know an operation in this file")
