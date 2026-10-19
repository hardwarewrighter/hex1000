`timescale 1ns/1ps
module tb;
 parameter TEST_ROWS=4;
 reg clk=0;
 always #5 clk=~clk;
 reg [15:0] pressed=0;
 reg [3:0] ops_n=15;
 reg [3:0] cols_n;
 tri1 [3:0] rows;
 wire din,sclk,load,oe;
 wire [2:0] leds;
 hex1000_calculator #(.ROW_CLOCKS(TEST_ROWS),.ENABLE_CLOCKS(TEST_ROWS==256 ? 1048576 : 32)) dut(
   .clk(clk),.pad_col_n(cols_n),.op_n(ops_n),.pad_row_n(rows),
   .max_din(din),.max_clk(sclk),.max_load(load),.max_oe(oe),.led_n(leds));
 always @(posedge clk) begin
   if(!dut.enabled && oe===1'b1) $fatal(1,"OE enabled before startup delay");
 end
 integer row;
 always @* begin
   cols_n=15;
   for(row=0;row<4;row=row+1)
     if(rows[row]===1'b0) cols_n=cols_n & ~pressed[row*4 +:4];
 end
 task clocks;
 input integer n;
 integer i;
 begin for(i=0;i<n;i=i+1) @(negedge dut.machine_clk); end
 endtask
 task ready;
 integer tries;
 begin
   tries=0;
   while(!(dut.r[15] && dut.panel.phase==0) && tries<100000) begin clocks(1);tries=tries+1;end
   if(tries==100000) $fatal(1,"ready timeout");
 end
 endtask
 task key;
 input integer code;
 integer tries;
 begin
   ready;
   if(code<16) pressed=16'b1<<((3-code/4)*4+code%4);
   else ops_n=~(4'b1<<(code-16));
   clocks(256);
   tries=0;
   while(dut.panel.phase!=3 && tries<100000) begin clocks(1);tries=tries+1;end
   if(tries==100000) $fatal(1,"key acceptance timeout %0d",code);
   pressed=0; ops_n=15;
   ready;
 end
 endtask
 reg [15:0] serial_word=0;
 integer serial_bits=0, serial_words=0;
 reg [7:0] display[0:7];
 always @(posedge sclk) begin
   if(load!==0) $fatal(1,"clock while LOAD high");
   serial_word={serial_word[14:0],din}; serial_bits=serial_bits+1;
 end
 always @(posedge load) begin
   if(serial_bits!=0) begin
     if(serial_bits!=16) $fatal(1,"SPI word has %0d bits",serial_bits);
     if(serial_word[15:8]>=1 && serial_word[15:8]<=8)
       display[serial_word[15:8]-1]=serial_word[7:0];
     else if(serial_word!=16'h0c01 && serial_word!=16'h0f00 && serial_word!=16'h0900 && serial_word!=16'h0b07 && serial_word!=16'h0a04)
       $fatal(1,"invalid MAX7219 command %h",serial_word);
     serial_words=serial_words+1;
     serial_bits=0;
   end
 end
 task check;
 input [39:0] expected;
 input [63:0] expected_segments;
 begin
   clocks(1000); // more than two complete serial refreshes
   if(dut.panel.digits!==expected) $fatal(1,"digits %h expected %h",dut.panel.digits,expected);
   if({display[7],display[6],display[5],display[4],display[3],display[2],display[1],display[0]}!==expected_segments)
     $fatal(1,"MAX7219 segments disagree with expected screen");
 end
 endtask
 initial begin
   wait(!dut.rst); ready;
   check({35'b0,5'd16},64'h3d4f773d1f4f4f47);
   // A short bouncing press must not be accepted.
   pressed=16'h1000;clocks(32);pressed=0;clocks(160);
   if(dut.panel.accepted!=0 || dut.panel.phase!=0) $fatal(1,"bounce accepted");
   if(dut.panel.have_key!==0) $fatal(1,"bounce cleared startup banner");
   key(1);check({35'b0,5'd17},64'h0000000000000030);
   if(dut.panel.have_key!==1) $fatal(1,"first key did not clear banner");
   $display("PASS DEADBEEF startup, bounce persistence and first key processed normally");
   key(2);key(16);key(3);key(4);key(19);
   check({30'b0,5'd20,5'd22},64'h000000000000335f);
   $display("PASS physical scanning and serial display: 12+34=46");
   key(19);check({35'b0,5'd16},64'h000000000000007e);
   $display("PASS second equals clears to zero");
   key(10);key(18);key(11);key(19);
   check({30'b0,5'd22,5'd30},64'h0000000000005f4f);
   $display("PASS A*B=6E");
   key(19);key(5);key(17);key(7);key(19);
   check({5'd31,5'd31,5'd31,5'd31,5'd31,5'd31,5'd31,5'd30},64'h474747474747474f);
   $display("PASS 5-7=FFFFFFFE");
   key(19);key(12);key(0);key(13);key(14);key(16);key(11);key(14);key(14);key(15);key(19);
   check({15'b0,5'd17,5'd23,5'd31,5'd28,5'd29},64'h0000003070474e3d);
   $display("PASS C0DE+BEEF=17FCD");
   if(!oe || serial_words<100) $fatal(1,"enable/serial refresh missing");
   $display("PASS physical panel, debounce, held-key handshake, arithmetic, == clear and MAX7219 framing");
   $finish;
 end
 initial begin #1000000000; $fatal(1,"global timeout"); end
endmodule
