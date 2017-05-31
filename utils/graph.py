""" Module graph

Defines functionality to manage, draw and store graphs. A graph is
represented using an adjacency list; the root of this module is the
Graph class, which represents a list of Node objects, which are in turn
connected by Edge instances.

The objects can be overloaded to provide application specific functionality,
if required.

This module also defines functions and classes to compare graphs.

Note that there is also a package called "graphine". The main difference
of visvis.utils.graph is that it is based on visvis.Point's and the nodes
explicitly have a location in a 2D or 3D space.

Example
-------

# Create graph with nodes
g = Graph()
n1 = g.AppendNode(3,4)
n2 = g.AppendNode(5,7)
n3 = g.AppendNode(3,8)
n4 = g.AppendNode(2,5)
n5 = g.AppendNode(4,6)

# Define connections
g.CreateEdge(n1, n2)
g.CreateEdge(n2, n3)
g.CreateEdge(n1, n4)
g.CreateEdge(n2, n4)
g.CreateEdge(n1, n5)

# Draw it
vv.clf()
a = vv.gca()
g.Draw(lc='b')
a.camera = 2
a.SetLimits()

# Get some info
print(g.GetEdges())

"""

import numpy as np
import visvis as vv
from visvis import Point, Pointset
from visvis import ssdf


class Node(Point):
    """ Node(x,y,z,...)
    A Node object represents a point in 2D or 3D space, i.e. a vertex.
    It has a list of references to edge objects. Via these
    edges, the neighbouring node objects can be obtained.
    This class inherits the Point object.
    Use Graph.AppendNode() to create nodes.
    """
    
    def __init__(self, *args, **kwargs):
        Point.__init__(self, *args, **kwargs)
        self._edges = []
    
    
    def __hash__(self):
        return id(self)
    
    def GetEdge(self, otherNode):
        """ GetEdge(self, otherNode)
        Gives the edge from this node to the given node. If there
        is no edge between these nodes, None is returned.
        """
        for c in self._edges:
            if otherNode is c.GetOtherEnd(self):
                return c
        else:
            return None
    
    
    def GetNeighbours(self):
        """ GetNeighbours()
        Get a list of the nodes that this node is adjecent to.
        """
        return [c.GetOtherEnd(self) for c in self._edges]
    
    
    @property
    def degree(self):
        """ The number of neighbours of this node. """
        return len(self._edges)
    
    
    def GetProps(self, index):
        """ GetProps(index)
        Get a list of the property at the given index asociated with the
        edges to the neighboring nodes, matching with what is returned
        by GetNeighbours.
        """
        return [c.props[index] for c in self._edges]
    
    
    def __str__(self):
        """ Make string representation.
        """
        s = Point.__str__(self)
        s.replace('point', 'node')

class Edge:
    """ Edge(node1, node2, *props)
    The base edge class. An edge consists of the references
    of the two nodes it connects and a list of properties asociated with
    the edge.
    Use Graph.CreateEdge to create edges.
    """
    
    def __init__(self, p1, p2, *props):
        if not isinstance(p1, Node) or not isinstance(p2, Node):
            raise ValueError("First two arguments of an edge should be nodes.")
        
        # The two end points
        self.end1 = p1
        self.end2 = p2
        # Store properties
        self.props = [prop for prop in props]
        
        # The indices of the end nodes, only make sense right after calling
        # Graph.GetEdges()
        self._i1 = self._i2 = -1
        
        # A varible to bookkeep whether the edge is connected or not
        self._connected = False
    
    
    def IsEnd(self, end):
        """ IsEnd(self, end)
        Returns True if the given node is a valid end. """
        return (end is self.end1) or (end is self.end2)
    
    
    def GetOtherEnd(self, end):
        """ GetOtherEnd(self, end)
        Given one node, get the node representing the other end of
        the edge. """
        if not self.IsEnd(end):
            raise ValueError("Given end is not a valid end for this edge.")
        if self.end1 is end:
            return self.end2
        else:
            return self.end1
    
    
    def Connect(self):
        """ Connect(self)
        Connect the edge, registering it with both end nodes.
        """
        # make sure not to have the same edge twice
        self.Disconnect()
        # append edge
        self.end1._edges.append(self)
        self.end2._edges.append(self)
        self._connected = True
    
    
    def Disconnect(self):
        """ Disconnect(self)
        Disconnect the edge, unregistering it with the end nodes.
        """
        while self in self.end1._edges:
            self.end1._edges.remove(self)
        while self in self.end2._edges:
            self.end2._edges.remove(self)
        self._connected = False
   


