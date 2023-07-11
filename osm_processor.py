import os

import osmnx as ox
import tempfile
import geopandas
from redis.commands.graph import Edge
from redis.commands.graph.node import Node
import redis
import nanoid

r = redis.Redis(host='0.0.0.0', port=6379, db=0)


def process_map(file_path: str):
    """Process the map file and return the graph."""
    g_path, graph, graph_index = preprocess_osm_file(file_path)

    redis_nodes = create_nodes(g_path, graph)
    create_edges(g_path, graph, redis_nodes)
    graph.commit()

    print("Done processing map")

    query_result = r.graph(index_name=graph_index).query("MATCH (a:vertex)-[r:CONNECTS]->(b:vertex) RETURN r,a,b")

    vertices = []
    edges = []

    for row in query_result.result_set:
        [edge, start_node, end_node] = row
        ee: Edge = edge
        aa: Node = start_node
        bb: Node = end_node
        v_aa = {'x': aa.properties['x'], 'y': aa.properties['y'], 'osm_id': aa.properties['osmid']}
        v_bb = {'x': bb.properties['x'], 'y': bb.properties['y'], 'osm_id': bb.properties['osmid']}

        e_ee = {
            'from': ee.properties['u'],
            'to': ee.properties['v'],
            'length': ee.properties['length'],
            'max_speed': ee.properties['maxspeed'],
            'name': ee.properties['name'] or '',
            'osm_id': ee.properties['osmid'] or '',
        }

        vertices.append(v_aa)
        vertices.append(v_bb)
        edges.append(e_ee)

    return {
        'vertices': list(vertices),
        'edges': list(edges),
    }


def preprocess_osm_file(file_path):
    """Preprocess the osm file and return the graph."""

    # verify that the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    print(f"Processing file {file_path}")
    g_path = f'{tempfile.gettempdir()}/{nanoid.generate()}_graph.gpkg'
    print('Saving graph to', g_path)
    osm_data = ox.graph.graph_from_xml(filepath=file_path)
    ox.io.save_graph_geopackage(osm_data, filepath=g_path, directed=True)
    print('Graph saved to', g_path)
    graph_index = nanoid.generate()
    graph = r.graph(index_name=graph_index)

    return g_path, graph, graph_index


def create_edges(g_path, graph, redis_nodes):
    """Create edges from the graph for redis."""
    print('Creating edges')
    edges = geopandas.read_file(g_path, layer='edges')
    filtered_edges = edges.query(
        "highway in ('residential','primary','secondary','tertiary','primary_link') or access == 'destination'")
    for idx, edge in enumerate(filtered_edges.drop(
            columns=['geometry', 'width', 'bridge', 'ref', 'landuse', 'highway', 'area', 'tunnel', 'access',
                     'service', 'junction', 'reversed', 'oneway', 'lanes', 'key']).to_dict('index').values()):
        s_node = find_node(redis_nodes, edge['u'])
        d_node = find_node(redis_nodes, edge['v'])
        redis_edge = Edge(src_node=s_node, dest_node=d_node, properties=edge, relation='CONNECTS')
        graph.add_edge(redis_edge)


def create_nodes(g_path, graph):
    """Create nodes from the graph for redis."""
    print('Creating nodes')
    # process nodes
    nodes = geopandas.read_file(g_path, layer='nodes')
    try:
        nodes = nodes.drop(columns=['geometry', 'highway', 'ref'])
    except KeyError:
        pass
    # create redis nodes
    redis_nodes = [Node(node_id=n['osmid'], label="vertex", properties=n) for n in nodes.to_dict('index').values()]
    for n in redis_nodes:
        graph.add_node(n)
    return redis_nodes


def find_node(nodes: list[Node], node_id: int) -> Node:
    """Find a node in the list of nodes."""
    for n in nodes:
        if n.id == node_id:
            return n

    raise Exception("No node found")
