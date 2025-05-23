/*
*  bowtie modules and workflows
*/

/*
 * Bowtie index
 */
process bowtieIdx {
    container "quay.io/biocontainers/bowtie:1.2.3--py37hc9558a2_0"
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
 * Bowtie alignment
 */
process bowtieAln {
    publishDir("bowtie_output", pattern: '*.sam')
    container "quay.io/biocontainers/bowtie:1.2.3--py37hc9558a2_0"
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

workflow BOWTIE {
 
    take: 
    reffile
    input
    
    main:
		bow_index = bowtieIdx(reffile)
		bowtieAln(bow_index, input)
    emit:
    	sam = bowtieAln.out.samples_sam
    	logs = bowtieAln.out.samples_log
}



