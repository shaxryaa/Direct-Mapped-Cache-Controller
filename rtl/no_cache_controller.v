`timescale 1ns/1ps
// Baseline with the SAME CPU handshake, lookup stage and memory protocol.
// Every request accesses one memory word; no cache storage or refill.
module no_cache_controller #(
    parameter ADDRESS_BITS=32, CACHE_BYTES=1024, BLOCK_BYTES=16
)(
    input wire clk, reset,
    input wire cpu_req_valid, output wire cpu_req_ready,
    input wire cpu_req_write, input wire [ADDRESS_BITS-1:0] cpu_req_addr,
    input wire [31:0] cpu_req_wdata,
    output wire cpu_rsp_valid, input wire cpu_rsp_ready,
    output wire [31:0] cpu_rsp_rdata, output wire cpu_rsp_hit,
    output wire mem_req_valid, input wire mem_req_ready,
    output wire mem_req_write, output wire [ADDRESS_BITS-1:0] mem_req_addr,
    output wire [31:0] mem_req_wdata,
    input wire mem_rsp_valid, input wire [31:0] mem_rsp_rdata,
    output reg hit_event, miss_event
);
    localparam IDLE=0, LOOKUP=1, REQUEST=2, WAIT=3, RESPONSE=4;
    reg [2:0] state;
    reg write_q;
    reg [ADDRESS_BITS-1:0] addr_q;
    reg [31:0] data_q, response_q;
    assign cpu_req_ready=!reset && state==IDLE;
    assign cpu_rsp_valid=!reset && state==RESPONSE;
    assign cpu_rsp_rdata=response_q;
    assign cpu_rsp_hit=0;
    assign mem_req_valid=!reset && state==REQUEST;
    assign mem_req_addr=addr_q;
    assign mem_req_write=write_q;
    assign mem_req_wdata=data_q;
    always @(posedge clk) begin
        if (reset) begin
            state<=IDLE; write_q<=0; addr_q<=0; data_q<=0;
            response_q<=0; hit_event<=0; miss_event<=0;
        end else begin
            hit_event<=0; miss_event<=0;
            case(state)
                IDLE: if(cpu_req_valid) begin
                    addr_q<=cpu_req_addr; data_q<=cpu_req_wdata;
                    write_q<=cpu_req_write; state<=LOOKUP;
                end
                LOOKUP: begin miss_event<=1; state<=REQUEST; end
                REQUEST: if(mem_req_ready) state<=WAIT;
                WAIT: if(mem_rsp_valid) begin
                    response_q<=write_q ? 0 : mem_rsp_rdata; state<=RESPONSE;
                end
                RESPONSE: if(cpu_rsp_ready) state<=IDLE;
                default: state<=IDLE;
            endcase
        end
    end
endmodule
