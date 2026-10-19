// Physical panel implementation; checked against libs/Front/src/Front.xtl.
// External inputs must already be synchronized to clk by the board wrapper.
module front #(parameter ROW_CLOCKS = 256)(
  input wire clk, input wire rst,
  input wire [3:0] cols_n, input wire [3:0] ops_n,
  input wire [5:0] machine_o, input wire [15:0] machine_r,
  output wire [3:0] row_enable,
  output wire [4:0] keyboard,
  output reg max_din, output reg max_clk, output reg max_load
);
  reg [7:0] tick;
  reg [1:0] row;
  reg [15:0] scan;
  reg [19:0] candidate;
  reg [2:0] stable;
  reg [19:0] accepted;
  reg [15:0] scan_next;
  wire [19:0] frame = {~ops_n, scan_next};
  assign row_enable = 4'b0001 << row;
  always @* begin
    scan_next = scan;
    case (row)
      0: scan_next[3:0] = ~cols_n;
      1: scan_next[7:4] = ~cols_n;
      2: scan_next[11:8] = ~cols_n;
      3: scan_next[15:12] = ~cols_n;
    endcase
  end
  always @(posedge clk) begin
    if (rst) begin
      tick <= 0; row <= 0; scan <= 0;
      candidate <= 0; stable <= 0; accepted <= 0;
    end else if (tick == ROW_CLOCKS-1) begin
      tick <= 0; row <= row + 1'b1; scan <= scan_next;
      if (row == 3) begin
        if (frame != candidate) begin candidate <= frame; stable <= 0; end
        else if (stable != 7) stable <= stable + 1'b1;
        else accepted <= frame;
      end
    end else tick <= tick + 1'b1;
  end

  reg [1:0] phase;
  reg [4:0] key;
  reg last_equals;
  reg [4:0] first_code;
  reg found;
  integer i;
  always @* begin
    first_code = 0;
    found = 0;
    for (i=0; i<20; i=i+1) begin
      if (accepted[i] && !found) begin
        found = 1;
        if (i < 16) first_code = (3-i/4)*4 + i%4;
        else first_code = i;
      end
    end
  end
  assign keyboard = (phase == 2 && machine_r[8+key[4:2]])
                  ? (5'b00001 << key[1:0]) : 5'b0;
  always @(posedge clk) begin
    if (rst) begin phase <= 0; key <= 0; last_equals <= 0; end
    else case (phase)
      0: if (|accepted) begin
        key <= first_code == 19 && last_equals ? 20 : first_code;
        last_equals <= first_code == 19 && !last_equals;
        phase <= 1;
      end
      1: if (machine_r[15]) phase <= 2;
      2: if (!machine_r[15]) phase <= 3;
      3: if (accepted == 0) phase <= 0;
    endcase
  end

  reg [39:0] digits;
  reg [15:0] previous_r;
  integer d;
  always @(posedge clk) begin
    if (rst) begin digits <= 0; previous_r <= 0; end
    else begin
      previous_r <= machine_r;
      for (d=0; d<8; d=d+1)
        if (machine_r[d] && !previous_r[d]) digits[5*d +: 5] <= machine_o[4:0];
    end
  end

  function [6:0] segments;
    input [4:0] digit;
    reg [6:0] font;
    begin
      case (digit[3:0])
        0: font=7'h7e; 1: font=7'h30; 2: font=7'h6d; 3: font=7'h79;
        4: font=7'h33; 5: font=7'h5b; 6: font=7'h5f; 7: font=7'h70;
        8: font=7'h7f; 9: font=7'h7b; 10: font=7'h77; 11: font=7'h1f;
        12: font=7'h4e; 13: font=7'h3d; 14: font=7'h4f; 15: font=7'h47;
      endcase
      segments = digit[4] ? font : 7'b0;
    end
  endfunction
  reg [5:0] spi_phase;
  reg [3:0] word_index;
  reg [15:0] shift;
  reg [15:0] word_value;
  always @* begin
    case (word_index)
      0: word_value=16'h0c01;
      1: word_value=16'h0f00;
      2: word_value=16'h0900;
      3: word_value=16'h0b07;
      4: word_value=16'h0a04;
      default: word_value = {4'b0, (word_index-4'd4), 1'b0,
                             segments(digits[(word_index-5)*5 +: 5])};
    endcase
  end
  always @(posedge clk) begin
    if (rst) begin
      spi_phase <= 0; word_index <= 0; shift <= 0;
      max_din <= 0; max_clk <= 0; max_load <= 1;
    end else begin
      if (spi_phase == 35) begin
        spi_phase <= 0;
        word_index <= word_index == 12 ? 0 : word_index + 1'b1;
      end else spi_phase <= spi_phase + 1'b1;
      if (spi_phase == 0) begin
        shift <= word_value; max_din <= word_value[15]; max_clk <= 0; max_load <= 0;
      end else if (spi_phase < 32) begin
        max_clk <= spi_phase[0];
        if (!spi_phase[0]) begin shift <= shift << 1; max_din <= shift[14]; end
      end else if (spi_phase == 32) begin max_clk <= 0; max_load <= 1; end
    end
  end
endmodule
