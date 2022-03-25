# NiViz-Rater Test Data Sample

This directory contains all the data required to launch a test run of NiViz-Rater

## Contents

- `test-lorem.yaml` - this is the `qc-specification-file` for rating the generated dataset
- `file_list` - provides a list of sample file names to generate
- `generate_images.sh` - small script to read a list of file-names and produce images from
- `images/` - directory where you may output generated images into


## Generating Test Images

Test images can be generated using the `generate_images.sh` script:

```
# ./generate_images.sh FILE_LIST OUT_DIR
./generate_images.sh ./file_list ./images
```

## Locally installed NiViz-Rater

```
niviz-rater -i images/ -c test-lorem.yaml initialize_db
niviz-rater -i images/ -c test-lorem.yaml runserver
```

## Docker image of NiViz-Rater

*See main README.md for instructions on building Docker image*

```
docker run -v $PWD:/data \
  --network="host" \
  niviz-rater:[TAG] \
  -i /data/images \
  -c /data/test-lorem.yaml \
  --db-file /data/niviz.db \
  initialize_db

docker run -v $PWD:/data \
  --network="host" \
  niviz-rater:[TAG] \
  -i /data/images \
  -c /data/test-lorem.yaml \
  --db-file /data/niviz.db \
  runserver [--port PORT] [--fileserver-port FILESERVER_PORT]

```

You may now open the NiViz-Rater UI on localhost:5000 (you may change the port using `--port` option)

