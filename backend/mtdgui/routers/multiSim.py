import logging
import time
from typing import Annotated, List
from auth import get_current_active_user
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from concurrent.futures import Future
from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Lock
from controllers import serialize_graph
from models import User, ParameterRequest
from sessions import sessions
import copy
from controllers.pools import handleRequest

logger = logging.getLogger(__name__)
print(logger)
router = APIRouter(
    prefix="/network", tags=["network"], responses={404: {"description": "Not found"}}
)

# initializing variables
futuresComplete = False
messageQueueLock = Lock()
messageQueue = []
set_params = None


@router.post("/multi-graph-params")
async def get_prams(
    params: List[ParameterRequest],
):
    global set_params
    set_params = params
    return JSONResponse(content="prams set" , status_code=status.HTTP_202_ACCEPTED)


@router.get("/multi-graph")
async def get_graph(client: Annotated[User, Depends(get_current_active_user)]):
    global set_params
    params = set_params

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(handleRequest, req) for req in params]
        results = [future.result() for future in as_completed(futures)]
        
        # print(results)
        
        logger.debug("Stopped checking futures' completion.")

        sessions[client.uuid]["snapshots"] = {
            result[0]:copy.deepcopy(result[1]["snapshots"]) for result in results
        }
        
        sessions[client.uuid]["evaluation"] = {
            result[0]:copy.deepcopy(result[1]["evaluation"]) for result in results
        }


    try:
        
        response = {
            graphNumber: [serialize_graph(graph_item) for graph_item in graph]
            for graphNumber,graph in sessions[client.uuid]["snapshots"].items()
            
        }
        
        logger.debug(f"Returning result: {response}")
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
    except IndexError:
        logger.error("Result not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Result not found"
        )


@router.get("/result/{index}")
async def get_result(
    index: int, client: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get the result of a simulation snapshot.

    Parameters
    ----------
    index : int
        The index of the snapshot to retrieve.
    client : User
        The authenticated user making the request.

    Returns
    -------
    JSONResponse
        A JSON response containing the serialized graph data.

    Raises
    ------
    HTTPException
        If the specified snapshot index is out of range.
    """
    try:
        response = [
            serialize_graph(graph)
            for graph in sessions[client.uuid]["snapshots"][index]
        ]
        # logger.debug(f"Returning result: {response}")
        return JSONResponse(content=response, status_code=status.HTTP_202_ACCEPTED)
    except IndexError:
        logger.error("Result not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Result not found"
        )


@router.get("/evaluation/{index}")
async def get_result(
    index: int, client: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get the result of a simulation evaluation.

    Parameters
    ----------
    index : int
        The index of the evaluation to retrieve.
    client : User
        The authenticated user making the request.

    Returns
    -------
    JSONResponse
        A JSON response containing the result of the evaluation.

    Raises
    ------
    HTTPException
        If the specified evaluation index is out of range.
    """
    try:
        evaluation = sessions[client.uuid]["evaluation"][index]
        response = evaluation.compromised_num()
        print(response)
        logger.debug(f"Returning result: {response}")
        return JSONResponse(content=response, status_code=status.HTTP_202_ACCEPTED)
    except IndexError:
        logger.error("Result not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Result not found"
        )


@router.post("/config")
async def get_config(
    prams: List[ParameterRequest],
    client: Annotated[User, Depends(get_current_active_user)],
) -> JSONResponse:
    """
    Handle POST request to get configuration parameters for a simulation.

    Parameters:
    -----------
    prams : List[ParameterRequest]
        A list of ParameterRequest objects containing the parameters for the simulation.
    client : Annotated[User, Depends(get_current_active_user)]
        The authenticated user making the request.

    Returns:
    --------
    JSONResponse
        A JSON response containing the stored parameters and a status code of 202 (Accepted).
    """
    print(prams)

    # Handle run parameters
    global stored_params
    run_params = [pram.run.model_dump() for pram in prams]
    stored_params = [
        {key: value for key, value in pram.items() if value is not None}
        for pram in run_params
    ]

    # #Handle config_variables
    # config_params = prams.config
    # if (item.config is not None):
    #     config_params = config_params.model_dump()
    # configs.config = configs.set_config(config_params)
    return JSONResponse(content=stored_params, status_code=status.HTTP_202_ACCEPTED)
