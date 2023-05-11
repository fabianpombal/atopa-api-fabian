import json

from igraph import Graph
import igraph as ig
import matplotlib.pyplot as plt
# g = Graph()
# g.add_vertices(3)
# g.add_edges([(0,1), (1,2)])
# g.add_edges([(2, 0)])
# g.add_vertices(3)
# g.add_edges([(2, 3), (3, 4), (4, 5), (5, 3)])
# ig.plot(g)

# g = Graph([(0,0),(0,1), (1,0), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)], directed=True)
# # g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
# # g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
# # g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
# # g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]
# # g.vs["label"] = g.vs["name"]
# # color_dict = {"m": "blue", "f": "pink"}
# # g.vs["color"] = [color_dict[gender] for gender in g.vs["gender"]]
# # layout = g.layout("kk")
# # ig.plot(g, layout=layout, bbox=(300, 300), margin=20)  # Cairo backend
# # import matplotlib.pyplot as plt
# # fig, ax = plt.subplots()
# # ig.plot(g, layout=layout, bbox=(300, 300), margin=20, target=ax)  # matplotlib backend
# visual_style = {}
# visual_style["vertex_size"] = [20 if gender=="f" else 15 for gender in g.vs["gender"]]
# visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
# visual_style["vertex_label"] = g.vs["name"]
# visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
# # visual_style["edge_label"] = ["Formal" if is_formal else "Informal" for is_formal in g.es["is_formal"]]
# visual_style["layout"] = layout
# visual_style["bbox"] = (300, 300)
# visual_style["margin"] = 50
# visual_style["vertex_label_dist"] = 1
# visual_style["edge_curved"] = False # individual
# visual_style["bbox"] = (1000,1000)
# ig.plot(g, **visual_style)

from pyvis.network import Network
import networkx as nx
# nx_graph = nx.MultiDiGraph()
# nx_graph.add_nodes_from(range(10))
# nx_graph.nodes[1]['label'] = 'Number 1'
# nx_graph.nodes[1]['group'] = 1
# nx_graph.nodes[3]['label'] = 'I belong to a different group!'
# nx_graph.nodes[3]['group'] = 10
# nx_graph.add_node(20, size=20, label='couple', group=2)
# nx_graph.add_node(21, size=15, label='couple', group=2)
# nx_graph.add_edge(20, 21, weight=5)
# nx_graph.add_edge(21, 20, weight=5)
# nx_graph.add_node(25, size=25, label='lonely', group=3)


_nodes = [
          { 'id': 1, 'value': 2, 'label': "Algie" },
          { 'id': 2, 'value': 31, 'label': "Alston" },
          { 'id': 3, 'value': 12, 'label': "Barney" },
          { 'id': 4, 'value': 16, 'label': "Coley" },
          { 'id': 5, 'value': 17, 'label': "Grant" },
          { 'id': 6, 'value': 15, 'label': "Langdon" },
          { 'id': 7, 'value': 6, 'label': "Lee" },
          { 'id': 8, 'value': 5, 'label': "Merlin" },
          { 'id': 9, 'value': 30, 'label': "Mick" },
          { 'id': 10, 'value': 18, 'label': "Tod" },
        ]
_edges = [
    {'edge':(2,  8), 'weight': 3, 'label': "3 emails per week", 'physics': False },
{'edge':(8,  2), 'weight': 3, 'label': "3 emails per week", 'physics': False },
    {'edge':(2,  9), 'weight': 5, 'label': "5 emails per week", 'physics': True },
     {'edge':(2,  10), 'weight': 1, 'label': "1 emails per week", 'physics': True },
      {'edge':(4,  6),'weight': 8, 'label': "8 emails per week", 'physics': True },
       {'edge':(5,  7), 'weight': 2, 'label': "2 emails per week", 'physics': True },
        {'edge':(4,  5), 'weight': 1, 'label': "1 emails per week", 'physics': True },
         {'edge':(9,  10), 'weight': 2, 'label': "2 emails per week", 'physics': True },
          {'edge':(2,  3), 'weight': 6, 'label': "6 emails per week", 'physics': True },
           {'edge':(3,  9), 'weight': 4, 'label': "4 emails per week", 'physics': True },
            {'edge':(5,  3), 'weight': 1, 'label': "1 emails per week", 'physics': True },
             {'edge':(2,  7), 'weight': 4, 'label': "4 emails per week", 'physics': True },
]
nt = Network('500px', '500px', directed=True)
for n in _nodes:
    nt.add_node(n['id'], label=n['label'], size=n['value'])
for e in _edges:
    nt.add_edge(e['edge'][0],e['edge'][1] ,value=(e['weight']/5.0 - 0.2)*6.0, physics=e['physics'])

nt.set_edge_smooth('dynamic')
options = {'physics': {
                'barnesHut': {
                  'gravitationalConstant': -2000,
                  'centralGravity': 0.3,
                  'springLength': 300,
                  'springConstant': 0.04,
                  'damping': 0.09,
                  'avoidOverlap': 0
                },
                'forceAtlas2Based': {
                  'gravitationalConstant': -50,
                  'centralGravity': 0.01,
                  'springConstant': 0.08,
                  'springLength': 300,
                  'damping': 0.4,
                  'avoidOverlap': 0
                },
                'repulsion': {
                  'centralGravity': 0.2,
                  'springLength': 500,
                  'springConstant': 0.05,
                  'nodeDistance': 500,
                  'damping': 0.09
                },
                'hierarchicalRepulsion': {
                  'centralGravity': 0.0,
                  'springLength': 500,
                  'springConstant': 0.01,
                  'nodeDistance': 500,
                  'damping': 0.09,
                  'avoidOverlap': 0
                }
              }}
# nt.from_nx(nx_graph)
nt.set_options(json.dumps(options))
nt.show('nx.html')


from html2image import Html2Image
hti = Html2Image()
hti.screenshot(html_file='nx.html', save_as='out.png')
from PIL import Image
im = Image.open("out.png")
im.size  # (364, 471)
im.getbbox()  # (64, 89, 278, 267)
im2 = im.crop(im.getbbox())
im2.size  # (214, 178)
im2.save("out2.png")
