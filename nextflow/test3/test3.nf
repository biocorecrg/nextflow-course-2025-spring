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
outdir                          : ${params.outdir}
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
fastqcOutputFolder    = "${params.outdir}/ouptut_fastqc"
alnOutputFolder       = "${params.outdir}/ouptut_aln"
multiqcOutputFolder   = "${params.outdir}/ouptut_multiQC"


/* Reading the file list and creating a "Channel": a queue that connects different channels.
 * The queue is consumed by channels, so you cannot re-use a channel for different processes. 
 * If you need the same data for different processes you need to make more channels.
 */
 
Channel
    .fromPath( params.reads )  											 
    .ifEmpty { error "Cannot find any reads matching: ${params.reads}" } 
    .set {reads} 											 

reference = file(params.reference)

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

/*
 * Process 4. Run multiQC on fastQC results
 */
process multiQC {
    publishDir multiqcOutputFolder, mode: 'copy' 	// this time do not link but copy the output file

    input:
    path (inputfiles)

    output:
    path("multiqc_report.html") 					

    script:
    """
    multiqc .
    """
}

workflow {
    reads.view()
	fastqc_out = fastQC(reads)
	bowtie_index = bowtieIdx(reference)
	bowtieAln(bowtie_index, reads)
	
	multiQC(fastqc_out.mix(bowtieAln.out.samples_log).collect())
}


workflow.onComplete { 
	println ( workflow.success ? "\nDone! Open the following report in your browser --> ${multiqcOutputFolder}/multiqc_report.html\n" : "Oops .. something went wrong" )
}


