"""Methods for dynamic network."""

import sys
import numpy as np
from collections import deque

def eventBetweenness_plain(events, events_reversed=None, 
                           nodeBetweenness=None,
                           include_path_ends=False):
    """Calculate the event betweenness of all events.

    The event betweenness is defined as the total number of
    time-respecting paths that go through an event.

    Parameters
    ----------
    events : sequence of tuples (int, int, int)
        A sequence of events where each event is a tuple (t, i, j),
        meaning that an event takes place at time t between nodes i
        and j. Events are undirected. `events` must be sorted by time
        in increasing order.
    events_reversed : iterable (default: None)
        Normally it should be possible to iterate through `events` in
        reversed order. If this is difficult to arrange, you can
        supply `events_reversed` which is then used to go through the
        events in reversed order. In this case `events` can be any
        iterable object.
    nodeBetweenness : dict (default: None)
        If an empty dictionary is given, node event betweenness will
        be calculated and saved in it, with a key corresponding to the
        node id.
    include_path_ends : bool (default: False)
        If True, the ends of the paths are included when calculating
        the node event betweenness. Otherwise only paths that go
        _through_ the node are counted.

    Yield
    -----
    (t, event_betweenness) : (int, int)
        At each iteration an event time is returned with the
        corresponding event betweenness. The values are returned in
        the same order as in `events`.

    Notes
    -----
    Both the time and space complexity of this algorithm are linear.
    """

    # Preprocessing:
    if events_reversed is None:
        events_reversed = reversed(events)

    # Phase I: Build the number of leaving paths.
    #sys.stderr.write("Phase I: Build the number of leaving paths.\n")
    L_count = {}
    L_diff = deque()
    for counter, (t, i, j) in enumerate(events_reversed):
        l_i = L_count.setdefault(i, 0)
        l_j = L_count.setdefault(j, 0)
        c_new = l_i + l_j + 1
        L_diff.append((c_new-l_i, c_new-l_j))
        L_count[i] = L_count[j] = c_new
        #if (counter % 10000) == 0:
        #    sys.stderr.write("Event %d: (%d, %d)\n" % (counter,l_i,l_j))

    # Phase II: Calculate event betweenness.
    #sys.stderr.write("Phase II: Calculate event betweenness.\n")
    A_count = {}
    for counter, (t, i, j) in enumerate(events):
        # Invariants:
        #   A_count[i] contains the number of paths arriving at node i
        #   before the current event.
        #   L_count[i] contains the number of paths leaving from node i
        #   at or after the current event.

        # Get the number of paths arriving to nodes i and j before the
        # current event.
        a_i = A_count.setdefault(i, 0)
        a_j = A_count.setdefault(j, 0)

        # Update L_count to get the number of leaving paths after the
        # current event.
        i_update, j_update = L_diff.pop()
        L_count[i] -= i_update
        L_count[j] -= j_update
        l_i, l_j = L_count[i], L_count[j]

        # FOR DEBUGGING:
        #print ("t = %d, Arr(%d) = %d, Lea(%d) = %d, Arr(%d) = %d, Lea(%d) = %d" 
        #       % (t, i, a_i, i, l_i, j, a_j, j, l_j))

        # Calculate node betweenness if required. Count only paths
        # arriving at node i via the current event; this way each
        # path is only counted once.
        if nodeBetweenness is not None:
            nb_i = nodeBetweenness.setdefault(i,0) + a_j*l_i + l_i
            nb_j = nodeBetweenness.setdefault(j,0) + a_i*l_j + l_j
            if include_path_ends:
                # Add the contribution of paths starting from or
                # ending at the current event. Because no other
                # adjacent event is involved in these paths, there is
                # no risk of counting them twice.
                nb_i += a_j + l_j
                nb_j += a_i + l_i
            nodeBetweenness[i] = nb_i
            nodeBetweenness[j] = nb_j

        # Yield edge betweenness.
        yield t, a_i*l_j + a_j*l_i + a_i + a_j + l_i + l_j

        # Update the number of paths arriving to nodes i and j at or
        # before the current event.
        c_new = a_i + a_j + 1
        A_count[i] = A_count[j] = c_new 

        #if (counter % 10000) == 0:
        #    sys.stderr.write("Event %d: (%d, %d)\n" % (counter,l_i,l_j))



