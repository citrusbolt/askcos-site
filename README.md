
# ASKCOS:
Software package for the prediction of feasible synthetic routes towards a desired compound and associated tasks related to synthesis planning. Originally developed under the DARPA Make-It program and now being developed under the [MLPDS Consortium](http://mlpds.mit.edu).

# v0.3.1 Release

Video demo of new UI features: https://drive.google.com/open?id=1SnxTGxgLuZKR1buvYo-4t0Zagof9385Q

Release Notes
User notes:
* HTTPS support
* Tree builder jobs from web user interface run asynchronously and are automatically saved to view later
* Interactive path planner has new hierarchical view
* Support email creates issue directly in our development space (gitlab)
* Support ticket communication is confidential and can only be viewed by the person who logged the issue (outside of our group). The shared flag will be checked to determine if the contents of the issue can be used to create an FAQ in the future. The default is to have the shared flag unchecked.

Developer notes:
* New GitLab development space
* Upgraded to Python 3.5, Django 2.2, and celery 4.3
* New deploy script to help manage order of starting new services
* New mysql (v5.7) and mongodb (v4.0.10) microservices, for user data and job results, respectively
* mysql services decouples user data from front end, i.e. - updates to front end won't erase user data or require backup/restore
* Templates and buyable compounds now exist in a mongo database. Templates are still loaded (now from DB), once at initialization, however buyable lookups are live, i.e. - changes to DB will be reflected in the application without requiring a restart. A future version will include a front end for interaction with buyables database.

Bug fixes:
* Context recommender API can now return scores with ‘return_scores’ parameter
* Correct number of workers now appear on status page after scaling services
* Removed Google Analytics snippet left over from public site

### Upgrade information

The easiest way to upgrade to the new version of ASKCOS is using Docker and docker-compose. To get started, make sure both docker and docker-compose are installed on your machine. We have a pre-built docker image of ASKCOS hosted on DockerHub. It is a private repository; if you do not have access to pull the image contact mef231@mit.edu. In addition, you need to have the deploy/ folder from our code repository. To get the most recent version of ASKCOS:

docker login # enter credentials
docker pull mefortunato/askcos:0.3.1

Then, follow the instructions under “How do I upgrade ASKCOS to a new version?” below using the new version of the deploy folder from this repository.

### Using GitLab Deploy Tokens

We are in the process of migrating our development space from GitHub to GitLab. There are a number of beneficial features provided through GitLab that encouraged this move. The first of which are deploy tokens, providing __read-only__ access to source code and our container registry available through GitLab. For the next few releases, code and containers will continue to be made available via the GitHub and DockerHub repositories you may be familiar with, but eventually we plan to move exclusively to GitLab. Below is a complete example showing how to deploy the askcos application using deploy tokens (omitted in this example). The only software prerequisites are git, docker, and docker-compose.

```bash
$ export DEPLOY_TOKEN_USERNAME=
$ export DEPLOY_TOKEN_PASSWORD=
$ git clone https://$DEPLOY_TOKEN_USERNAME:$DEPLOY_TOKEN_PASSWORD@gitlab.com/mlpds_mit/askcos/askcos
$ docker login registry.gitlab.com -u $DEPLOY_TOKEN_USERNAME -p $DEPLOY_TOKEN_PASSWORD
$ docker pull registry.gitlab.com/mlpds_mit/askcos/askcos:0.3.1
$ docker tag registry.gitlab.com/mlpds_mit/askcos/askcos:0.3.1 mefortunato/askcos:0.3.1
$ cd askcos/deploy
$ git checkout v0.3.1
$ bash deploy
```

__NOTE:__ The git clone command pulls enough to deploy the application (but not all the data files hosted using git large file store). To acquire the complete source code repository including large data files (if you want to rebuild a custom image, for example), please install git lfs and pull the rest of the repository.


# First Time Deployment with Docker

### Prerequisites

 - If you're buidling the image from scratch, make sure git (and git lfs) is installed on your machine
 - Install Docker [OS specific instructions](https://docs.docker.com/install/)
 - Install docker-compose [installation instructions](https://docs.docker.com/compose/install/#install-compose)

### Deploying the web application

The entrypoint for deployment is a bash script that runs a few docker-compose commands in a specific order. A few of the database services need to be started first, and more importantly seeded with data, before other services (which rely on the availability of data in the database) can start. The bash script can be found and should be run from the deploy folder as follows:

```
$ bash deploy.sh
```

There are three optional arguments you can pass along:
* --skip-seed: This will skip seeding the mongo database. Unless you know that the mongo database is currently up and running, you should probably choose to seed the database
* --skip-ssl: This will skip the generation of a random self-signed ssl certificate. If you are supplying your own, use this option so as to not override the certificates
* --skip-migration: This will skip performing the db migration required by django. Only use this if you know the migration has already been performed and the db models have not changed.


To stop a currently running application, run the following from the deploy folder, where you ran deploy.sh:

```bash
$ docker-compose stop
```

If you would like to clean up and remove everything from a previous deployment (__NOTE: you will lose user data__), run the following from the deploy folder:

```bash
$ docker-compose down -v
```

### Upgrading or moving deployments

#### Backing up user data

If you are upgrading the deployment from a previous version,or moving the application to a different server, you may want to retain user accounts and user-saved data/results. Previous to version 0.3.1, user data was stored in an sqlite db at `askcos/db.sqlite3` and a user\_saves directory at `makeit/data/user_saves`, _in the running app container service_. Versions >=0.3.1 use a mysql service for user data, and a mongo db for user results. Although the process for backing-up/restoring data is different, currently the `backup.sh` and `restore.sh` scripts are capable of handling the backup process. Please read the following carefully so as to not lose any user data:

1) Start by making sure the previous version you would like to backup is __currently up and running__ with `docker-compose ps`.
2) Checkout the newest version of the source code (only the deploy folder is necessary)
3) Run `$ bash backup.sh`
4) Make sure that the `deploy/backup` folder is present, and there is a folder with a long string of numbers (year+month+date+time) that corresponds to the time you just ran the backup command
5) If the backup was successful (`db.json` and `user_saves` (\<v0.3.1) or `results.mongo` (\>=0.3.1) should be present), you can safely tear down the old application with `docker-compose down -v`
6) Deploy the new application with `bash deploy.sh`
7) Restore user data with `bash restore.sh`

