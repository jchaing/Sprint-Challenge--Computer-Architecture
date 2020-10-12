"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # Memory:
        self.ram = [0] * 256

        # Register:
        self.reg = [0] * 8

        # SP initial
        self.reg[7] = 0xF4

        # Pointer:
        self.pc = 0

        # Running
        self.running = True

    def ram_read(self, address):
        """Returns value from memory address"""

        print(self.ram[address])

    def ram_write(self, value, address):
        """Writes value to memory address"""

        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        # address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        if (len(sys.argv)) != 2:
            print("remember to pass the second file name")
            print("usage: python3 cpu.py <second_file_name.py>")
            sys.exit()

        address = 0

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    possible_number = line[: line.find("#")]
                    if possible_number == "":
                        continue

                    instruction = int(possible_number, 2)
                    self.ram[address] = instruction
                    address += 1

        except FileNotFoundError:
            print(f"Error from {sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit()

    # load()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def run(self):
        """Run the CPU."""

        while self.running:
            IR = self.ram[self.pc]

            # number_to_increase_pc = 1
            num_args = IR >> 6

            # LDI instruction
            if IR == 0b10000010:
                reg_idx = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]

                self.reg[reg_idx] = value

            # MULT instruction
            elif IR == 0b10100010:
                reg_idx_1 = self.ram[self.pc + 1]
                reg_idx_2 = self.ram[self.pc + 2]

                self.reg[reg_idx_1] = self.reg[reg_idx_1] * self.reg[reg_idx_2]

            elif IR == 0b10100000:
                self.alu("ADD", self.ram[self.pc + 1], self.ram[self.pc + 2])

            # PRN instruction
            elif IR == 0b01000111:
                reg_idx = self.ram[self.pc + 1]
                value = self.reg[reg_idx]
                print(value)

            # PUSH instruction
            elif IR == 0b01000101:
                # 1. Decrement the 'SP'
                # where is the 'SP'
                self.reg[7] -= 1
                print(self.reg)
                # 2. Copy the value in the given register to the address pointed to by 'SP
                # get the value from the given register
                # how to find which register to look at
                reg_idx = self.ram[self.pc + 1]
                value = self.reg[reg_idx]

                # How to copy the value to the correct address
                SP = self.reg[7]
                self.ram[SP] = value

            # POP instruction
            elif IR == 0b01000110:
                # 1. Copy the value from the address pointed to by 'SP'
                # we need the SP Address
                SP = self.reg[7]

                # we need the value from that address
                value = self.ram[SP]

                # we need the register address
                reg_idx = self.ram[self.pc + 1]

                # then put the value in the register
                self.reg[reg_idx] = value

                # 2. Increment 'SP"
                self.reg[7] += 1

            # CALL instruction
            elif IR == 0b01010000:
                return_address = self.pc + 2

                self.reg[7] -= 1

                SP = self.reg[7]
                self.ram[SP] = return_address

                reg_idx = self.ram[self.pc + 1]

                subroutine_address = self.reg[reg_idx]

                self.pc = subroutine_address

            # RET instruction
            elif IR == 0b00010001:
                SP = self.reg[7]
                return_address = self.ram[SP]

                self.pc = return_address

                self.reg[7] += 1

            # HLT instruction
            elif IR == 0b00000001:
                self.running = False

            else:
                print("Unknown Command!")
                self.running = False

            sets_pc_directly = ((IR >> 4) & 0b0001) == 1
            if not sets_pc_directly:
                self.pc += 1 + num_args

        # print(self.reg)
        # print(self.ram)