def eventBetweenness_dieoff(events, events_reversed=None, nodeBetweenness=None,
                            include_path_ends=False, die_off=0.8):
    """Calculate the event betweenness of all events with a die-off.

    The event betweenness is defined as the total number of
    time-respecting paths that go through an event. The contribution
    of the path is decreased by a factor given by `die_off` for each
    event the path passes through.

    Parameters
    ----------
    events : sequence of tuples (int, int, int)
        A sequence of events where each event is a tuple (t, i, j),
        meaning that an event takes place at time t between nodes i
        and j. Events are undirected. `events` must be sorted by time
        in increasing order.
    events_reversed : iterable (default: None)
        Normally it should be possible to iterate through `events` in
        reversed order. If this is difficult to arrange, you can
        supply `events_reversed` which is then used to go through the
        events in reversed order. In this case `events` can be any
        iterable object.
    nodeBetweenness : dict (default: None)
        If an empty dictionary is given, node event betweenness will
        be calculated and saved in it, with a key corresponding to the
        node id.
    include_path_ends : bool (default: False)
        If True, the ends of the paths are included when calculating
        the node event betweenness. Otherwise only paths that go
        _through_ the node are counted.
    die_off : float (default: 0.8, must be in (0,1))
        Factor by which the contribution of each path is decreased for
        each new event.

    Yield
    -----
    (t, event_betweenness) : (int, float)
        At each iteration an event time is returned with the
        corresponding event betweenness. The values are returned in
        the same order as in `events`.

    Notes
    -----
    Both the time and space complexity of this algorithm are linear.
    """

    # Preprocessing:
    if events_reversed is None:
        events_reversed = reversed(events)

    # Phase I: Build the number of leaving paths.
    #sys.stderr.write("Phase I: Build the number of leaving paths.\n")
    L_count = {}
    L_diff = deque()
    for counter, (t, i, j) in enumerate(events_reversed):
        l_i = L_count.setdefault(i, 0)
        l_j = L_count.setdefault(j, 0)
        #c_new = l_i + l_j + 1
        l_i_new = 1 + l_i + die_off*l_j
        l_j_new = 1 + l_j + die_off*l_i
        L_diff.append((l_i_new - l_i, l_j_new - l_j))
        L_count[i] = l_i_new
        L_count[j] = l_j_new
        #if (counter % 10000) == 0:
        #    sys.stderr.write("Event %d: (%d, %d)\n" % (counter,l_i,l_j))

    # Phase II: Calculate event betweenness.
    #sys.stderr.write("Phase II: Calculate event betweenness.\n")
    A_count = {}
    for counter, (t, i, j) in enumerate(events):
        # Invariants:
        #   A_count[i] contains the number of paths arriving at node i
        #   before the current event.
        #   L_count[i] contains the number of paths leaving from node i
        #   at or after the current event.

        # Get the number of paths arriving to nodes i and j before the
        # current event.
        a_i = A_count.setdefault(i, 0)
        a_j = A_count.setdefault(j, 0)

        # Update L_count to get the number of leaving paths after the
        # current event.
        i_update, j_update = L_diff.pop()
        L_count[i] -= i_update
        L_count[j] -= j_update
        l_i, l_j = L_count[i], L_count[j]

        # FOR DEBUGGING:
        #print ("t = %d, Arr(%d) = %d, Lea(%d) = %d, Arr(%d) = %d, Lea(%d) = %d" 
        #       % (t, i, a_i, i, l_i, j, a_j, j, l_j))

        # Calculate node betweenness if required. Count only paths
        # arriving at node i via the current event; this way each
        # path is only counted once.
        if nodeBetweenness is not None:
            nb_i = nodeBetweenness.setdefault(i,0) + a_j*l_i + l_i
            nb_j = nodeBetweenness.setdefault(j,0) + a_i*l_j + l_j
            if include_path_ends:
                # Add the contribution of paths starting from or
                # ending at the current event. Because no other
                # adjacent event is involved in these paths, there is
                # no risk of counting them twice.
                nb_i += a_j + l_j
                nb_j += a_i + l_i
            nodeBetweenness[i] = nb_i
            nodeBetweenness[j] = nb_j

        # Yield edge betweenness.
        yield t, a_i*l_j + a_j*l_i + a_i + a_j + l_i + l_j

        # Update the number of paths arriving to nodes i and j at or
        # before the current event.
        a_i_new = 1 + a_i + die_off*a_j
        a_j_new = 1 + a_j + die_off*a_i
        A_count[i] = a_i_new
        A_count[j] = a_j_new

        #if (counter % 10000) == 0:
        #    sys.stderr.write("Event %d: (%d, %d)\n" % (counter,a_i,a_j))



