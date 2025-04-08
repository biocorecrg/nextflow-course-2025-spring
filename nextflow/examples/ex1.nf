// This is a comment

/*
 * This is a block of comments
 */

/* 
* This is a channel creating 
* from string values
*/

str = Channel.from('hello', 'hola', 'bonjour')

/* 
* You can also assign a channel using the set operator
* https://www.nextflow.io/docs/latest/operator.html#set
*/

Channel.from('hello', 'hola', 'bonjour').set{str2}

/*
* The operator view() can be used to view the channel `str`
* https://www.nextflow.io/docs/latest/operator.html#view
*/

str.view()