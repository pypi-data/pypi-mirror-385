from py4j.java_gateway import JavaGateway, GatewayParameters # requires py4j
from py4j.java_collections import ListConverter
from py4j.protocol import Py4JNetworkError
import json
import os

def store_selection(df, dsName:str, objectClassIdx:int, selectionName:str, indexCol:str= "Indices", positionCol:str= "Position", dsPath:str=None, showObjects:bool=False, showTracks:bool=False, openSelection:bool=False, objectClassIdxDisplay:int=-1, interactiveObjectClassIdx:int=-1, port:int=None, python_proxy_port:int=None, address:str=None, verbose=False, **gateway_parameters):
    """Stores a selection to bacmman using python gateway (py4j). Bacmman must be running with an active python gateway server.

    Parameters
    ----------
    df : pandas DataFrame
        each line of the DataFrame is one element of the selection, defined by columns Indices & Position
    dsName : str
        bacmman dataset name to store the selection to.
    dsPath : str
        path to the folder containing the bacmman dataset. Can be omitted if BACMMAN is open and dsName is a relative name to the working directory currently set in BACMMAN
    objectClassIdx : int
        index of the object class of the elements of the selection in the bacmman dataset
    selectionName : str
        name of the selection
    showObjects : bool
        whether contours of objects should be shown
    showTracks : bool
        whether track links of objects should be shown
    openSelection : bool
        whether the first kymograph of the selection should be open
    objectClassIdxDisplay : int
        if openSelection is true, object class idx of the opened kymograph
    interactiveObjectClassIdx : int
        if openSelection is true, interactive object class idx
    python_proxy_port : int
        python port of the java gateway
    """
    if port is None:
        port = int(os.getenv("PYBACMMAN_PORT", 25335))
    if python_proxy_port is None:
        python_proxy_port = int(os.getenv("PYBACMMAN_PYPROXYPORT", 25334))
    if address is None:
        address = os.getenv("PYBACMMAN_ADDRESS", '127.0.0.1')
    # fix path if called from from docker
    container_dir = os.getenv("BACMMAN_CONTAINER_DIR")
    wd = os.getenv("BACMMAN_WD")
    if container_dir is not None and wd is not None and container_dir in dsPath:
        dsPath_host = dsPath.replace(container_dir, wd)
    else:
        dsPath_host = dsPath
    if verbose:
        print(f"store_selection: name={selectionName} size={df.shape[0]} dataset={dsName}, oc={objectClassIdx} path={dsPath_host} (local path: {dsPath} container dir: {container_dir} working dir: {wd} ) gateway address={address} port: {port} proxy port: {python_proxy_port}" , flush=True)
    gateway = JavaGateway(python_proxy_port=python_proxy_port, gateway_parameters=GatewayParameters(address=address, port=port, **gateway_parameters))
    try:
        idx = ListConverter().convert(df[indexCol].tolist(), gateway._gateway_client)
        pos = ListConverter().convert(df[positionCol].tolist(), gateway._gateway_client)
        gateway.saveCurrentSelection(dsName, dsPath_host, objectClassIdx, selectionName, idx, pos, showObjects, showTracks, openSelection, False, objectClassIdxDisplay, interactiveObjectClassIdx)
    except Py4JNetworkError as err:
        print("Could not connect, is BACMMAN started? Check that Python Gateway parameters match (BACMMAN menu MISC>Python Gateway)")
        print(err)
        if dsPath is None:
            print("path to dataset dsPath must be provided to save selection as a file")
            print(err)
        else:  # try to fallback to saveSelectionFile method if dsPath is provided
            print(f"Could not connect through python gateway, saving selection as a file to {dsPath}")
            store_selection_file(df, dsPath=dsPath, objectClassIdx=objectClassIdx, selectionName=selectionName, indexCol=indexCol, positionCol=positionCol)

def store_selection_file(df, dsPath:str, objectClassIdx:int, selectionName:str, indexCol:str= "Indices", positionCol:str= "Position"):
    data = {
        "name": selectionName,
        "objectClassIdx": objectClassIdx,
        "objects": {position : list(g[indexCol]) for position, g in df.groupby(positionCol)}
    }
    json_object = json.dumps(data)
    sel_path = os.path.join(dsPath, "Output", "Selections")
    assert os.path.exists(dsPath), f"dataset path not found: {dsPath} cannot save selection"
    if not os.path.exists(sel_path): # check path and create if necessary
        os.makedirs(sel_path, exist_ok=True)
        if not os.path.exists(sel_path):
            print(f"could not create selection dir: {sel_path}, cannot save selection")
    file_path = os.path.join(sel_path, selectionName + ".json")
    with open(file_path, "w") as outfile:
        outfile.write(json_object)
