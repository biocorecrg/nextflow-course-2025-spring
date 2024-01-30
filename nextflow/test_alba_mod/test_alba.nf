#!/usr/bin/env nextflow


/* 
 * This code enables the new dsl of Nextflow. 
 */

nextflow.enable.dsl=2


/* 
 * NextFlow test pipe
 * @authors
 * Luca Cozzuto <lucacozzuto@gmail.com>
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
images                           : ${params.images}
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
output_denoise     = "output_denoise"
output_aggregate   = "output_aggregate"

include { denoise } from "${baseDir}/modules/denoise" addParams(OUTPUT: output_denoise, LABEL:"twocpus")
include { normalize } from "${baseDir}/modules/normalize"
include { aggregate } from "${baseDir}/modules/aggregate" addParams(OUTPUT: output_aggregate)


/* Reading the file list and creating a "Channel": a queue that connects different channels.
 * The queue is consumed by channels, so you cannot re-use a channel for different processes. 
 * If you need the same data for different processes you need to make more channels.
 */
 
Channel
    .fromFilePairs( params.images, size:1 , checkIfExists: true)  											 
    .set {images} 			                								 


workflow {

	// HERE WE DO DENOISING 
	denois_out = denoise(images)
	// HERE WE JOIN DENOISE OUTPUT WITH ORIGINAL IMAGES JUST FOR PRINTING PURPOSES
    images.join(denois_out).view()
    // HERE WE RUN NORMALIZE 
	normalized_out = normalize(images.join(denois_out))
	aggregate(normalized_out.collect())
}


workflow.onComplete { 
	println ( workflow.success ? "\nDone! The results are in --> ${output_aggregate}\n" : "Oops .. something went wrong" )
}


