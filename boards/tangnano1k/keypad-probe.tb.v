`timescale 1ns/1ps
module tb;
 reg clk=0;always #5 clk=~clk;
 wire [3:0] rows;reg [3:0] cols=15;
 wire din,sck,load,oe;wire[2:0] led;
 reg [15:0] pressed=0;reg short_rows=0;
 keypad_probe #(.HALF_CLOCKS(1),.ENABLE_CLOCKS(2),.ROW_HOLD(10000)) dut(
 .clk(clk),.pad_col_n(cols),.pad_row_n(rows),.max_din(din),.max_clk(sck),.max_load(load),.max_oe(oe),.led_n(led));
 integer r,c;
 always @* begin
  cols=15;
  for(r=0;r<4;r=r+1) for(c=0;c<4;c=c+1)
    if(pressed[4*r+c] && (rows[r]===1'b0 || (short_rows && (r==0 || r==3) && (rows[0]===1'b0 || rows[3]===1'b0)))) cols[c]=0;
 end
 reg [15:0] shift=0;integer bits=0,words=0;
 reg [15:0] expected;
 always @(posedge sck) begin shift={shift[14:0],din};bits=bits+1;end
 always @(posedge load) if(bits!=0) begin
  if(bits!=16) $fatal(1,"SPI bit count %d",bits);
  if(words<13) begin
   case(words)
    0:expected=16'h0f00;1:expected=16'h0900;2:expected=16'h0b07;
    3:expected=16'h0a00;4:expected=16'h0c01;
    default:expected=0;
   endcase
   if(words>=5) begin
    expected=((words-4)<<8)|8'h7e;
    if(words==9) expected=16'h0530;
   end
   if(shift!==expected) $fatal(1,"SPI word %d got %h expected %h",words,shift,expected);
  end
  words=words+1;bits=0;
 end
 integer key,rr,j;reg[3:0] mask;
 initial begin
  wait(words>=13);
  $display("PASS SPI startup row 1 and no columns: 00010000");
  for(key=0;key<16;key=key+1) begin
   pressed=16'b1<<key;
   for(rr=0;rr<4;rr=rr+1) begin
    wait(dut.row==rr && dut.row_timer==100);
    #1;mask=(key/4==rr)?(1<<(key%4)):0;
    if(dut.cols_sync!==(~mask)) $fatal(1,"key %d row %d cols %h expected mask %h",key,rr,dut.cols_sync,mask);
    if(dut.value!==((rr+1)<<16 | mask)) $fatal(1,"raw display encoding");
    for(j=0;j<4;j=j+1) if(rows[j]!==((j==rr)?1'b0:1'bz)) $fatal(1,"row drive %d",j);
   end
  end
  pressed=16'h1000;short_rows=1;
  wait(dut.row==0 && dut.row_timer==100);#1;
  if(dut.cols_sync!==4'b1110) $fatal(1,"shorted-row diagnosis");
  $display("PASS all 16 keys across four rows; inactive rows high impedance; row-short visible independently of key mapping");
  $finish;
 end
 initial begin #30000000;$fatal(1,"timeout");end
endmodule
