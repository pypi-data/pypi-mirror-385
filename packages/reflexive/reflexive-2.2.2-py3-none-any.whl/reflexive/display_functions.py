from graph_tool.all import (
    Graph,
    VertexPropertyMap,
    EdgePropertyMap,
    GraphPropertyMap,
    graph_draw,
    ungroup_vector_property,
    group_vector_property
)
import cairo
from itertools import chain
from spacy import displacy

# Text Display functions

def _create_displacy_ents(name,text,offsets):
    return {"text": text,
            "ents": [{"start":s,"end":e,"label":l}for (s,e),l in offsets.items()],
            "title": name}
    
def _render_annotated_text(ents,inline=True):
    #default to inline
    page_opt = False
    jupyter_opt = True
    if not inline:
        page_opt = True
        jupyter_opt = False
    
    return displacy.render(ents,manual=True,style="ent", options=_get_text_display_options(),page=page_opt,jupyter=jupyter_opt)

def _get_text_display_options():
    colours = dict([(prop['lbl'],prop['clr']) for prop in _res_graph_properties().values()])
    return {"ents": list(colours.keys()), "colors": colours}

# RES properties for all graphs
def _res_graph_properties()->dict:
    return {0:{ "lbl":"RR",
                "pos":(0.2,6.5),
                "clr":"#00AEEF"},
            1:{ "lbl":"NR",
                "pos":(5,10),
                "clr":"#ED1B23"},
            2:{ "lbl":"AR",
                "pos":(9.8,6.5),
                "clr":"#00A64F"},
            3:{ "lbl":"AF",
                "pos":(7.9,1),
                "clr":"#EC008C"},
            4:{ "lbl":"EP",
                "pos":(2.1,1),
                "clr":"#FFF200"}}

# Create a graph from an adjacency matrix
def _create_graph(matrix,id)->Graph:
    if matrix:
        graph = _graph_from_edges(dict(_matrix_to_dict(matrix)))
    else:
        graph = _graph_no_edges()
    prop_list = _res_graph_properties().values()
    graph.vp["v_positions"] = graph.new_vp("vector<double>",vals=[prop['pos'] for prop in prop_list])
    graph.vp["v_labels"] = graph.new_vp("string",vals=[prop['lbl'] for prop in prop_list])
    graph.gp["id"] = graph.new_gp("string",val=id)
    return graph
        
    # # Vertex properties common to all graphs    
    # v_lbl = graph.new_vp("string",vals=_get_prop_values('lbl'))
    # v_pos = graph.new_vp("vector<double>",vals=_get_prop_values('pos'))
    # # Make propertyMaps internal to the graph
    # graph.vp["v_colour"] = v_clr
    # graph.vp["v_position"] = v_pos
    # graph.vp["v_label"] = v_lbl
    # graph.ep["e_weights"] = e_weight
    
def _graph_from_edges(edges:dict)->Graph:
    graph = Graph(g=edges.keys(),directed=False)
    graph.ep["e_weights"] = graph.new_ep("double",vals=edges.values())
    graph.ep["e_widths"] = graph.new_ep("double",vals=_scale_weights(edges.values()))
    graph.vp["v_colours"] = _get_vcolours_from_edges(graph)
    return graph

def _scale_weights(weights,factor=5):
    return [round(w*factor,1) for w in weights]
      
def _graph_no_edges()->Graph:
      graph = Graph(g=_empty_edge_dict(),directed=False)
      graph.ep["e_weights"] = graph.new_ep("double")
      graph.ep["e_widths"] = graph.new_ep("double")
      graph.vp["v_colours"] = graph.new_vp("string",val="#cccccc")
      return graph
    
def _get_vcolours_from_edges(graph:Graph)->VertexPropertyMap:
    prop_list:dict[int,dict] = _res_graph_properties()
    for i in _isolated_vertices(graph):
        prop_list[i]['clr']= "#cccccc"
    return graph.new_vp("string",[prop['clr'] for prop in prop_list.values()])   

def _isolated_vertices(graph):
    edgelist = chain.from_iterable([sorted((int(e.source()),int(e.target()))) for e in graph.edges()])
    return set(range(5)) - set([e for e in set(edgelist)])

#
def _matrix_to_dict(matrix):
    egen =  ((((tuple(sorted((r,c))),w)) for c,w in enumerate(row) if w>0) for r,row in enumerate(matrix) if sum(row)>0)
    return dict(chain.from_iterable(egen))
    # edges = {}
    # for r,row in enumerate(matrix):
    #     # if empty row, add to iso_vertices
    #     # if sum(row) == 0:
    #     #     self.iso_vertices.add(r)
    #     # else:
    #     if sum(row) > 0: # edge exists
    #         for c,weight in enumerate(row):
    #             if weight > 0:
    #                 edge = tuple(sorted((r,c)))
    #                 #print("r,c:",edge," - ",weight)
    #                 edges[edge] = weight
    # return edges

#
def _empty_edge_dict():
    empty_edges = {}
    for idx in range(5): #self.gt_props.keys():
        empty_edges[idx] = []
    return empty_edges

#
def _get_prop_values(key):
    values_list =  self.gt_props.values()
    return [p[key] for p in values_list]

# flip coordinates for graph-tool
def _flipY(vpositions):
    x, y = ungroup_vector_property(vpositions, [0, 1])
    y.fa *= -1
    y.fa -= y.fa.min()
    return group_vector_property([x, y])

#
def _draw_graph(graph:Graph,inline=True):

    positions = _flipY(graph.vp["v_positions"])
    labels = graph.vp["v_labels"]
    colors = graph.vp["v_colours"]
    widths = graph.ep["e_widths"]
    graph_draw(graph, inline=inline,output_size=(300,300),fit_view=0.7,
                    pos=positions, 
                    vertex_text=labels,
                    vertex_font_family="sans serif",
                    vertex_font_size=18,
                    vertex_font_weight=cairo.FONT_WEIGHT_BOLD,
                    vertex_fill_color=colors,
                    vertex_size = 50,
                    vertex_halo=False,
                    vertex_pen_width=1.2,
                    vertex_color="#999999",
                    edge_pen_width=widths)
    
# def get_vertex_labels(self):
#     return self._get_prop_values('lbl')

# def get_vertex_colours(self):
#     return self._get_prop_values('clr')

# def get_vertex_positions(self):
#     return self._get_prop_values('pos')