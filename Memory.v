module Memory#(BYTE_SIZE=4, ADDR_WIDTH=32)(
input clk,
input [1:0]WE,
input [ADDR_WIDTH-1:0] ADDR,
input [(BYTE_SIZE*8)-1:0] WD,
output [(BYTE_SIZE*8)-1:0] RD 
);

reg [7:0] mem [255:0];

genvar i;
generate
	for (i = 0; i < BYTE_SIZE; i = i + 1) begin: read_generate
		assign RD[8*i+:8] = mem[ADDR+i];
	end
endgenerate	
integer k;

always @(posedge clk) begin
    if(WE == 2'b01) begin	//WORD
        for (k = 0; k < BYTE_SIZE; k = k + 1) begin
            mem[ADDR+k] <= WD[8*k+:8];
        end
    end
	 else if(WE == 2'b10) begin	//HALF WORD
        for (k = 0; k < 2; k = k + 1) begin
            mem[ADDR+k] <= WD[8*k+:8];
        end
    end
	 else if(WE == 2'b11) begin	//BYTE
        for (k = 0; k < 1; k = k + 1) begin
            mem[ADDR+k] <= WD[8*k+:8];
        end
    end
end

endmodule