"""
Error Propagation Library V6.
Drawing with GraphViz.
"""

import pygraphviz as pgv
import re

class Drawing(object):
    """@brief Drawing class """

    def __init__(self):
        """@brief Constructor"""
        self.colors = ['darkviolet', 'turquoise', 'navy', \
            'slateblue', 'steelblue', 'blueviolet', 'mediumvioletred', \
            'indigo', 'magenta', 'blue']
        self.layouts = ["neato", "dot", "twopi", "circo", \
            "fdp", "nop", "wc", "acyclic", "gvpr", "gvcolor", \
            "ccomps", "sccmap", "tred", "sfdp"]
        self.layout = self.layouts[1]
        self.max_nodes_in_grpah = 200
        self.zoom = 1
        self.show_cf = True
        self.show_df = True

    def zoom_in(self, value=0.5):
        """zoom in"""
        self.zoom += value
        return self.zoom

    def zoom_out(self, value=0.5):
        """zoom in"""
        if self.zoom - value > 0.1:
            self.zoom -= value
        return self.zoom

    def switch_view(self):
        """all -> cf -> df"""
        if self.show_cf and self.show_df:
            self.show_df = False
            return True
        if self.show_cf and not self.show_df:
            self.show_df = True
            self.show_cf = False
            return True
        if not self.show_cf and self.show_df:
            self.show_df = True
            self.show_cf = True
            return True
        self.show_df = True
        self.show_cf = True
        return False

    def set_view(self, show_cf, show_df):
        """all -> cf -> df"""
        if not show_cf and not show_df:
            return False
        self.show_cf = show_cf
        self.show_df = show_df

    def __add_element(self, model, graph, name):
        """add element node to graph"""
        label = name
        penwidth = 1*self.zoom
        style = 'rounded, filled'
        if model.initial_element == name:
            penwidth = 2*self.zoom
        if model.elements[name]['sub_model']:
            style = 'rounded, filled, dotted'
            label = label + ' | sub sytem'
        if model.elements[name]['repetitions'] > 1:
            style = 'rounded, filled, dotted'
            label = label + ' | x' + str(model.elements[name]['repetitions'])
        #peripheries = 1
        #if model.elements[name]['sub_model']:
        #    peripheries = 2
        color = 'black'
        fcolor = 'gray'
        if model.elements[name]['cf_prism_commands']:
            fcolor = 'skyblue'
        if model.elements[name]['ep_prism_commands']:
            fcolor = 'slateblue'
        graph.add_node(name, \
            label=label, \
            style=style, \
            shape='rectangle', \
            fontsize=10*self.zoom, \
            #peripheries=peripheries, \
            height=0.2*self.zoom, \
            width=0.4*self.zoom, \
            fontname="Helvetica", \
            penwidth=penwidth, \
            color=color, \
            rank='same', \
            fillcolor=fcolor)

    def __add_data(self, graph, name):
        """add element node to graph"""
        color = 'blue'
        fcolor = 'gray'
        label = name
        graph.add_node(name, \
            label=label, \
            style='filled', \
            shape='rectangle', \
            color=color, \
            fillcolor=fcolor, \
            fontsize=10*self.zoom, \
            fontname="Helvetica", \
            height=0.2*self.zoom, \
            penwidth=1*self.zoom, \
            width=0.4*self.zoom)

    def __add_cf_arc(self, graph, from_name, to_name, style='solid'):
        """add cf_arc edge to graph"""
        graph.add_edge(from_name, to_name, \
                    color='black', \
                    penwidth=1*self.zoom, \
                    arrowsize=1*self.zoom, \
                    style=style, \
                    weight=10)

    def __add_df_arc(self, graph, from_name, to_name, style='solid'):
        """add df_arc edge to graph"""
        graph.add_edge(from_name, to_name, \
            color='blue', \
            penwidth=0.5*self.zoom, \
            arrowsize=0.5*self.zoom, \
            style=style, \
            weight=1)

    def __add_failure(self, model, graph, name):
        """add element node to graph"""
        color = 'red'
        fcolor = 'lightcoral'
        label = name
        graph.add_node(name, \
            label=label, \
            style='filled', \
            shape='cds', \
            color=color, \
            fillcolor=fcolor, \
            fontsize=10*self.zoom, \
            fontname="Helvetica", \
            height=0.3*self.zoom, \
            penwidth=1*self.zoom, \
            width=0.5*self.zoom)
        varaibles = re.split(\
            '[\n \t ; ( ) , + - * / = ! & | < > ? != => <= >= <=>]', \
            model.failures[name])
        for data in model.data.keys():
        #TODO normal check
            if data in varaibles:
                if data in graph.nodes():
                    graph.add_edge(data, name, \
                        color='red', \
                        style='dashed', \
                        penwidth=0.5*self.zoom, \
                        arrowsize=0.5*self.zoom, \
                        weight=5)
        for element in model.elements.keys():
            if element in varaibles:
                graph.add_edge(element, name, \
                    color='red', \
                    style='dashed', \
                    penwidth=0.5*self.zoom, \
                    arrowsize=0.5*self.zoom, \
                    weight=5)

    def __generate_graph(self):
        """add generates label for graph with logo and model data"""
        label = "< <table border=\"0\">"
        label += "<tr><td ALIGN=\"LEFT\" fixedsize=\"true\" width=\"116\" height=\"43\">"
        label += "TODO: ErrorPro"
        #TODO image in label not working on my mac, no idea
        #label += "<img src=\"ep_logo.png\" />"
        label += "</td></tr>"
        label += "<tr><td> </td></tr></table>  >"
        graph = pgv.AGraph(directed=True, \
            #strict=False, \
            overlap=False, \
            #splines="ortho", \
            #splines="spline", \
            #label=label, \
            #labelloc="top", \
            #labeljust="left",\
            fontsize=10*self.zoom, \
            fontname="Helvetica", \
            #compound=True, \
            margin=0, \
            pad=0, \
            dpi=72)
        #graph.node_attr['shape'] = 'rectangle'
        return graph

    def __correct_graph(self, graph, logger=None):
        """corrects escaped edges"""
        bb = [float(b) for b in pgv.graphviz.agget(graph.handle, \
            'bb'.encode('utf-8')).decode("utf-8").split(",")]
        for edge in graph.edges():
            if edge[0] == edge[1]:
                continue
                # TODO this is a patch for graphviz 3n+1 warning:
                # if we correct an that goes from and to the same node
                # with high probability graphviz raises th warning about the 3n+1 points
                # because of this warning pygraphviz crashes with the issues discussed in
                # https://github.com/pygraphviz/pygraphviz/issues/117
                # in my mac I've also patched pygraphviz via adding .decode(self.encoding) to
                # the lines 1335 and 1338 of agraph.py:
                # raise IOError(b"".join(errors).decode(self.encoding))
                # warnings.warn(b"".join(errors).decode(self.encoding), RuntimeWarning)
            posstr = "e,"
            poses = edge.attr['pos'][2:].split(" ")
            for pos in poses:
                possplit = pos.split(",")
                if float(possplit[0]) < bb[0]:
                    if logger:
                        logger.warning("Escaped edge (left) corrected: " + str(edge))
                    posstr += str(bb[0]) + ","
                elif float(possplit[0]) > bb[2]:
                    if logger:
                        logger.warning("Escaped edge (right) corrected: " + str(edge))
                    posstr += str(bb[2]) + ","
                else:
                    posstr += possplit[0] + ","
                if float(possplit[1]) < bb[1]:
                    if logger:
                        logger.warning("Escaped edge (bottom) corrected: " + str(edge))
                    posstr += str(bb[1]) + ","
                elif float(possplit[1]) > bb[3]:
                    if logger:
                        logger.warning("Escaped edge (top) corrected: " + str(edge))
                    posstr += str(bb[3]) + ","
                else:
                    posstr += possplit[1] + " "
            posstr = posstr[:-1]
            edge.attr['pos'] = posstr
        return graph


    def get_agraph_system(self, model):
        """draw complete model with nesting to a single pdf"""
        graph = self.__generate_graph()
        if len(model.elements) + len(model.data)  + len(model.failures) > self.max_nodes_in_grpah:
            graph.add_node('Model is too big to be drawn, sorry')
            graph.layout(prog=self.layout)
            model.logger.warning("Model is too big to be drawn.")
            return graph
        # add elements
        for element_name in model.elements:
            self.__add_element(model, graph, element_name)
        # add data
        if self.show_df:
            for data_name in model.data:
                self.__add_data(graph, data_name)
        # control flow arcs
        if self.show_cf:
            for element_name in model.elements:
                for cf_output in model.elements[element_name]['cf_outputs']:
                    self.__add_cf_arc(graph, element_name, cf_output)
        # data flow arcs
        if self.show_df:
            for d_name, d_value in model.data.items():
                for df_input in d_value['df_inputs']:
                    self.__add_df_arc(graph, df_input, d_name)
                for df_output in d_value['df_outputs']:
                    self.__add_df_arc(graph, d_name, df_output)
        # add failures
        for failure_name in model.failures.keys():
            self.__add_failure(model, graph, failure_name)
        graph.layout(prog=self.layout)
        graph = self.__correct_graph(graph, logger=model.logger)
        return graph

    def draw_model(self, model, file_name="model.png"):
        """draw flat system"""
        graph = self.get_agraph_system(model)
        if graph.nodes():
            graph.draw(file_name)
            #model.logger.message("The graph has been saved to " + file_name)
        return graph

    def draw_model_complete(self, model, file_name="model.png"):
        """draw nested system"""
        graph = self.get_agraph_system(model)
        graph.draw(file_name)
        for el_name, el_value in model.elements.items():
            #TODO check instance of the model
            if el_value['sub_model']:
                f_name = file_name[:-4] + "_" + el_name + file_name[-4:]
                self.draw_model_complete(el_value['sub_model'], f_name)
