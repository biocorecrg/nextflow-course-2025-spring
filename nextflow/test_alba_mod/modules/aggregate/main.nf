/*
*  aggregate module
*/

params.OUTPUT = ""

process aggregate {
    publishDir params.OUTPUT, mode: 'copy' 	
    
    input:
    path (inputfiles)

    output:
    path("*") 					

    script:
    """
    step3_aggregate_and_save.py ./
    """
}