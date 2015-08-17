# Quora & CL
----

This repo contains my current progress on a project I'm working on related to [Quora](www.quora.com) and predicting various attributes of questions and their answers.

## Python Files

* `Quora`
	* `.QuoraScraper`: Core scraping functions to extract data from Quora
	* `.ScrapeServer`: Server that assigns job urls to clients
	* `.ScrapeClient`: Script that takes urls passed by server and scrapes them for data
	* `.exp`: Experiment scripts
		* `.ans_hist`: Generates histogram of number of answers questions get
	* `.util`: Utility scripts
		* `.getText`: Parses out text from data entries (for use with N-gram modeling)
		* `.reparse`: Reparses entries from stored HTML
		* `.sortOutput`: Moves output files into sorted directory tree based on month/date
		* `.stats`: Generates some basic stats about a dataset

## Running

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

## Data format

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