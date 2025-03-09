#!/usr/bin/env python3
from validator import Validator
from node import Node
from uuid import uuid4
from pprint import pprint

validator = Validator()
nodes = [Node(), Node(), Node()]

pprint(nodes)

for node in nodes:
    validator.register(str(uuid4()).split("-")[-1], node.pk)


pprint(Validator.registry)

#
