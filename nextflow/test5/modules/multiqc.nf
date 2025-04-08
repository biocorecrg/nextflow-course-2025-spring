/*
*  multiqc module
*/

process multiqc {
    publishDir("multiqc_output", mode: 'copy')
    container "quay.io/biocontainers/multiqc:1.9--pyh9f0ad1d_0"

    input:
    path (inputfiles)

    output:
    path "multiqc_report.html"

    script:
    """
	    multiqc .
    """
}
