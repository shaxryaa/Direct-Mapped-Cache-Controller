`timescale 1ns/1ps
module cache_tag_comparator #(parameter TAG_BITS=22)(
    input wire valid,
    input wire [TAG_BITS-1:0] stored_tag, request_tag,
    output wire hit
);
    assign hit = valid && stored_tag == request_tag;
endmodule