Note: For versions >=0.3.1, user data persists in docker volumes, and is not tied to the lifecycle of the container services. In other words, as long as you do not include the [-v] flag to `docker-compose down`, volumes do not get removed, and user data is safe. In this case, the backup/restore procedure is not necessary.

### (Optional) Building the ASKCOS Image

The askcos image itself can be built using the Dockerfile in this repository.

```bash
$ git clone https://gitlab.com/mlpds_mit/askcos/askcos  
$ cd askcos/makeit/data  
$ git lfs pull  
$ cd ../../  
$ docker build -t askcos .
```

### Add customization

There are a few parts of the application that you can customize:
* Header sub-title next to ASKCOS (to designate this as a local deployment at your organization)
* Contact emails for centralized IT support

These are handled as environment variables that can change upon deployment (and are therefore not tied into the image directly). They can be found in `deploy/customization`. Please let us know what other degrees of customization you would like.

### Managing Django

If you'd like to manage the Django app (i.e. - run python manage.py ...), for example, to create an admin superuser, you can run commands in the _running_ app service (do this _after_ `docker-compose up`) as follows:

`docker-compose exec app bash -c "python /usr/local/ASKCOS/askcos/manage.py createsuperuser"`

In this case you'll be presented an interactive prompt to create a superuser with your desired credentials.

## Important Notes

#### First startup

The celery worker will take a few minutes to start up (possibly up to 5 minutes; it reads a lot of data into memory from disk). The web app itself will be ready before this, however upon the first get request (only the first for each process) a few files will be read from disk, so expect a 1-2 second delay.

#### Scaling workers

