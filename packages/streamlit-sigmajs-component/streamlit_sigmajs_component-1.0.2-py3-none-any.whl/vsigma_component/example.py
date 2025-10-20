import json
import random
import streamlit as st
from vsigma_component import vsigma_component


# Default settings

DEBUG = False
ENABLE_FILTERS = True
EXPERIMENTAL_FLAG = True  # Enable experimental features
PROFILE = False  # Enable profiling

import cProfile
import pstats
from io import StringIO
pr = cProfile.Profile()
if PROFILE:
    print("Start profiling...")
    pr.enable()

# Streamlit App Settings

st.set_page_config(
    layout = 'wide',
    page_title = 'Network Viz'
)

# State Variables

ss = st.session_state
if 'sigmaid' not in ss:
    ss.sigmaid = 0
if 'hidden_attributes' not in ss:
    ss.hidden_attributes = [
        # 'x', 'y',
        'type',
        'size', 'color', 'image',
        'label','hidden', 'forceLabel',
        'zIndex', 'index'
    ]

if 'draw_count' not in ss:
    ss.draw_count = 0

if "positions" not in ss:
    ss.positions = {}

if "node_filters" not in ss:
    if "kind_of_nodes_filters" in ss:
        ss.node_filters = ss.kind_of_nodes_filters
    else:
        ss.node_filters = []
if "edge_filters" not in ss:
    if "kind_of_edges_filters" in ss:
        ss.edge_filters = ss.kind_of_edges_filters
    else:
        ss.edge_filters = []

ss.graph_state = {} # holds the VSigma internal state data

# Helper Functions

list_nodes_html = '--'
def list_nodes(state):
    data = ss.graph_state["state"].get('lastselectedNodeData', {})
    list_nodes_html = [
        n['key'] + ' : ' + ', '.join(
            [att + '=' + n['attributes'][att] for att in n['attributes']]
        )
        for n in ss.my_nodes if n['attributes']['nodetype']==data['nodetype']
    ]
    return list_nodes_html
list_edges_html = '--'
def list_edges(state):
    data = ss.graph_state["state"].get('lastselectedEdgeData', {})
    list_edges_html = [
        n['key'] + ' : ' + ', '.join(
            [att + '=' + n['attributes'][att] for att in n['attributes']]
        )
        for n in ss.my_edges if n['attributes']['edgetype']==data['edgetype']
    ]
    return list_edges_html

# Customize nodes and edges features based on their type (or other attributes)
def customize_node(node):
    kind = node['attributes']['nodetype']
    if kind == 'A':
        node['color'] = 'red'
        node['size'] = 5
        node['image'] = 'https://cdn.iconscout.com/icon/free/png-256/atom-1738376-1470282.png'
        node['label'] = node.get('label', node['key'])

    return node
def customize_edge(edge):
    kind = edge['attributes']['edgetype']
    if kind == 'A':
        edge['color'] = 'red'
        edge['size'] = 1
        edge['type'] = edge.get('type', 'arrow') # arrow, line
        edge['label'] = edge.get('label', edge['key'])

    return edge

def customize_nodes_edges():
    for node in ss.my_nodes:
        customize_node(node)
    for edge in ss.my_edges:
        customize_edge(edge)