class Graph(list):
    """ Graph()
    
    A Graph represents a collection of nodes that are connected by edges.
    The nodes can be either 2D or 3D points.
    
    Use AppendNode to create nodes and CreateEdge to connect them.
    
    Notes
    -----
    This class cannot inherit from Pointset, because we need to store
    the Node instances to keep track of which nodes are connected by
    which.
    
    Inherits from list, newly implemented methods can be recocnized
    because they start with a capital letter. The use of these methods
    is preferred over the lower case versions.
    
    """
    
    def __init__(self):
        
        # for drawing
        self._lines = []
        self._activeLines = []
    
    
    def __repr__(self):
        tmp =  '<Graph with %i nodes and %i edges at %s>'
        return tmp % (len(self), self.CountEdges(), hex(id(self)))
    
    
    def __to_ssdf__(self):
        return self.Pack()
    
    @classmethod
    def __from_ssdf__(self, s):
        g = Graph()
        g.Unpack(s)
        return g
    
    
    def Pack(self):
        """ Pack()
        Pack the contents in an ssdf struct, such that it can be stored.
        """
        
        # If nodelist is empty, ndim defaults to two
        ndim = 2
        
        # Get a list of all edges
        cc = self.GetEdges()
        
        # Check whether the nodes are homogenous, otherwise we cannot store
        if len(self):
            ndim = self[0].ndim
            for node in self:
                if not node.ndim == ndim:
                    raise ValueError('All nodes should have the same dimension.')
        
        # Init struct
        struct = ssdf.new()
        
        # Create array of nodes
        pp = Pointset(ndim)
        for node in self:
            pp.append(node)
        struct.nodes = pp.data
        
        # Create the edges
        tmp = np.zeros((len(cc), 2), dtype=np.uint32)
        for i in range(len(cc)):
            c = cc[i]
            tmp[i,0] = c._i1
            tmp[i,1] = c._i2
        struct.edges = tmp
        
        
        # Store the properties of the edges. The propRefs array
        # Does contain redundant data, but it can be stored efficiently
        # because the compression handles that...
        allProps = b''
        propRefs = np.zeros((len(cc), 2), dtype=np.uint32)
        for i in range(len(cc)):
            tmp = serializeProps(cc[i].props)
            propRefs[i, 0] = len(allProps)
            propRefs[i, 1] = len(allProps) + len(tmp)
            allProps += tmp
        struct.edgePropRefs = propRefs
        if allProps:
            struct.edgeProps = np.frombuffer( allProps, dtype=np.uint8)
        else:
            struct.edgeProps = np.zeros( (0,), dtype=np.uint8)
        
        # done
        return struct
    
    
    def Unpack(self, struct):
        """ Unpack(struct)
        Load the contents from an ssdf struct.
        This removes the old nodes and edges.
        """
        
        # clear first
        self.Clear()
        
        # First create nodes
        pp = Pointset(struct.nodes)
        for p in pp:
            self.AppendNode(p)
        
        # Make backward compatible
        if hasattr(struct, 'connections'):
            struct.edges = struct.connections
            struct.edgePropRefs = struct.connectionPropRefs
            struct.edgeProps = struct.connectionProps
        
        # Create the edges
        for i in range( struct.edges.shape[0] ):
            # Get serialized property and convert it
            i1 = struct.edgePropRefs[i,0]
            i2 = struct.edgePropRefs[i,1]
            tmp = struct.edgeProps[i1:i2].tostring()
            props = deserializeProps(tmp)
            # Get which nodes belong to it and create edge object
            i1 = int(struct.edges[i,0])
            i2 = int(struct.edges[i,1])
            self.CreateEdge(i1, i2, *props)
    
    
    def Clear(self):
        """ Clear()
        Clear all nodes and edges.
        """
        self[:]=[]
    
    
    def ClearEdges(self):
        """ ClearEdges()
        Clear the edges only.
        """
        for node in self:
            node._edges[:] = []
    
    
    def Copy(self):
        """ Copy()
        Create a full copy of the object (using pack/unpack).
        """
        tmp = self.Pack()
        new = Graph()
        new.Unpack(tmp)
        return new
    
    
    def CountEdges(self):
        """ CountEdges()
        Count the number of edges. """
        count = 0
        for node in self:
            count += len(node._edges)
        return count/2 # because we count each edge twice
    
    
    def GetEdges(self):
        """ GetEdges()
        Get a list of all edges in the graph.
        This is obtained by collecting the edges from all nodes.
        This also sets the _i1 and _i2 properties of all edge
        objects: the index of the two nodes it connects. Note that
        these values become invalid when a node is popped or inserted.
        """
        # Init set (so that each edge is present only once)
        cc = set()
        
        # Check each node
        for i in range(len(self)):
            p = self[i]
            
            # Check each edge
            for c in p._edges:
                # Add if not already added
                cc.add(c)
                # Add reference to the index of this node.
                if c.end1 is p:
                    c._i1 = i
                else:
                    c._i2 = i
        
        # Make list and sort so the order is deterministic
        ccl = list(cc)
        ccl.sort(key=edgeHash)
        
        # Done
        return ccl
    
    
    #def CollectGroups(self, asGraphs=False):
    def CollectGroups(self):
        """ CollectGroups()
        
        Collect all groups of the graph.
        
        """
        
        # Init empty list of groups, each group being a set
        groups = []
        
        # Init search heap
        nodes2search = set([node for node in self])
        
        # Collect group
        while nodes2search:
            # Initialize a new group with one node
            group1 = set() # initial
            group2 = set() # final
            group1.add(nodes2search.pop())
            
            # Search the whole group
            while group1:
                # Take a note from group 1
                node = group1.pop()
                # Make official: put in group2, remove from nodes2search
                group2.add(node)
                nodes2search.discard(node)
                # Pul all its neighbours in group 1, if not alread in group 2
                for neighbour in [c.GetOtherEnd(node) for c in node._edges]:
                    if neighbour not in group2:
                        group1.add(neighbour)
            
            # Add group
            groups.append(group2)
        
        # todo: Enable returning the groups as graph objects?
        
        return groups

    
    def AppendNode(self, *p):
        """ AppendNode(p)
        Append a node (if a point is given, it is converted to a node).
        Overload this to append nodes of a specific class. Returns the
        appended instance.
        """
        if len(p) == 1:
            p = p[0]
        
        if isinstance(p, Node):
            pass
        elif isinstance(p, Point):
            p = Node(p)
        else:
            #raise ValueError("Only Node objects should be appended.")
            # Try to accept it as a point
            p = Node(p)
        # Append and return
        self.append(p)
        return p
    
    
    def _CheckNodes(self, p1, p2):
        """ _CheckNodes(p1,p2)
        Check the given nodes. If they are indices the corresponding
        node objects are returned. If they are node objects, it's
        checked whether they are in the list.
        """
        # Convert indices to nodes, or check if it's a valid node
        if isinstance(p1, int):
            p1 = self[p1]
        else:
            if p1 not in self:
                raise ValueError("First given node not in list!")
        if isinstance(p2, int):
            p2 = self[p2]
        else:
            if p2 not in self:
                raise ValueError("Second given node not in list!")
        
        return p1, p2
    
    
    def CreateEdge(self, p1, p2, *props):
        """ CreateEdge(self, p1, p2, *props)
        Creates an edge instance between the two given nodes.
        The edge replaces any existing edge.
        """
        
        # Check nodes
        p1, p2 = self._CheckNodes(p1, p2)
        
        # Get new and old edge
        cnew = Edge(p1, p2, *props)
        cold = p1.GetEdge(p2) # can be None
        
        # Disconnect old one if necesary. Connect new one
        if cold is not None:
            cold.Disconnect()
        cnew.Connect()
        
        # return edge
        return cnew
    
    
    def Remove(self, node):
        """ Remove(node)
        Remove the node (which can also be given using its index,
        disconnecting all its edges.
        """
        if isinstance(node, int):
            node = self[node]
        for c in [c for c in node._edges]:
            c.Disconnect()
        self.remove(node)
    
    
    def Draw(self, mc='g', lc='y', mw=7, lw=0.6, alpha=0.5, axes=None):
        """ Draw(mc='g', lc='y', mw=7, lw=0.6, alpha=0.5, axes=None)
        Draw nodes and edges.
        """
        
        # We can only draw if we have any nodes
        if not len(self):
            return
        
        # Make sure there are elements in the lines list
        while len(self._lines)<2:
            self._lines.append(None)
        
        # Build node list
        if mc and mw:
            pp = Pointset(self[0].ndim)
            for p in self:
                pp.append(p)
            # Draw nodes, reuse if possible!
            l_node = self._lines[0]
            if l_node and len(l_node._points) == len(pp):
                l_node.SetPoints(pp)
            elif l_node:
                l_node.Destroy()
                l_node = None
            if l_node is None:
                l_node = vv.plot(pp, ls='', ms='o', mc=mc, mw=mw,
                    axesAdjust=0, axes=axes, alpha=alpha)
                self._lines[0] = l_node
        
        # For simplicity, always redraw edges
        if self._lines[1] is not None:
            self._lines[1].Destroy()
        
        # Build edge list
        if lc and lw:
            cc = self.GetEdges()
            # Draw edges
            pp = Pointset(self[0].ndim)
            for c in cc:
                pp.append(c.end1); pp.append(c.end2)
            tmp = vv.plot(pp, ms='', ls='+', lc=lc, lw=lw,
                axesAdjust=0, axes=axes, alpha=alpha)
            self._lines[1] = tmp
    

