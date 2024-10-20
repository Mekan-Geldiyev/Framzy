from .function import _Function
import uuid
from typing import List, Iterator
def map(iterable):
    if not _Function.print_graph:
        for item in iterable:
            yield item
    else:
        map_name = "map:"+str(uuid.uuid4())
        prev_node, param = iterable
        if param.__name__ != "List" and param.__name__ != "Iterator":
            raise Exception("Iterable must be a list or iterator")

        iterable_arg = param.__args__[0]
        _Function.graph.add_node(map_name, inputs={"iterable": param}, output_types=[iterable_arg], type="map")

        _Function.graph.add_edge(prev_node, map_name, param=param.schema(), input="iterable")
        return (map_name, iterable_arg)

def aggregate(iterable_arg):
    if not _Function.print_graph:
        return iterable_arg
    else:
        aggregate_name = "aggregate:"+str(uuid.uuid4())
        prev_node, param = iterable_arg

        iterable_arg = param.__args__[0]
        _Function.graph.add_node(aggregate_name, inputs={"iterable": param}, output_types=[List[iterable_arg]], type="aggregate")

        _Function.graph.add_edge(prev_node, aggregate_name, param=param.schema(), input="iterable")
        return (aggregate_name, List[iterable_arg])

def inner_join(iterables, join_fields):
    if not _Function.print_graph:
        return iterables
    else:
        join_name = "join:"+str(uuid.uuid4())
        prev_nodes = []
        params = []
        for iterable in iterables:
            prev_node, param = iterable
            prev_nodes.append(prev_node)
            params.append(param)

        iterable_arg = params[0].__args__[0]
        _Function.graph.add_node(join_name, inputs={"iterable": params[0], "iterable2": params[1]}, output_types=[iterable_arg], type="join")

        _Function.graph.add_edge(prev_nodes[0], join_name, param=params[0].schema(), input="iterable")
        _Function.graph.add_edge(prev_nodes[1], join_name, param=params[1].schema(), input="iterable2")
        return (join_name, iterable_arg)