Only 1 worker per queue is deployed by default with limited concurrency. This is not ideal for many-user demand. You can easily scale the number of celery workers you'd like to use with `docker-compose up -d --scale tb_c_worker=N` where N is the number of workers you want, for example. The above note applies to each worker you start, however, and each worker will consume RAM.

## Future Improvements

 - Container orchestration with Kubernetes (will allow for distributed celery workers on multiple machines)


# Installation without Docker

A coarse installation guide can be found in ```install_cli.sh``` (i.e., "install command line interface"). Note that this shell script is  _not_ meant to actually be run as a shell script. 

We also have an installation guide for the Django web interface, which uses Celery for asynchronous task management (```install_webapp.sh```). This relies on RabbitMQ and Redis servers and uWSGI/NGINX or Apache for deployment.

Please note that this code relies on either (1) additional data files not contained in this repo, but available from ccoley@mit.edu or (2) connection to a MongoDB with specific expectations for databases/collections/etc.

### Dependencies
The code has primarily been developed for Python 2.7.6 on Ubuntu 16.04. However, we have made an effort to make it work on Python 3.6.1 as well (tested on macOS 10.13.3). 

Included in this repository is a conda environment ```askcos.yml```. Note that this is a fairly messy file and there are some extraneous packages listed. Additionally, some packages are slightly out of date and could be updated without any issues. We are woring to clean this script up and streamline the deployment process. 


### Make-It installation instructions (Ubuntu 16.04, Python 2.7.6)
1. Place the Make-It repository inside an ```ASKCOS``` folder in your home folder

1. Download miniconda2 (or miniconda3 for Python 3) and add it to the system path
	```
	wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
	bash Miniconda2-latest-Linux-x86_64.sh -b -p $HOME/miniconda
	export PATH=~/miniconda/bin:$PATH
	echo 'export PATH=~/miniconda/bin:$PATH' >> ~/.bashrc
	```

1. [MIGHT BE NECESSARY] Install libxext6, libsm6, and zlib-1.2.9, and add ```$HOME/miniconda/lib/python2.7/site-packages``` to ```PYTHONPATH``` and ```$HOME/miniconda/lib``` to ```LD_LIBRARY_PATH```

1. Prepare system-wide dependencies before setting up python packages

	```
	sudo apt install heimdal-dev
	sudo apt install libkrb5-dev 
	sudo apt-get install libhdf5-dev
	sudo apt-get install build-essential
	```

1. Create the "askcos" conda environment using the provided ```askcos.yml``` as a starting point

	```
	conda-env create -f askcos.yml -n askcos
	```

1. Add Make-It folder and askcos subfolder to your ```PYTHONPATH``` environment variable

	```
	export PYTHONPATH=~/ASKCOS/Make-It:~/ASKCOS/Make-It/askcos:$PYTHONPATH
	echo 'export PYTHONPATH=~/ASKCOS/Make-It:~/ASKCOS/Make-It/askcos:$PYTHONPATH' >> ~/.bashrc 
	```

1. [OPTIONAL] create a link between ```Make-It/makeit/data``` and wherever you actually want to store the data

1. Install RDKit and Pymongo

	```
	source activate askcos
	conda install rdkit -c rdkit
	pip install pymongo
	sudo apt install libxrender-dev 

	export PYTHONPATH=~/miniconda/envs/askcos/lib/python2.7/site-packages:$PYTHONPATH
	export LD_LIBRARY_PATH=~/miniconda/envs/askcos/lib:$LD_LIBRARY_PATH

	echo 'export PYTHONPATH=~/miniconda/envs/askcos/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.bashrc
	echo 'export LD_LIBRARY_PATH=~/miniconda/envs/askcos/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
	```

1. Install a more recent verison of Tensorflow

	```
	pip install tensorflow==1.4.1
	```

1. Set the default Keras backend to ```"theano"``` by editing ```~/.keras/keras.json```. If this is the first time you're running keras, this file won't exist. Run ```python -c "import keras"``` to have this file be generated.

1. Test Make-It by running any of the individual modules below and/or the full planning script.

