module Extender (
    output reg [31:0]Extended_data,
    input [24:0]DATA,
    input [2:0]select
);

localparam 	R_TYPE = 3'b111,
				I_TYPE = 3'b000,
				S_TYPE = 3'b001,
				B_TYPE = 3'b010,
				U_TYPE = 3'b011,
				J_TYPE = 3'b100;

always @(*) begin
    case (select)

		I_TYPE: Extended_data = {{21{DATA[24]}}, DATA[23:18], DATA[17:14], DATA[13]};

      S_TYPE: Extended_data = {{21{DATA[24]}}, DATA[23:18], DATA[4:1], DATA[0]};

      B_TYPE: Extended_data = {{20{DATA[24]}}, DATA[0], DATA[23:18], DATA[4:1], 1'b0};

		U_TYPE: Extended_data = {DATA[24:5], 12'b0};

		J_TYPE: Extended_data = {{12{DATA[24]}}, DATA[12:5], DATA[13], DATA[23:18], DATA[17:14], 1'b0};
		
      default: Extended_data = 32'd0;
    endcase
end
    
endmodule
