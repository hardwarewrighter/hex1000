`timescale 1ns/1ps
module tb;
  reg clk = 0;
  wire [2:0] led_n;
  hex1000_selftest dut(clk, led_n);
  always #5 clk = ~clk;
  integer clocks = 0;
  initial begin
    // A complete internally keyed calculation, with the real /28 divider.
    wait (!dut.machine_rst);
    while (!dut.passed && !dut.failed && clocks < 50000) begin
      @(negedge dut.machine_clk);
      clocks = clocks + 1;
    end
    if (dut.failed || !dut.passed) $fatal(1, "selftest failed/timeout, digits=%h index=%d", dut.digits, dut.key_index);
    if (led_n[0] !== 1 || led_n[2] !== 0) $fatal(1, "pass LED polarity/mapping");
    if (dut.key_index !== 6 || !dut.saw_zero || !dut.digit0_seen)
      $fatal(1, "startup or six-key handshake not checked");
    $display("PASS: startup zero, digit strobes, six virtual keys, 12+34=46 (%0d machine clocks)", clocks);
    // Check the heartbeat edge and that the pass state remains sticky.
    @(negedge clk); dut.heartbeat = 25'h0ffffff;
    @(posedge clk); #1;
    if (led_n[1] !== 0 || !dut.passed) $fatal(1, "heartbeat or pass latch");
    $display("PASS: active-low RGB LEDs and heartbeat");
    // Prove the same checker lights red on a corrupted result and on timeout.
    @(negedge dut.machine_clk);
    dut.passed = 0; dut.failed = 0; dut.phase = 2; dut.digits[4:0] = 0;
    @(posedge dut.machine_clk); #1;
    if (!dut.failed || dut.passed || led_n[0] !== 0)
      $fatal(1, "wrong-result detector/LED failed");
    @(negedge dut.machine_clk);
    dut.failed = 0; dut.phase = 3; dut.elapsed = 20'hfffff;
    @(posedge dut.machine_clk); #1;
    if (!dut.failed) $fatal(1, "watchdog failed");
    $display("PASS: corrupted-result and watchdog failure detection");
    $finish;
  end
  initial begin #20000000; $fatal(1, "global simulation timeout"); end
endmodule
