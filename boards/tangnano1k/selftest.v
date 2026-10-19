// Peripheral-free HEX1000 test. Only clock and onboard RGB LED are ports.
module hex1000_selftest(input wire clk, output wire [2:0] led_n);
  reg [3:0] divider = 0;
  reg machine_clk = 0;
  reg [24:0] heartbeat = 0;
  always @(posedge clk) begin
    heartbeat <= heartbeat + 1'b1;
    if (divider == 13) begin
      divider <= 0;
      machine_clk <= ~machine_clk;
    end else divider <= divider + 1'b1;
  end

  // Synchronous reset spans fifteen machine clocks, including ROM reads.
  reg [3:0] startup = 0;
  wire machine_rst = startup != 15;
  always @(posedge machine_clk)
    if (startup != 15) startup <= startup + 1'b1;

  wire [5:0] machine_o;
  wire [15:0] machine_r;
  reg [2:0] key_index;
  reg [1:0] phase;
  reg [4:0] key_code;
  wire [4:0] keyboard = (phase == 1 && machine_r[8 + key_code[4:2]])
                        ? (5'b00001 << key_code[1:0]) : 5'b0;
  always @* begin
    case (key_index)
      0: key_code = 1;
      1: key_code = 2;
      2: key_code = 16; // +
      3: key_code = 3;
      4: key_code = 4;
      default: key_code = 19; // =
    endcase
  end
  hex1000 machine(.clk(machine_clk), .rst(machine_rst), .in_k(keyboard),
                  .out_o(machine_o), .out_r(machine_r));

  reg [15:0] previous_r;
  reg [39:0] digits;
  reg saw_zero;
  reg digit0_seen;
  reg passed;
  reg failed;
  reg [19:0] elapsed;
  integer digit;
  wire result_ok = digits[4:0] == 5'h16 && digits[9:5] == 5'h14 &&
                   !(digits[14] | digits[19] | digits[24] |
                     digits[29] | digits[34] | digits[39]);
  always @(posedge machine_clk) begin
    if (machine_rst) begin
      previous_r <= 0;
      digits <= 0;
      saw_zero <= 0;
      digit0_seen <= 0;
      passed <= 0;
      failed <= 0;
      elapsed <= 0;
      key_index <= 0;
      phase <= 0;
    end else begin
      previous_r <= machine_r;
      for (digit = 0; digit < 8; digit = digit + 1)
        if (machine_r[digit] && !previous_r[digit])
          digits[digit*5 +: 5] <= machine_o[4:0];
      if (machine_r[0] && !previous_r[0]) digit0_seen <= 1;
      if (!passed && !failed) begin
        elapsed <= elapsed + 1'b1;
        if (&elapsed) failed <= 1;
        case (phase)
          0: if (machine_r[15]) begin
            if (key_index == 0) saw_zero <= digit0_seen && digits[4:0] == 16;
            if (key_index == 6) phase <= 2;
            else phase <= 1;
          end
          1: if (!machine_r[15]) begin
            key_index <= key_index + 1'b1;
            phase <= 0;
          end
          2: begin
            passed <= result_ok && saw_zero && digit0_seen;
            failed <= !(result_ok && saw_zero && digit0_seen);
            phase <= 3;
          end
          default: phase <= 3;
        endcase
      end
    end
  end
  // Active low: red=failure, blue=heartbeat, green=calculator passed.
  assign led_n = {~passed, ~heartbeat[24], ~failed};
endmodule
