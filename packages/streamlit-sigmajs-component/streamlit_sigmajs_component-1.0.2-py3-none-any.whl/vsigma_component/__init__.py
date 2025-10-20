import os
import streamlit.components.v1 as components

PRODUCTION = True  # Set to True for production mode

if PRODUCTION:
    # PRODUCTION: points to component build directory:
    print(f'** PRO MODE ** (PRO={PRODUCTION})')
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "vue_sigma/dist")
    _c = components.declare_component(
        "vsigma_component",
        path=build_dir
    )
else:
    print(f'** DEV MODE ** (PRO={PRODUCTION})')
    _c = components.declare_component(
        # DEV: points to local dev server
        "vsigma_component",
        url="http://localhost:5173",
    )

# wrapper function
def vsigma_component(nodes, edges, settings, positions={}, key=None):
    """Create a new instance of "vsigma_component".

    Parameters
    ----------
    nodes: list
        list of nodes
    edges: list
        list of edges
    key: str or None
        An optional key that uniquely identifies this component.

    Returns
    -------
    dict
        Returns a data object with the state information of the vue_sigma (Vue3) component.
        (This is the value passed to `Streamlit.setComponentValue` on the
        frontend.)
    """
    result = _c(nodes=nodes, edges=edges, settings=settings, positions=positions,key=key, default={})
    return result, _c
