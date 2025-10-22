"""
Our awesome editor module in which we
have all the classes that interact with
it and make it possible.

This is the nodes module, in which we have
all the classes that make the concept work.
"""
from abc import ABC, abstractmethod
from typing import Union


class Node(ABC):
    """
    *Abstract class*

    *This class has to be inherited by any class that
    is able to handle some input to obtain an output
    as a result*

    The abstract class of a Node, which is the entity
    that is able to process some input to return an
    output that can be sent to the next node.
    """

    @abstractmethod
    def process(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        **kwargs
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the input and obtain a result as the output.
        """
        pass

# Specific classes below
class ProcessorNode(Node):
    """
    A simple processor node that is capable of
    processing inputs and obtain a single output.

    This type of node is for the effects and 
    transitions.
    """

    def process(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        **kwargs
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the input and obtain a result as the output.
        """
        raise NotImplementedError


"""
Note for the developer:

A guide to the different types of nodes we will have
when imitating DaVinci Resolve.

Node (abstracto)
├── ProcessorNode (procesa un solo flujo)
│   ├── EffectNode (filtros, LUTs, shaders…)
│   └── TransitionNode (mezcla entre dos entradas)
│
├── CompositeNode (combina múltiples flujos)
│   ├── SerialNode (uno tras otro)
│   ├── ParallelNode (ramas simultáneas)
│   └── LayerNode (capas con blending o máscaras)
│
└── GroupNode (contiene una mini subred de nodos)

"""
