`timescale 1ns/1ps
module cache_metadata #(parameter LINES=64, INDEX_BITS=6, TAG_BITS=22)(
    input wire clk, input wire reset,
    input wire [INDEX_BITS-1:0] index,
    output wire [TAG_BITS-1:0] stored_tag,
    output wire line_valid,
    input wire invalidate,
    input wire install,
    input wire [TAG_BITS-1:0] new_tag
);
    reg [TAG_BITS-1:0] tags [0:LINES-1];
    reg valids [0:LINES-1];
    integer i;
    assign stored_tag = tags[index];
    assign line_valid = valids[index];
    always @(posedge clk) begin
        if (reset) begin
            for (i=0;i<LINES;i=i+1) valids[i] <= 0;
        end else begin
            if (invalidate) valids[index] <= 0;
            if (install) begin tags[index] <= new_tag; valids[index] <= 1; end
        end
    end
endmodule