def addNode():
    nid = 'N' + str(len(ss.my_nodes)+1).rjust(3, '0')
    eid = 'R' + str(len(ss.my_edges)+1).rjust(3, '0')
    rnid = 'N' + str(1+int(len(ss.my_nodes)*random.random())).rjust(3, '0')

    st.write(f"Add Node {nid}, connect to {rnid}")
    print(f"Add Node {nid}, connect to {rnid}")

    new_node = {
        "key": nid,
        "attributes": {
            "nodetype": "Person",
            "label": "New Person",
            "color": "blue",
            "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
    }
    new_edge = {
        "key": eid,
        "source": rnid,
        "target": nid,
        "attributes": {
            "edgetype": "Person-Person",
            "label": "New Edge"
        }
    }

    new_node = customize_node(new_node)
    new_edge = customize_edge(new_edge)

    ss.my_nodes.append(new_node)
    ss.my_edges.append(new_edge)
    if ENABLE_FILTERS: 
        if new_node['attributes']['nodetype'] in ss.node_filters:
            ss.my_filtered_nodes.append(new_node)
        if new_edge['attributes']['edgetype'] in ss.edge_filters:
            ss.my_filtered_edges.append(new_edge)
    ss.positions[new_node['key']] = { "x": random.random(), "y": random.random() }

def removeRandomNode():
    if len(ss.my_nodes) > 0:
        nid = random.choice(ss.my_nodes)['key']
        st.write(f"Remove Node {nid} and its edges")
        print(f"Remove Node {nid} and its edges")
        ss.my_nodes = [n for n in ss.my_nodes if n['key'] != nid]
        ss.my_filtered_nodes = [n for n in ss.my_filtered_nodes if n['key'] != nid]
        ss.my_edges = [e for e in ss.my_edges if e['source'] != nid and e['target'] != nid]
        ss.my_filtered_edges = [e for e in ss.my_filtered_edges if e['source'] != nid and e['target'] != nid]
        if nid in ss.positions:
            del ss.positions[nid]

def removeRandomEdge():
    if len(ss.my_edges) > 0:    
        eid = random.choice(ss.my_edges)['key']
        st.write(f"Remove Edge {eid}")
        print(f"Remove Edge {eid}")
        ss.my_edges = [e for e in ss.my_edges if e['key'] != eid]
        ss.my_filtered_edges = [e for e in ss.my_filtered_edges if e['key'] != eid]

# LOAD DATA, 'local data' or fallback 'test data' imports, only run once
def load_or_reuse_data(force=False):
    if force or not('my_nodes' in st.session_state and 'my_edges' in st.session_state):
        data = None
        try:
            from local_data import localdata as data
        except:
            data = None
            try:
                from test_data import testdata as data
            except:
                data = None
        if data is None:
            ss.my_nodes = [n for n in data['nodes']]
            ss.kind_of_nodes_filters = data['node_filters']
            ss.my_edges = [e for e in data['edges']]
            ss.kind_of_edges_filters = data['edge_filters']
            ss.my_settings = data['settings']
        else:
            ss.my_nodes = [n for n in data['nodes']]
            ss.kind_of_nodes_filters = data['node_filters']
            ss.my_edges = [e for e in data['edges']]
            ss.kind_of_edges_filters = data['edge_filters']
            ss.my_settings = data['settings']
        
        for node in ss.my_nodes:
            customize_node(node)
        for edge in ss.my_edges:
            customize_edge(edge)

        ss.my_filtered_nodes = ss.my_nodes
        ss.my_filtered_edges = ss.my_edges

load_or_reuse_data()

# PAGE LAYOUT

st.subheader("VSigma Component Demo App")
st.markdown("This is a VSigma component. It is a simple component that displays graph network data. It is a good example of how to use the VSigma component.")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

# Graph and Customize

if EXPERIMENTAL_FLAG:
    tab_graph, tab_filters, tab_customize, tab_experimental = st.tabs(["Graph", "Filters", "Customize", "Experimental Features"])
else:
    tab_graph, tab_filters, tab_customize = st.tabs(["Graph", "Filters", "Customize"])

if EXPERIMENTAL_FLAG:
    with tab_experimental:

        # Experimental features

        if EXPERIMENTAL_FLAG:
            st.markdown("### Experimental features")
            st.markdown("These features are experimental and may not work as expected.")
            st.markdown("They are not enabled by default, you can enable them in the code.")

            if st.button("Add Node", key="add_node"):
                addNode()
                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Nodes and edges were added. Reloading component ...")

            if st.button("Remove Random Node", key="remove_node"):
                removeRandomNode()
                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Node was removed. Reloading component ...")

            if st.button("Remove Random Edge", key="remove_edge"):
                removeRandomEdge()
                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Edge was removed. Reloading component ...")

            if st.button("Reset data", key="reset_data"):
                ss.my_nodes = None
                ss.kind_of_nodes_filters = None
                ss.my_edges = None
                ss.kind_of_edges_filters = None
                ss.my_settings = None

                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Data was added. Reloading component ...")

                load_or_reuse_data(force=True)

with tab_filters:

    left_col, center_col, right_col = st.columns([1,4,1], gap="small")

    with center_col:

        if ENABLE_FILTERS:
            # TODO: handle consistency and remove unlinked nodes
            filters_flag = st.toggle("Use Filters", False)
            if filters_flag:
                # ss.edge_filters = st.pills("Edge filters:", options=kind_of_edges_filters, default=kind_of_edges_filters, key="edgefilters", selection_mode="multi")
                # ss.node_filters = st.pills("Node filters (be carefull for inconsistency with edge filter):", options=kind_of_nodes_filters, default=kind_of_nodes_filters, key="nodefilters", selection_mode="multi")
                ss.edge_filters = st.multiselect("Edge filters:", options=ss.kind_of_edges_filters, default=ss.kind_of_edges_filters, key="edgefilters")
                ss.node_filters = st.multiselect("Node filters (be carefull for inconsistency with edge filter):", options=ss.kind_of_nodes_filters, default=ss.kind_of_nodes_filters, key="nodefilters")
                # ss.sigmaid = len(ss.node_filters)*100 + len(ss.edge_filters)
                ss.my_filtered_nodes = [n for n in ss.my_nodes if n['attributes']['nodetype'] in ss.node_filters]
                ss.my_filtered_edges = [e for e in ss.my_edges if e['attributes']['edgetype'] in ss.edge_filters]

                if st.button("update graph"):
                    ss.sigmaid += 1
                    st.write(f"sigmaid updated to {ss.sigmaid}")

        else:
            ss.my_filtered_nodes = ss.my_nodes
            ss.my_filtered_edges = ss.my_edges

        if DEBUG:
            st.write("Enabled Filters:")
            if 'edge_filters' in ss:
                st.write("Edge filters:", ", ".join(ss.edge_filters))
            else:
                st.write("Edge filters: None")
            if 'node_filters' in ss:
                st.write("Node filters:", ", ".join(ss.node_filters))
            else:
                st.write("Node filters: None")

with tab_customize:

    cust_left_col, cust_center_col, cust_right_col = st.columns([1,4,1], gap="small")

    with cust_center_col:

        st.write("Base settings:")
        st.write(ss.my_settings)
        if EXPERIMENTAL_FLAG:
            st.write("Custom settings:")
            custom_settings = st.text_area(
                "Custom Settings", 
                value="", 
                height=None, 
                max_chars=None, 
                key=None, 
                help=None, 
                on_change=None, 
                args=None, 
                kwargs=None, 
                placeholder=None, 
                disabled=False, 
                label_visibility="collapsed"
            )
            if custom_settings:
                cs = custom_settings.split('\\n')
                cs = [s.strip() for s in cs]
                cs_list = []
                for setting in cs:
                    cs_split = setting.split(":")
                    if len(cs_split)>1:
                        cs_list.append(cs_split)
                st.write(cs_list)

with tab_graph:

    # Graph and details
    col_graph, col_details = st.columns([3,1], gap="small")

    with col_graph:
        ss.draw_count += 1
        if DEBUG: st.markdown(f"Draw count: {ss.draw_count} - sigmaid: {ss.sigmaid}")
        ss.graph_state, ss.sigma_component = vsigma_component(ss.my_filtered_nodes, ss.my_filtered_edges, ss.my_settings, positions=ss.positions, key="vsigma"+str(ss.sigmaid)) # add key to avoid reinit

    with col_details:

        if ss.graph_state:
            if 'state' in ss.graph_state:
                data = {}
                label = ""
                gtype = ""
                if type(ss.graph_state['state'].get('lastselectedNodeData','')) == dict:
                    data ={k:v for k,v in ss.graph_state['state'].get('lastselectedNodeData', '').items() if k not in ss.hidden_attributes}
                    label = ss.graph_state["state"].get("lastselectedNode","")
                    gtype = "node"
                if type(ss.graph_state['state'].get('lastselectedEdgeData','')) == dict:
                    data ={k:v for k,v in ss.graph_state['state'].get('lastselectedEdgeData', '').items() if k not in ss.hidden_attributes}
                    label = ss.graph_state["state"].get("lastselectedEdge","")
                    gtype = "edge"

                table_div = ''.join([
                    f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>'
                    for k,v in data.items()
                ])
                table_div = '<table>'+table_div+'</table>'
                if len(gtype) > 0:
                    st.markdown(f'''
                        <div class="card">
                        <p class="mca_node">{label} ({gtype})<br></p>
                        <div class="container">{table_div}</div>
                        </div>
                        ''', unsafe_allow_html = True
                    )
                if DEBUG:
                    if 'hidden_attributes' in ss:
                        st.write("Hidden attributes:", ", ".join(ss.hidden_attributes))

if 'state' in ss.graph_state:
    if type(ss.graph_state['state'].get('lastselectedNodeData','')) == dict:
        if st.button("List all nodes of this type.", key="list_all"):
            html = list_nodes(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{"<br>".join(html)}</div><br>', unsafe_allow_html = True)
    if type(ss.graph_state['state'].get('lastselectedEdgeData','')) == dict:
        if st.button("List all edges of this type.", key="list_all"):
            html = list_edges(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{"<br>".join(html)}</div><br>', unsafe_allow_html = True)
    if 'positions' in ss.graph_state['state']:
        if len(ss.graph_state['state']['positions'])>0:
            ss.positions = ss.graph_state['state']['positions']

# Debug information

if DEBUG:

    if st.button("update sigma id to refresh component"):
        ss.sigmaid += 1
        st.write(f"sigmaid updated to {ss.sigmaid}")

    if st.button("Test positioning"):
        # ss.positions = ss.graph_state["state"].get("positions", {})
        for pos in ss.positions.values():
            pos['x'] = pos.get('x', 0) + random.random() * 5.0 - 2.5
            pos['y'] = pos.get('y', 0) + random.random() * 5.0 - 2.5
        st.write("Added random jitter to positions...")
        st.write(ss.positions.values()[:3])
        st.write("...")

    st.write("---")
    st.write(f"sigmaid: {ss.sigmaid}")
    with st.expander("Details graph state (debug)"):
        st.write(f"vsigma id: {ss.sigmaid}")
        st.write(ss.graph_state)
    with st.expander("Details actual graph data"):
        st.write("Positions:")
        st.write(ss.positions)
        st.write("Nodes:")
        st.write(ss.my_nodes)
        st.write("Edges:")
        st.write(ss.my_edges)
        st.write("Settings:")
        st.write(ss.my_settings)
        st.write("Filtered Nodes:")
        st.write(ss.my_filtered_nodes)
        st.write("Filtered Edges:")
        st.write(ss.my_filtered_edges)

if PROFILE:
    pr.disable()
    s = StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print(s.getvalue())
    with st.expander("Profiling info"):
        st.text(s.getvalue())
    print("Ended profiling.")
