`timescale 1ns/1ps
module cache_tb;
    parameter CACHE_BYTES=1024, BLOCK_BYTES=16;
    reg clk=0; always #5 clk=~clk;
    reg reset=1, req_valid=0, req_write=0, rsp_ready=0;
    reg [31:0] req_addr=0, req_wdata=0;
    wire req_ready, rsp_valid, rsp_hit;
    wire [31:0] rsp_data;
    wire mv, mr, mw, rv, he, me;
    wire [31:0] ma, md, rd;
    direct_mapped_cache #(.CACHE_BYTES(CACHE_BYTES), .BLOCK_BYTES(BLOCK_BYTES)) dut(
        .clk(clk), .reset(reset), .cpu_req_valid(req_valid), .cpu_req_ready(req_ready),
        .cpu_req_write(req_write), .cpu_req_addr(req_addr), .cpu_req_wdata(req_wdata),
        .cpu_rsp_valid(rsp_valid), .cpu_rsp_ready(rsp_ready), .cpu_rsp_rdata(rsp_data),
        .cpu_rsp_hit(rsp_hit), .mem_req_valid(mv), .mem_req_ready(mr),
        .mem_req_write(mw), .mem_req_addr(ma), .mem_req_wdata(md),
        .mem_rsp_valid(rv), .mem_rsp_rdata(rd), .hit_event(he), .miss_event(me));
    main_memory mem(.clk(clk), .reset(reset), .req_valid(mv), .req_ready(mr),
        .req_write(mw), .req_addr(ma), .req_wdata(md), .rsp_valid(rv), .rsp_rdata(rd));
    reg [31:0] reference [0:16383];
    integer tags [0:1023];
    reg valids [0:1023];
    integer cycle=0, hits=0, misses=0, mem_reads=0, mem_writes=0;
    integer hit_events=0, miss_events=0;
    integer fd, out, rc, op, index, tag_value, expected_hit, start_cycle, n=0, i;
    reg [31:0] address, value, expected_data;
    reg [1023:0] trace_path, result_path, wave_path;
    reg prev_mem_stall=0, prev_rsp_stall=0;
    reg [64:0] held_mem;
    reg [32:0] held_rsp;
    always @(posedge clk) begin
        cycle <= cycle+1;
        if (reset) begin
            prev_mem_stall <= 0; prev_rsp_stall <= 0;
        end else begin
            if (prev_mem_stall && (!mv || {mw,ma,md} !== held_mem))
                $fatal(1,"Memory request changed under backpressure");
            if (prev_rsp_stall && (!rsp_valid || {rsp_hit,rsp_data} !== held_rsp))
                $fatal(1,"CPU response changed under backpressure");
            prev_mem_stall <= mv && !mr; held_mem <= {mw,ma,md};
            prev_rsp_stall <= rsp_valid && !rsp_ready; held_rsp <= {rsp_hit,rsp_data};
            if (he) hit_events <= hit_events+1;
            if (me) miss_events <= miss_events+1;
            if (mv && mr) begin
                if (mw) mem_writes <= mem_writes+1;
                else mem_reads <= mem_reads+1;
            end
        end
    end
    // Alternate response availability to exercise response holding.
    always @(negedge clk) rsp_ready = !reset && cycle % 5 == 0;
    initial begin
        if (!$value$plusargs("TRACE=%s",trace_path)) trace_path="traces/directed.trace";
        if (!$value$plusargs("RESULT=%s",result_path)) result_path="results/directed.csv";
        if ($value$plusargs("VCD=%s",wave_path)) begin
            $dumpfile(wave_path); $dumpvars(0,cache_tb);
        end
        fd=$fopen(trace_path,"r"); out=$fopen(result_path,"w");
        if (!fd || !out) $fatal(1,"Cannot open trace/result file");
        $fdisplay(out,"request,op,address,data,hit,latency_cycles");
        for (i=0;i<16384;i=i+1) reference[i]=32'hA5A50000 ^ i;
        for (i=0;i<1024;i=i+1) begin tags[i]=0; valids[i]=0; end
        repeat (3) @(negedge clk);
        reset=0;
        while (!$feof(fd)) begin
            rc=$fscanf(fd,"%d %h %h\n",op,address,value);
            if (rc != 3) $fatal(1,"Malformed trace");
            if ((op != 0 && op != 1) || address[1:0] || address >= 65536)
                $fatal(1,"Unsupported trace request");
            index=(address/BLOCK_BYTES) % (CACHE_BYTES/BLOCK_BYTES);
            tag_value=address/CACHE_BYTES;
            expected_hit=valids[index] && tags[index]==tag_value;
            expected_data=op ? 0 : reference[address/4];
            if (!op && !expected_hit) begin valids[index]=1; tags[index]=tag_value; end
            if (op) reference[address/4]=value;
            @(negedge clk);
            req_valid=1; req_write=op; req_addr=address; req_wdata=value;
            @(posedge clk);
            while (!req_ready) @(posedge clk);
            start_cycle=cycle;
            @(negedge clk); req_valid=0;
            @(posedge clk);
            while (!(rsp_valid && rsp_ready)) @(posedge clk);
            if (rsp_data !== expected_data || rsp_hit !== (expected_hit != 0))
                $fatal(1,"Request %0d addr=%h: data=%h expected=%h hit=%b expected=%0d",
                    n,address,rsp_data,expected_data,rsp_hit,expected_hit);
            if (rsp_hit) hits=hits+1; else misses=misses+1;
            $fdisplay(out,"%0d,%0d,%08h,%08h,%0d,%0d",n,op,address,rsp_data,rsp_hit,cycle-start_cycle);
            n=n+1;
        end
        @(negedge clk);
        // Verify every backing-memory word, including all write-through updates.
        for (i=0;i<16384;i=i+1)
            if (mem.words[i] !== reference[i]) $fatal(1,"Backing memory mismatch at %0d",i);
        if (hits != hit_events || misses != miss_events) $fatal(1,"Event count mismatch");
        $display("PASS requests=%0d hits=%0d misses=%0d memory_reads=%0d memory_writes=%0d",n,hits,misses,mem_reads,mem_writes);
        $fclose(fd); $fclose(out); $finish;
    end
    initial begin #20000000; $fatal(1,"Simulation timeout"); end
endmodule
