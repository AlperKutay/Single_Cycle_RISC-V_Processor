/*
	XORID: KEMAL ID : 2375491 --> 32'h243F43
			 ALPER ID : 2375467 --> 32'h243F2B
			 
			 ********** XOR(KEMAL,ALPER) = 32'h68 ************
*/
module Datapath
	(
	input clk,reset,
	input ALUSrc,RegWrite,xorid,shift,
	input [1:0]MemWrite,ResultSrc,PCSrc,regWriteSource,
	input [2:0]ImmSrc,
	input [3:0]ALUControl,
	input [4:0] Debug_Source_select,
	output [31:0] Debug_out,
	output [31:0] PC,Instr,
	output [1:0]Zero
	);
	
//WIRES ON DATAPATH
wire [31:0]PCNext,PCPlus4;
wire [31:0]SrcA,SrcB,ImmExt, ALUInput2;
wire [31:0]ALUResult,WriteData,PCTarget;
wire [31:0]ReadData, Result, RegFileWrite;
wire [4:0]shamt;
//MULTIPLEXERS
Mux_4to1#(.WIDTH(32)) pcmux 
	(
		.select(PCSrc),
		.input_0(PCPlus4),
		.input_1(PCTarget),
		.input_2(ALUResult),
		.input_3(32'b0),		
		.output_value(PCNext)
	);	
	
Mux_2to1#(.WIDTH(32)) srcbControl 
	(
		.select(ALUSrc),
		.input_0(WriteData),
		.input_1(ImmExt),
		.output_value(SrcB)
	);	
	
Mux_4to1#(.WIDTH(32)) resultControl
	(
		.select(ResultSrc),
		.input_0(ALUResult),
		.input_1(ReadData),
		.input_2(ReadData[15:0]),
		.input_3(ReadData[7:0]),
		.output_value(Result)
	);	

Mux_4to1#(.WIDTH(32)) regWriteControl 
	(
		.select(regWriteSource),
		.input_0(Result),
		.input_1(PCPlus4),
		.input_2(ImmExt),
		.input_3(PCTarget),		
		.output_value(RegFileWrite)
	);		

Mux_2to1#(.WIDTH(32)) aluInp2Control 
	(
		.select(xorid),
		.input_0(SrcB),
		.input_1(32'h68),
		.output_value(ALUInput2)
	);	

Mux_2to1#(.WIDTH(32)) shiftControl 
	(
		.select(shift),	//0 for R type 1 for I type
		.input_0(WriteData[4:0]),	
		.input_1(Instr[24:20]),
		.output_value(shamt)
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
		.DATA(RegFileWrite),  
		.out_0(SrcA), 
		.out_1(WriteData), 
		.Debug_out(Debug_out)
	);

//ALU
ALU#(.WIDTH(32)) alu
	(
		.control(ALUControl),
		.shamt(shamt),
		.DATA_A(SrcA),
		.DATA_B(ALUInput2),
		.OUT(ALUResult),
		.Zero(Zero)
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
