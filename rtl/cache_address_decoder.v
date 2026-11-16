`timescale 1ns/1ps
module cache_address_decoder #(
    parameter ADDRESS_BITS=32, OFFSET_BITS=4, INDEX_BITS=6,
    WORD_BITS=2, TAG_BITS=22
)(
    input wire [ADDRESS_BITS-1:0] address,
    output wire [INDEX_BITS-1:0] index,
    output wire [WORD_BITS-1:0] word_offset,
    output wire [TAG_BITS-1:0] tag,
    output wire [ADDRESS_BITS-1:0] block_base
);
    assign index = address[OFFSET_BITS +: INDEX_BITS];
    assign word_offset = address[2 +: WORD_BITS];
    assign tag = address[ADDRESS_BITS-1 -: TAG_BITS];
    assign block_base = (address >> OFFSET_BITS) << OFFSET_BITS;
endmodule
