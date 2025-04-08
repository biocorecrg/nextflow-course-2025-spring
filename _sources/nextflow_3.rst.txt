.. _nextflow_3-page:

*******************
3 Nextflow
*******************

Decoupling resources, parameters, and Nextflow script
=======================

When making complex pipelines it is convenient to keep the definition of resources needed, the default parameters, and the main script separately from each other.
This can be achieved using two additional files:

- nextflow.config
- params.yaml

The **nextflow.config** file allows you to indicate resources needed for each class of processes.
This is achieved by labeling processes in the `nextflow.config` file:

.. literalinclude:: ../nextflow/test2/nextflow.config
   :language: groovy

The first part defines the "default" resources for a process:

.. literalinclude:: ../nextflow/test2/nextflow.config
   :language: groovy
   :emphasize-lines: 1-4


Then are specified the resources needed for a class of processes labeled **bigmem**. In brief, the default options will be overridden for the processes labeled **bigmem** and **onecpu**:

.. literalinclude:: ../nextflow/test2/nextflow.config
   :language: groovy
   :emphasize-lines: 6-14

.. tip::
	To propagate the errors among different Linux commands, you can add the default configuration for shell executions within the nextflow.config file:
.. code-block:: groovy

	process {
  		shell = ['/bin/bash', '-euo', 'pipefail']
		...

In the script **/test2/test2.nf file**, there are two processes to run two programs:

- `fastQC <https://www.bioinformatics.babraham.ac.uk/projects/fastqc/>`__ - a tool that calculates a number of quality control metrics on single fastq files;
- `multiQC <https://multiqc.info/>`__ - an aggregator of results from bioinformatics tools and samples for generating a single html report.


.. literalinclude:: ../nextflow/test2/test2.nf
   :language: groovy
   :emphasize-lines: 66


You can see that the process **fastQC** is labeled 'bigmem'.


The last two rows of the config file indicate which containers to use.
In this example, -- and by default, if the repository is not specified, -- a container is pulled from the DockerHub.
In the case of using a singularity container, you can indicate where to store the local image using the **singularity.cacheDir** option:

.. code-block:: groovy

	process.container = 'biocorecrg/c4lwg-2018:latest'
	singularity.cacheDir = "$baseDir/singularity"


Let's now launch the script **test2.nf**. We need to specify the params.yaml file with the nextflow parameter `-params-file`

.. code-block:: console
   :emphasize-lines: 42,43

	cd test2;
	nextflow run test2.nf -params-file params.yaml 

	N E X T F L O W  ~  version 20.07.1
	Launching `test2.nf` [distracted_edison] - revision: e3a80b15a2
	BIOCORE@CRG - N F TESTPIPE  ~  version 1.0
	=============================================
	reads                           : /home/ec2-user/git/CRG_Nextflow_Jun_2022/nextflow/nextflow/test2/../testdata/*.fastq.gz
	executor >  local (2)
	[df/2c45f2] process > fastQC (B7_input_s_chr19.fastq.gz) [  0%] 0 of 2
	[-        ] process > multiQC                            -
	Error executing process > 'fastQC (B7_H3K4me1_s_chr19.fastq.gz)'

	Caused by:
	  Process `fastQC (B7_H3K4me1_s_chr19.fastq.gz)` terminated with an error exit status (127)

	Command executed:

	  fastqc B7_H3K4me1_s_chr19.fastq.gz

	Command exit status:
	  127

	executor >  local (2)
	[df/2c45f2] process > fastQC (B7_input_s_chr19.fastq.gz) [100%] 2 of 2, failed: 2 ✘
	[-        ] process > multiQC                            -
	Error executing process > 'fastQC (B7_H3K4me1_s_chr19.fastq.gz)'

	Caused by:
	  Process `fastQC (B7_H3K4me1_s_chr19.fastq.gz)` terminated with an error exit status (127)

	Command executed:

	  fastqc B7_H3K4me1_s_chr19.fastq.gz

	Command exit status:
	  127

	Command output:
	  (empty)

	Command error:
	  .command.sh: line 2: fastqc: command not found

	Work dir:
	  /home/ec2-user/git/CRG_Nextflow_Jun_2022/nextflow/nextflow/test2/work/c5/18e76b2e6ffd64aac2b52e69bedef3

	Tip: when you have fixed the problem you can continue the execution adding the option `-resume` to the run command line


We will get a couple of errors since no executable is found in our environment/path. This is because the executables are stored in our docker image, and we have to tell Nextflow to use the docker image, using the `-with-docker` parameter.


.. code-block:: console
   :emphasize-lines: 1

	nextflow run test2.nf -params-file params.yaml  -with-docker

	N E X T F L O W  ~  version 20.07.1
	Launching `test2.nf` [boring_hamilton] - revision: e3a80b15a2
	BIOCORE@CRG - N F TESTPIPE  ~  version 1.0
	=============================================
	reads                           : /home/ec2-user/git/CRG_Nextflow_Jun_2022/nextflow/nextflow/test2/../testdata/*.fastq.gz
	executor >  local (3)
	[22/b437be] process > fastQC (B7_H3K4me1_s_chr19.fastq.gz) [100%] 2 of 2 ✔
	[1a/cfe63b] process > multiQC                              [  0%] 0 of 1
	executor >  local (3)
	[22/b437be] process > fastQC (B7_H3K4me1_s_chr19.fastq.gz) [100%] 2 of 2 ✔
	[1a/cfe63b] process > multiQC                              [100%] 1 of 1 ✔


This time it worked because Nextflow used the image specified in the **nextflow.config** file and containing the executables.

Now let's take a look at the **params.yaml** file:

.. literalinclude:: ../nextflow/test2/params.yaml
   :language: yaml

As you can see, we indicated two pipeline parameters, `reads` and `email`; when running the pipeline, they can be overridden using `\-\-reads` and `\-\-email`.


Now, let's examine the folders generated by the pipeline.

.. code-block:: console

	ls  work/2a/22e3df887b1b5ac8af4f9cd0d88ac5/

	total 0
	drwxrwxr-x 3 ec2-user ec2-user  26 Apr 23 13:52 .
	drwxr-xr-x 2 root     root     136 Apr 23 13:51 multiqc_data
	drwxrwxr-x 3 ec2-user ec2-user  44 Apr 23 13:51 ..


We observe that Docker runs as "root". This can be problematic and generates security issues. To avoid this we can add this line of code within the process section of the config file:

.. code-block:: groovy

	containerOptions = { workflow.containerEngine == "docker" ? '-u $(id -u):$(id -g)': null}


This will tell Nextflow that if it is run with Docker, it has to produce files that belong to a user rather than the root.

Publishing final results
-------------------------

The script **test2.nf** generates two new folders, **output_fastqc** and **output_multiQC**, that contain the result of the pipeline output.
We can indicate which process and output can be considered the final output of the pipeline using the **publishDir** directive that has to be specified at the beginning of a process.

In our pipeline, we define these folders here:

.. literalinclude:: ../nextflow/test2/test2.nf
   :language: groovy
   :emphasize-lines: 32-36,54,74



You can see that the default mode to publish the results in Nextflow is `soft linking`. You can change this behavior by specifying the mode as indicated in the **multiQC** process.

.. note::
	IMPORTANT: You can also "move" the results but this is not suggested for files that will be needed for other processes. This will likely disrupt your pipeline


Adding a 'help' section to a pipeline
=============================================

Here we describe another good practice: the use of the `\-\-help` parameter. At the beginning of the pipeline, we can write:


.. literalinclude:: ../nextflow/test2/test2.nf
   :language: groovy
   :emphasize-lines: 15-30


so that launching the pipeline with `\-\-help` will show you just the parameters and the help.

.. code-block:: console

	nextflow run test2.nf --help

	N E X T F L O W  ~  version 20.07.1
	Launching `test2.nf` [mad_elion] - revision: e3a80b15a2
	BIOCORE@CRG - N F TESTPIPE  ~  version 1.0
	=============================================
	reads                           : /home/ec2-user/git/CRG_Nextflow_Jun_2022/nextflow/nextflow/test2/../testdata/*.fastq.gz
	This is the Biocore's NF test pipeline
	Enjoy!

EXERCISE
===============

- Look at the very last EXERCISE of the day before. Change the script and the config file using the label for handling failing processes.

.. raw:: html

   <details>
   <summary><a>Solution</a></summary>

The process should become:

.. literalinclude:: ../nextflow/test1/sol/sol_lab.nf
   :language: groovy
   :emphasize-lines: 34



and the nextflow.config file would become:

.. literalinclude:: ../nextflow/test1/sol/nextflow.config
   :language: groovy


.. raw:: html

   </details>
|
|

- Now look at **test2.nf**.
Change this script and the config file using the label for handling failing processes by retrying 3 times and incrementing time.

You can specify a very low time (5, 10 or 15 seconds) for the fastqc process so it would fail at the beginning.

.. raw:: html

   <details>
   <summary><a>Solution</a></summary>


The code should become:

.. literalinclude:: ../nextflow/test2/retry/retry.nf
   :language: groovy
   :emphasize-lines: 66



while the nextflow.config file would be:

.. literalinclude:: ../nextflow/test2/retry/nextflow.config
   :language: groovy
   
   
.. raw:: html

   </details>
|
|
Using Singularity
=======================

We recommend using Singularity instead of Docker in HPC environments.
This can be done using the Nextflow parameter `-with-singularity` without changing the code.

Nextflow will take care of **pulling, converting, and storing the image** for you. This will be done only once and then Nextflow will use the stored image for further executions.

Within an AWS main node, both Docker and Singularity are available. While within the AWS batch system, only Docker is available.


.. code-block:: console

	nextflow run test2.nf -params-file params.yaml -with-singularity -bg > log

	tail -f log
	N E X T F L O W  ~  version 20.10.0
	Launching `test2.nf` [soggy_miescher] - revision: 5a0a513d38

	BIOCORE@CRG - N F TESTPIPE  ~  version 1.0
	=============================================
	reads                           : /home/ec2-user/git/CoursesCRG_Containers_Nextflow_May_2021/nextflow/test2/../../testdata/*.fastq.gz

	Pulling Singularity image docker://biocorecrg/c4lwg-2018:latest [cache /home/ec2-user/git/CoursesCRG_Containers_Nextflow_May_2021/nextflow/test2/singularity/biocorecrg-c4lwg-2018-latest.img]
	[da/eb7564] Submitted process > fastQC (B7_H3K4me1_s_chr19.fastq.gz)
	[f6/32dc41] Submitted process > fastQC (B7_input_s_chr19.fastq.gz)
	...


Let's inspect the folder `singularity`:

.. code-block:: console

	ls singularity/
	biocorecrg-c4lwg-2018-latest.img


This singularity image can be used to execute the code outside the pipeline **exactly the same way** as inside the pipeline.

Sometimes we can be interested in launching only a specific job, because it might fail or for making a test. For that, we can go to the corresponding temporary folder; for example, one of the fastQC temporary folders:

.. code-block:: console

	cd work/da/eb7564*/


Inspecting the `.command.run` file shows us this piece of code:

.. code-block:: groovy

	...

	nxf_launch() {
	    set +u; env - PATH="$PATH" SINGULARITYENV_TMP="$TMP" SINGULARITYENV_TMPDIR="$TMPDIR" singularity exec /home/ec2-user/git/CoursesCRG_Containers_Nextflow_May_2021/nextflow/test2/singularity/biocorecrg-c4lwg-2018-latest.img /bin/bash -c "cd $PWD; /bin/bash -ue /home/ec2-user/git/CoursesCRG_Containers_Nextflow_May_2021/nextflow/test2/work/da/eb756433aa0881d25b20afb5b1366e/.command.sh"
	}
	...


This means that Nextflow is running the code by using the **singularity exec** command.

Thus we can launch this command outside the pipeline (locally):

.. code-block:: console

	bash .command.run

	Started analysis of B7_H3K4me1_s_chr19.fastq.gz
	Approx 5% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 10% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 15% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 20% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 25% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 30% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 35% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 40% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 45% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 50% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 55% complete for B7_H3K4me1_s_chr19.fastq.gz
	Approx 60% complete for B7_H3K4me1_s_chr19.fastq.gz
	...

If you have to submit a job to a HPC you need to use the corresponding program, such as **qsub** if you have a Sun Grid Engine or **sbatch** if you have Slurm. Here an example using Slurm:

.. code-block:: console

	sbatch .command.run


Profiles
=================

For deploying a pipeline in a cluster or Cloud, in the **nextflow.config** file, we need to indicate what kind of the `executor <https://www.nextflow.io/docs/latest/process.html#executor>`__ to use.

In the Nextflow framework architecture, the executor indicates which **batch-queue system** to use to submit jobs to an HPC or to Cloud.

The executor is completely abstracted, so you can switch from SGE to SLURM just by changing this parameter in the configuration file.

You can group different classes of configuration or **profiles** within a single **nextflow.config** file.

Let's inspect the **nextflow.config** file in **test3** folder. We can see three different profiles:

- standard
- cluster
- cloud

The first profile indicates the resources needed for running the pipeline locally. They are quite small since we have little power and CPU on the test node.


.. literalinclude:: ../nextflow/test3/nextflow.config
   :language: groovy
   :lines: 1-19


As you can see, we explicitly indicated the **local** executor. By definition, the local executor is a default executor if the pipeline is run without specifying a profile.

The second profile is for running the pipeline on the **cluster**; here in particular for the cluster supporting the SLURM Workload Manager queuing system:

.. literalinclude:: ../nextflow/test3/nextflow.config
   :language: groovy
   :lines: 20-36


This profile indicates that the system uses **SLURM** as a job scheduler and that we have different queues for small jobs and more intensive ones.

.. note::
	IMPORTANT: You need to have either Docker or Singularity installed and running in your computing nodes to run the pipeline. In some HPC you might need to "load" the programs using the modules. For this we advice to add this command inside your **.bash_profile** file.

.. code-block:: console

	vi $HOME/.bash_profile

	#ADD THIS

	module load apptainer
	


Deployment in the AWS cloud
=============================


The final profile is for running the pipeline in the **Amazon Cloud**, known as Amazon Web Services or AWS. In particular, we will use **AWS Batch** that allows the execution of containerized workloads in the Amazon cloud infrastructure (where NNNN is the number of your bucket, which you can see in the mounted folder `/mnt` by typing the command **df**).

.. literalinclude:: ../nextflow/test3/nextflow.config
   :language: groovy
   :emphasize-lines: 38-55


We indicate the **AWS specific parameters** (**region** and **cliPath**) and the executor **awsbatch**.
Then we indicate the working directory, which should be mounted as `S3 volume <https://aws.amazon.com/s3/>`__.
This is mandatory when running Nextflow on the cloud.

We can now launch the pipeline, indicating `-profile cloud`:

.. code-block:: console

	nextflow run test3.nf -bg -with-docker -profile cloud > log


Note that there is no longer a **work** folder in the directory where test3.nf is located, because, in the AWS cloud, the output is copied locally in the folder **/mnt/nf-class-bucket-NNN/work** (you can see the mounted folder - and the corresponding number - typing **df**).

The multiqc report can be seen on the AWS webpage at https://nf-class-bucket-NNN.s3.eu-central-1.amazonaws.com/results/ouptut_multiQC/multiqc_report.html

But you need before to change permissions for that file (where NNNN is the number of your bucket):

.. code-block:: console

	chmod 775 /mnt/nf-class-bucket-NNNN/results/ouptut_multiQCmultiqc_report.html


Sometimes, you can find that the Nextflow process itself is very memory intensive and the main node can run out of memory. To avoid this, you can reduce the memory needed by setting an environmental variable:

.. code-block:: console

	export NXF_OPTS="-Xms50m -Xmx500m"


Again we can copy the output file to the bucket.

We can also tell Nextflow to directly copy the output file to the S3 bucket: to do so, change the parameter **outdir** in the params file (use the bucket corresponding to your AWS instance):

.. code-block:: groovy

	outdir = "s3://nf-class-bucket-NNNN/results"


