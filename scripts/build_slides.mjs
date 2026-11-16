import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(path.join(ROOT,'build/entry.cjs'));
const {Presentation,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const SKILL='/Users/shauryasharma/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const PY='/Users/shauryasharma/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const {finalizePresentation,resolvePresentationFont,applyPresentationChartFont}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const font=resolvePresentationFont();
console.log('Font:',font);
const p=Presentation.create({slideSize:{width:1280,height:720}});
const navy='#102B46', teal='#087F8C', gray='#43586C';
function text(s,value,x,y,w,h,size=28,bold=false,color=navy){
 const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=value; t.text.style={fontFamily:font,typeface:font,fontSize:size,bold,color,verticalAlignment:'top'};
 return t;
}
function slide(title,notes=''){
 const s=p.slides.add(); s.background.fill='#F8FAFC';
 text(s,title,70,48,1140,100,44,true);
 text(s,`${p.slides.items.length}`,1170,662,40,24,18,false,gray);
 s.speakerNotes.text=notes; return s;
}
function lines(s,items,y=190){
 items.forEach((item,i)=>text(s,item,80,y+i*91,1110,78,29,false,gray));
}
function table(s,rows,widths,y=190,height=370){
 const t=s.tables.add({rows:rows.length,columns:rows[0].length,left:80,top:y,width:1120,height,
 columnWidths:widths,values:rows});
 for(let r=0;r<rows.length;r++) for(let c=0;c<rows[0].length;c++){
  const cell=t.getCell(r,c); cell.fill=r===0?'#DCECF1':r%2?'#FFFFFF':'#EDF3F7';
  cell.text.style={fontFamily:font,typeface:font,fontSize:25,color:navy,bold:r===0};
 }
 return t;
}
let s=slide('Direct-Mapped Cache Controller', 'Modern Computer Architecture, Project 6. Actual group: Shaurya Sharma and Lakshay Saharan. Sources and measurements accompany this deck.');
text(s,'RTL implementation and access-trace analysis',80,220,1050,90,38,false,teal);
text(s,'1 KB cache   /   16-byte blocks   /   32-bit addresses',80,350,1100,60,30);
text(s,'Shaurya Sharma (2401010439)\nLakshay Saharan (2401020034)',80,485,1000,100,27,false,gray);
s=slide('Cache organization','Data capacity excludes tags and valid bits. The cache has one possible line per block. Reference: https://www.cs.cornell.edu/courses/cs3410/2026sp/notes/caches.html');
table(s,[['Property','Configuration'],['Data capacity','1024 bytes'],['Lines and block size','64 lines, 16 bytes each'],['Access width','32-bit aligned words'],['Write policy','Write-through, no-write-allocate'],['Outstanding CPU requests','One']],[430,690],170,430);
s=slide('Tag, index and offset','Address arithmetic is independently checked in the scoreboards. 0x00000400 is 1024 bytes. Cornell cache notes explain direct mapping.');
for (const [x,label,bits] of [[80,'TAG: 22 bits','[31:10]'],[450,'INDEX: 6 bits','[9:4]'],[820,'OFFSET: 4 bits','[3:0]']]) {
 text(s,label,x,190,350,65,32,true,teal); text(s,bits,x,265,350,60,30);
}
lines(s,['1024 / 16 = 64 lines','Offset = 2 word bits + 2 byte bits','Addresses 0 and 1024 share index 0, with different tags'],365);
s=slide('Controller state transitions','State codes: IDLE=0, LOOKUP=1, REFILL_REQ=2, REFILL_WAIT=3, WRITE_REQ=4, WRITE_WAIT=5, RESPONSE=6. See docs/ARCHITECTURE.md for the complete FSM diagram. Reset takes all states to IDLE.');
table(s,[['Path','State sequence'],['Read hit','IDLE, LOOKUP, RESPONSE'],['Read miss','LOOKUP, REFILL_REQ, REFILL_WAIT'],['More refill words','REFILL_WAIT repeats the request/wait pair'],['Last refill word','Install tag and valid, then RESPONSE'],['Write','LOOKUP, WRITE_REQ, WRITE_WAIT, RESPONSE'],['Response accepted','RESPONSE returns to IDLE']],[320,800],170,450);
s=slide('Write behavior','A write completes only after the memory acknowledgement. A write miss preserves the indexed victim line. Reference: Cornell CS3410 cache notes, https://www.cs.cornell.edu/courses/cs3410/2026sp/notes/caches.html');
table(s,[['Request','Cache action','Memory action'],['Write hit','Update selected word','Write the same word'],['Write miss','Preserve current line','Write without refill']],[250,420,450],190,230);
text(s,'Every write waits for acknowledgement before responding.',80,470,1100,90,31,false,gray);
text(s,'Dirty bits and write-back eviction are unnecessary.',80,565,1100,60,29,false,teal);
s=slide('Verification evidence','Sources: results/run.log, results/reset.log, transaction CSVs and scripts/analyze.py. Both scoreboards independently derive tags/data. Tests are scenario-based evidence, not formal exhaustive proof.');
lines(s,['18,504 checked transactions: RTL, baseline and FPGA netlist','Eight workloads, including conflicts and mixed reads/writes','Independent Verilog and Python reference models','Memory stalls and CPU response backpressure','Reset during refill and during a held response'],165);
s=slide('Locality determines the hit rate','Exact rates from results/summary.json for the default 1024-byte cache and 16-byte block. Repeated: 496/512. Sequential: 768/1024. Random: 14/1024. Conflict: 0/256. All four plotted traces contain only reads.');
const results=JSON.parse(await fs.readFile(path.join(ROOT,'results/summary.json'),'utf8'));
const names=['repeated','sequential','random','conflict'];
const c=s.charts.add('bar',{position:{left:95,top:180,width:1090,height:390},
 categories:['Repeated','Sequential','Random','Conflict'],
 series:[{name:'Hit rate',values:names.map(n=>results.find(r=>r.workload===n).hit_rate),fill:teal}],
 hasLegend:false,barOptions:{direction:'column'},
 yAxis:{min:0,max:1,majorUnit:0.2,numberFormatCode:'0%',textStyle:{fontSize:23}},
 xAxis:{textStyle:{fontSize:25}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00%',textStyle:{fontSize:24}},
 chartFill:'#F8FAFC',plotAreaFill:'#F8FAFC'});
applyPresentationChartFont(c,{fontFamily:font});
text(s,'1 KB cache, 16-byte blocks. Results from the included simulations.',100,602,1080,45,23,false,gray);
s=slide('AMAT and response latency','Ideal read hit=2 cycles. Each serial refill word adds 7 cycles with a 5-cycle memory model. Read miss=30 cycles. Write=9 cycles. Real measurements also include memory acceptance stalls and CPU response backpressure. Source: docs/REPORT.md and results/summary.json.');
text(s,'AMAT for reads = 2 + miss rate x 28 cycles',80,170,1120,70,34,true,teal);
table(s,[['Workload','Ideal AMAT','Measured response'],...['repeated','sequential','conflict'].map(n=>{
 const r=results.find(r=>r.workload===n); return [n,`${r.ideal_amat_cycles.toFixed(3)} cycles`,`${r.measured_response_cycles.toFixed(3)} cycles`];
})],[360,360,400],285,260);
text(s,'Measured time includes interface stalls. It excludes driver idle gaps.',80,590,1120,60,25,false,gray);
s=slide('Reference FPGA implementation','Source: results/fpga_summary.json. iCE40 HX8K, CT256, seed 1, 25 MHz target. Internal post-route timing estimate with automatic IO placement and no external delay constraints. No board programming was performed.');
text(s,'75.35 MHz',80,180,900,120,82,true,teal);
text(s,'estimated post-route internal Fmax',80,305,1050,60,32);
lines(s,['610 / 7680 logic cells and 4 / 32 RAM blocks','25 MHz target met; all 206 package IOs used','Reference build with automatic IO placement, no board test'],420);
s=slide('Demonstration and extensions','Run python3 scripts/run.py. Open results/directed.vcd in a waveform viewer. Follow docs/DEMO_AND_VIVA.md. Proposed extensions are future work, not implemented features.');
lines(s,['Run: python3 scripts/run.py','Repeated reads: 1.826x faster than the no-cache baseline','Explain write-through and no-write-allocate using the trace','Extensions: write buffer, burst refill or set associativity'],180);
text(s,'Current scope: one request at a time, aligned words, shared reset.',80,580,1120,60,25,false,teal);
await fs.mkdir(path.join(ROOT,'build/slides'),{recursive:true});
for(const [i,sl] of p.slides.items.entries()){
 const blob=await p.export({slide:sl,format:'png',scale:1});
 await fs.writeFile(path.join(ROOT,`build/slides/slide-${i+1}.png`),new Uint8Array(await blob.arrayBuffer()));
}
const candidatePath=path.join(ROOT,'build/slides/candidate-rubric.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(ROOT,'output/presentation/Cache_Controller_Rubric_Slides.pptx');
const done=await finalizePresentation({workspaceDir:ROOT,candidatePath,finalPath,pythonExecutable:PY,
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...[2,4,5,8].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[2,4,5,8],requiredNativeChartOwnerSlides:[7],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[font]},
 verifyArtifactToolImport:true,receiptPath:path.join(ROOT,'build/slides/validation-rubric.json')});
console.log(JSON.stringify(done));
