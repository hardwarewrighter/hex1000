// Raw electrical keypad diagnostic, independent of calculator key mapping.
// Each row is low for two seconds; others are high impedance.
// Display 000R000C: R=selected row 1..4; C=column mask 0,1,2,4,8.
module keypad_probe #(parameter HALF_CLOCKS=14, parameter ENABLE_CLOCKS=1048576,
 parameter ROW_HOLD=1928571)(
 input wire clk, input wire [3:0] pad_col_n,
 output wire [3:0] pad_row_n,
 output reg max_din=0, output reg max_clk=0, output reg max_load=1,
 output wire max_oe, output wire [2:0] led_n
);
 reg [10:0] divider=0;
 reg probe_clk=0;
 reg [24:0] heartbeat=0;
 reg enabled=0;
 always @(posedge clk) begin
   heartbeat<=heartbeat+1'b1;
   if(heartbeat==ENABLE_CLOCKS) enabled<=1;
   if(divider==HALF_CLOCKS-1) begin divider<=0;probe_clk<=~probe_clk;end
   else divider<=divider+1'b1;
 end
 reg [1:0] enable_sync=0;
 always @(posedge probe_clk) enable_sync<={enable_sync[0],enabled};
 assign max_oe=enable_sync[1];
 assign led_n={~heartbeat[24],2'b11}; // blinking green; red/blue off
 reg [5:0] phase=0;
 reg [3:0] word_index=0;
 reg [15:0] shift=0;
 function [7:0] hex_segment;
 input [3:0] digit;
 begin
   case(digit)
     0:hex_segment=8'h7e;1:hex_segment=8'h30;2:hex_segment=8'h6d;3:hex_segment=8'h79;
     4:hex_segment=8'h33;5:hex_segment=8'h5b;6:hex_segment=8'h5f;7:hex_segment=8'h70;
     8:hex_segment=8'h7f;9:hex_segment=8'h7b;10:hex_segment=8'h77;11:hex_segment=8'h1f;
     12:hex_segment=8'h4e;13:hex_segment=8'h3d;14:hex_segment=8'h4f;15:hex_segment=8'h47;
   endcase
 end
 endfunction
 reg [20:0] row_timer=0;
 reg [1:0] row=0;
 reg [3:0] cols_meta=15,cols_sync=15;
 always @(posedge probe_clk) begin
   cols_meta<=pad_col_n;cols_sync<=cols_meta;
   if(!enable_sync[1]) begin row_timer<=0;row<=0;end
   else if(row_timer==ROW_HOLD-1) begin row_timer<=0;row<=row+1'b1;end
   else row_timer<=row_timer+1'b1;
 end
 genvar i;
 generate for(i=0;i<4;i=i+1) begin: row_pins
   assign pad_row_n[i]=(enable_sync[1] && row==i) ? 1'b0 : 1'bz;
 end endgenerate
 wire [3:0] row_number={2'b0,row}+4'd1;
 wire [31:0] value={12'b0,row_number,12'b0,~cols_sync};
 function [15:0] make_command;
 input [3:0] index;
 input [31:0] digits;
 begin
   case(index)
     0:make_command=16'h0f00; // display-test mode off
     1:make_command=16'h0900; // raw segments
     2:make_command=16'h0b07; // eight digits
     3:make_command=16'h0a00; // minimum intensity
     4:make_command=16'h0c01; // normal operation
     default:make_command={4'b0,(index-4'd4),hex_segment(digits[(index-5)*4 +: 4])};
   endcase
 end
 endfunction
 wire [15:0] command=make_command(word_index,value);
 always @(posedge probe_clk) begin
   if(!enable_sync[1]) begin
     phase<=0;word_index<=0;shift<=0;
     max_din<=0;max_clk<=0;max_load<=1;
   end else begin
     if(phase==35) begin phase<=0;word_index<=word_index==12?0:word_index+1'b1;end
     else phase<=phase+1'b1;
     if(phase==0) begin shift<=command;max_din<=command[15];max_clk<=0;max_load<=0;end
     else if(phase<32) begin
       max_clk<=phase[0];
       if(!phase[0]) begin shift<=shift<<1;max_din<=shift[14];end
     end else if(phase==32) begin max_clk<=0;max_load<=1;end
   end
 end
endmodule
