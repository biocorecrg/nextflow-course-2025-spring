.. _nextflow_4-page:

*******************
4 Nextflow 
*******************

Using Singularity
=======================

We recommend using Singularity instead of Docker in HPC environments.
This can be done using the Nextflow parameter `-with-singularity` without changing the code.

Nextflow will take care of **pulling, converting, and storing the image** for you. This will be done only once and then Nextflow will use the stored image for further executions.

Within an AWS main node, both Docker and Singularity are available. While within the AWS batch system, only Docker is available.


.. code-block:: console

	nextflow run test2.nf -with-singularity -bg > log

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
   :lines: 1-21


As you can see, we explicitly indicated the **local** executor. By definition, the local executor is a default executor if the pipeline is run without specifying a profile.

The second profile is for running the pipeline on the **cluster**; here in particular for the cluster supporting the Sun Grid Engine queuing system:

.. literalinclude:: ../nextflow/test3/nextflow.config
   :language: groovy
   :lines: 22-38


This profile indicates that the system uses **Sun Grid Engine** as a job scheduler and that we have different queues for small jobs and more intensive ones.

Deployment in the AWS cloud
=============================

The final profile is for running the pipeline in the **Amazon Cloud**, known as Amazon Web Services or AWS. In particular, we will use **AWS Batch** that allows the execution of containerized workloads in the Amazon cloud infrastructure (where NNNN is the number of your bucket which you can see in the mounted folder `/mnt` by typing the command **df**).

.. literalinclude:: ../nextflow/test3/nextflow.config
   :language: groovy
   :emphasize-lines: 40-57


We indicate the **AWS specific parameters** (**region** and **cliPath**) and the executor **awsbatch**.
Then we indicate the working directory, which should be mounted as `S3 volume <https://aws.amazon.com/s3/>`__.
This is mandatory when running Nextflow on the cloud.

We can now launch the pipeline indicating `-profile cloud`:

.. code-block:: console

	nextflow run test3.nf -bg -with-docker -profile cloud > log


Note that there is no longer a **work** folder in the directory where test3.nf is located, because, in the AWS cloud, the output is copied locally in the folder **/mnt/nf-class-bucket-NNN/work** (you can see the mounted folder - and the corresponding number - typing **df**).

The multiqc report can be seen on the AWS webpage at https://nf-class-bucket-NNN.s3.eu-central-1.amazonaws.com/results/ouptut_multiQC/multiqc_report.html

But you need before to change permissions for that file (where NNNN is the number of your bucket):

.. code-block:: console

	chmod 775 /mnt/nf-class-bucket-NNNN/results/ouptut_multiQCmultiqc_report.html


Sometimes you can find that the Nextflow process itself is very memory intensive and the main node can run out of memory. To avoid this, you can reduce the memory needed by setting an environmental variable:

.. code-block:: console

	export NXF_OPTS="-Xms50m -Xmx500m"


Again we can copy the output file to the bucket.

We can also tell Nextflow to directly copy the output file to the S3 bucket: to do so, change the parameter **outdir** in the params file (use the bucket corresponding to your AWS instance):

.. code-block:: groovy

	outdir = "s3://nf-class-bucket-NNNN/results"


Making a Nextflow pipeline for image processing
======================

We can build a pipeline incrementally adding more and more processes.
Nextflow will handle the dependencies between the input/output and the parallelization.

Let's see the content of the folder **nextflow/ex_alba**

.. code-block:: console

	ls
	etl_peem.py  importUview_v3.py  step1_denoise.py  step2_normalize.py  step3_aggregate_and_save.py

We have some Python scripts made by Fernán and Nicolas for making those steps:

- **step1_denoise.py**: it will read an image file (".dat"), turn it into a NumPy array ("_den.npy"), and denoise it.

.. code-block:: console

	# command line
	./step1_denoise.py my_image.dat
	# output my_image_den.npy


- **step2_normalize.py**: it will read a denoised NumPy array ("_den.npy"), that is output by the previous step and produces a nomalized / denoised NumPy array ("_den_norm.npy"). It needs the original image file in the current directory for working even if not specified in the command line. 

.. code-block:: console

	ls ./
	step2_normalize.py my_image_den.npy my_image.dat
	# command line
	./step2_normalize.py my_image_den.npy
	# output my_image_den_norm.npy


- **step3_aggregate_and_save.py**: it will read all the normalized/denoised NumPy arrays together and it will produce a NeXus/HDF5 file called **example.nxs**




EXERCISE
============

