/*
	R-Type: ALU and SHIFT operations
	I-Type: LOAD,SHIFT[I],ALU[I] and JALR operations
	S-Type: STORE opeations
	B-Type: BRANCH operations
	U-Type: LUI and AUIPC operations
	J-Type: JAL operation
*/

/*
	XORID: KEMAL ID : 2375491 --> 32'h243F43
			 ALPER ID : 2375467 --> 32'h243F2B
			 
			 ********** XOR(KEMAL,ALPER) = 32'h68 ************
*/
module Controller 
	(
		input clk, reset,
		input [1:0]Zero,
		input [31:0]Instr,
		output reg [3:0]ALUControl, 
		output reg [2:0]ImmSrc, 
		output reg ALUSrc,xorid,shift,
		output reg RegWrite,
		output reg [1:0] MemWrite,ResultSrc,PCSrc,regWriteSource
	);
	
	localparam	xADD = 4'b0000,	//ALU OPERATIONS
					xSUB = 4'b0001,
					xSLT = 4'b0010,
					xSLTU= 4'b0011,
					xXOR = 4'b0100,
					xORR = 4'b0101,
					xAND = 4'b0110,
					xSLL = 4'b0111,
					xSRL = 4'b1000,
					xSRA = 4'b1001,
					xADDU= 4'b1010,
					xSUBU= 4'b1011;
	
	localparam	ADD_SUB = 3'b000, //funct3 types for ALU_SHIFT
					SLL = 3'b001,
					SLT = 3'b010,
					SLTU= 3'b011,
					XOR = 3'b100,
					SRL_SRA = 3'b101,
					ORR = 3'b110,
					AND = 3'b111;
					
	localparam 	ALU_SHIFT = 7'b0110011,	//OPCODES
					LOAD = 7'b0000011,
					ALUI_SHIFTI = 7'b0010011,
					JALR = 7'b1100111,
					STORE = 7'b0100011,
					BRANCH = 7'b1100011,
					LUI = 7'b0110111,
					AUIPC = 7'b0010111,
					JAL = 7'b1101111,
					XORID = 7'b0001011;

	localparam 	R_TYPE = 3'b111,	//INSTRUCTION TYPES ACCORDING TO EXTENDER
					I_TYPE = 3'b000,
					S_TYPE = 3'b001,
					B_TYPE = 3'b010,
					U_TYPE = 3'b011,
					J_TYPE = 3'b100;
					
	localparam	LB = 3'b000,	//LOAD TYPES
					LH = 3'b001,
					LW = 3'b010,
					LBU= 3'b100,
					LHU= 3'b101;

	localparam	SB = 3'b000,	//STORE TYPES
					SH = 3'b001,
					SW = 3'b010;					
	
	localparam	BEQ = 3'b000,	//BRANCH TYPES
					BNE = 3'b001,
					BLT = 3'b100,
					BGE = 3'b101,
					BLTU= 3'b110,
					BGEU= 3'b111;
	
	wire [7:0]op;
	wire [2:0]funct3;
	wire funct7_5;
	
	assign op = Instr[6:0];
	assign funct3 = Instr[14:12];
	assign funct7_5 = Instr[30];	
	
	initial begin
		xorid = 1'b0;
		ImmSrc = R_TYPE;
		regWriteSource = 2'b00;				
		PCSrc = 2'b00;
		ResultSrc  = 2'b00;
		ALUSrc = 1'b0;
		RegWrite = 1'b1;
		MemWrite = 2'b00;
		ALUControl = xADD;
		shift = 1'b0;
	end
	
	always@(*) begin
		if(!reset) begin
			case(op)
				//R-TYPE
				ALU_SHIFT: begin
					ImmSrc = R_TYPE;
					regWriteSource = 2'b00;				
					PCSrc = 2'b00;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b0;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b0;
					xorid = 1'b0;
					case(funct3)
						ADD_SUB:begin
							if(funct7_5 == 1'b0) begin //ADD
								ALUControl = xADD;
							end
							else begin						//SUB
								ALUControl = xSUB;					
							end
						end
						SLL:begin						
							ALUControl = xSLL;						
						end
						SLT:begin
							ALUControl = xSLT;					
						end
						SLTU:begin
							ALUControl = xSLTU;					
						end
						XOR:begin
							ALUControl = xXOR;				
						end
						SRL_SRA:begin						
							if(funct7_5 == 1'b0) begin //SRL
								ALUControl = xSRL;							
							end
							else begin						//SRA
								ALUControl = xSRA;							
							end
						end
						ORR:begin				
							ALUControl = xORR;				
						end
						AND:begin					
							ALUControl = xAND;					
						end
						default: begin
							ALUControl = xADD;
						end
					endcase
				end
				//I-TYPE
				LOAD: begin
					ImmSrc = I_TYPE;
					regWriteSource = 2'b00;
					PCSrc = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b1;
					xorid = 1'b0;
					case(funct3)
						LB:begin
							ALUControl = xADD;
							ResultSrc  = 2'b11;
						end
						LH:begin
							ALUControl = xADD;
							ResultSrc  = 2'b10;
						end
						LW:begin
							ALUControl = xADD;
							ResultSrc  = 2'b01;
						end
						LBU:begin
							ALUControl = xADDU;
							ResultSrc  = 2'b11;
						end
						LHU:begin
							ALUControl = xADDU;
							ResultSrc  = 2'b10;
						end
						default: begin
							ALUControl = xADD;
							ResultSrc  = 2'b01;
						end
					endcase
				end
				ALUI_SHIFTI: begin
					ImmSrc = I_TYPE;
					regWriteSource = 2'b00;
					PCSrc = 2'b00;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b1;
					xorid = 1'b0;				
					case(funct3)
						ADD_SUB:begin
							ALUControl = xADD;			
						end
						SLL:begin						
							ALUControl = xSLL;						
						end
						SLT:begin
							ALUControl = xSLT;					
						end
						SLTU:begin
							ALUControl = xSLTU;					
						end
						XOR:begin
							ALUControl = xXOR;				
						end
						SRL_SRA:begin						
							if(funct7_5 == 1'b0) begin //SRL
								ALUControl = xSRL;							
							end
							else begin						//SRA
								ALUControl = xSRA;							
							end
						end
						ORR:begin				
							ALUControl = xORR;				
						end
						AND:begin					
							ALUControl = xAND;					
						end
						default: begin
							ALUControl = xADD;
						end					
					endcase			
				end
			
				JALR: begin
					ImmSrc = I_TYPE;
					regWriteSource = 2'b01;				
					PCSrc = 2'b10;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b1;
					ALUControl = xADD;
					xorid = 1'b0;
				end
				
				XORID: begin
					ImmSrc = I_TYPE;
					regWriteSource = 2'b00;
					PCSrc = 2'b00;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b1;
					ALUControl = xXOR;
					xorid = 1'b1;
				end
				//S-TYPE
				STORE:begin
					ImmSrc = S_TYPE;
					regWriteSource = 2'b00;
					PCSrc = 2'b00;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b0;
					shift = 1'b0;
					xorid = 1'b0;
					case(funct3)
						SB:begin
							ALUControl = xADD;
							MemWrite = 2'b11;
						end
						SH:begin
							ALUControl = xADD;
							MemWrite = 2'b10;
						end
						SW:begin
							ALUControl = xADD;
							MemWrite = 2'b01;
						end
						default: begin
							ALUControl = xADD;
							MemWrite  = 2'b01;
						end					
					endcase				
				end
				//B_TYPE
				BRANCH:begin
					ImmSrc = B_TYPE;
					regWriteSource = 2'b00;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b0;
					RegWrite = 1'b0;
					MemWrite = 2'b00;
					shift = 1'b0;
					xorid = 1'b0;
					case(funct3)
						BEQ:begin
							ALUControl = xSUB;
							PCSrc = (Zero == 2'b00)? 2'b01:2'b00;
						end
						BNE:begin
							ALUControl = xSUB;
							PCSrc = (Zero != 2'b00)? 2'b01:2'b00;				
						end
						BLT:begin
							ALUControl = xSUB;
							PCSrc = ( Zero == 2'b11)? 2'b01:2'b00;
						end
						BGE:begin
							ALUControl = xSUB;
							PCSrc = (Zero == 2'b01 || Zero == 2'b00)? 2'b01:2'b00;
						end
						BLTU:begin
							ALUControl = xSUBU;
							PCSrc = (Zero == 2'b11)? 2'b01:2'b00;
						end
						BGEU:begin
							ALUControl = xSUBU;
							PCSrc = (Zero == 2'b01 || Zero == 2'b00)? 2'b01:2'b00;
						end
						default:begin
							ALUControl = xSUB;
							PCSrc = (Zero == 32'b0)? 2'b01:2'b00;
						end
					endcase
				end
				//U_TYPE
				LUI:begin
					ImmSrc = U_TYPE;
					regWriteSource = 2'b10;
					PCSrc = 2'b00;
					ALUControl = xADD;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b0;
					xorid = 1'b0;
				end
				
				AUIPC:begin
					ImmSrc = U_TYPE;
					regWriteSource = 2'b11;
					PCSrc = 2'b00;
					ALUControl = xADD;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b0;
					xorid = 1'b0;
				end
				//J_TYPE
				JAL:begin
					ImmSrc = J_TYPE;
					regWriteSource = 2'b01;				
					PCSrc = 2'b01;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b1;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b0;
					ALUControl = xADD;
					xorid = 1'b0;
				end
				
				default: begin
					ImmSrc = R_TYPE;
					regWriteSource = 2'b00;				
					PCSrc = 2'b00;
					ResultSrc  = 2'b00;
					ALUSrc = 1'b0;
					RegWrite = 1'b1;
					MemWrite = 2'b00;
					shift = 1'b0;
					ALUControl = xADD;
					xorid = 1'b0;
				end
			endcase
		end
		else begin
			ImmSrc = R_TYPE;
			regWriteSource = 2'b00;				
			PCSrc = 2'b00;
			ResultSrc  = 2'b00;
			ALUSrc = 1'b0;
			RegWrite = 1'b1;
			MemWrite = 2'b00;
			shift = 1'b0;
			ALUControl = xADD;
			xorid = 1'b0;
		end
	end
	
endmodule