### Website installation instructions (Ubuntu 16.04, Python 2.7.6)

1. Install Redis as the results backend

	```
	sudo add-apt-repository -y ppa:chris-lea/redis-server 
	sudo apt-get update
	sudo apt-get install redis-server
	sudo service redis start 
	```

1. Install RabbitMQ as the message broker

	```
	echo "deb https://dl.bintray.com/rabbitmq/debian xenial main" | sudo tee /etc/apt/sources.list.d/bintray.rabbitmq.list 
	wget -O- https://dl.bintray.com/rabbitmq/Keys/rabbitmq-release-signing-key.asc |
	     sudo apt-key add - 
	sudo apt-get update 

	wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb 
	sudo dpkg -i erlang-solutions_1.0_all.deb
	sudo apt-get update
	sudo apt-get install erlang 
	sudo apt-get install rabbitmq-server # on OS X, brew install rabbitmq

	sudo service redis start 
	sudo service rabbitmq-server start
	```
	
1. Install uWSGI

	```
	pip install uwsgi
	sudo apt-get install nginx
	sudo /etc/init.d/nginx start 
	```
	
1. Test that uWSGI is working by temporarily running the webserver

	```
	uwsgi --http :8000 --wsgi-file wsgi.py
	```

	and in a new terminal window...

	```
	curl http://localhost:8000
	```

1. Inside the askcos folder, get uwsgi_params

	```
	wget https://raw.githubusercontent.com/nginx/nginx/master/conf/uwsgi_params
	```

1. Edit /etc/nginx/nginx.conf as needed, according to http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html and/or using the nginx.conf file provided in the deploy subfolder as a template

1. Start the uWSGI server (long-term, this should be run as a service)

	```
	uwsgi --socket :8000 --wsgi-file wsgi.py
	```

1. Start the NGINX server

	```
	sudo service nginx start
	```
	
1. Test basic website functionality
	- SCScore
	- Buyable page
	- Drawing
	- Saving/restoring pages
	
1. Test Celery functionality by starting up context recommender workers
	1. 

		```
		celery -A askcos_site worker -c 1 -Q cr_coordinator -n "cr_coordinator@$(hostname)" --max-tasks-per-child 1000 --loglevel=$CELERY_LOG_LEVEL  --logfile=celery_logs/%p.log &
		celery -A askcos_site worker -c 1 -Q cr_network_worker -n "cr_network_worker@$(hostname)" --max-tasks-per-child 5000 --loglevel=$CELERY_LOG_LEVEL  --logfile=celery_logs/%p.log &
		```
	1. Go to the /context/ page on the website and make a request for the neurla network context recommender model
	
1. Edit ```spawn_workers.sh``` to reflect the anticipated server load (i.e., number of workers needed to support each task) before running the script to spawn them.

	_note: if you want the workers to run on a separate server, you will need to edit ```askcos/askcos_site/celery.py``` to give an explicit SERVERHOST instead of localhost. You will also need to open up the ports for the message broker (5672) and redis server (6379) to the other server._


### Setting up the Celery workers on a different server from the Webserver

For scalability, it is possible to have the webserver and compute servers completely separately. The webserver will host the website, RabbitMQ, and Redis servers. The compute server will be where Celery workers are spun up.

