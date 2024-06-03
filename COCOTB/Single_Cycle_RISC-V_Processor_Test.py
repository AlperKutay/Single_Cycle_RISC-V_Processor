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
        self.memory = ByteAddressableMemory(1024)

        self.clock_cycle_count = 0        
          
    #Calls user populated log functions    
    def log_dut(self):
        Log_Datapath(self.dut,self.logger)
        Log_Controller(self.dut,self.logger) 

    #Compares and lgos the PC and register file of Python module and HDL design
    def compare_result(self):
        self.logger.debug("************* Performance Model / DUT Data  **************")
        self.logger.debug("PC:%d \t PC:%d",self.PC,self.dut_PC.value.integer)
        for i in range(32):
            if(self.Register_File[i] < 0):
                self.logger.debug("Register%d: %d \t %d",i,self.Register_File[i]+(2**32), self.dut_regfile.Reg_Out[i].value.integer)
            else:
                self.logger.debug("Register%d: %d \t %d",i,self.Register_File[i], self.dut_regfile.Reg_Out[i].value.integer)
        #self.logger.debug("Register%d: %d \t %d",15,self.Register_File[15], self.dut_regfile.Reg_15.value.integer)
        assert self.PC == self.dut_PC.value
        for i in range(32):
           assert self.Register_File[i] == self.dut_regfile.Reg_Out[i].value
        #assert self.Register_File[15] == self.dut_regfile.Reg_15.value
        
    #A model of the verilog code to confirm operation, data is In_data
    def performance_model (self):
        self.logger.debug("**************** Clock cycle: %d **********************",self.clock_cycle_count)
        self.clock_cycle_count = self.clock_cycle_count+1
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
                if (inst_fields.Funct7 == "0000000"):
                    match inst_fields.Funct3:
                        case "000":#ADD
                            datap_result = R1 + R2
                            self.Register_File[inst_fields.Rd] = datap_result
                        case "001":#SLL
                            datap_result = shift_helper(R1,R2,0)
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
                            datap_result = shift_helper(R1,R2,1)
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
                        datap_result = shift_helper(R1,R2,1)
                        self.Register_File[inst_fields.Rd] = datap_result & 0xFFFFFFFF
                        
            elif(inst_fields.Op == "0010011"):
                R1 = self.Register_File[inst_fields.Rs1]
                IMM = inst_fields.Imm
                #match inst_fields.Funct3: 
                
                if(inst_fields.Funct3 == "000"):#ADDI
                    datap_result = R1 + IMM
                    print(f"R1 : {R1} and  IMM: {IMM}")
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
                
                
            #Memory Operations case        
            elif(inst_fields.Op == 1):
                if(inst_fields.L==1):
                    self.Register_File[inst_fields.Rd]= int.from_bytes(self.memory.read(self.Register_File[inst_fields.Rn] +inst_fields.imm12))
                else:
                    self.memory.write(self.Register_File[inst_fields.Rn] + inst_fields.imm12,self.Register_File[inst_fields.Rd])
            #Branch case
            elif(inst_fields.Op == 2):
                if (inst_fields.L_branch):
                    self.Register_File[14]=self.PC
                #Only +4 since we already increment 4 at the start
                self.PC = self.PC + 4 + (inst_fields.imm24*4)
            else:
                self.logger.error("Invalid operation type of 3!!")
                assert False
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
        while(int(self.Instruction_list[int((self.PC)/4)].replace(" ", ""),16)!=0):
            self.performance_model()
            #Log datapath and controller before clock edge, this calls user filled functions
            self.log_dut()
            await RisingEdge(self.dut.clk)
            await FallingEdge(self.dut.clk)
            self.compare_result()
                
                   
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