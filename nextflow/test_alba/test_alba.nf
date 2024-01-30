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
output_denoise     = "ouptut_denoise"
output_aggregate   = "output_aggregate"


/* Reading the file list and creating a "Channel": a queue that connects different channels.
 * The queue is consumed by channels, so you cannot re-use a channel for different processes. 
 * If you need the same data for different processes you need to make more channels.
 */
 
Channel
    .fromFilePairs( params.images, size:1 , checkIfExists: true)  											 
    .set {images} 			                								 


/*
 * Process 1. De-noise input image
 */
process denoise {
    publishDir output_denoise  			

    tag { "${image}" }  				
    label 'big_mem' 

    input:
    tuple val(id), path (image)   						

    output:								
   	tuple val(id), path("*_den.npy")

    script:								
    """
		step1_denoise.py ${image}
    """
}

/*
 * Process 1. Normalise the de-noise image
 */
process normalize {

    tag { "${image}" }  				
    label 'big_mem' 

    input:
    tuple val(id), path(image), path(denoised)    	// WE NEED THE IMAGE TO BE THERE BUT NOT IN THE COMMAND LINE					

    output:								
    path("*_den_norm.npy")

    script:								
    """
		step2_normalize.py ${denoised}
    """
}

/*
 * Process 2. Run multiQC on fastQC results
 */
process aggregate {
    publishDir output_aggregate, mode: 'copy' 	// this time do not link but copy the output file

    input:
    path (inputfiles)

    output:
    path("*") 					// do not send the results to any channel

    script:
    """
    step3_aggregate_and_save.py ./
    """
}

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
	println ( workflow.success ? "\nDone! Open the following report in your browser --> ${multiqcOutputFolder}/multiqc_report.html\n" : "Oops .. something went wrong" )
}


