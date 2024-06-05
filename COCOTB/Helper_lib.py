def read_file_to_list(filename):
    """
    Reads a text file and returns a list where each element is a line in the file.

    :param filename: The name of the file to read.
    :return: A list of strings, where each string is a line from the file.
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        # Stripping newline characters from each line
        lines = [line.strip() for line in lines]
    return lines

class Inst_Types:
    # Define your constant values as class attributes for operation types
    R_Type = 0
    I_Type = 1
    S_Type = 2
    B_Type = 3
    U_Type = 4
    J_Type = 5
    
class Instruction:
    """
    Parses a 32-bit ARM instruction in hexadecimal format.

    :param instruction: A string representing the 32-bit instruction in hex format.
    :return: This class with the fields .
    """
    def __init__(self, instruction):
        # Convert the hex instruction to a 32-bit binary string
        self.binary_instr = format(int(instruction, 16), '032b')
        #Since python indexing is reversed to extract fields (31-index) for msb and (32-index) for lsb
        #For single bits do (31-index)
        self.Op = self.binary_instr[(31-6):(32-0)]
        self.Rd = int(self.binary_instr[(31-11):(32-7)], 2)
        self.Funct3 = self.binary_instr[(31-14):(32-12)]
        self.Funct7 = self.binary_instr[(31-31):(32-25)]
        self.Rs1 = int(self.binary_instr[(31-19):(32-15)], 2)
        self.Rs2 = int(self.binary_instr[(31-24):(32-20)], 2)   
        if(self.Op =="0010011" or self.Op =="0000011"):
            self.Imm = int(self.binary_instr[(31-31):(32-20)], 2)
        elif(self.Op =="0100011"):
            self.Imm = int((self.binary_instr[(31-31):(32-25)]),2) * 32 
            self.Imm = self.Imm + int((self.binary_instr[(31-11):(32-7)]),2)
        elif(self.Op == "1100011"):
            Imm12   = (int(self.binary_instr[0], 2) << 12) & 0xFFFFFFFF#(31-31):(32-31)
            Imm10_5 = (int(self.binary_instr[(31-30):(32-25)], 2) << 5)& 0xFFFFFFFF
            Imm4_1  = (int(self.binary_instr[(31-11):(32-8)], 2) << 1)& 0xFFFFFFFF
            Imm11    = (int(self.binary_instr[24], 2) << 11) & 0xFFFFFFFF#(31-7):(32-7)
            if Imm12:
                self.Imm =  (Imm12 | Imm11 | Imm10_5 | Imm4_1) | 0xFFFFE000
                self.Imm = self.Imm - (1 << 32)
            else:
                self.Imm =  (Imm12 | Imm11 | Imm10_5 | Imm4_1) & 0xFFFFFFFF
            #1 1 00111110 0110
            #1111111001000
            
        elif(self.Op=="0010111"):
            self.Imm   = int(self.binary_instr[(31-31):(32-12)], 2)
        elif(self.Op=="0110111"):
            self.Imm = int(self.binary_instr[(31-31):(32-12)], 2)
        elif(self.Op == "1101111"):
            Imm20   = (int(self.binary_instr[0], 2) << 20) & 0xFFFFFFFF#(31-31):(32-31)
            Imm10_1 = (int(self.binary_instr[(31-30):(32-21)], 2) << 1)& 0xFFFFFFFF
            Imm19_12 = (int(self.binary_instr[(31-19):(32-12)], 2) << 12)& 0xFFFFFFFF
            Imm11    = (int(self.binary_instr[31-20], 2) << 11) & 0xFFFFFFFF#(31-7):(32-7)
            if Imm20:#0001 0000 0000 0000 1110
                self.Imm =  (Imm20 | Imm10_1 | Imm19_12 | Imm11) | 0xFFE00000
                self.Imm = self.Imm - (1 << 32)
            else:
                self.Imm =  (Imm20 | Imm10_1 | Imm19_12 | Imm11) & 0xFFFFFFFF
        elif(self.Op == "1100111"):
            self.Imm = int(self.binary_instr[(31-31):(32-20)], 2)
            
    def log(self,logger):
        logger.debug("****** Current Instruction *********")
        logger.debug("Binary string:%s", self.binary_instr)
        logger.debug("Op:%s ",self.Op)
        if(self.Op == "0110011"):
            logger.debug("R-Type Instruction")
            self.Type = Inst_Types.R_Type
            if (self.Funct7 == "0000000"):
                if(self.Funct3 == "000"):
                    logger.debug("******ADD****** Instruction")
                elif(self.Funct3 == "001"):
                    logger.debug("******SLL****** Instruction")
                elif(self.Funct3 == "010"):
                    logger.debug("******SLT****** Instruction")
                elif(self.Funct3 == "011"):
                    logger.debug("******SLTU****** Instruction")
                elif(self.Funct3 == "100"):
                    logger.debug("******XOR****** Instruction")
                elif(self.Funct3 == "101"):
                    logger.debug("******SRL****** Instruction")
                elif(self.Funct3 == "110"):
                    logger.debug("******OR****** Instruction")
                elif(self.Funct3 == "111"):
                    logger.debug("******AND****** Instruction")
            elif(self.Funct7 == "0100000"):
                if(self.Funct3 == "000"):
                    logger.debug("******SUB****** Instruction")
                elif(self.Funct3 == "101"):
                    logger.debug("******SRA****** Instruction")
            else:
                logger.debug("It is not True Instruction")
            logger.debug("Funct3:%s ",self.Funct3)
            logger.debug("Funct7:%s ",self.Funct7)
            logger.debug("Rd:%d \t Rs1:%d \t Rs2:%d",self.Rd,self.Rs1,self.Rs2)
            
        elif(self.Op == "0010011"):
            logger.debug("I-Type Instruction")
            if(self.Funct3 == "000"):
                logger.debug("ADDI Instruction")
            elif(self.Funct3 == "001"):
                logger.debug("SLLI Instruction")
                self.Imm = int(self.binary_instr[(31-24):(32-20)],2)
                if(self.Funct7 != "0000000"):
                    logger.debug("SRLI Instruction")
                    exit()
            elif(self.Funct3 == "100"):
                logger.debug("XORI Instruction")
            elif(self.Funct3 == "101"):
                self.Imm = int(self.binary_instr[(31-24):(32-20)],2)
                if(self.Funct7 == "0000000"):
                    logger.debug("SRLI Instruction")
                elif(self.Funct7 == "0100000"):
                    logger.debug("SRAI Instruction")
                else:
                    exit()
            elif(self.Funct3 == "110"):
                logger.debug("ORI Instruction")
            elif(self.Funct3 == "111"):
                logger.debug("ANDI Instruction")
            logger.debug("Funct3:%s ",self.Funct3)
            logger.debug("Rs1:%d \t Rd:%d ",self.Rs1,self.Rd)
            logger.debug("Imm:%s",self.Imm)
            
        elif(self.Op == "0000011"):
            logger.debug("I-Type Instruction Load and Jump")
            if(self.Funct3 == "000"):
                logger.debug("LB Instruction")
            elif(self.Funct3 == "001"):
                logger.debug("LH Instruction")
            elif(self.Funct3 == "010"):
                logger.debug("LW Instruction")
            elif(self.Funct3 == "100"):
                logger.debug("LBU Instruction")
            elif(self.Funct3 == "101"):
                logger.debug("LHU Instruction")
            logger.debug("Funct3:%s ",self.Funct3)
            logger.debug("Rs1:%d \t Rd:%d ",self.Rs1,self.Rd)
            logger.debug("Imm:%d",self.Imm)

        elif(self.Op == "0100011"):
            logger.debug("S-Type Instruction")
            if(self.Funct3 == "000"):
                logger.debug("SB Instruction")
            elif(self.Funct3 == "001"):
                logger.debug("SH Instruction")
            elif(self.Funct3 == "010"):
                logger.debug("SW Instruction")
            logger.debug("Funct3:%s ",self.Funct3)
            logger.debug("Rs1:%d \t Rs2:%d ",self.Rs1,self.Rs2)
            logger.debug("Imm:%d",self.Imm)
            
        elif(self.Op == "1100011"):
            logger.debug("B-Type Instruction")
            if(self.Funct3 == "000"):
                logger.debug("BEQ Instruction")
            elif(self.Funct3 == "001"):
                logger.debug("BNE Instruction")
            elif(self.Funct3 == "101"):
                logger.debug("BGE Instruction")
            elif(self.Funct3 == "100"):
                logger.debug("BLT Instruction")
            elif(self.Funct3 == "110"):
                logger.debug("BLTU Instruction")
            elif(self.Funct3 == "111"):
                logger.debug("BGEU Instruction")
            logger.debug("Funct3:%s ",self.Funct3)
            logger.debug("Rs1:%d \t Rs2:%d ",self.Rs1,self.Rs2)
            logger.debug("Imm:%d",self.Imm)
            
            
        elif(self.Op == "0010111"):
            logger.debug("U-Type Instruction")
            logger.debug("AUIPC Instruction")
            logger.debug("Rd:%d ",self.Rd)
            logger.debug("Imm:%d",self.Imm)
        
        elif(self.Op == "0110111"):
            logger.debug("U-Type Instruction")
            logger.debug("LUI Instruction")
            logger.debug("Rd:%d ",self.Rd)
            logger.debug("Imm:%d",self.Imm)
        
            
        elif(self.Op == "1100111" or self.Op == "1101111"):
            logger.debug("J-Type Instruction")     
            if (self.Op == "1101111"):
                logger.debug("JAL Instruction")
            elif (self.Op == "1100111"):
                logger.debug("JALR Instruction")
                if self.Funct3 != "000":
                    logger.debug("Funct3 is not 000")
                    exit()
            logger.debug("Rd:%d R1:%d",self.Rd,self.Rs1)
            logger.debug("Imm:%d",self.Imm)

def rotate_right(value, shift, n_bits=32):
    """
    Rotate `value` to the right by `shift` bits.

    :param value: The integer value to rotate.
    :param shift: The number of bits to rotate by.
    :param n_bits: The bit-width of the integer (default 32 for standard integer).
    :return: The value after rotating to the right.
    """
    shift %= n_bits  # Ensure the shift is within the range of 0 to n_bits-1
    return (value >> shift) | (value << (n_bits - shift)) & ((1 << n_bits) - 1)

def shift_helper(value, shift,shift_type, n_bits=32):
    shift %= n_bits  # Ensure the shift is within the range of 0 to n_bits-1
    match shift_type:
        case 0:
            return (value  << shift)% 0x100000000
        case 1:
            return (value  >> shift) % 0x100000000
        case 2:
            if((value & 0x80000000)!=0):
                    filler = (0xFFFFFFFF >> (n_bits-shift))<<((n_bits-shift))
                    return ((value  >> shift)|filler) % 0x100000000
            else:
                return (value  >> shift) % 0x100000000
        case 3:
            return rotate_right(value,shift,n_bits)
        
def reverse_hex_string_endiannes(hex_string):  
    reversed_string = bytes.fromhex(hex_string)
    reversed_string = reversed_string[::-1]
    reversed_string = reversed_string.hex()        
    return  reversed_string
class ByteAddressableMemory:
    def __init__(self, size):
        self.size = size
        self.memory = bytearray(size)  # Initialize memory as a bytearray of the given size

    def read(self, address):
        if address < 0 or address + 4 > self.size:
            raise ValueError("Invalid memory address or length")
        return_val = bytes(self.memory[address : address + 4])
        return_val = return_val[::-1]
        return return_val

    def write(self, address, data):
        if address < 0 or address + 4> self.size:
            raise ValueError("Invalid memory address or data length")
        data_bytes = data.to_bytes(4, byteorder='little')
        self.memory[address : address + 4] = data_bytes        


def Log_Datapath(dut,logger):
    #Log whatever signal you want from the datapath, called before positive clock edge
    logger.debug("************ DUT DATAPATH Signals ***************")
    dut._log.info("reset:%s", hex(dut.my_datapath.reset.value.integer))
    dut._log.info("ALUSrc:%s", hex(dut.my_datapath.ALUSrc.value.integer))
    dut._log.info("MemWrite:%s", hex(dut.my_datapath.MemWrite.value.integer))
    dut._log.info("RegWrite:%s", hex(dut.my_datapath.RegWrite.value.integer))
    dut._log.info("PCSrc:%s", hex(dut.my_datapath.PCSrc.value.integer))
    dut._log.info("MemtoReg:%s", hex(dut.my_datapath.MemtoReg.value.integer))
    dut._log.info("RegSrc:%s", hex(dut.my_datapath.RegSrc.value.integer))
    dut._log.info("ImmSrc:%s", hex(dut.my_datapath.ImmSrc.value.integer))
    dut._log.info("ALUControl:%s", hex(dut.my_datapath.ALUControl.value.integer))
    dut._log.info("CO:%s", hex(dut.my_datapath.CO.value.integer))
    dut._log.info("OVF:%s", hex(dut.my_datapath.OVF.value.integer))
    dut._log.info("N:%s", hex(dut.my_datapath.N.value.integer))
    dut._log.info("Z:%s", hex(dut.my_datapath.Z.value.integer))
    dut._log.info("CarryIN:%s", hex(dut.my_datapath.CarryIN.value.integer))
    dut._log.info("ShiftControl:%s", hex(dut.my_datapath.ShiftControl.value.integer))
    dut._log.info("shamt:%s", hex(dut.my_datapath.shamt.value.integer))
    dut._log.info("PC:%s", hex(dut.my_datapath.PC.value.integer))
    dut._log.info("Instruction:%s", hex(dut.my_datapath.Instruction.value.integer))

def Log_Controller(dut,logger):
    #Log whatever signal you want from the controller, called before positive clock edge
    logger.debug("************ DUT Controller Signals ***************")
    dut._log.info("Op:%s", hex(dut.my_controller.Op.value.integer))
    dut._log.info("Funct:%s", hex(dut.my_controller.Funct.value.integer))
    dut._log.info("Rd:%s", hex(dut.my_controller.Rd.value.integer))
    dut._log.info("Src2:%s", hex(dut.my_controller.Src2.value.integer))
    dut._log.info("PCSrc:%s", hex(dut.my_controller.PCSrc.value.integer))
    dut._log.info("RegWrite:%s", hex(dut.my_controller.RegWrite.value.integer))
    dut._log.info("MemWrite:%s", hex(dut.my_controller.MemWrite.value.integer))
    dut._log.info("ALUSrc:%s", hex(dut.my_controller.ALUSrc.value.integer))
    dut._log.info("MemtoReg:%s", hex(dut.my_controller.MemtoReg.value.integer))
    dut._log.info("ALUControl:%s", hex(dut.my_controller.ALUControl.value.integer))
    dut._log.info("FlagWrite:%s", hex(dut.my_controller.FlagWrite.value.integer))
    dut._log.info("ImmSrc:%s", hex(dut.my_controller.ImmSrc.value.integer))
    dut._log.info("RegSrc:%s", hex(dut.my_controller.RegSrc.value.integer))
    dut._log.info("ShiftControl:%s", hex(dut.my_controller.ShiftControl.value.integer))
    dut._log.info("shamt:%s", hex(dut.my_controller.shamt.value.integer))
    dut._log.info("CondEx:%s", hex(dut.my_controller.CondEx.value.integer))