## Helper classes and functions


def edgeHash(x):
    """ edgeHash(edge)
    Produces a hash for an edge that can be used in sorting.
    requires the edges to be "marked with node indices". Will use
    the first property (if available).
    """
    if x.props:
        return '%0.30f' % x.props[0] + '_' + str(x._i1) + '_' + str(x._i2)
    else:
        return '_' + str(x._i1) + '_' + str(x._i2)
    
def serializeProps(props):
    """ serializeProps(props)
    Encodes the properties of an edge in a bytes string
    for efficient storing.
    """
    
    # Init data bits
    databits = b''
    
    # Create bits of data
    for prop in props:
        if isinstance(prop, float):
            tmp = np.array(prop, dtype=np.float32)
            databits += b'\x00'
            databits += tmp.tostring()
        elif isinstance(prop, int):
            tmp = np.array(prop, dtype=np.int32)
            databits += b'\x01'
            databits += tmp.tostring()
        elif isinstance(prop, Pointset):
            databits += b'\x09'
            databits += np.array(len(prop), dtype=np.int32).tostring()
            databits += chr(prop.ndim).encode('utf-8')
            databits += prop.data.tostring()
        else:
            print('Warning: do not know how to store %s' % repr(prop))
    
    # Return
    return databits


def deserializeProps(bb):
    """ deserializeProps(bb)
    Set the properties by decoding them from a bytes string.
    """
    
    # Init list of properties
    props = []
    
    # Decode the string
    i = 0
    while i < len(bb):
        if bb[i] == b'\x00'[0]:
            # float
            tmp = np.frombuffer( bb[i+1:i+5], dtype=np.float32 )
            props.append( float(tmp) )
            i += 5
        elif bb[i] == b'\x01'[0]:
            # int
            tmp = np.frombuffer( bb[i+1:i+5], dtype=np.int32 )
            props.append( int(tmp) )
            i += 5
        elif bb[i] == b'\x09'[0]:
            n = np.frombuffer( bb[i+1:i+5], dtype=np.int32 )
            ndim = bb[i+5]
            if not isinstance(ndim, int): ndim = ord(ndim)
            nbytes = n*ndim*4
            tmp = np.frombuffer( bb[i+6:i+6+nbytes], dtype=np.float32 )
            tmp.shape = n, ndim
            props.append( Pointset(tmp) )
            i += 6 + nbytes
    
    # Return properties
    return props


