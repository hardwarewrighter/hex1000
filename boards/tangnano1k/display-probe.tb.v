`timescale 1ns/1ps
module tb;
 reg clk=0;
 always #5 clk=~clk;
 wire din,sclk,load,oe;
 wire [2:0] led;
 display_probe #(.HALF_CLOCKS(4),.ENABLE_CLOCKS(32)) dut(clk,din,sclk,load,oe,led);
 reg [15:0] word=0;
 integer bits=0,words=0;
 reg [7:0] display[0:7];
 reg [15:0] expected;
 integer j;
 reg [63:0] expected_display=64'h3d4f773d1f4f4f47;
 always @(posedge sclk) begin
   if(!oe || load) $fatal(1,"clock before enable or while LOAD high");
   word={word[14:0],din};bits=bits+1;
 end
 always @(posedge load) begin
   if(bits) begin
     if(bits!=16) $fatal(1,"word length %0d",bits);
     case(words%13)
       0:expected=16'h0f00;1:expected=16'h0900;2:expected=16'h0b07;
       3:expected=16'h0a00;4:expected=16'h0c01;
       default:expected=((words%13-4)*256)+expected_display[(words%13-5)*8 +: 8];
     endcase
     if(word!==expected) $fatal(1,"command %h expected %h",word,expected);
     if(word[15:8]>=1 && word[15:8]<=8) display[word[15:8]-1]=word[7:0];
     words=words+1;bits=0;
   end
 end
 initial begin
   wait(words==26);
   for(j=0;j<8;j=j+1) if(display[j]!==expected_display[j*8 +: 8]) $fatal(1,"digit %0d wrong glyph",j);
   if(led[1:0]!==2'b11) $fatal(1,"unexpected red/blue indicator");
   @(negedge clk);dut.heartbeat=25'h0ffffff;
   @(posedge clk);#1;if(led[2]!==0) $fatal(1,"green heartbeat failed");
   $display("PASS: two complete display-only initialization/DEADBEEF frames, OE gating and green heartbeat");
   $finish;
 end
 initial begin #1000000;$fatal(1,"timeout");end
endmodule
