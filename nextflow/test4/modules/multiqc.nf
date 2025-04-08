/*
*  multiqc module
*/


process multiqc {
    publishDir("multiqc_output", mode: 'copy')

    input:
    path (inputfiles)

    output:
    path "multiqc_report.html"

    script:
    """
    multiqc .
    """
}
