module Datapath
	(
	input clk,reset,
	input PCSrc,ResultSrc,MemWrite,ALUSrc,RegWrite,SrcAControl,
	input [1:0]ImmSrc,
	input [3:0]ALUControl,
	input [4:0]shamt,
	input [1:0]shiftControl,
	input [4:0] Debug_Source_select,
	output [31:0] Debug_out,
	output [31:0] PC,
	output N,Z,CO,OVF
	);

	
//WIRES ON DATAPATH
wire [31:0]PCNext,PCPlus4;
wire [31:0]Instr;
wire [31:0]SrcA,SrcB,ImmExt;
wire [31:0]ALUResult,WriteData,PCTarget;
wire [31:0]ReadData, Result;
wire [31:0]RD1;
wire [31:0]shifter_output;

//MULTIPLEXERS
Mux_2to1#(.WIDTH(32)) pcmux 
	(
		.select(PCSrc),
		.input_0(PCPlus4),
		.input_1(PCTarget),
		.output_value(PCNext)
	);	

Mux_2to1#(.WIDTH(32)) srcaControl 
	(
		.select(SrcAControl),
		.input_0(RD1),
		.input_1(shifter_output),
		.output_value(SrcA)
	);	
	
Mux_2to1#(.WIDTH(32)) srcbControl 
	(
		.select(ALUSrc),
		.input_0(WriteData),
		.input_1(ImmExt),
		.output_value(SrcB)
	);	
	
Mux_2to1#(.WIDTH(32)) resultControl
	(
		.select(ResultSrc),
		.input_0(ALUResult),
		.input_1(ReadData),
		.output_value(Result)
	);	
	

//PC REGISTER
Register_reset#(.WIDTH(32)) regPC
	(
	.clk(clk), 
	.reset(reset), 
	.DATA(PCNext), 
	.OUT(PC)
	);

//PC PLUS 4
Adder#(.WIDTH(32)) pcp4
	(
		.DATA_A(PC), 
		.DATA_B(4), 
		.OUT(PCPlus4)
	);	

//PC TARGET
Adder#(.WIDTH(32)) pcTarget
	(
		.DATA_A(PC), 
		.DATA_B(ImmExt), 
		.OUT(PCTarget)
	);	
	
//INSTRUCTION MEMORY
Inst_Memory#(.BYTE_SIZE(4), .ADDR_WIDTH(32)) instMemory
	(
		.ADDR(PC),
		.RD(Instr)
	);

//REGISTER FILE
Register_file #(.WIDTH(32)) regFile
	(
		.clk(clk), 
		.write_enable(RegWrite), 
		.reset(reset), 
		.Source_select_0(Instr[19:15]), 
		.Source_select_1(Instr[24:20]), 
		.Debug_Source_select(Debug_Source_select), 
		.Destination_select(Instr[11:7]), 
		.DATA(Result),  
		.out_0(RD1), 
		.out_1(WriteData), 
		.Debug_out(Debug_out)
	);

//SHIFTER	
shifter#(.WIDTH(32)) shft
	(
		.control(shiftControl),
		.shamt(shamt),
		.DATA(RD1),
		.OUT(shifter_output)
	);

//ALU
ALU#(.WIDTH(32)) alu
	(
		.control(ALUControl),
		.CI(CO),
		.DATA_A(SrcA),
		.DATA_B(SrcB),
		.OUT(ALUResult),
		.CO(CO),
		.OVF(OVF),
		.N(N),
		.Z(Z)
	);

//EXTENDER
Extender extend
	(
		.Extended_data(ImmExt),
		.DATA(Instr[31:7]),
		.select(ImmSrc)
	);
	
//DATA MEMORY
Memory#(.BYTE_SIZE(4),.ADDR_WIDTH(32)) dataMemory
	(
		.clk(clk),
		.WE(MemWrite),
		.ADDR(ALUResult),
		.WD(WriteData),
		.RD(ReadData)
	);
endmodule
