# OSM-Map-Graph-Converter for OpenStreetMaps

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

## Output Example

```jsonc
// vertex
{
  "x":9.9268353,
  "y":51.5331826,
  "osm_id":28095800
}

// edge
{
  "from":208650206,
  "to":277409422,
  "length":7.829,
  "max_speed":"30",
  "name":"Waageplatz",
  "osm_id":"24827765"
}

// Response
{
  "filename": "file.osm",
  "length": 187,
  "graph": {
    "vertices": [/*...*/],
    "edges": [/*...*/]
  }
}
```
