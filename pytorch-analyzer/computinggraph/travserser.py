# Our drawing graph functions. We rely / have borrowed from the following
# python libraries:
# https://github.com/szagoruyko/pytorchviz/blob/master/torchviz/dot.py
# https://github.com/willmcgugan/rich
# https://graphviz.readthedocs.io/en/stable/
# https://benjamin-computer.medium.com/visualising-the-pytorch-compute-graph-for-bug-fixing-aa131324f34e
# https://discuss.pytorch.org/t/traversing-computation-graph-and-seeing-saved-tensors-problem-edited-hopefuly-clearer/20575
# def draw_graph(start, watch=[]):
#     from graphviz import Digraph
#     node_attr = dict(style='filled',
#                     shape='box',
#                     align='left',
#                     fontsize='12',
#                     ranksep='0.1',
#                     height='0.2')
#     graph = Digraph(node_attr=node_attr, graph_attr=dict(size="12,12"))
#     assert(hasattr(start, "grad_fn"))
#     if start.grad_fn is not None:
#         _draw_graph(loss.grad_fn, graph, watch=watching)
#     size_per_element = 0.15
#     min_size = 12
#     # Get the approximate number of nodes and edges
#     num_rows = len(graph.body)
#     content_size = num_rows * size_per_element
#     size = max(min_size, content_size)
#     size_str = str(size) + "," + str(size)
#     graph.graph_attr.update(size=size_str)
#     graph.render(filename='net_graph.jpg')
# def _draw_graph(var, graph, watch=[], seen=[], indent="", pobj=None):
#     ''' recursive function going through the hierarchical graph printing off
#     what we need to see what autograd is doing.'''
#     from rich import print
#     if hasattr(var, "next_functions"):
#         for fun in var.next_functions:
#             joy = fun[0]
#             if joy is not None:
#                 if joy not in seen:
#                     label = str(type(joy)).replace(
#                         "class", "").replace("'", "").replace(" ", "")
#                     label_graph = label
#                     colour_graph = ""
#                     seen.append(joy)
#                     if hasattr(joy, 'variable'):
#                         happy = joy.variable
#                         if happy.is_leaf:
#                             label += " \U0001F343"
#                             colour_graph = "green"
#                             for (name, obj) in watch:
#                                 if obj is happy:
#                                     label += " \U000023E9 " + \
#                                         "[b][u][color=#FF00FF]" + name + \
#                                         "[/color][/u][/b]"
#                                     label_graph += name
#                                     colour_graph = "blue"
#                                     break
#                             vv = [str(obj.shape[x])
#                                 for x in range(len(obj.shape))]
#                             label += " [["
#                             label += ', '.join(vv)
#                             label += "]]"
#                             label += " " + str(happy.var())
#                     graph.node(str(joy), label_graph, fillcolor=colour_graph)
#                     print(indent + label)
#                     _draw_graph(joy, graph, watch, seen, indent + ".", joy)
#                     if pobj is not None:
#                         graph.edge(str(pobj), str(joy))

# import torch

# x = torch.Tensor([2])
# w = torch.randn(1,requires_grad=True)
# b =torch.randn(1,requires_grad=True)
# y = torch.mul(w,x)
# z = torch.add(y,b)

# print(w)
# print(x)
# print(y.grad_fn.next_functions)

import torch
import os
import psutil

# print(os.cpu_count())
# print(torch.cuda.device_count())
# print(psutil.cpu_count())

cpu = torch.device('cpu',0)
cuda = torch.device('cuda',0)
print(cpu)
print(cuda)
print(torch.get_num_threads())
print(torch.get_num_interop_threads())

# Simple module for demonstration
class MyModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.param = torch.nn.Parameter(torch.rand(3, 4))
        self.linear = torch.nn.Linear(4, 5)

    def forward(self, x):
        # x = x.to("cpu:0")
        y = self.linear(x + self.param)
        # y = y.to("cuda:0")
        return y.clamp(min=0.0, max=1.0)

module = MyModule().to(cpu)

with torch.autograd.profiler.profile(use_cuda=False) as prof:
    input = torch.randn(3, 4,device="cpu")
    output = module.forward(x=input)
    print(output)
print("Exported trace")
prof.export_chrome_trace("/tmp/test1.json")
# from torch.fx import symbolic_trace
# # Symbolic tracing frontend - captures the semantics of the module
# symbolic_traced : torch.fx.GraphModule = symbolic_trace(module)

# # High-level intermediate representation (IR) - Graph representation
# print(symbolic_traced.graph)

# print(symbolic_traced.code)