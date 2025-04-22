/*
* Let's create the channel `my_files`
* using the method fromPath
*/

Channel
    .fromPath( "*.txt" )
    .set {my_files}

/*
* Let's create the channel `my_words`
* using the method from
*/

Channel
    .from('hello', 'hola', 'bonjour')
    .set {my_words}


/*
* Let's mix them using the operator mix
*/

my_files
    .mix(my_words)
    .toSortedList()
    .flatten()
    .view()
