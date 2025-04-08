/*
*  fastqc module
*/

process fastqc {
    publishDir('fastqc_output', mode: 'copy')
    tag { "${reads}" }
    container 'quay.io/biocontainers/fastqc:0.11.9--0'

    input:
    path(reads)

    output:
    path("*_fastqc*")

    script:
    """
        fastqc -t ${task.cpus} ${reads}
    """
}
