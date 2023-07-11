# OSM-Map-Graph-Converter

Convert any .osm export to a directed graph.

Currently, only streets as edges are supported. 

## Setup

1. install docker with compose
2. clone this repository and run `docker compose up -d`

## Usage

```bash
$ curl -F file=@example.osm http://localhost:8000/upload/ 
```

The processing can take a few minutes.
