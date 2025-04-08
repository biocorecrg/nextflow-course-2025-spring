Channel
    .fromPath("{aa,bb,cc}.txt")
    .set {my_files}

my_files
    .collect()
    .view()

// You can also write it as: my_files.collect().view()

my_files
    .combine(my_files)
    .view()

