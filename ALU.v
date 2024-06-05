module ALU #(parameter WIDTH=8)
    (
	  input [3:0] control,
	  input [4:0] shamt,
	  input [WIDTH-1:0] DATA_A,
	  input [WIDTH-1:0] DATA_B,
     output reg [WIDTH-1:0] OUT,
	  output [WIDTH-1:0] Zero
    );
localparam	ADD = 4'b0000,
				SUB = 4'b0001,
				SLT = 4'b0010,
				SLTU= 4'b0011,
				XOR = 4'b0100,
				ORR = 4'b0101,
				AND = 4'b0110,
				SLL = 4'b0111,
				SRL = 4'b1000,
				SRA = 4'b1001,
				ADDU= 4'b1010,
				SUBU= 4'b1011;
assign Zero = OUT;				
				
always@(*) begin
	case(control)
		ADD:begin
			OUT = $signed(DATA_A) + $signed(DATA_B);
		end
		SUB:begin
			OUT = $signed(DATA_A) - $signed(DATA_B);
		end
		SLT:begin
			OUT = ($signed(DATA_A) < $signed(DATA_B))? {{(WIDTH-1){1'b0}}, 1'b1} : {WIDTH{1'b0}};
		end
		SLTU:begin
			OUT = ($unsigned(DATA_A) < $unsigned(DATA_B))? {{(WIDTH-1){1'b0}}, 1'b1} : {WIDTH{1'b0}};
		end
		XOR:begin
			OUT = DATA_A ^ DATA_B;
		end
		ORR:begin
			OUT = DATA_A | DATA_B;
		end
		AND:begin
			OUT = DATA_A & DATA_B;
		end
		SLL:begin
			OUT = DATA_A << shamt;
		end
		SRL:begin
			OUT = DATA_A >> shamt;
		end
		SRA:begin
			OUT = $signed(DATA_A) >>> shamt;
		end
		ADDU:begin
			OUT = $unsigned(DATA_A) + $unsigned(DATA_B);
		end
		SUBU:begin
			OUT = $unsigned(DATA_A) - $unsigned(DATA_B);
		end		
		default:begin
			OUT = {WIDTH{1'b0}};
		end
	endcase
end
	 
endmodule	 