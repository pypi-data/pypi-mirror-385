import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import asyncio
    import os

    import marimo as mo

    os.putenv("LOG_LEVEL", "WARNING")
    return asyncio, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # Notebook to test Control Servers using Marimo

    Make sure the CGSE core services are running.
    """
    )
    return


@app.cell
def _(asyncio, mo):
    from egse.async_control import AsyncControlServer

    mo.md("""
    Start the control server and keep it running in the background as an `asyncio` Task.

    The server will be stooped by an `AsyncControlClient`, but the Task needs to be awaited 
    at the end of the notebook.
    """)

    server = AsyncControlServer()
    server_task = asyncio.create_task(server.start())
    return (server_task,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r""" """)
    return


@app.cell
async def _():
    from egse.registry.client import AsyncRegistryClient

    with AsyncRegistryClient() as _reg:
        _services = await _reg.list_services()
        print([x["name"] for x in _services])
    return


@app.cell
async def _():
    from egse.async_control import AsyncControlClient
    from egse.async_control import CONTROL_SERVER_SERVICE_TYPE

    client = await AsyncControlClient.create(service_type=CONTROL_SERVER_SERVICE_TYPE)
    client.connect()
    return CONTROL_SERVER_SERVICE_TYPE, client


@app.cell
async def _(client):
    _response = await client.ping()
    print(f"{_response=}")
    return


@app.cell
async def _(client):
    _response = await client.info()
    print(f"{_response=}")
    return


@app.cell
async def _(CONTROL_SERVER_SERVICE_TYPE):
    from egse.async_control import is_control_server_active

    _is_active = await is_control_server_active(service_type=CONTROL_SERVER_SERVICE_TYPE)
    print(f"Server status: {'active' if _is_active else 'unreachable'}")
    return (is_control_server_active,)


@app.cell
async def _(client):
    _response = await client.stop_server()
    print(f"{_response=}")
    return


@app.cell
async def _(
    CONTROL_SERVER_SERVICE_TYPE,
    is_control_server_active,
    server_task,
):
    await server_task

    _is_active = await is_control_server_active(service_type=CONTROL_SERVER_SERVICE_TYPE)
    print(f"Server status: {'active' if _is_active else 'unreachable'}")
    return


if __name__ == "__main__":
    app.run()
