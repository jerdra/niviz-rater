# NiViz Rater

Interface for rating BIDS-compliant QC outputs from NiViz. 

Database: SQLite
Web framework: bottle 
Frontend: svelte 

## Get started

### Installation

If you prefer to use Docker please go directly to the docker section for more information! Virtualenv/Pyenv/Local installers read on ahead.

Installation of Niviz can be done, but the following requirements must be met:

1. You have Python>3.8 with `pip`
2. You have an installation of `npm`

With both of the above requirements satisfied, first clone the repository:

```
git clone https://github.com/jerdra/niviz-rater.git
```

Next, we need to build the relevant client-side bundle:

```
cd niviz-rater/niviz_rater/client
npm run build
```

This will auto-install any dependencies and build the client-side bundle to be served (CSS, JS)


Finally you can install the package using `pip`:

```
cd ../../

# You should be in the repository root directory
pip install -r requirements.txt
pip install .
```

This will install the `niviz-rater` console script that you can now use to QC your data!


### How to use Niviz-Rater

***

This is a general overview of how you can use NiViz-Rater with your own data. If you want to play with some sample test data check out the `data/` folder where you can generate fake data and try running NiViz-Rater yourself

***

Niviz-Rater was designed to be a flexible application facilitating the quality control and review process for researchers. A result of this flexibility is that the *users need to tell Niviz how they want to rate their images*. Researchers can talk to Niviz-Rater using a `qc-specification-file` which is a YAML file written in a [schema](niviz_rater/data/schema.yaml) that Niviz-Rater understands. In addition, NiViz-Rater expects that the user has their images named using BIDS entities to make the process of fetching files easier.

Looking directly at the [schema](niviz_rater/data/schema.yaml) is a little bit intimidating, instead let's work through an example. Suppose we have a set of QC images in a directory organized as follows:

```
qc_images
├── sub-A
│   ├── sub-A_desc-qc1_bold.svg
│   ├── sub-A_desc-qc1_T1w.svg
│   ├── sub-A_desc-qc2_bold.svg
│   └── sub-A_desc-qc2_T1w.svg
├── sub-B
│   ├── sub-B_desc-qc1_bold.svg
│   ├── sub-B_desc-qc1_T1w.svg
│   ├── sub-B_desc-qc2_bold.svg
│   └── sub-B_desc-qc2_T1w.svg
├── sub-C
│   ├── sub-C_desc-qc1_bold.svg
│   ├── sub-C_desc-qc1_T1w.svg
│   ├── sub-C_desc-qc2_bold.svg
│   └── sub-C_desc-qc2_T1w.svg
└── sub-D
    ├── sub-D_desc-qc1_bold.svg
    ├── sub-D_desc-qc1_T1w.svg
    ├── sub-D_desc-qc2_bold.svg
    └── sub-D_desc-qc2_T1w.svg
```

In summary, we have 2 QC images (denoted by desc-qc1 or desc-qc2) for our two modalities (_bold and _T1w). When reviewing images, the rater wants to assess the quality of the bold and T1w images; each of the qc images provides a view into each stage of whatever processing was done. 

In order to tell Niviz we need to tell it:
1. What are the entities being rated - in this case it is our T1w and bold images
2. What should we use to assess each of our entities - the corresponding qc1/qc2 images

You can think of this as grouping our QC images by the actual underlying image (bold/T1w) being assessed. Now that we have an idealized layout, let's communicate it with Niviz-Rater! This is done using a `qc-specification-file`, let's call it `my_qc.yaml`:


#### The QC Specification File

`my_qc.yaml`
```
# Extensions that we want to search through, you can use this to ignore certain file-types
ImageExtensions: ["svg"]	

RowDescription:
	# Which BIDS entity to use to define what is a row
	entities: [subject]

	# Formatting for row-names in exportable spreadsheet
	name: "${subject}"

# Each listing in component concerns an underlying entity we want to qc (i.e bold, T1w)
Components:

	# What should the name of this QC entity be (for T1w)
	- name: "${subject} anatomical"

	# Which BIDS entities to aggregate over when generating QC views
	# and for columns in the exportable spreadsheet
	# this will make more sense with the BOLD component
	  entities: [subject]

	# What is the column name in the exportable spreadsheet	
	  column: "anatomical"

	# Which images to use to assess quality of image
	# Each entry is a key-value of BIDS entities
	  images:
	  	- { description: qc1, suffix: T1w }
	  	- { description: qc2, suffix: T1w }

	# Finally define a preset list of rating categories for T1w
	  ratings:
	  	- Incorrect MNI transformation
		- T1 surface reconstruction issue
		- Skullstrip failure
		- Good


	# For BOLD, each subject/task combination gets its own rating
	- name: "${subject} task:${task} fMRI"
	  entities: [subject, task]
	  column: "task-${task}_bold"
	  images:
	  	- {description: qc1, suffix: bold}
	  	- {description: qc2, suffix: bold}
	  ratings:
	  	- EPI-T1 mismatch
		- Bad SDC correction
		- Bad masking
		- Good
```


***

Note that NiViz-Rater uses `pybids` under the hood to pull entities. In some cases you may
have BIDS entitites that are not natively recognized by `pybids`. Feel free to write a
`qc-specification-file` using them for now. NiViz-Rater allows users to extend the
list of valid bids entities using the `--bids-settings` argument

***

#### Running NiViz-Rater

Now that you've done the hard work of defining a `qc-specification-file` it's time to rate
our images! This is a quick two-step process:

```
niviz-rater -i <path_to_qc_images> -c <path_to_my_qc_yaml> \
	[--bids-settings BIDS_CONFIG_JSON ] [--db-file DB_FILE ] \
	initialize_db

niviz-rater -i <path_to_qc_images> -c <path_to_my_qc_yaml> \
	[--bids-settings BIDS_CONFIG_JSON ] [--db-file DB_FILE ]\
	runserver [--fileserver-port FILESERVER_PORT] [--port WEBSERVER_PORT]
```

Explanation of options:

- `--bids-settings` - This extends `pybids` with a BIDS config `.json` file. See `pybids` documentation for more info. Alteratively look at `niviz_rater/data/bids.json` for an example
- `--db-file` - Defines the output SQLite DB file, by default it will be `niviz.db` in the current directory. Make sure you use the same `DB_FILE` when you run both commands! 
- `--fileserver-port` - NiViz-Rater spins up a simple fileserver in order to serve your QC images to the web-page, you can modify the port (default=`5001`) here
- `--port` - Port to use for NiViz-Rater's web-server

Running the `runserver` command will spin up a webserver you can access on your browser on `localhost:5000` or `localhost:<WEBSERVER_PORT>` if you set `--port` explicitly!


### Using Docker

NiViz-Rater can be run easily using Docker! First clone this repository:

```
git clone https://github.com/jerdra/niviz-rater.git
```

Next build:

```
# Template
docker build . -t niviz-rater[:TAG] [--rm]

# This will create niviz-rater:latest
docker build . -t niviz-rater --rm
```

NiViz-Rater can be used from within the container as follows:

```
docker run \
	[docker options...] \
	--network="host" \	# export host ports and localhost to container
	--user $UID \	# ensure that container has user permissions
	niviz-rater:[TAG]	# i.e latest
	-i /path/to/input/dataset \
	-c /path/to/yaml/file/containing/specification \
	[initialize_db, runserver] [...options]
```

Follow the mini-walkthrough above for more information on how to use NiViz-Rater!
