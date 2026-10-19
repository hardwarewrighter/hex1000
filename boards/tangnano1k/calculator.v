// Clock/reset, input synchronization and physical pins; no UART.
module hex1000_calculator #(parameter ROW_CLOCKS=256, parameter ENABLE_CLOCKS=1048576)(
 input wire clk, input wire [3:0] pad_col_n, input wire [3:0] op_n,
 output wire [3:0] pad_row_n,
 output wire max_din, output wire max_clk, output wire max_load,
 output wire max_oe, output wire [2:0] led_n
);
 reg [3:0] divider=0;
 reg machine_clk=0;
 reg [24:0] heartbeat=0;
 reg enabled=0;
 always @(posedge clk) begin
   heartbeat <= heartbeat+1'b1;
   if (heartbeat == ENABLE_CLOCKS) enabled <= 1;
   if (divider==13) begin divider<=0; machine_clk<=~machine_clk; end
   else divider<=divider+1'b1;
 end
 reg [1:0] enable_sync=0;
 reg [3:0] startup=0;
 reg [3:0] cols_meta=15,cols_sync=15,ops_meta=15,ops_sync=15;
 always @(posedge machine_clk) begin
   enable_sync <= {enable_sync[0], enabled};
   if (startup!=15) startup<=startup+1'b1;
   cols_meta<=pad_col_n; cols_sync<=cols_meta;
   ops_meta<=op_n; ops_sync<=ops_meta;
 end
 wire rst=(startup!=15) || !enable_sync[1];
 wire [5:0] o;
 wire [15:0] r;
 wire [4:0] k;
 wire [3:0] rows;
 hex1000 machine(.clk(machine_clk),.rst(rst),.in_k(k),.out_o(o),.out_r(r));
 front #(.ROW_CLOCKS(ROW_CLOCKS)) panel(.clk(machine_clk),.rst(rst),.cols_n(cols_sync),.ops_n(ops_sync),
   .machine_o(o),.machine_r(r),.row_enable(rows),.keyboard(k),
   .max_din(max_din),.max_clk(max_clk),.max_load(max_load));
 genvar i;
 generate for(i=0;i<4;i=i+1) begin: row_pins
   assign pad_row_n[i]=(!rst && rows[i]) ? 1'b0 : 1'bz;
 end endgenerate
 assign max_oe=enable_sync[1] && startup==15;
 assign led_n={~r[15],~heartbeat[24],~r[14]};
endmodule
