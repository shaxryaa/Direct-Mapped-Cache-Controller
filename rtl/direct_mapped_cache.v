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
    reg [31:0] data_ram [0:LINES*WORDS-1];
    reg [TAG_BITS-1:0] tag_ram [0:LINES-1];
    reg valid_ram [0:LINES-1];
    reg [ADDRESS_BITS-1:0] addr_q;
    reg [31:0] wdata_q, rdata_q;
    reg write_q, hit_q;
    reg [WORD_BITS-1:0] refill_word;
    wire [INDEX_BITS-1:0] line_index = addr_q[OFFSET_BITS +: INDEX_BITS];
    wire [WORD_BITS-1:0] word_offset = addr_q[2 +: WORD_BITS];
    wire [TAG_BITS-1:0] address_tag = addr_q[ADDRESS_BITS-1 -: TAG_BITS];
    wire lookup_hit = valid_ram[line_index] && tag_ram[line_index] == address_tag;
    wire [ADDRESS_BITS-1:0] block_base = (addr_q >> OFFSET_BITS) << OFFSET_BITS;
    integer i;
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
            // Tags/data need no reset: valid bits hide uninitialized storage.
            for (i=0; i<LINES; i=i+1) valid_ram[i] <= 0;
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
                        if (lookup_hit) data_ram[line_index*WORDS+word_offset] <= wdata_q;
                        rdata_q <= 0;
                        state <= WRITE_REQ;
                    end else if (lookup_hit) begin
                        rdata_q <= data_ram[line_index*WORDS+word_offset];
                        state <= RESPONSE;
                    end else begin
                        valid_ram[line_index] <= 0;
                        refill_word <= 0; state <= REFILL_REQ;
                    end
                end
                REFILL_REQ: if (mem_req_valid && mem_req_ready) state <= REFILL_WAIT;
                REFILL_WAIT: if (mem_rsp_valid) begin
                    data_ram[line_index*WORDS+refill_word] <= mem_rsp_rdata;
                    if (refill_word == word_offset) rdata_q <= mem_rsp_rdata;
                    if (refill_word == WORDS-1) begin
                        tag_ram[line_index] <= address_tag;
                        valid_ram[line_index] <= 1;
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
