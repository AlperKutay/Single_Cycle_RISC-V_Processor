module SingleCycleRISCVProcessor
	(
		input clk,reset,
		input [4:0]Debug_source_select,
		output [31:0]PC, Debug_out
	);

wire ALUSrc,RegWrite,xorid,shift;
wire [1:0]MemWrite,ResultSrc,PCSrc,regWriteSource;
wire [2:0]ImmSrc;
wire [3:0]ALUControl;
wire [31:0]Instr,Zero;
	
Datapath dp
	(
		.clk(clk),
		.reset(reset),
		.ALUSrc(ALUSrc),
		.RegWrite(RegWrite),
		.xorid(xorid),
		.shift(shift),
		.MemWrite(MemWrite),
		.ResultSrc(ResultSrc),
		.PCSrc(PCSrc),
		.regWriteSource(regWriteSource),
		.ImmSrc(ImmSrc),
		.ALUControl(ALUControl),
		.Debug_Source_select(Debug_source_select),
		.Debug_out(Debug_out),
		.PC(PC),
		.Instr(Instr),
		.Zero(Zero)	
	);
	
Controller cntrl
	(
		.clk(clk), 
		.reset(reset),
		.Instr(Instr),
		.Zero(Zero),
		.ALUControl(ALUControl), 
		.ImmSrc(ImmSrc),
		.xorid(xorid),
		.shift(shift),
		.ALUSrc(ALUSrc),
		.RegWrite(RegWrite),
		.MemWrite(MemWrite),
		.ResultSrc(ResultSrc),
		.PCSrc(PCSrc),
		.regWriteSource(regWriteSource)	
	);
endmodule
