`timescale 1ns/1ps
// Blocking, direct-mapped cache. All addresses are BYTE addresses.
// CPU requests must be aligned 32-bit words. Write-through/no-write-allocate.
module direct_mapped_cache #(
    parameter ADDRESS_BITS = 32,
    parameter CACHE_BYTES = 1024,
    parameter BLOCK_BYTES = 16
)(
    input wire clk, input wire reset,
    input wire cpu_req_valid, output wire cpu_req_ready,
    input wire cpu_req_write,
    input wire [ADDRESS_BITS-1:0] cpu_req_addr,
    input wire [31:0] cpu_req_wdata,
    output wire cpu_rsp_valid, input wire cpu_rsp_ready,
    output wire [31:0] cpu_rsp_rdata, output wire cpu_rsp_hit,
    output wire mem_req_valid, input wire mem_req_ready,
    output wire mem_req_write,
    output wire [ADDRESS_BITS-1:0] mem_req_addr,
    output wire [31:0] mem_req_wdata,
    input wire mem_rsp_valid, input wire [31:0] mem_rsp_rdata,
    output reg hit_event, output reg miss_event
);
    localparam LINES = CACHE_BYTES / BLOCK_BYTES;
    localparam WORDS = BLOCK_BYTES / 4;
    localparam OFFSET_BITS = $clog2(BLOCK_BYTES);
    localparam INDEX_BITS = $clog2(LINES);
    localparam WORD_BITS = $clog2(WORDS);
    localparam TAG_BITS = ADDRESS_BITS - OFFSET_BITS - INDEX_BITS;
    localparam IDLE=0, LOOKUP=1, REFILL_REQ=2, REFILL_WAIT=3,
               WRITE_REQ=4, WRITE_WAIT=5, RESPONSE=6;
    reg [2:0] state;
    reg [ADDRESS_BITS-1:0] addr_q;
    reg [31:0] wdata_q, rdata_q;
    reg write_q, hit_q;
    reg [WORD_BITS-1:0] refill_word;
    wire [INDEX_BITS-1:0] line_index;
    wire [WORD_BITS-1:0] word_offset;
    wire [TAG_BITS-1:0] address_tag, stored_tag;
    wire [ADDRESS_BITS-1:0] block_base;
    wire line_valid, lookup_hit;
    wire [31:0] ram_read_data;
    wire read_miss = state == LOOKUP && !write_q && !lookup_hit;
    wire install_line = state == REFILL_WAIT && mem_rsp_valid && refill_word == WORDS-1;
    wire write_hit = state == LOOKUP && write_q && lookup_hit;
    wire refill_write = state == REFILL_WAIT && mem_rsp_valid;
    wire [INDEX_BITS+WORD_BITS-1:0] ram_read_addr = state == IDLE
        ? cpu_req_addr[2 +: INDEX_BITS+WORD_BITS]
        : addr_q[2 +: INDEX_BITS+WORD_BITS];
    wire [INDEX_BITS+WORD_BITS-1:0] ram_write_addr =
        {line_index, refill_write ? refill_word : word_offset};
    cache_address_decoder #(.ADDRESS_BITS(ADDRESS_BITS), .OFFSET_BITS(OFFSET_BITS),
        .INDEX_BITS(INDEX_BITS), .WORD_BITS(WORD_BITS), .TAG_BITS(TAG_BITS)) decoder(
        .address(addr_q), .index(line_index), .word_offset(word_offset),
        .tag(address_tag), .block_base(block_base));
    cache_metadata #(.LINES(LINES), .INDEX_BITS(INDEX_BITS), .TAG_BITS(TAG_BITS)) metadata(
        .clk(clk), .reset(reset), .index(line_index), .stored_tag(stored_tag),
        .line_valid(line_valid), .invalidate(read_miss), .install(install_line), .new_tag(address_tag));
    cache_tag_comparator #(.TAG_BITS(TAG_BITS)) comparator(
        .valid(line_valid), .stored_tag(stored_tag), .request_tag(address_tag), .hit(lookup_hit));
    cache_data_ram #(.WORD_COUNT(LINES*WORDS), .ADDR_BITS(INDEX_BITS+WORD_BITS)) data_store(
        .clk(clk), .read_addr(ram_read_addr), .read_data(ram_read_data),
        .write_enable(!reset && (write_hit || refill_write)), .write_addr(ram_write_addr),
        .write_data(refill_write ? mem_rsp_rdata : wdata_q));
    assign cpu_req_ready = !reset && state == IDLE;
    assign cpu_rsp_valid = !reset && state == RESPONSE;
    assign cpu_rsp_rdata = rdata_q;
    assign cpu_rsp_hit = hit_q;
    assign mem_req_valid = !reset && (state == REFILL_REQ || state == WRITE_REQ);
    assign mem_req_write = state == WRITE_REQ;
    assign mem_req_addr = state == WRITE_REQ ? addr_q : block_base + (refill_word * 4);
    assign mem_req_wdata = wdata_q;
    always @(posedge clk) begin
        if (reset) begin
            state <= IDLE;
            addr_q <= 0; wdata_q <= 0; rdata_q <= 0;
            write_q <= 0; hit_q <= 0; refill_word <= 0;
            hit_event <= 0; miss_event <= 0;
            // Metadata owns reset invalidation; data RAM needs no reset.
        end else begin
            hit_event <= 0; miss_event <= 0;
            case (state)
                IDLE: if (cpu_req_valid && cpu_req_ready) begin
                    addr_q <= cpu_req_addr; wdata_q <= cpu_req_wdata;
                    write_q <= cpu_req_write; state <= LOOKUP;
                end
                LOOKUP: begin
                    hit_q <= lookup_hit;
                    hit_event <= lookup_hit; miss_event <= !lookup_hit;
                    if (write_q) begin
                        rdata_q <= 0;
                        state <= WRITE_REQ;
                    end else if (lookup_hit) begin
                        rdata_q <= ram_read_data;
                        state <= RESPONSE;
                    end else begin
                        refill_word <= 0; state <= REFILL_REQ;
                    end
                end
                REFILL_REQ: if (mem_req_valid && mem_req_ready) state <= REFILL_WAIT;
                REFILL_WAIT: if (mem_rsp_valid) begin
                    if (refill_word == word_offset) rdata_q <= mem_rsp_rdata;
                    if (refill_word == WORDS-1) begin
                        state <= RESPONSE;
                    end else begin
                        refill_word <= refill_word + 1'b1; state <= REFILL_REQ;
                    end
                end
                WRITE_REQ: if (mem_req_valid && mem_req_ready) state <= WRITE_WAIT;
                WRITE_WAIT: if (mem_rsp_valid) state <= RESPONSE;
                RESPONSE: if (cpu_rsp_ready) state <= IDLE;
                default: state <= IDLE;
            endcase
        end
    end
endmodule