## Functions and classes to compare graphs


class MatchingScore:
    """ MatchingScore(TP, FN, FP)
    
    Class to store a matching score using three indicaters
    represented by the matched (true-positive), missed (false-negative),
    and wrong (false-positive) amounts.
    
    The value (.val) is calculated as TP/(TP+FP+FN). Which is the
    intersection devided by the union of the two graphs. Let D=FP+FN be
    the "edit distance" between the two graphs. Then a sensible score
    measure that would scale between 0 and 1 would be 1-D/(D+TP). It can
    be shown that this is the same as TP/(TP+D).
    
    Supports equating and smaller/larger than operators (and thus sorting).
    Also supports combining matching scores by simply adding them, and
    un-combining by subtracting them.
    """
    
    def __init__(self, TP, FN, FP):
        # Calculate score and set
        if TP==0 and FP==0 and FN==0:
            val = -1 # Null matching score
        else:
            # How I had it first. Tannimoto Coefficient TC    DSC = 2*TC/(TC+1)
            #val = float(TP) / (TP+FP+FN)
            # Dice Similarity Coefficient (DSC)
            val = float(2*TP) / (2*TP + FP + FN)
        
        self.val = val
        # Store other attributes
        self.nmatch = TP
        self.nmiss = FN
        self.nwrong = FP
    
    def __lt__(self, other):
        if isinstance(other, MatchingScore): return self.val < other.val
        else: return self.val < other
    
    def __gt__(self, other):
        if isinstance(other, MatchingScore): return self.val > other.val
        else: return self.val > other
    
    def __eq__(self, other):
        if isinstance(other, MatchingScore): return self.val == other.val
        else: return self.val == other
    
    def __ne__(self, other):
        if isinstance(other, MatchingScore): return self.val != other.val
        else: return self.val != other
    
    def __repr__(self):
        formatstr = '<MatchingScore %1.2f with %i/%i/%i>'
        return formatstr % (self.val, self.nmatch, self.nmiss, self.nwrong)
    
    @property
    def value(self):
        return self.val
    
    @property
    def TP(self):
        return self.nmatch
    
    @property
    def FN(self):
        return self.nmiss
    
    @property
    def FP(self):
        return self.nwrong
    
    def toTuple(self):
        """ toTuple()
        return (self.TP, self.FN, self.FP)."""
        return (self.nmatch, self.nmiss, self.nwrong)
    
    
    def __add__(self, other):
        t = MatchingScore(self.TP+other.TP, self.FN+other.FN, self.FP+other.FP)
        return t
    
    
    def __sub__(self, other):
        t = MatchingScore(self.TP-other.TP, self.FN-other.FN, self.FP-other.FP)
        return t


