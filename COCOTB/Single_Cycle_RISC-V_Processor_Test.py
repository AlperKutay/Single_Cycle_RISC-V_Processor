# ==============================================================================
# Authors:              Doğu Erkan Arkadaş
#
# Cocotb Testbench:     For Single Cycle ARM Laboratory
#
# Description:
# ------------------------------------
# Test bench for the single cycle laboratory, used by the students to check their designs
#
# License:
# ==============================================================================
class Constants:
    # Define your constant values as class attributes for operation types
    ADD = 4
    SUB = 2
    AND = 0
    ORR = 12
    CMP = 10
    MOV = 13
    EQ = 0
    NE = 1
    AL = 14
    
class Inst_Types:
    # Define your constant values as class attributes for operation types
    R_Type = 0
    I_Type = 1
    S_Type = 2
    B_Type = 3
    U_Type = 4
    J_Type = 5


import logging
import cocotb
from Helper_lib import read_file_to_list,Instruction,rotate_right, shift_helper, ByteAddressableMemory,reverse_hex_string_endiannes
from Helper_Student import Log_Datapath,Log_Controller
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Edge, Timer
from cocotb.binary import BinaryValue



class TB:
    def __init__(self, Instruction_list,dut,dut_PC,dut_regfile):
        self.dut = dut
        self.dut_PC = dut_PC
        self.dut_regfile = dut_regfile
        self.Instruction_list = Instruction_list
        #Configure the logger
        self.logger = logging.getLogger("Performance Model")
        self.logger.setLevel(logging.DEBUG)
        #Initial values are all 0 as in a FPGA
        self.PC = 0
        self.Z_flag = 0
        self.Register_File =[]
        for i in range(32):
            self.Register_File.append(0)
        #Memory is a special class helper lib to simulate HDL counterpart    
        self.memory = ByteAddressableMemory(4096)

        self.clock_cycle_count = 0        
          
    #Calls user populated log functions    
    def log_dut(self):
        Log_Datapath(self.dut,self.logger)
        Log_Controller(self.dut,self.logger) 

    #Compares and lgos the PC and register file of Python module and HDL design
    def compare_result(self):
        self.logger.debug("************* Performance Model / DUT Data  **************")
        self.logger.debug("PC:%08x \t PC:%08x",self.PC,self.dut_PC.value.integer)
        self.Register_File[0] = 0
        for i in range(32):
            self.logger.debug("Register%d: %08x \t\t %08x",i,self.Register_File[i],self.dut_regfile.Reg_Out[i].value.integer )
            assert self.Register_File[i] == self.dut_regfile.Reg_Out[i].value.integer
        #self.logger.debug("Register%d: %d \t %d",15,self.Register_File[15], self.dut_regfile.Reg_15.value.integer)
        assert self.PC == self.dut_PC.value
         
        #assert self.Register_File[15] == self.dut_regfile.Reg_15.value
        
    #A model of the verilog code to confirm operation, data is In_data
    def performance_model (self):
        self.logger.debug("**************** Clock cycle: %d **********************",self.clock_cycle_count)
        self.clock_cycle_count = self.clock_cycle_count+1
        bit_length = 32
        #Read current instructions, extract and log the fields
        self.logger.debug("**************** Instruction No: %d **********************",int((self.PC)/4))
        current_instruction = self.Instruction_list[int((self.PC)/4)]
        current_instruction = current_instruction.replace(" ", "")
        #We need to reverse the order of bytes since little endian makes the string reversed in Python
        current_instruction = reverse_hex_string_endiannes(current_instruction)
        #Initial R15 value for operations
        #self.Register_File[15] = self.PC + 8  
        self.PC = self.PC + 4
        #Flag to check if the current instruction will be executed.
        execute_flag = True
        #Call Instruction calls to get each field from the instruction
        inst_fields = Instruction(current_instruction)
        inst_fields.log(self.logger)
        '''
        match inst_fields.Cond:
            case Constants.AL:
                execute_flag=True
            case Constants.EQ:
                if(self.Z_flag == 1):
                    execute_flag = True
            case Constants.NE:
                if(self.Z_flag == 0):
                    execute_flag = True
        '''
        if(execute_flag):
            #binary_instr is jsut for BX check             
            binary_instr = format(int(current_instruction, 16), '032b')
            #Weird BX condition
            """
            if(binary_instr[4:28]=="000100101111111111110001"):
                self.PC = self.Register_File[inst_fields.Rm]   """
            if(inst_fields.Op == "0110011"):
                #R-Type Instruction
                R1 = self.Register_File[inst_fields.Rs1]
                R2 = self.Register_File[inst_fields.Rs2]
                shamt = R2
                if (inst_fields.Funct7 == "0000000"):
                    match inst_fields.Funct3:
                        case "000":#ADD
                            datap_result = (R1 + R2) & 0xFFFFFFFF
                            self.Register_File[inst_fields.Rd] = datap_result
                        case "001":#SLL
                            datap_result = shift_helper(R1,shamt,0)
                            self.Register_File[inst_fields.Rd] = datap_result
                        case "010":#SLT
                            if(R1 < R2):
                                self.Register_File[inst_fields.Rd] = 1
                            else:
                                self.Register_File[inst_fields.Rd] = 0
                        case "011":#SLTU
                            R1 = R1 & 0xFFFFFFFF
                            R2 = R2 & 0xFFFFFFFF
                            if(R1 < R2):
                                self.Register_File[inst_fields.Rd] = 1
                            else:
                                self.Register_File[inst_fields.Rd] = 0
                        case "100":#XOR
                            datap_result = R1 ^ R2
                            self.Register_File[inst_fields.Rd] = datap_result
                        case "101":#SRL
                            datap_result = shift_helper(R1,shamt,1)
                            self.Register_File[inst_fields.Rd] = datap_result
                        case "110":#OR
                            datap_result = R1 | R2
                            self.Register_File[inst_fields.Rd] = datap_result
                        case "111":#AND
                            datap_result = R1 & R2
                            self.Register_File[inst_fields.Rd] = datap_result
                        case _:#Default
                            self.logger.error("Not supported data processing instruction!!")
                            assert False 
                elif(inst_fields.Funct7 == "0100000"):
                    if(inst_fields.Funct3 == "000"):#SUB
                        datap_result = R1 - R2
                        self.Register_File[inst_fields.Rd] = datap_result & 0xFFFFFFFF
                    elif(inst_fields.Funct3 == "101"):#SRA
                        if R1 & 0x80000000:
                            R1 = R1 - 0x100000000
                        datap_result = shift_helper(R1,shamt,1)
                        self.Register_File[inst_fields.Rd] = datap_result & 0xFFFFFFFF
                else:
                    self.logger.debug("Wrong Instruction in R-Type Instruction")
                        
            elif(inst_fields.Op == "0010011"):
                #I-Type Instruction
                R1 = self.Register_File[inst_fields.Rs1]
                IMM = inst_fields.Imm
                if(IMM & 0x800):
                    IMM = IMM | 0xFFFFF000
                if(inst_fields.Funct3 == "000"):#ADDI
                    datap_result = R1 + IMM
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "001"):#SLLI
                    datap_result = shift_helper(R1,IMM,0)
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "100") :#XORI
                    datap_result = R1 ^ IMM
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "101"):
                    if(inst_fields.Funct7 == "0000000"):#SLLI
                        datap_result = shift_helper(R1,IMM,1)
                        self.Register_File[inst_fields.Rd] = datap_result
                    elif(inst_fields.Funct7 == "0100000"):#SRAI
                        if R1 & 0x80000000:
                            R1 = R1 - 0x100000000
                        datap_result = shift_helper(R1,IMM,1)
                        self.Register_File[inst_fields.Rd] = datap_result & 0xFFFFFFFF
                elif(inst_fields.Funct3 == "110"):#ORI
                    datap_result = R1 | IMM
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "111"):#ANDI
                    datap_result = R1 & IMM
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "010"):#SLTI
                    if R1 & 0x80000000:
                        R1 = R1 - 0x100000000
                    if(R1 < IMM):
                        datap_result = 1
                    else:
                        datap_result = 0
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "011"):#SLTIU
                    R1 = R1 & 0xFFFFFFFF
                    IMM = IMM & 0xFFFFFFFF
                    if(R1 < IMM):
                        datap_result = 1
                    else:
                        datap_result = 0
                    self.Register_File[inst_fields.Rd] = datap_result
                else:
                    self.logger.debug("Wrong Instruction in I-Type Instruction")
            
            elif(inst_fields.Op == "0000011"):# I-Type Instruction Load and Jump 
                R1 = self.Register_File[inst_fields.Rs1]
                IMM = inst_fields.Imm   
                if(inst_fields.Funct3 == "000"):#LB
                    offset = R1 + IMM
                    datap_result = int.from_bytes(self.memory.read(offset), byteorder='big', signed=False) & 0xFF
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "001"):#LH
                    offset = R1 + IMM
                    first_half_byte = int.from_bytes(self.memory.read(offset), byteorder='big', signed=False) & 0xFF
                    second_half_byte = int.from_bytes(self.memory.read(offset+1), byteorder='big', signed=False) & 0xFF
                    datap_result = ((second_half_byte << 8) | first_half_byte) & 0xFFFFFFFF
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "010") :#LW
                    offset = R1 + IMM
                    first_half_byte = int.from_bytes(self.memory.read(offset), byteorder='big', signed=False) & 0xFF
                    second_half_byte = int.from_bytes(self.memory.read(offset+1), byteorder='big', signed=False) & 0xFF
                    third_half_byte = int.from_bytes(self.memory.read(offset+2), byteorder='big', signed=False) & 0xFF
                    fourth_half_byte = int.from_bytes(self.memory.read(offset+3), byteorder='big', signed=False) & 0xFF
                    datap_result = ((  fourth_half_byte << 24) | (  third_half_byte << 16) | (second_half_byte << 8) | first_half_byte) & 0xFFFFFFFF
                    self.Register_File[inst_fields.Rd] = datap_result
                elif(inst_fields.Funct3 == "100"):#LBU
                    R1 = R1 & 0xFFFFFFFF
                    IMM = IMM & 0xFFFFFFFF
                    offset = R1 + IMM
                    self.Register_File[inst_fields.Rd]= int.from_bytes(self.memory.read(offset), byteorder='big', signed=False) & 0xFF
                elif(inst_fields.Funct3 == "101"):#LHU
                    R1 = R1 & 0xFFFFFFFF
                    IMM = IMM & 0xFFFFFFFF
                    offset = R1 + IMM
                    first_half_byte = int.from_bytes(self.memory.read(offset), byteorder='big', signed=False) & 0xFF
                    print(first_half_byte)
                    second_half_byte = int.from_bytes(self.memory.read(offset+1), byteorder='big', signed=False) & 0xFF
                    datap_result = ((second_half_byte << 8) | first_half_byte) & 0xFFFFFFFF
                    self.Register_File[inst_fields.Rd] = datap_result
                else:
                    self.logger.debug("Wrong Instruction in I-Type Instruction Load and Jump ")
                    
            elif(inst_fields.Op == "0100011"):#S-Type Instruction
                R1 = self.Register_File[inst_fields.Rs1]
                R2 = self.Register_File[inst_fields.Rs2]
                IMM = inst_fields.Imm
                if(inst_fields.Funct3 == "000"):#SB
                    offset = R1 + IMM
                    datap_result = R2 & 0xFF
                    self.memory.write(offset,datap_result)
                elif(inst_fields.Funct3 == "001"):#SH
                    offset = R1 + IMM
                    datap_result_1 = R2 & 0xFF
                    datap_result_2 = (R2 >> 8) & 0xFF
                    self.memory.write(offset,datap_result_1)
                    self.memory.write(offset+1,datap_result_2)
                elif(inst_fields.Funct3 == "010"):#SW
                    offset = R1 + IMM
                    datap_result_1 = R2 & 0xFF
                    datap_result_2 = (R2 >> 8) & 0xFF
                    datap_result_3 = (R2 >> 16) & 0xFF
                    datap_result_4 = (R2 >> 24) & 0xFF
                    self.memory.write(offset,datap_result_1)
                    self.memory.write(offset+1,datap_result_2)
                    self.memory.write(offset+2,datap_result_3)
                    self.memory.write(offset+3,datap_result_4)
                else:
                    self.logger.debug("Wrong Instruction in S-Type Instruction ")   


            elif(inst_fields.Op == "1100011"):#B-Type Instruction
                R1_Unsigned = self.Register_File[inst_fields.Rs1]
                R2_Unsigned = self.Register_File[inst_fields.Rs2]
                if R1_Unsigned & (1 << (bit_length - 1)):
                    R1 = R1_Unsigned - (1 << bit_length)
                else:
                    R1 = R1_Unsigned        
                    
                if R2_Unsigned & (1 << (bit_length - 1)):
                    R2 = R2_Unsigned - (1 << bit_length)
                else:
                    R2 = R2_Unsigned

                IMM = inst_fields.Imm 
                if(inst_fields.Funct3 == "000"):#BEQ
                    if(R1 == R2):
                        self.PC = self.PC + IMM - 4 
                        
                elif(inst_fields.Funct3 == "001"):#BNE
                    if(R1 != R2):
                        self.PC = self.PC + IMM - 4 
                        
                elif(inst_fields.Funct3 == "101"):#BGE
                    if(R1 >= R2):
                        self.PC = self.PC + IMM - 4 
                        
                elif(inst_fields.Funct3 == "100"):#BLT
                    if(R1 < R2):
                        self.PC = self.PC + IMM - 4 
                        
                elif(inst_fields.Funct3 == "110"):#BLTU
                    if(R1_Unsigned < R2_Unsigned):
                        self.PC = self.PC + IMM - 4 
                        
                elif(inst_fields.Funct3 == "111"):#BGEU
                    if(R1_Unsigned >= R2_Unsigned):
                        self.PC = self.PC + IMM - 4 
                else:
                    self.logger.debug("Wrong Instruction in B-Type Instruction ")   
                    
                    
            elif(inst_fields.Op == "0010111"):#U-Type AUIPC Instruction
                IMM = inst_fields.Imm
                self.Register_File[inst_fields.Rd] = self.PC + (IMM << 12) -4
            
            elif(inst_fields.Op == "0110111"):#U-Type LUI Instruction 
                IMM = inst_fields.Imm
                self.Register_File[inst_fields.Rd] = (IMM << 12)
            
            elif (inst_fields.Op == "1101111"):#J-Type JAL Instruction
                IMM = inst_fields.Imm
                self.Register_File[inst_fields.Rd] = self.PC
                self.PC = self.PC + (IMM) - 4
                
            elif (inst_fields.Op == "1100111"):#J-Type JALR Instruction
                IMM = inst_fields.Imm
                R1= self.Register_File[inst_fields.Rs1]
                self.Register_File[inst_fields.Rd] = self.PC
                self.PC = R1 + (IMM) 
                
            elif(inst_fields.Op == "0001011"):
                R1= self.Register_File[inst_fields.Rs1]
                student_id_alper = 2375467
                student_id_kemal = 2375491
                xorid = student_id_alper ^ student_id_kemal
                self.Register_File[inst_fields.Rd] = xorid ^ R1
        else:
            self.logger.debug("Current Instruction is not executed")

        #We change register file 15 (PC + 8) after increment and branches because we compare after the clock cycle
        #self.Register_File[15] = self.PC + 8
    async def run_test(self):
        self.performance_model()
        #Wait 1 us the very first time bc. initially all signals are "X"
        await Timer(1, units="us")
        self.log_dut()
        await RisingEdge(self.dut.clk)
        await FallingEdge(self.dut.clk)
        self.compare_result()
        try:
            while(int(self.Instruction_list[int((self.PC)/4)].replace(" ", ""),16)!=0):
                self.performance_model()
                #Log datapath and controller before clock edge, this calls user filled functions
                self.log_dut()
                await RisingEdge(self.dut.clk)
                await FallingEdge(self.dut.clk)
                self.compare_result()
                input()
        except IndexError:
            print("Code is done.")       
                   
@cocotb.test()
async def Single_cycle_test(dut):
    #Generate the clock
    await cocotb.start(Clock(dut.clk, 10, 'us').start(start_high=False))
    #Reset onces before continuing with the tests
    dut.reset.value=1
    await RisingEdge(dut.clk)
    dut.reset.value=0
    await FallingEdge(dut.clk)
    instruction_lines = read_file_to_list('Instructions.hex')
    #Give PC signal handle and Register File MODULE handle
    tb = TB(instruction_lines,dut, dut.PC, dut.dp.regFile)
    await tb.run_test()