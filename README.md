# QuoraProject
----

This repo contains my current progress on a project I'm working on related to [Quora](www.quora.com) and predicting various attributes of questions and their answers.

## Python Files

* `Quora`: Scraping & Processing of Quora
	* `QuoraScraper` : Core scraping functions to extract data from Quora
	* `ScrapeServer` : Server that assigns job urls to clients
	* `ScrapeClient` : Script that takes urls passed by server and scrapes them for data
	* `exp`          : Experiment scripts
	* `util`         : Utility scripts
* `Pylinear` : Formatting, training, and predicting features from data
	* `main`    : Main entry point to cmd line utility
	* `feature` : All functions for generating feature files
	* `model`   : All functions for templating, training models, and prediciting
	* `exp`     : Experiment scripts
	* `util`    : Utility scripts
* `Tests`: Unittests for the project


## Running Quora Scraper

On `localhost`:

```bash
$ python -m Quora.ScrapeServer
INFO:root:Starting server on :9999
INFO:root:Server ready
...

$ python -m Quora.ScrapeClient
INFO:root:Connecting to localhost on port 9999
...
```

With `qsub`:

```bash
$ qsub scripts/start_server.sh
$ tail -f /export/a04/wpovell/logs/ScrapeServer.o$ID
**********************************************************************
Finding an available port...
trying port $PORT... which is good
Available port found: $HOST:$PORT
INFO:root:Starting server on :$PORT
INFO:root:Server ready
...
$ qsub scripts/start_clients.sh $HOST $PORT 1
$ tail -r /export/a04/wpovell/logs/ScrapeClient.o$ID
INFO:root:Connecting to $HOST on port $PORT
...
```

## Data format of QuoraScraper output

```
{
	"data" : {
		"answers" : [
			{
				"author",
				"text",
				"upvotes",
			}
		],
		"question",
		"details",
		"followers",
		"topics" : [ ],
		"links" : [ ]
	}
	"html",
	"log" : {
		"author",
		"date"
	}
	"time"
	"url"
}
```

## PyLinear Directory Setup

```
/ {train, tune, dev, test}
	/ data
		(All data for split)
	/ features
		ngrams.txt
		followers.txt
		... (more feature files)
	/ results
		(Output directory for templated features)
/results
	(Output directory for predictions)
```	