1. If using AWS, open up connections between instances in the same security group (following the slightly-outdated https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules-reference.html#sg-rules-other-instances)

1. [On the webserver] Allow remote connections to RabbitMQ. It is possible to create specific users for the default vhost to limit access, but it is easiest to open up all remote connections to the "guest" user (https://www.rabbitmq.com/access-control.html). This relies on non-RabbitMQ security measures to prevent unwanted connections to the server's port. Create ```/etc/rabbitmq/rabbitmq.conf``` if it does not exits and enter one line:

	```
	loopback_users = none
	```

1. [On the webserver] Edit ```/etc/redis/redis.conf``` to allow remote connections from worker machine. Ideally, you can bind to a specific IP by editing the ```bind 127.0.0.1``` line. This seems to work fine on our local servers but did not work well on AWS. The alternative is to completely open up connections by changing the ```bind``` line to ```bind 0.0.0.0``` and edit the following block to say ```protected-mode off```. As with the RabbitMQ settings, this means that Redis will rely on other firewalls/security measures.


1. [On the compute server] Change the ```SERVERHOST``` in ```askcos/askcos_site/celery.py``` to the IP of the webserver, so the Celery workers know where to look for the RabbitMQ/Redis servers. If using AWS, this should be the _private_ IP of the webserver instance.

1. [On the compute server] Spin up as many workers as desired using ```spawn_workers.sh``` from inside the ```askcos``` folder. The most computationally intensive task is the TreeBuilder, for which we generally allocate 4-12 processes in each worker pool. Each process requires 3-4 GB of RAM. The other Celery workers (aside from the nearest neighbor context recommender, which should be deprecated) are relatively small in memory footprint.


# Customization

### Changing the database of buyable chemicals

Information about what chemicals are considered buyable is stored in a flat pickle file at ```makeit/data/local_db_dumps/pricer_using_reaxys_v2-chemicals_and_reaxys_v2-buyables.pkl```. It contains three dictionaries:

- ```prices``` - a dictionary that maps RDKit-canonicalized isomeric SMILES strings to chemical prices in price-per-gram
- ```prices_flat``` - the same dictionary but with non-isomeric SMILES strings
- ```prices_by_rxn``` - was intended to be a dictionary that maps Elsevier chemical IDs to price-per-gram

In the code, these dictionaries are loaded from disk by the ```Pricer``` class defined in ```makeit/utilities/buyable/pricer.py```. To update what is considered buyable, you can create an object of ```Pricer``` class, call the ```load()``` method, add chemicals from your own database into the dictionaries stored under the ```prices``` and ```prices_flat``` attributes, then dump the information back out to the pickle file with ```Pricer.dump_to_file()```.

Once the database is updated, it will be necessary to spin down/up the retrosynthetic workers (```tb_c_worker``` and ```tb_coordinator_mcts```) as well as the primary webservice for them to reload the data. The buyable module (http://askcos.mit.edu/price/) can be used to check that the web service has been updated with the new buyable database.

As a final note, a price per gram of 0 is used throughout the codebase to be considered ```not buyable```. So to add in-inventory systems without consideration of cost, using a placeholder of $1/g or $100/g is recommended. In the future, we might have a special note for ```in stock``` that is independent of price information.


# How to run individual modules
Many of the individual modules -- at least the ones that are the most interesting -- can be run "standalone". Examples of how to use them are often found in the ```if __name__ == '__main__'``` statement at the bottom of the script definitions. For example...

#### Using the learned synthetic complexity metric (SCScore)
```makeit/prioritization/precursors/scscore.py```

#### Obtaining a single-step retrosynthetic suggestion with consideration of chirality
```makeit/retrosynthetic/transformer.py```

#### Finding recommended reaction conditions based on a trained neural network model
```makeit/synthetic/context/neuralnetwork.py```

#### Using the template-free forward predictor
```makeit/synthetic/evaluation/template_free.py```

#### Using the coarse "fast filter" (binary classifier) for evaluating reaction plausibility
```makeit/synthetic/evaluation/fast_filter.py```

#### Integrated CASP tool
For the integrated synthesis planning tool at ```makeit/application/run.py```, there are several options available. The currently enabled options for the command-line tool can be found at ```makeit/utilities/io/arg_parser.py```. There are some options that are only available for the website and some that are only available for the command-line version. As an example of the former, the consideration of popular but non-buyable chemicals as suitable "leaf nodes" in the search. An example of how to use this module is:

```python ASKCOS/Make-It/makeit/application/run.py --TARGET atropine```

##### Model choices.
The following options influence which models are used to carry out the different tasks within the algorithm.

- Context recommendation: via '--context_recommender', currently has the following options:

	-'Nearest_Neighbor': Uses a nearest neighbor based database search (memory intensive, ~30GB, and slow; relies on external data file)
	
	-'Neural_Network': Uses a pretrained neural network (highly recommended!!)

- Context prioritization: via '--context_prioritization', specifies how we should determine the "best" context for a proposed reaction. It currently has the following options:

	-'Probability': uses the likelihood of success for the reaction under that condition
	
	-'Rank': uses the rank of the reaction under that condition relative to all other outcomes

- Forward evaluation: via '--forward_scoring', is used to evaluate the likelihood of success of a reaction. It currently has the following options:

	-'Template_Based': uses the original forward evaluation method enumerating all possible outcomes by applying templates and then predicting the most likely main product [https://pubs.acs.org/doi/abs/10.1021/acscentsci.7b00064] (NOTE: the template-based forward predictor requires a custom built version of RDKit from https://github.com/connorcoley/rdkit - we highly recommend using the template-free approach)
	
    -'Template_Free': uses the higher-performing and faster template-free method based on graph convolutional neural networks [https://arxiv.org/abs/1709.04555]
    
    -'Fast_Filter': uses a binary classifier to distinguish good and bad reaction suggestions. It is imperfect, but very fast. Based on the "in-scope filter" suggested by Marwin Segler [https://www.nature.com/articles/nature25978]

- Retrosynthetic template prioritization: via '--template_prioritization', is used to minimize the number of reaction templates that must be applied to the target compound at each iteration. It currently has the following options:

	-'Relevance': Quantifies how relevant a given template is for the considered reactants, based on the approach suggested by Marwin Segler [https://onlinelibrary.wiley.com/doi/abs/10.1002/chem.201605499]
	
	-'Popularity': Ranking based on number of references in literature, independent of the product species

- Precursor prioritization: via '--precusor_prioritization', is used to determine which precursor is the most promising branch to pursue. It currently has the following options:

	-'Heuristic': Simple heuristic, with decreasing score as number of atoms, rings and chiral centers increases
	
	-'SCScore': Synthetic Complexity Score - learned quantity indicating how complex a molecule is. Tries to interpret molecules with a protection/deprotection group as less complex than their non-protected counterparts. [https://pubs.acs.org/doi/abs/10.1021/acs.jcim.7b00622]



- Tree scoring: via '--tree_scoring', determines how final synthesis trees should be sorted/ranked. It currently has the following options:

	-'Product': uses the product of template score and forward prediction score
	
	-'Forward_only': uses only the forward prediction score
	
	-'Template_only': uses only the template score

#### Limits and thresholds: the following options will set limits for the different parts of the program

- Expansion time via '--expansion_time': limit the amount of time the program spends expanding the retro synthetic tree. Default value is 60 seconds.
  
- Maximum search depth via '--max_depth': limit the search depth in the retro synthetic expansion. Default value is 4.
  
- Maximum degree of branching via '--max_branching': limit the number of branches generated in each layer of the retro synthetic tree. Default value is 20
  
- Maximum number of buyable trees via '--max_trees': limit the number of buyable trees the program  should search for. Default value is 500.

- Maximum number of templates to be applied via '--template_count': limit the number of templates that are appied for each expansion when using the popularity prioritizer. Default value is 10000.

- Minimal number of templates to be considered in retro synthetic direction for non-chiral reactions via '--mincount_retro'. Default value is 25.
  
- Minimal number of templates to be considered in retro synthetic direction for chiral reactions via '--mincoun_retro_c'. Default value is 10.
 
- Minimal number of templates to be considered in synthetic direction via '--synth_mincount'. Default value is 25.
  
- Minimal target rank for considering a target feasible via '--rank_threshold'. Default value is 10.

- Minimal probability for considering a target feasible via '--prob_threshold'. Default value is 0.01.

- Maximum number of contexts to be proposed for each reaction via '--max_contexts'. Default value is 10

- Maximum price per gram for a component to be considered buyable via '--max_ppg'. Default value is 100
  
- Precursor filtering: via '--apply_fast_filter' and '--filter_threshold', is used to impose rapid filtering of low-quality retrosynthetic suggestions. Default is True and 0.75