Make the pipeline considering the use of the docker/singularity image **biocorecrg/alba:0.1** hosted at dockerhub. The images are at **../../testdata/test_images/** and the executor must be specified for working with our infrastructure. 


.. raw:: html

   <details>
   <summary><a>Solution</a></summary>

.. literalinclude:: ../nextflow/test_alba/test_alba.nf
   :language: groovy

.. raw:: html

   </details>
|

Modules and how to re-use the code
==================================

A great advantage of the new DSL2 is to allow the **modularization of the code**.
In particular, you can move a named workflow within a module and keep it aside for being accessed by different pipelines.

The **test4** folder provides an example of using modules.


.. literalinclude:: ../nextflow/test4/test4.nf
   :language: groovy
   

We now include two modules, named **fastqc** and **multiqc**, from ```${baseDir}/modules/fastqc.nf``` and ```${baseDir}/modules/multiqc.nf```.
Let's inspect the **multiQC** module:


.. literalinclude:: ../nextflow/test4/modules/multiqc.nf
   :language: groovy


The module **multiqc** takes as **input** a channel with files containing reads and produces as **output** the files generated by the multiqc program.

The module contains the directive **publishDir**, the tag, and the container to be used and has a similar input, output, and script session as the fastqc process in **test3.nf**.

A module can contain its own parameters that can be used for connecting the main script to some variables inside the module.

In this example, we have the declaration of two **parameters** that are defined at the beginning:

.. literalinclude:: ../nextflow/test4/modules/fastqc.nf
   :language: groovy
   :emphasize-lines: 5-6


They can be overridden from the main script that is calling the module:

- The parameter **params.OUTPUT** can be used for connecting the output of this module with the one in the main script.
- The parameter **params.CONTAINER** can be used for declaring the image to use for this particular module.

In this example, in our main script, we pass only the OUTPUT parameters by writing them as follows:

.. literalinclude:: ../nextflow/test4/test4.nf
   :language: groovy
   :emphasize-lines: 54


While we keep the information of the container inside the module for better reproducibility:

.. literalinclude:: ../nextflow/test4/modules/multiqc.nf
   :language: groovy
   :emphasize-lines: 5


Here you see that we are not using our own image, but rather we use the image provided by **biocontainers** in `quay <https://quay.io/>`__.


Let's have a look at the **fastqc.nf** module:

.. literalinclude:: ../nextflow/test4/modules/fastqc.nf
   :language: groovy


It is very similar to the multiqc one: we just add an extra parameter for connecting the resources defined in the **nextflow.config** file and the label indicated in the process. Also in the script part, there is a connection between the fastqc command line and the number of threads defined in the nextflow config file.

To use this module, we have to change the main code as follows:

.. literalinclude:: ../nextflow/test4/test4.nf
   :language: groovy
   :emphasize-lines: 55

The label **twocpus** is specified in the **nextflow.config** file for each profile:

.. literalinclude:: ../nextflow/test4/modules/nextflow.config
   :language: groovy
   :emphasize-lines: 16,32,53

.. note::

	IMPORTANT: You have to specify a default image to run nextflow -with-docker or -with-singularity and you have to have a container(s) defined inside modules.

EXERCISE
===========

Make some module wrapper for the **test_alba** pipeline

.. raw:: html

   <details>
   <summary><a>Solution</a></summary>

**Solution in the folder test5**

.. raw:: html

   </details>
|
|


Reporting and graphical interface
===================================

Nextflow has an embedded function for reporting information about the resources requested for each job and the timing; to generate a html report, run Nextflow with the `-with-report` parameter :

.. code-block:: console

	nextflow run test5.nf -with-docker -bg -with-report > log


.. image:: images/report.png
  :width: 800


**Nextflow Tower** is an open-source monitoring and managing platform for Nextflow workflows. There are two versions:

- Open source for monitoring of single pipelines.
- Commercial one for workflow management, monitoring, and resource optimization.

We will show the open-source one.

First, you need to access the `tower.nf <https://tower.nf/>`__ website and login.


.. image:: images/tower.png
  :width: 800

We recommend using either Google or GitHub for login. The email has to be accepted manually by the tower team.

.. image:: images/tower0.png
  :width: 800

Once you are signed in you will see a page like this:

.. image:: images/tower2.png
  :width: 800


You can generate your token at `https://tower.nf/tokens <https://tower.nf/tokens>`__ and copy-paste it into your pipeline using this snippet in the configuration file:

.. code-block:: groovy

	tower {
	  accessToken = '<YOUR TOKEN>'
	  enabled = true
	}


or exporting those environmental variables:

.. code-block:: groovy

	export TOWER_ACCESS_TOKEN=*******YOUR***TOKEN*****HERE*******


Now we can launch the pipeline:

.. code-block:: console

	nextflow run test5.nf -with-singularity -with-tower -bg > log


	CAPSULE: Downloading dependency io.nextflow:nf-tower:jar:20.09.1-edge
	CAPSULE: Downloading dependency org.codehaus.groovy:groovy-nio:jar:3.0.5
	CAPSULE: Downloading dependency io.nextflow:nextflow:jar:20.09.1-edge
	CAPSULE: Downloading dependency io.nextflow:nf-httpfs:jar:20.09.1-edge
	CAPSULE: Downloading dependency org.codehaus.groovy:groovy-json:jar:3.0.5
	CAPSULE: Downloading dependency org.codehaus.groovy:groovy:jar:3.0.5
	CAPSULE: Downloading dependency io.nextflow:nf-amazon:jar:20.09.1-edge
	CAPSULE: Downloading dependency org.codehaus.groovy:groovy-templates:jar:3.0.5
	CAPSULE: Downloading dependency org.codehaus.groovy:groovy-xml:jar:3.0.5


and go to the tower website again:


.. image:: images/tower3.png
  :width: 800


When the pipeline is finished we can also receive a mail.


.. image:: images/tower4.png
  :width: 800




