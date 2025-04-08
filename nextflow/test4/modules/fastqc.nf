/*
*  fastqc module
*/

process fastqc {
    tag { "${reads}" }

    publishDir("fastqc_out", mode: 'copy')
    container "quay.io/biocontainers/fastqc:0.11.9--0"
    label 'onecpu'

    input:
    path(reads)

    output:
    path("*_fastqc*")

    script:
    """
        fastqc -t ${task.cpus} ${reads}
    """
}
