/* 
 * Creates a channel emitting some string values
 */
 
str = Channel.from('hello', 'hola', 'bonjour')

/*
 * Creates a process which receive an input channel containing values
 * Each value emitted by the channel triggers the execution 
 * of the process. The process stdout is caputured and send over 
 * the another channel. 
 */

process printHello {
    
    input:
    val str_in

    output: 
    stdout
    
    script:
    """
    echo ${str_in} in Italian is ciao 
    """
}

/*
 * A workflow consist of a number of invocations of processes
 * where they are fed with the expected input channels 
 * as they were cutom functions. You can only invoke once a process per workflow.
 */

workflow {
    result = printHello(str)
    result.view()
}
 
