import json
from bulbs.rexster import Config
from bulbs.titan import Graph
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime, Dictionary

"""
I used this for a Titan import, though any rexster-implementing graph
database should work.

It's important to note however, there are *much* better ways for batch
importing graphs into Titan, see:
http://s3.thinkaurelius.com/docs/titan/0.9.0-M2/bulk-loading.html
"""

config = Config('http://localhost:32813/graphs/graph')
g = Graph(config)

class Entity(Node):
    element_type = "entity"
    oid = String(nullable=False)
    date_added = DateTime()
    date_updated = DateTime()
    fullname = String(nullable=False)
    msgs = Dictionary(default={})
    name = String(nullable=False)
    service = String(default="instagram")
    user_id = Integer()


class Likes(Relationship):
    label = "likes"
    date_updated = DateTime()
    weight = Integer()


class Comments(Relationship):
    label = "comments"
    date_updated = DateTime()
    weight = Integer()

class Mentions(Relationship):
    label = "mentions"
    date_updated = DateTime()
    weight = Integer()


def preprocess_node(line):
    datum = json.loads(line)
    datum['oid'] = datum['_id']['$oid']
    del datum['_id']
    del datum['msgs']

    datum['fullname'] = datum['fullname'][0] if len(datum['fullname']) else ''
    datum['name'] = datum['name'][0] if len(datum['name']) else ''
    del datum['neighbors']

    return datum

def preprocess_edge(line):
    datum = json.loads(line)

    if 'ga' not in datum or 'gb' not in datum:
        return None

    u = nodes[datum['ga']['$oid']]
    v = nodes[datum['gb']['$oid']]
    linktype = datum['linktype']

    return (u, v, linktype, {'weight': datum['weight']})

# oid -> vertex object
nodes = {}


if __name__ == '__main__':
    g.add_proxy("entity", Entity)
    g.add_proxy("likes", Likes)
    g.add_proxy("comments", Comments)
    g.add_proxy("mentions", Mentions)

    with open('sample-entity.json', 'rb') as infile:
        for (i, line) in enumerate(infile):
            if i % 10000 == 0:
                print i

            node = preprocess_node(line)
            nodes[node['oid']] = g.entity.create(node)

    with open('sample-link.json', 'rb') as infile:
        for (i, line) in enumerate(infile):
            if i % 10000 == 0:
                print i

            edge = preprocess_edge(line)

            if not edge:
                continue
            else:
                u, v, linktype, datum = edge

            if linktype == 'comments':
                g.comments.create(u, v, datum)
            elif linktype == 'likes':
                g.likes.create(u, v, datum)
            elif linktype == 'mentions':
                g.mentions.create(u, v, datum)
            else:
                raise Exception('Unknown linktype %s' % linktype)
