`timescale 1ns/1ps
// Reset aborts an outstanding transaction; CPU and memory share reset.
module reset_tb;
    reg clk=0; always #5 clk=~clk;
    reg reset=1, cv=0, cw=0, cr=1;
    reg [31:0] ca=0, cd=0;
    wire cq, sv, sh, mv, mq, mw, mr, he, me;
    wire [31:0] sd, ma, md, mrd;
    direct_mapped_cache dut(.clk(clk),.reset(reset),
        .cpu_req_valid(cv),.cpu_req_ready(cq),.cpu_req_write(cw),
        .cpu_req_addr(ca),.cpu_req_wdata(cd),.cpu_rsp_valid(sv),
        .cpu_rsp_ready(cr),.cpu_rsp_rdata(sd),.cpu_rsp_hit(sh),
        .mem_req_valid(mv),.mem_req_ready(mq),.mem_req_write(mw),
        .mem_req_addr(ma),.mem_req_wdata(md),.mem_rsp_valid(mr),
        .mem_rsp_rdata(mrd),.hit_event(he),.miss_event(me));
    main_memory mem(.clk(clk),.reset(reset),.req_valid(mv),.req_ready(mq),
        .req_write(mw),.req_addr(ma),.req_wdata(md),.rsp_valid(mr),.rsp_rdata(mrd));
    task pulse_reset;
        begin
            @(negedge clk); reset=1; cv=0;
            repeat (2) @(negedge clk);
            if (sv || mv || cq) $fatal(1,"Interface active during reset");
            reset=0;
        end
    endtask
    task issue_read;
        input [31:0] address;
        begin
            @(negedge clk); cv=1; cw=0; ca=address;
            @(posedge clk); while (!cq) @(posedge clk);
            @(negedge clk); cv=0;
        end
    endtask
    task expect_read;
        input expected_hit;
        begin
            @(posedge clk); while (!sv) @(posedge clk);
            if (sh !== expected_hit || sd !== (32'hA5A50000 ^ (ca/4)))
                $fatal(1,"Bad response after reset");
            @(negedge clk);
        end
    endtask
    initial begin
        pulse_reset;
        issue_read(0); expect_read(0);
        issue_read(4); expect_read(1);
        pulse_reset;
        issue_read(4); expect_read(0); // Warm line must become invalid.
        issue_read(1024);
        wait (dut.state == 3); // Abort during an outstanding refill word.
        pulse_reset;
        repeat (12) begin
            @(negedge clk);
            if (sv) $fatal(1,"Stale response after reset");
        end
        issue_read(1024); expect_read(0);
        cr=0;
        issue_read(1028);
        wait(sv);
        repeat (3) @(negedge clk);
        pulse_reset; // Abort a held CPU response.
        cr=1;
        issue_read(1028); expect_read(0);
        $display("PASS reset: cold start, warm invalidation, refill abort, response abort");
        $finish;
    end
    initial begin #100000; $fatal(1,"Reset test timeout"); end
endmodule
