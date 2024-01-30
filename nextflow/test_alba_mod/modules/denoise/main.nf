/*
*  denoise module
*/

params.OUTPUT = ""
params.LABEL = ""

/*
 * Process 1. De-noise input image
 */
process denoise {
    publishDir(params.OUTPUT)

    tag { "${image}" }  				
    label (params.LABEL)

    input:
    tuple val(id), path (image)   						

    output:								
   	tuple val(id), path("*_den.npy")

    script:								
    """
		step1_denoise.py ${image}
    """
}