def compareGraphs(graph1, graph2, maxDist):
    """ compareGraphs(graph1, graph2, maxDist)
    Compare two graphs to produce a matching score. Returns a MatchingScore
    instance.
    
    Matching and not-matching edges are counted to obtain a matching
    score. nodes should be closer than maxDist to be considered 'at the
    same location'.
    """
    
    # Check graphs
    if not graph1 or not graph2:
        print('Warning: one of the graphs to compare is empty.')
        return MatchingScore(0,1,0)
        #raise ValueError('One of the graphs to compare is empty.')
    
    # Create pointsets of the nodes
    pp1 = Pointset(3)
    for node in graph1:
        pp1.append(node)
    pp2 = Pointset(3)
    for node in graph2:
        pp2.append(node)
    
    # Match the nodes of graph1 to graph2
    for node in graph1:
        dists = node.distance(pp2)
        i, = np.where(dists==dists.min())
        node.match = None
        if len(i):
            i = int(i[0])
            dist = float(dists[i])
            if dist < maxDist:
                node.match = graph2[i]
#         if not hasattr(node, 'dontCare'):
#             node.dontCare = False
    
    # Match the nodes of graph2 to graph1
    for node in graph2:
        dists = node.distance(pp1)
        i, = np.where(dists==dists.min())
        node.match = None
        if len(i):
            i = int(i[0])
            dist = float(dists[i])
            if dist < maxDist:
                node.match = graph1[i]
