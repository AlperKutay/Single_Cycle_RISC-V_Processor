module Decoder_5to32
    (
	  input [4:0] IN,
      output reg [31:0] OUT
    );

always @(*) begin
	case(IN)
		5'h00:OUT=32'h00000001;
		5'h01:OUT=32'h00000002;
		5'h02:OUT=32'h00000004;
		5'h03:OUT=32'h00000008;

		5'h04:OUT=32'h00000010;
		5'h05:OUT=32'h00000020;
		5'h06:OUT=32'h00000040;
		5'h07:OUT=32'h00000080;

		5'h08:OUT=32'h00000100;
		5'h09:OUT=32'h00000200;
		5'h0a:OUT=32'h00000400;
		5'h0b:OUT=32'h00000800;

		5'h0c:OUT=32'h00001000;
		5'h0d:OUT=32'h00002000;
		5'h0e:OUT=32'h00004000;
		5'h0f:OUT=32'h00008000;

		5'h10:OUT=32'h00010000;
		5'h11:OUT=32'h00020000;
		5'h12:OUT=32'h00040000;
		5'h13:OUT=32'h00080000;

		5'h14:OUT=32'h00100000;
		5'h15:OUT=32'h00200000;
		5'h16:OUT=32'h00400000;
		5'h17:OUT=32'h00800000;

		5'h18:OUT=32'h01000000;
		5'h19:OUT=32'h02000000;
		5'h1a:OUT=32'h04000000;
		5'h1b:OUT=32'h08000000;

		5'h1c:OUT=32'h10000000;
		5'h1d:OUT=32'h20000000;
		5'h1e:OUT=32'h40000000;
		5'h1f:OUT=32'h80000000;
	endcase
end

endmodule