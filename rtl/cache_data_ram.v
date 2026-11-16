`timescale 1ns/1ps
// Single-clock RAM with independent synchronous read and write ports.
// No array reset: valid bits in cache_metadata hide uninitialized lines.
module cache_data_ram #(parameter WORD_COUNT=256, parameter ADDR_BITS=8)(
    input wire clk,
    input wire [ADDR_BITS-1:0] read_addr,
    output reg [31:0] read_data,
    input wire write_enable,
    input wire [ADDR_BITS-1:0] write_addr,
    input wire [31:0] write_data
);
    reg [31:0] words [0:WORD_COUNT-1];
    always @(posedge clk) begin
        read_data <= words[read_addr];
        if (write_enable) words[write_addr] <= write_data;
    end
endmodule
