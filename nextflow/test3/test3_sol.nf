/* 
 * NextFlow test pipe
 * @authors
 * Luca Cozzuto <luca.cozzuto@crg.eu>
 * 
 */

/*
 * Input parameters: read pairs
 * Params are stored in the params.config file
 */

version                 = "1.0"
// this prevents a warning of undefined parameter
params.help             = false

// this prints the input parameters
log.info """
BIOCORE@CRG - N F TESTPIPE  ~  version ${version}
=============================================
reads                           : ${params.reads}
reference                       : ${params.reference}
"""

// this prints the help in case you use --help parameter in the command line and it stops the pipeline
if (params.help) {
    log.info 'This is the Biocore\'s NF test pipeline'
    log.info 'Enjoy!'
    log.info '\n'
    exit 1
}

/*
 * Defining the output folders.
 */
fastqcOutputFolder    = "ouptut_fastqc"
alnOutputFolder       = "ouptut_aln"
multiqcOutputFolder   = "ouptut_multiQC"


/* Reading the file list and creating a "Channel": a queue that connects different channels.
 * The queue is consumed by channels, so you cannot re-use a channel for different processes. 
 * If you need the same data for different processes you need to make more channels.
 */
 
Channel
    .fromPath( params.reads )  											 
    .ifEmpty { error "Cannot find any reads matching: ${params.reads}" } 
    .set {reads} 											 

reference = file(params.reference)
multiconf = file("config.yaml")

/*
 * Process 1. Run FastQC on raw data. A process is the element for executing scripts / programs etc.
 */
process fastQC {
    publishDir fastqcOutputFolder  			
    tag { "${reads}" }  							

    input:
    path reads   							

    output:									
   	path "*_fastqc.*"

    script:									
    """
        fastqc ${reads} 
    """
}

/*
 * Process 2. Bowtie index
 */
process bowtieIdx {
    tag { "${ref}" }  							

    input:
    path ref   							

    output:									
   	tuple val("${ref}"), path ("${ref}*.ebwt")

    script:									
    """
        gunzip -c ${ref} > reference.fa
        bowtie-build reference.fa ${ref}
        rm reference.fa
    """
}

/*
 * Process 3. Bowtie alignment
 */
process bowtieAln {
    publishDir alnOutputFolder, pattern: '*.sam'

    tag { "${reads}" }  							
    label 'twocpus' 

    input:
    tuple val(refname), path (ref_files)
    path reads  							

    output:									
    path "${reads}.sam", emit: samples_sam
    path "${reads}.log", emit: samples_log

    script:									
    """
    bowtie -p ${task.cpus} ${refname} -q ${reads} -S > ${reads}.sam 2> ${reads}.log
    """
}

/*
 * Process 4. Run multiQC on fastQC results
 */
process multiQC {
    publishDir multiqcOutputFolder, mode: 'copy' 	// this time do not link but copy the output file

    input:
	path (multiconf)
    path (inputfiles)
	
    output:
    path("multiqc_report.html") 					

    script:
    """
    multiqc . -c ${multiconf}
    """
}

/*
 * First workflow. They are like mini-pipelines:
 * take: receive inputs from channels
 * main: execute processes and / or operators
 * emit: emit outputs
 */

workflow flow1 {
	// expecting two inputs
    take: 
    reads
    ref
    
    // executing the processes fastQC, bowtieIdx and bowtieAln
    main:
	fastqc_out    = fastQC(reads)
	bowtie_index  = bowtieIdx(ref)
	bowtieAln(bowtie_index, reads)
	
	// emitting three outputs defined as aln_sams, aln_logs and fastqc_out
	emit:
	aln_sams      = bowtieAln.out.samples_sam
	aln_logs      = bowtieAln.out.samples_log
	fastqc_out    = fastqc_out
}


/*
 * Second workflow. It just run fastQC 
 * not really useful, just for example
 * it allows reusing fastQC in a different context
 */

workflow flow2 {
    // expecting one input
    take: alns
    
    // performing just fastqc
    main:
	fastqc_out2 = fastQC(alns)
	
	emit:
	fastqc_out2
}

/*
 * Main workflow. It runs both named workflows.
 * The output of each named workflows can be accessed using the "out" variable + the names defined in 
 * the emit sections
 */
 
workflow {
    flow1(reads, reference)
    
    flow2(flow1.out.sam)
    
    // collecting data for multiqc
    data_for_multiqc = flow1.out.fastqc_out.mix(flow1.out.aln_logs).mix(flow2.out.fastqc_out2).collect()
    
 	multiQC(multiconf, data_for_multiqc)
}


workflow.onComplete { 
	println ( workflow.success ? "\nDone! Open the following report in your browser --> ${multiqcOutputFolder}/multiqc_report.html\n" : "Oops .. something went wrong" )
}


