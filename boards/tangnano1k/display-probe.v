// Diagnostic fixture: no calculator, keypad or switch inputs.
// Continuously write 00000000 at minimum intensity, about 5 kHz SPI.
module display_probe #(parameter HALF_CLOCKS=1350, parameter ENABLE_CLOCKS=1048576)(
 input wire clk,
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
 function [15:0] make_command;
 input [3:0] index;
 begin
   case(index)
     0:make_command=16'h0f00; // display-test mode off
     1:make_command=16'h0900; // raw segments
     2:make_command=16'h0b07; // eight digits
     3:make_command=16'h0a00; // minimum intensity
     4:make_command=16'h0c01; // normal operation
     default:make_command={4'b0,(index-4'd4),8'h7e}; // 0
   endcase
 end
 endfunction
 wire [15:0] command=make_command(word_index);
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