def eventBetweenness(events, tau, delta, N_events=None, max_node_ID=None,
                     events_reversed=None, nodeBetweenness=None,
                     include_path_ends=False):
    """Calculate the event betweenness of all events.

    The event betweenness is defined as the total number of
    time-respecting paths that go through an event. The contribution
    of the path is decreased exponentially by a time, with a half_life
    given by the parameter `tau`, and by the path length, with
    attenuation `delta`**(n-1), where n is the path length.

    Parameters
    ----------
    events : sequence of tuples (int, int, int)
        A sequence of events where each event is a tuple (t, i, j),
        meaning that an event takes place at time t between nodes i
        and j. Events are undirected. `events` must be sorted by time
        in increasing order.
    tau : int or float
        The half-life of paths given in the units of time in
        `events`. The effective number of paths decreases
        exponentially with time, so that a path at current time is
        counted as 1 and a path `tau` time steps away is counted as
        0.5.
    delta : float (default: 1.0, must be in [0.0, 1.0])
        Factor by which the contribution of each path is decreased for
        each new event. Value 0.0 means that only events incident to
        or on the same edge are taken into account, and 1.0 means that
        there is no attenuation by path length.
    N_events : int (default: None)
        The number of events. If not given, len(events) will be used,
        and an error occurs if this is not possible.
    max_node_ID : int (default: None)
        The largest node index + 1. If the nodes are labeled from 0 to
        N-1, this corresponds to the number of nodes. If not given,
        the value will be found by going through `events`, which could
        be slow for large data sets.
    events_reversed : iterable (default: None)
        Normally it should be possible to iterate through `events` in
        reversed order. If this is difficult to arrange, you can
        supply `events_reversed` which is then used to go through the
        events in reversed order. In this case `events` can be any
        iterable object.
    nodeBetweenness : dict (default: None)
        If an empty dictionary is given, node event betweenness will
        be calculated and saved in it, with a key corresponding to the
        node id.
    include_path_ends : bool (default: False)
        If True, the ends of the paths are included when calculating
        the node event betweenness. Otherwise only paths that go
        _through_ the node are counted.

    Yield
    -----
    (event_betweenness, t, i, j) : (float, int, int, int)
        At each iteration an event betweenness is returned with the
        corresponding event time and nodes (i,j). The values are
        returned in the same order as in `events`.

    Notes
    -----
    The time complexity is O(N_events), and space complexity
    O(N_events + max_node_ID).
    """
    # Preprocessing:
    tau = float(tau)
    if events_reversed is None:
        events_reversed = reversed(events)

    # Find out the number of events and nodes if not given.
    if N_events is None:
        N_events = len(events)
    if max_node_ID is None:
        max_node_ID = 0
        for t,i,j in events:
            max_node_ID = max([max_node_ID, i, j])
    max_node_ID += 1

    # Phase I: Build the number of leaving paths.

    # Note: The previous implementation used a dictionary for TL_count
    # and a collections.deque for TL_diff. While these are intuitive
    # and algorithmically good choices (constant time operations for
    # all we need and not necessary to fix sizes), the Python
    # implementations take up ridiculous amount of memory. The use of
    # numpy arrays makes the code slightly less intuitive, but the
    # operations are equally fast and the memory consumption
    # significantly smaller.

    sys.stderr.write("Phase I: Build the number of leaving paths.\n")
    TL_count = np.zeros((max_node_ID,2),dtype=np.float64)
    TL_diff = np.zeros((N_events,4),dtype=np.float64)
    for counter, (t, i, j) in enumerate(events_reversed):
        lt_i, l_i = ((t,0) if TL_count[i][0] == 0 else TL_count[i])
        lt_j, l_j = ((t,0) if TL_count[j][0] == 0 else TL_count[j])
        #c_new = l_i/2**((lt_i-t)/tau) + l_j/2**((lt_j-t)/tau) + 1
        l_i_new = 1 + l_i/2**((lt_i-t)/tau) + delta*l_j/2**((lt_j-t)/tau)
        l_j_new = 1 + delta*l_i/2**((lt_i-t)/tau) + l_j/2**((lt_j-t)/tau)
        TL_diff[-counter-1] = (lt_i-t, l_i_new-l_i, lt_j-t, l_j_new-l_j)
        TL_count[i] = (t, l_i_new)
        TL_count[j] = (t, l_j_new)
        if (counter % 10000) == 0:
            sys.stderr.write("Event %d at t = %d\n" % (counter,t))
        #print t
        #print TL_count

    # Phase II: Calculate event betweenness.
    sys.stderr.write("Phase II: Calculate event betweenness.\n")
    TA_count = np.zeros((max_node_ID,2),dtype=np.float64)
    for counter, (t, i, j) in enumerate(events):
        # Invariants:
        #   TA_count[i] contains the effective number of paths
        #   arriving at node i before the current event, and the time
        #   of the most recent arriving event.
        #   TL_count[i] contains the effective number of paths leaving
        #   from node i at or after the current event, and the time of
        #   the next leaving event.

        # Get the effective number of paths arriving to nodes i and j
        # before the current event.
        at_i, a_i = ((t,0) if TA_count[i][0] == 0 else TA_count[i])
        at_j, a_j = ((t,0) if TA_count[j][0] == 0 else TA_count[j])

        # Update L_count to get the number of leaving paths after the
        # current event (that is, exclude the current event).
        lt_i_update, i_update, lt_j_update, j_update = TL_diff[counter]
        lt_i, l_i = TL_count[i]
        lt_j, l_j = TL_count[j]
        lt_i += lt_i_update
        lt_j += lt_j_update
        l_i -= i_update
        l_j -= j_update
        TL_count[i] = (lt_i, l_i)
        TL_count[j] = (lt_j, l_j)

        #print t
        #print TL_count
        #print TA_count

        # Calculate the effective number of paths at current time.
        ea_i = a_i/2**((t-at_i)/tau)
        ea_j = a_j/2**((t-at_j)/tau)
        el_i = l_i/2**((lt_i-t)/tau)
        el_j = l_j/2**((lt_j-t)/tau)

        #print (el_i, el_j), (ea_i, ea_j)

        # FOR DEBUGGING:
        #print ("t = %d, Arr(%d) = %d, Lea(%d) = %d, Arr(%d) = %d, Lea(%d) = %d" 
        #       % (t, i, a_i, i, l_i, j, a_j, j, l_j))

        # Calculate node betweenness if required. Count only paths
        # arriving at node i via the current event; this way each
        # path is only counted once.
        if nodeBetweenness is not None:
            nb_i = nodeBetweenness.setdefault(i,0) + ea_j*el_i + el_i
            nb_j = nodeBetweenness.setdefault(j,0) + ea_i*el_j + el_j
            if include_path_ends:
                # Add the contribution of paths starting from or
                # ending at the current event. Because no other
                # adjacent event is involved in these paths, there is
                # no risk of counting them twice.
                nb_i += ea_j + el_j
                nb_j += ea_i + el_i
            nodeBetweenness[i] = nb_i
            nodeBetweenness[j] = nb_j

        # Yield edge betweenness.
        yield ea_i*el_j + ea_j*el_i + ea_i + ea_j + el_i + el_j, t, i, j

        # Update the number of paths arriving to nodes i and j at or
        # before the current event.
        a_i_new = 1 + a_i/2**((t-at_i)/tau) + delta*a_j/2**((t-at_j)/tau)
        a_j_new = 1 + delta*a_i/2**((t-at_i)/tau) + a_j/2**((t-at_j)/tau)
        TA_count[i] = (t, a_i_new)
        TA_count[j] = (t, a_j_new)

        if (counter % 10000) == 0:
            sys.stderr.write("Event %d at t = %d: %.4f\n" % 
                             (counter,t,
                              ea_i*el_j + ea_j*el_i + ea_i + ea_j + el_i + el_j))


def eventBetweenness_PhoneEvents(events, tau, delta, nodeBetweenness=None,
                                 include_path_ends=False):
    """As eventBetweenness, but for PhoneEventsContainer object.

    Parameters
    ----------
    events : phone.PhoneEventsContainer object
        The events for which the event betweenness will be calculated.

    Other parameters and the output are identical to those in
    eventBetweenness, but because some parameters can be read from
    `events`, they need not be specified.
    """

    def event_iter(events):
        for e in events:
            yield e.time, e.fr, e.to

    def reversed_event_iter(events):
        for e in reversed(events):
            yield e.time, e.fr, e.to

    return eventBetweenness(event_iter(events), tau, delta,
                            events.numberOfEvents,
                            events.numberOfUsers,
                            reversed_event_iter(events),
                            nodeBetweenness, include_path_ends)

    

if __name__ == '__main__':
    """Run unit tests if called."""
    from tests.test_dynamics import *
    unittest.main()