#         if not hasattr(node, 'dontCare'):
#             node.dontCare = False
    
    # Init amounts
    nmatch1, nmatch2, nmiss, nwrong = 0,0,0,0
    
    # Count matches and wrongs
    for c in graph1.GetEdges():
        end1 = c.end1.match
        end2 = c.end2.match
        if end1 and end2:
            if end1 in end2.GetNeighbours():
                nmatch1 += 1
                continue
#         elif c.end1.dontCare or c.end2.dontCare:
#             continue
        nwrong += 1
    
    # todo: use dontCare 'beleid' or not?
    
    # Count matches and misses
    for c in graph2.GetEdges():
        end1 = c.end1.match
        end2 = c.end2.match
        if end1 and end2:
            if end1 in end2.GetNeighbours():
                nmatch2 += 1
                continue
#         elif c.end1.dontCare or c.end2.dontCare:
#             continue
        nmiss += 1
    
    # Compose score
    return MatchingScore(nmatch1, nmiss, nwrong)


def compareGraphsVisually(graph1, graph2, fig=None):
    """ compareGraphsVisually(graph1, graph2, fig=None)
    Show the two graphs together in a figure. Matched nodes are
    indicated by lines between them.
    """
    
    # Get figure
    if isinstance(fig,int):
        fig = vv.figure(fig)
    elif fig is None:
        fig = vv.figure()
    
    # Prepare figure and axes
    fig.Clear()
    a = vv.gca()
    a.cameraType = '3d'; a.daspectAuto = False
    
    # Draw both graphs
    graph1.Draw(lc='b', mc='b')
    graph2.Draw(lc='r', mc='r')
    
    # Set the limits
    a.SetLimits()
    
    # Make a line from the edges
    pp = Pointset(3)
    for node in graph1:
        if hasattr(node, 'match') and node.match is not None:
            pp.append(node); pp.append(node.match)
    
    # Plot edges
    vv.plot(pp, lc='g', ls='+')


if __name__ == '__main__':
    # Example
    
    # Create graph with nodes
    g = Graph()
    n1 = g.AppendNode(3,4)
    n2 = g.AppendNode(5,7)
    n3 = g.AppendNode(3,8)
    n4 = g.AppendNode(2,5)
    n5 = g.AppendNode(4,6)
    
    # Define connections
    g.CreateEdge(n1, n2)
    g.CreateEdge(n2, n3)
    g.CreateEdge(n1, n4)
    g.CreateEdge(n2, n4)
    g.CreateEdge(n1, n5)
    
    # Draw it
    vv.clf()
    a = vv.gca()
    g.Draw(lc='b')
    a.camera = 2
    a.SetLimits()
    
    # Get some info
    print(g.GetEdges())
