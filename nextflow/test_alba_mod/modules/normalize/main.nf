/*
*  normalize module
*/

process normalize {

    tag { "${image}" }  				

    input:
    tuple val(id), path(image), path(denoised)    	// WE NEED THE IMAGE TO BE THERE BUT NOT IN THE COMMAND LINE					

    output:								
    path("*_den_norm.npy")

    script:								
    """
		step2_normalize.py ${denoised}
    """
}
