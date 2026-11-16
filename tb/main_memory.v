`timescale 1ns/1ps
// Test-only, one-outstanding-request memory. Response is a one-cycle pulse.
module main_memory #(parameter WORD_COUNT=16384, parameter LATENCY=5)(
    input wire clk, input wire reset,
    input wire req_valid, output wire req_ready, input wire req_write,
    input wire [31:0] req_addr, input wire [31:0] req_wdata,
    output reg rsp_valid, output reg [31:0] rsp_rdata
);
    reg [31:0] words [0:WORD_COUNT-1];
    reg busy, write_q;
    reg [31:0] addr_q, data_q;
    integer remaining, cycle, i;
    assign req_ready = !reset && !busy && !rsp_valid && cycle % 4 != 0;
    always @(posedge clk) begin
        if (reset) begin
            busy <= 0; rsp_valid <= 0; rsp_rdata <= 0;
            remaining <= 0; cycle <= 0; write_q <= 0; addr_q <= 0; data_q <= 0;
            for (i=0; i<WORD_COUNT; i=i+1) words[i] <= 32'hA5A50000 ^ i;
        end else begin
            cycle <= cycle+1; rsp_valid <= 0;
            if (req_valid && req_ready) begin
                if (req_addr[1:0] != 0 || req_addr/4 >= WORD_COUNT)
                    $fatal(1, "Invalid memory address %h", req_addr);
                busy <= 1; remaining <= LATENCY;
                addr_q <= req_addr; data_q <= req_wdata; write_q <= req_write;
            end else if (busy) begin
                if (remaining == 1) begin
                    if (write_q) words[addr_q/4] <= data_q;
                    rsp_rdata <= write_q ? 0 : words[addr_q/4];
                    rsp_valid <= 1; busy <= 0;
                end else remaining <= remaining-1;
            end
        end
    end
endmodule
