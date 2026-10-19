`timescale 1ns/1ps
module tb;
 reg clk=0,rst=1;
 always #5 clk=~clk;
 reg [3:0] cols=15,ops=15;
 reg [5:0] o=0;
 reg [15:0] r=0;
 wire [3:0] rows;
 wire [4:0] k;
 wire di,cl,ld;
 front #(.ROW_CLOCKS(4)) dut(clk,rst,cols,ops,o,r,rows,k,di,cl,ld);
 integer file,count,i;
 integer cols_i,ops_i,o_i,r_i,tick_i,row_i,scan_i,candidate_i,stable_i,accepted_i;
 integer phase_i,key_i,last_i,k_i,p_i,w_i,sh_i,di_i,cl_i,ld_i;
 reg [63:0] digits_i;
 initial begin
   file=$fopen("work/board/calculator/front-trace.txt","r");
   if(!file) $fatal(1,"missing X_eTaL trace");
   @(posedge clk);#1;rst=0;
   i=0;
   while(!$feof(file)) begin
     count=$fscanf(file,"%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
       cols_i,ops_i,o_i,r_i,tick_i,row_i,scan_i,candidate_i,stable_i,accepted_i,
       phase_i,key_i,last_i,k_i,digits_i,p_i,w_i,sh_i,di_i,cl_i,ld_i);
     if(count!=21) $fatal(1,"bad trace row %0d fields %0d",i,count);
     @(negedge clk);cols=cols_i;ops=ops_i;o=o_i;r=r_i;
     @(posedge clk);#1;
     if(dut.tick!==tick_i[7:0] || dut.row!==row_i[1:0] || dut.scan!==scan_i[15:0] ||
       dut.candidate!==candidate_i[19:0] || dut.stable!==stable_i[2:0] || dut.accepted!==accepted_i[19:0])
       $fatal(1,"scanner/debounce mismatch at clock %0d",i);
     if(dut.phase!==phase_i[1:0] || dut.key!==key_i[4:0] || dut.last_equals!==last_i[0] || k!==k_i[4:0])
       $fatal(1,"key/equals handshake mismatch at clock %0d",i);
     if(dut.digits!==digits_i[39:0]) $fatal(1,"digit capture mismatch at clock %0d",i);
     if(dut.spi_phase!==p_i[5:0] || dut.word_index!==w_i[3:0] || dut.shift!==sh_i[15:0] ||
       di!==di_i[0] || cl!==cl_i[0] || ld!==ld_i[0])
       $fatal(1,"serial state mismatch at clock %0d, word %h/%h",i,dut.shift,sh_i);
     i=i+1;
   end
   if(i!=1100) $fatal(1,"trace truncated");
   $display("PASS: 1100 panel clocks match X_eTaL scanner, debounce, key handshake, == clear, digits and MAX7219 state");
   $finish;
 end
endmodule
