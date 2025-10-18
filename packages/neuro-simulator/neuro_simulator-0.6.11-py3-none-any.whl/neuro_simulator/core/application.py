# neuro_simulator/core/application.py
"""Main application file: FastAPI app instance, events, and websockets."""

import asyncio
import json
import logging
import random
import time
import os
from typing import Any, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
from starlette.websockets import WebSocketState

# --- Core Imports ---
from .config import config_manager, AppSettings
from ..core.agent_factory import create_agent
from ..core.chatbot_factory import create_chatbot
from ..agents.chatbot.core import Chatbot

# --- API Routers ---
from ..api.system import router as system_router

# --- Additional Imports for SPA Hosting ---
from importlib.resources import files  # Modern way to find package resources
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

# --- Services and Utilities ---
from ..services.audio import synthesize_audio_segment
from ..services.stream import live_stream_manager
from ..utils.logging import configure_server_logging, server_log_queue, agent_log_queue
from ..utils.process import process_manager
from ..utils.queue import (
    add_to_audience_buffer,
    add_to_neuro_input_queue,
    get_recent_audience_chats,
    is_neuro_input_queue_empty,
    get_all_neuro_input_chats,
    initialize_queues,
    get_recent_audience_chats_for_chatbot,
)
from ..utils.state import app_state
from ..utils.websocket import connection_manager
from ..utils.banner import display_banner
from .data_manager import reset_data_directories_to_defaults


# --- Logger Setup ---
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Neuro-Sama Simulator API",
    version="2.0.0",
    description="Backend for the Neuro-Sama digital being simulator.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config_manager.settings.server.client_origins  # type: ignore
    + ["http://localhost:8080", "https://dashboard.live.jiahui.cafe"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-API-Token"],
)

app.include_router(system_router)


# --- Bilibili API Proxy ---


@app.api_route(
    "/bilibili-api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy_bilibili(request: Request, path: str):
    """
    Reverse proxies requests from /bilibili-api/{path} to https://api.bilibili.com/{path}.
    This is necessary to bypass CORS restrictions on the Bilibili API when the client
    is served directly from the backend.
    """
    async with httpx.AsyncClient() as client:
        # Construct the target URL
        url = f"https://api.bilibili.com/{path}"

        # Prepare headers for the outgoing request.
        # Do NOT forward all headers from the client. Instead, create a clean
        # request with only the headers Bilibili is known to require,
        # mimicking the working Nginx configuration. This prevents potentially
        # problematic client headers from being passed through.
        headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
            "Origin": "https://www.bilibili.com",
        }

        # Read the body of the incoming request
        body = await request.body()

        # Make the proxied request
        try:
            response = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=request.query_params,
                timeout=20.0,  # Add a reasonable timeout
            )

            # Filter headers for the response to the client
            response_headers = {
                k: v
                for k, v in response.headers.items()
                if k.lower()
                not in [
                    "content-encoding",
                    "content-length",
                    "transfer-encoding",
                    "connection",
                ]
            }

            # Return the response from the Bilibili API to the client
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
            )
        except httpx.RequestError as e:
            logger.error(f"Bilibili proxy request failed: {e}")
            return Response(
                content=f"Failed to proxy request to Bilibili API: {e}", status_code=502
            )


# --- Redirect for trailing slash on dashboard ---


@app.get("/dashboard", include_in_schema=False)
async def redirect_dashboard_to_trailing_slash():
    return RedirectResponse(url="/dashboard/")


# --- Background Task Definitions ---


async def broadcast_events_task():
    """Broadcasts events from the live_stream_manager's queue to all clients."""
    while True:
        try:
            event = await live_stream_manager.event_queue.get()
            await connection_manager.broadcast(event)
            live_stream_manager.event_queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in broadcast_events_task: {e}", exc_info=True)


async def fetch_and_process_audience_chats():
    """Generates a batch of audience chat messages using the new ChatbotAgent."""
    chatbot = await create_chatbot()
    if not chatbot:
        logger.warning("Chatbot is not available or configured, skipping chat generation.")
        return
    try:
        # Get context for the chatbot
        current_neuro_speech = app_state.neuro_last_speech
        recent_history = get_recent_audience_chats_for_chatbot(limit=10)

        # Generate messages
        generated_messages = await chatbot.generate_chat_messages(
            neuro_speech=current_neuro_speech, recent_history=recent_history
        )

        if not generated_messages:
            return

        # Process and broadcast generated messages
        for chat in generated_messages:
            add_to_audience_buffer(chat)
            add_to_neuro_input_queue(chat)
            broadcast_message = {
                "type": "chat_message",
                **chat,
                "is_user_message": False,
            }
            await connection_manager.broadcast(broadcast_message)
            # Stagger the messages slightly to feel more natural
            await asyncio.sleep(random.uniform(0.2, 0.8))

    except Exception as e:
        logger.error(
            f"Error in new fetch_and_process_audience_chats: {e}", exc_info=True
        )


async def generate_audience_chat_task():
    """Periodically triggers the audience chat generation task."""
    while True:
        try:
            assert config_manager.settings is not None
            # Wait until the live phase starts
            # await app_state.live_phase_started_event.wait()

            asyncio.create_task(fetch_and_process_audience_chats())

            # Use the interval from the new chatbot config
            await asyncio.sleep(config_manager.settings.chatbot.generation_interval_sec)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in generate_audience_chat_task: {e}", exc_info=True)
            await asyncio.sleep(10)  # Avoid fast-looping on persistent errors


async def neuro_response_cycle():
    """The core response loop for the agent."""
    assert config_manager.settings is not None
    await app_state.live_phase_started_event.wait()
    agent = await create_agent()

    while True:
        try:
            selected_chats = []
            # Superchat logic
            if app_state.superchat_queue and (
                time.time() - app_state.last_superchat_time > 10
            ):
                sc = app_state.superchat_queue.popleft()
                app_state.last_superchat_time = time.time()
                await connection_manager.broadcast(
                    {"type": "processing_superchat", "data": sc}
                )

                # For BuiltinAgent and any other future agents
                selected_chats = [{"username": sc["username"], "text": sc["text"]}]

                # Clear the regular input queue to prevent immediate follow-up with normal chats
                get_all_neuro_input_chats()
            else:
                if app_state.is_first_response_for_stream:
                    add_to_neuro_input_queue(
                        {
                            "username": "System",
                            "text": config_manager.settings.neuro.initial_greeting,
                        }
                    )
                    app_state.is_first_response_for_stream = False
                elif is_neuro_input_queue_empty():
                    await asyncio.sleep(1)
                    continue

                current_queue_snapshot = get_all_neuro_input_chats()
                if not current_queue_snapshot:
                    continue
                sample_size = min(
                    config_manager.settings.neuro.input_chat_sample_size,
                    len(current_queue_snapshot),
                )
                selected_chats = random.sample(current_queue_snapshot, sample_size)

            if not selected_chats:
                continue

            response_result = await asyncio.wait_for(
                agent.process_and_respond(selected_chats), timeout=20.0
            )

            response_texts = response_result.get("final_responses", [])
            if not response_texts:
                continue

            # Push updated agent context to admin clients immediately after processing
            updated_context = await agent.get_message_history()
            await connection_manager.broadcast_to_admins(
                {
                    "type": "agent_context",
                    "action": "update",
                    "messages": updated_context,
                }
            )

            response_text = " ".join(response_texts)
            async with app_state.neuro_last_speech_lock:
                app_state.neuro_last_speech = response_text

            sentences = response_texts

            tts_id = config_manager.settings.neuro.tts_provider_id
            if not tts_id:
                logger.warning(
                    "TTS Provider ID is not set for the agent. Skipping speech synthesis."
                )
                continue

            num_responses = len(sentences)
            for i, sentence in enumerate(sentences):
                try:
                    # Synthesize audio for each sentence individually
                    synthesis_result = await synthesize_audio_segment(
                        sentence, tts_provider_id=tts_id
                    )

                    # Handle TTS timeout
                    if (
                        isinstance(synthesis_result, tuple)
                        and synthesis_result[0] == "timeout"
                    ):
                        logger.warning(
                            "TTS synthesis timed out for a sentence. Broadcasting TTS error."
                        )
                        await connection_manager.broadcast({"type": "neuro_error_signal"})
                        continue  # Move to the next sentence

                    # Handle other synthesis errors
                    if isinstance(synthesis_result, Exception):
                        raise synthesis_result

                    speech_package = {
                        "segment_id": 0,  # Each sentence is its own single-segment message
                        "text": sentence,
                        "audio_base64": synthesis_result[0],
                        "duration": synthesis_result[1],
                    }

                    # Process this single sentence as a complete speech event
                    live_stream_manager.set_neuro_speaking_status(True)
                    await connection_manager.broadcast(
                        {"type": "neuro_speech_segment", **speech_package, "is_end": False}
                    )
                    await asyncio.sleep(speech_package["duration"])
                    await connection_manager.broadcast(
                        {"type": "neuro_speech_segment", "is_end": True}
                    )
                    live_stream_manager.set_neuro_speaking_status(False)

                    # If there are more sentences to follow, apply the cooldown
                    if i < num_responses - 1:
                        cooldown_range = (
                            config_manager.settings.neuro.post_speech_cooldown_sec
                        )
                        delay = 1.0  # Fallback default
                        if isinstance(cooldown_range, list):
                            if len(cooldown_range) == 1:
                                delay = cooldown_range[0]
                            elif len(cooldown_range) >= 2:
                                min_delay = min(cooldown_range[0], cooldown_range[1])
                                max_delay = max(cooldown_range[0], cooldown_range[1])
                                delay = random.uniform(min_delay, max_delay)

                        await asyncio.sleep(delay)

                except Exception as e:
                    logger.error(
                        f"Error processing sentence '{sentence}': {e}", exc_info=True
                    )
                    # In case of an error with one sentence, signal it and try the next one
                    await connection_manager.broadcast({"type": "neuro_error_signal"})
                    live_stream_manager.set_neuro_speaking_status(
                        False
                    )  # Ensure status is reset
                    continue

        except asyncio.TimeoutError:
            logger.warning("Agent response timed out, skipping this cycle.")
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            live_stream_manager.set_neuro_speaking_status(False)
            break
        except Exception as e:
            logger.error(f"Critical error in neuro_response_cycle: {e}", exc_info=True)
            live_stream_manager.set_neuro_speaking_status(False)
            await asyncio.sleep(10)


# --- Application Lifecycle Events ---


@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup."""
    # --- Populate app_state for banner ---
    # This is done first so the banner can display status correctly.
    app_state.is_first_run = os.getenv('NEURO_SIM_FIRST_RUN') == 'true'
    app_state.work_dir = os.getenv('NEURO_SIM_WORK_DIR')
    app_state.server_host = os.getenv('NEURO_SIM_HOST', '127.0.0.1')
    app_state.server_port = os.getenv('NEURO_SIM_PORT', '8000')

    app_state.missing_providers = []
    app_state.unassigned_providers = []
    
    if config_manager.settings:
        settings = config_manager.settings
        if not settings.llm_providers:
            app_state.missing_providers.append("LLM Providers")
        if not settings.tts_providers:
            app_state.missing_providers.append("TTS Providers")

        if not settings.neuro.neuro_llm_provider_id:
            app_state.unassigned_providers.append("Neuro Actor LLM")
        if not settings.neuro.neuro_memory_llm_provider_id:
            app_state.unassigned_providers.append("Neuro Memory LLM")
        if not settings.neuro.tts_provider_id:
            app_state.unassigned_providers.append("Neuro TTS")
        if not settings.chatbot.chatbot_llm_provider_id:
            app_state.unassigned_providers.append("Chatbot Actor LLM")
        if not settings.chatbot.chatbot_memory_llm_provider_id:
            app_state.unassigned_providers.append("Chatbot Memory LLM")

        app_state.using_default_password = (
            settings.server.panel_password == "your-secret-api-token-here"
        )

    # --- Custom Exception Handler for Benign Connection Errors ---
    # This is to suppress the benign "ConnectionResetError" that asyncio's Proactor
    # event loop on Windows logs when a client disconnects abruptly. This error is
    # not catchable at the application level, so we handle it here.
    loop = asyncio.get_event_loop()

    def custom_exception_handler(loop, context):
        exception = context.get("exception")
        if isinstance(exception, ConnectionResetError):
            logger.debug(
                f"Suppressing benign ConnectionResetError: {context.get('message')}"
            )
        else:
            # If it's not the error we want to suppress, call the default handler.
            # This ensures other important errors are still logged.
            loop.default_exception_handler(context)

    loop.set_exception_handler(custom_exception_handler)

    # --- Mount Frontend ---
    # This logic is placed here to run at runtime, ensuring all package paths are finalized.

    class SPAStaticFiles(StaticFiles):
        async def get_response(self, path: str, scope):
            try:
                return await super().get_response(path, scope)
            except StarletteHTTPException as ex:
                if ex.status_code == 404:
                    return await super().get_response("index.html", scope)
                else:
                    raise ex

    try:
        # Production/Standard install: find frontend in the package
        frontend_dir_traversable = files("neuro_simulator").joinpath("dashboard")
        if not frontend_dir_traversable.is_dir():
            raise FileNotFoundError
        frontend_dir = str(frontend_dir_traversable)
        logger.info(
            f"Found frontend via package resources (production mode): '{frontend_dir}'"
        )
    except (ModuleNotFoundError, FileNotFoundError):
        # Editable/Development install: fall back to relative path from source
        logger.info(
            "Could not find frontend via package resources, falling back to development mode path."
        )
        dev_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "dashboard", "dist"
            )
        )
        if os.path.isdir(dev_path):
            frontend_dir = dev_path
            logger.info(
                f"Found frontend via relative path (development mode): '{frontend_dir}'"
            )
        else:
            frontend_dir = None

    # --- Mount Dashboard Frontend ---
    # Mount the dashboard frontend at /dashboard path (more specific) - MOUNT THIS FIRST
    if frontend_dir:
        app.mount(
            "/dashboard",
            SPAStaticFiles(directory=frontend_dir, html=True),
            name="dashboard",
        )
        logger.info("Dashboard frontend mounted at /dashboard")
    else:
        logger.error(
            "Frontend directory not found in either production or development locations."
        )

    # --- Mount Client Frontend ---
    # Mount the client frontend at / path (more general) - MOUNT THIS AFTER
    try:
        # Production/Standard install: find client frontend in the package
        client_frontend_dir_traversable = files("neuro_simulator").joinpath("client")
        if not client_frontend_dir_traversable.is_dir():
            raise FileNotFoundError
        client_frontend_dir = str(client_frontend_dir_traversable)
        logger.info(
            f"Found client frontend via package resources (production mode): '{client_frontend_dir}'"
        )
    except (ModuleNotFoundError, FileNotFoundError):
        # Editable/Development install: fall back to relative path from source
        logger.info(
            "Could not find client frontend via package resources, falling back to development mode path."
        )
        dev_client_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "client", "dist")
        )
        if os.path.isdir(dev_client_path):
            client_frontend_dir = dev_client_path
            logger.info(
                f"Found client frontend via relative path (development mode): '{client_frontend_dir}'"
            )
        else:
            client_frontend_dir = None

    if client_frontend_dir:
        app.mount(
            "/", SPAStaticFiles(directory=client_frontend_dir, html=True), name="client"
        )
        logger.info("Client frontend mounted at /")
    else:
        logger.error(
            "Client frontend directory not found in either production or development locations."
        )

    # 1. Configure logging first
    configure_server_logging()

    # 2. Initialize queues now that config is loaded
    initialize_queues()

    # 3. Initialize Chatbot Agent on startup via factory
    try:
        await create_chatbot()
    except Exception as e:
        logger.critical(
            f"Initial Chatbot agent creation failed on startup: {e}", exc_info=True
        )

    # 4. Register callbacks
    async def metadata_callback(settings: AppSettings):
        await live_stream_manager.broadcast_stream_metadata()

    config_manager.register_update_callback(metadata_callback)

    # 5. Initialize main agent (which will load its own configs)
    try:
        await create_agent()
        logger.debug("Successfully initialized agent.")
    except Exception as e:
        logger.critical(f"Agent initialization failed on startup: {e}", exc_info=True)

    logger.info("FastAPI application has started.")
    display_banner()


@app.on_event("shutdown")
def shutdown_event():
    """Actions to perform on application shutdown."""
    if process_manager.is_running:
        process_manager.stop_live_processes()
    logger.info("FastAPI application has shut down.")


# --- WebSocket Endpoints ---


@app.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    assert config_manager.settings is not None
    await connection_manager.connect(websocket)
    try:
        await connection_manager.send_personal_message(
            live_stream_manager.get_initial_state_for_client(), websocket
        )
        await connection_manager.send_personal_message(
            {
                "type": "update_stream_metadata",
                **config_manager.settings.stream.model_dump(),
            },
            websocket,
        )

        initial_chats = get_recent_audience_chats(
            config_manager.settings.server.initial_chat_backlog_limit
        )
        for chat in initial_chats:
            await connection_manager.send_personal_message(
                {"type": "chat_message", **chat, "is_user_message": False}, websocket
            )
            await asyncio.sleep(0.01)

        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            if data.get("type") == "user_message":
                user_message = {
                    "username": data.get("username", "User"),
                    "text": data.get("text", "").strip(),
                }
                if user_message["text"]:
                    add_to_audience_buffer(user_message)
                    add_to_neuro_input_queue(user_message)
                    await connection_manager.broadcast(
                        {
                            "type": "chat_message",
                            **user_message,
                            "is_user_message": True,
                        }
                    )
            elif data.get("type") == "superchat":
                sc_message = {
                    "username": data.get("username", "User"),
                    "text": data.get("text", "").strip(),
                    "sc_type": data.get("sc_type", "bits"),
                }
                if sc_message["text"]:
                    app_state.superchat_queue.append(sc_message)

    except (WebSocketDisconnect, ConnectionResetError):
        pass
    finally:
        connection_manager.disconnect(websocket)


@app.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Add the new admin client to a dedicated list
    connection_manager.admin_connections.append(websocket)
    try:
        # Wrap initial state sending in its own try-except block.
        try:
            # Send initial state
            for log_entry in list(server_log_queue):
                await websocket.send_json({"type": "server_log", "data": log_entry})
            for log_entry in list(agent_log_queue):
                await websocket.send_json(
                    {"type": "agent_log", "data": agent_log_queue.popleft()}
                )

            agent = await create_agent()
            initial_context = await agent.get_message_history()
            await websocket.send_json(
                {
                    "type": "agent_context",
                    "action": "update",
                    "messages": initial_context,
                }
            )

            # Send initial stream status
            status = {
                "is_running": process_manager.is_running,
                "backend_status": "running"
                if process_manager.is_running
                else "stopped",
            }
            await websocket.send_json({"type": "stream_status", "payload": status})
        except (WebSocketDisconnect, ConnectionResetError):
            # If client disconnects during initial send, just exit the function.
            # The 'finally' block will ensure cleanup.
            return

        # Main loop for receiving messages from the client and pushing log updates
        while websocket.client_state == WebSocketState.CONNECTED:
            try:
                # Check for incoming messages
                try:
                    raw_data = await asyncio.wait_for(
                        websocket.receive_text(), timeout=0.01
                    )
                    data = json.loads(raw_data)
                    await handle_admin_ws_message(websocket, data)
                except asyncio.TimeoutError:
                    pass  # No message received, continue to push logs

                # Push log updates
                if server_log_queue:
                    await websocket.send_json(
                        {"type": "server_log", "data": server_log_queue.popleft()}
                    )
                if agent_log_queue:
                    await websocket.send_json(
                        {"type": "agent_log", "data": agent_log_queue.popleft()}
                    )
                await asyncio.sleep(0.1)
            except (WebSocketDisconnect, ConnectionResetError):
                # Client disconnected, break the loop to allow cleanup.
                break
    finally:
        if websocket in connection_manager.admin_connections:
            connection_manager.admin_connections.remove(websocket)
        logger.info("Admin WebSocket client disconnected.")


async def handle_admin_ws_message(websocket: WebSocket, data: dict):
    """Handles incoming messages from the admin WebSocket."""
    assert config_manager.settings is not None
    action = data.get("action")
    payload = data.get("payload", {})
    request_id = data.get("request_id")

    agent = await create_agent()
    response: Dict[str, Any] = {"type": "response", "request_id": request_id, "payload": {}}

    try:
        # Core Memory Actions
        if action == "get_core_memory_blocks":
            blocks = await agent.get_memory_blocks()
            response["payload"] = blocks

        elif action == "get_core_memory_block":
            block = await agent.get_memory_block(**payload)
            response["payload"] = block

        elif action == "create_core_memory_block":
            block_id = await agent.create_memory_block(**payload)
            response["payload"] = {"status": "success", "block_id": block_id}
            # Broadcast the update to all admins
            updated_blocks = await agent.get_memory_blocks()
            await connection_manager.broadcast_to_admins(
                {"type": "core_memory_updated", "payload": updated_blocks}
            )

        elif action == "update_core_memory_block":
            await agent.update_memory_block(**payload)
            response["payload"] = {"status": "success"}
            # Broadcast the update to all admins
            updated_blocks = await agent.get_memory_blocks()
            await connection_manager.broadcast_to_admins(
                {"type": "core_memory_updated", "payload": updated_blocks}
            )

        elif action == "delete_core_memory_block":
            await agent.delete_memory_block(**payload)
            response["payload"] = {"status": "success"}
            # Broadcast the update to all admins
            updated_blocks = await agent.get_memory_blocks()
            await connection_manager.broadcast_to_admins(
                {"type": "core_memory_updated", "payload": updated_blocks}
            )

        # Temp Memory Actions
        elif action == "get_temp_memory":
            temp_mem = await agent.get_temp_memory()
            response["payload"] = temp_mem

        elif action == "add_temp_memory":
            await agent.add_temp_memory(**payload)
            response["payload"] = {"status": "success"}
            updated_temp_mem = await agent.get_temp_memory()
            await connection_manager.broadcast_to_admins(
                {"type": "temp_memory_updated", "payload": updated_temp_mem}
            )

        elif action == "delete_temp_memory_item":
            await agent.delete_temp_memory_item(**payload)
            response["payload"] = {"status": "success"}
            updated_temp_mem = await agent.get_temp_memory()
            await connection_manager.broadcast_to_admins(
                {"type": "temp_memory_updated", "payload": updated_temp_mem}
            )

        elif action == "clear_temp_memory":
            await agent.clear_temp_memory()
            response["payload"] = {"status": "success"}
            updated_temp_mem = await agent.get_temp_memory()
            await connection_manager.broadcast_to_admins(
                {"type": "temp_memory_updated", "payload": updated_temp_mem}
            )

        # Init Memory Actions
        elif action == "get_init_memory":
            init_mem = await agent.get_init_memory()
            response["payload"] = init_mem

        elif action == "update_init_memory":
            await agent.update_init_memory(**payload)
            response["payload"] = {"status": "success"}
            updated_init_mem = await agent.get_init_memory()
            await connection_manager.broadcast_to_admins(
                {"type": "init_memory_updated", "payload": updated_init_mem}
            )

        elif action == "update_init_memory_item":
            await agent.update_init_memory_item(**payload)
            response["payload"] = {"status": "success"}
            updated_init_mem = await agent.get_init_memory()
            await connection_manager.broadcast_to_admins(
                {"type": "init_memory_updated", "payload": updated_init_mem}
            )

        elif action == "delete_init_memory_key":
            await agent.delete_init_memory_key(**payload)
            response["payload"] = {"status": "success"}
            updated_init_mem = await agent.get_init_memory()
            await connection_manager.broadcast_to_admins(
                {"type": "init_memory_updated", "payload": updated_init_mem}
            )

        # Tool Actions
        elif action == "get_all_tools":
            agent_instance = getattr(agent, "agent_instance", agent)
            all_tools = agent_instance.tool_manager.get_all_tool_schemas()
            response["payload"] = {"tools": all_tools}

        elif action == "get_agent_tool_allocations":
            agent_instance = getattr(agent, "agent_instance", agent)
            allocations = agent_instance.tool_manager.get_allocations()
            response["payload"] = {"allocations": allocations}

        elif action == "set_agent_tool_allocations":
            agent_instance = getattr(agent, "agent_instance", agent)
            allocations_payload = payload.get("allocations", {})
            agent_instance.tool_manager.set_allocations(allocations_payload)
            response["payload"] = {"status": "success"}
            # Broadcast the update to all admins
            updated_allocations = agent_instance.tool_manager.get_allocations()
            await connection_manager.broadcast_to_admins(
                {
                    "type": "agent_tool_allocations_updated",
                    "payload": {"allocations": updated_allocations},
                }
            )

        elif action == "reload_tools":
            agent_instance = getattr(agent, "agent_instance", agent)
            agent_instance.tool_manager.reload_tools()
            response["payload"] = {"status": "success"}
            # Broadcast an event to notify UI to refresh tool lists
            all_tools = agent_instance.tool_manager.get_all_tool_schemas()
            await connection_manager.broadcast_to_admins(
                {"type": "available_tools_updated", "payload": {"tools": all_tools}}
            )

        elif action == "execute_tool":
            result = await agent.execute_tool(**payload)
            response["payload"] = {"result": result}

        # Stream Control Actions
        elif action == "start_stream":
            # --- Pre-flight validation checks ---
            settings = config_manager.settings

            # 1. Check if provider lists are defined
            if not settings.llm_providers:
                raise ValueError("No LLM Providers have been defined. Please add one in the settings.")
            if not settings.tts_providers:
                raise ValueError("No TTS Providers have been defined. Please add one in the settings.")

            # 2. Create sets of defined provider IDs for efficient lookup
            defined_llm_ids = {p.provider_id for p in settings.llm_providers}
            defined_tts_ids = {p.provider_id for p in settings.tts_providers}

            # 3. Check all required LLM provider assignments
            required_llm_fields = {
                "Neuro Actor": settings.neuro.neuro_llm_provider_id,
                "Neuro Memory": settings.neuro.neuro_memory_llm_provider_id,
                "Chatbot Actor": settings.chatbot.chatbot_llm_provider_id,
                "Chatbot Memory": settings.chatbot.chatbot_memory_llm_provider_id,
            }

            for name, provider_id in required_llm_fields.items():
                if not provider_id:
                    raise ValueError(f"{name} does not have an LLM Provider configured.")
                if provider_id not in defined_llm_ids:
                    raise ValueError(
                        f"'{name}' is configured with provider ID '{provider_id}', but no such provider is defined in the LLM Providers list."
                    )
            
            # 4. Check TTS assignment
            tts_provider_id = settings.neuro.tts_provider_id
            if not tts_provider_id:
                raise ValueError("Agent (Neuro) does not have a TTS Provider configured.")
            if tts_provider_id not in defined_tts_ids:
                raise ValueError(
                    f"Agent (Neuro) is configured with TTS provider ID '{tts_provider_id}', but no such provider is defined in the TTS Providers list."
                )

            logger.info("Start stream action received. Resetting agent and chatbot memory...")
            agent = await create_agent()
            await agent.reset_memory()
            chatbot = await create_chatbot()
            if chatbot:
                await chatbot.reset_memory()
                if isinstance(chatbot, Chatbot):
                    await chatbot.initialize_runtime_components()

            if not process_manager.is_running:
                process_manager.start_live_processes()
            response["payload"] = {"status": "success", "message": "Stream started"}
            # Broadcast stream status update
            status = {
                "is_running": process_manager.is_running,
                "backend_status": "running"
                if process_manager.is_running
                else "stopped",
            }
            await connection_manager.broadcast_to_admins(
                {"type": "stream_status", "payload": status}
            )

        elif action == "stop_stream":
            if process_manager.is_running:
                await process_manager.stop_live_processes()
            response["payload"] = {"status": "success", "message": "Stream stopped"}
            # Broadcast stream status update
            status = {
                "is_running": process_manager.is_running,
                "backend_status": "running"
                if process_manager.is_running
                else "stopped",
            }
            await connection_manager.broadcast_to_admins(
                {"type": "stream_status", "payload": status}
            )

        elif action == "restart_stream":
            # 1. Stop the stream
            if process_manager.is_running:
                await process_manager.stop_live_processes()
            
            await asyncio.sleep(1) # Give tasks a moment to cancel

            # 2. Start the stream (with full validation and memory reset)
            # --- Pre-flight validation checks ---
            settings = config_manager.settings

            # 1. Check if provider lists are defined
            if not settings.llm_providers:
                raise ValueError("No LLM Providers have been defined. Please add one in the settings.")
            if not settings.tts_providers:
                raise ValueError("No TTS Providers have been defined. Please add one in the settings.")

            # 2. Create sets of defined provider IDs for efficient lookup
            defined_llm_ids = {p.provider_id for p in settings.llm_providers}
            defined_tts_ids = {p.provider_id for p in settings.tts_providers}

            # 3. Check all required LLM provider assignments
            required_llm_fields = {
                "Neuro Actor": settings.neuro.neuro_llm_provider_id,
                "Neuro Memory": settings.neuro.neuro_memory_llm_provider_id,
                "Chatbot Actor": settings.chatbot.chatbot_llm_provider_id,
                "Chatbot Memory": settings.chatbot.chatbot_memory_llm_provider_id,
            }

            for name, provider_id in required_llm_fields.items():
                if not provider_id:
                    raise ValueError(f"{name} does not have an LLM Provider configured.")
                if provider_id not in defined_llm_ids:
                    raise ValueError(
                        f"'{name}' is configured with provider ID '{provider_id}', but no such provider is defined in the LLM Providers list."
                    )
            
            # 4. Check TTS assignment
            tts_provider_id = settings.neuro.tts_provider_id
            if not tts_provider_id:
                raise ValueError("Agent (Neuro) does not have a TTS Provider configured.")
            if tts_provider_id not in defined_tts_ids:
                raise ValueError(
                    f"Agent (Neuro) is configured with TTS provider ID '{tts_provider_id}', but no such provider is defined in the TTS Providers list."
                )

            logger.info("Restart stream action received. Resetting agent and chatbot memory...")
            agent = await create_agent()
            await agent.reset_memory()
            chatbot = await create_chatbot()
            if chatbot:
                await chatbot.reset_memory()
                if isinstance(chatbot, Chatbot):
                    await chatbot.initialize_runtime_components()

            if not process_manager.is_running:
                process_manager.start_live_processes()
            
            response["payload"] = {"status": "success", "message": "Stream restarted"}
            # Broadcast stream status update
            status = {
                "is_running": process_manager.is_running,
                "backend_status": "running"
                if process_manager.is_running
                else "stopped",
            }
            await connection_manager.broadcast_to_admins(
                {"type": "stream_status", "payload": status}
            )

        elif action == "get_stream_status":
            status = {
                "is_running": process_manager.is_running,
                "backend_status": "running"
                if process_manager.is_running
                else "stopped",
            }
            response["payload"] = status

        # Config Management Actions
        elif action == "get_settings_schema":
            response["payload"] = config_manager.settings.model_json_schema()

        elif action == "get_configs":
            response["payload"] = config_manager.settings.model_dump()

        elif action == "update_configs":
            await config_manager.update_settings(payload)
            updated_configs = config_manager.settings.model_dump()
            response["payload"] = updated_configs
            await connection_manager.broadcast_to_admins(
                {"type": "config_updated", "payload": updated_configs}
            )

        elif action == "reload_configs":
            await config_manager.update_settings({})
            response["payload"] = {
                "status": "success",
                "message": "Configuration reloaded",
            }
            updated_configs = config_manager.settings.model_dump()
            await connection_manager.broadcast_to_admins(
                {"type": "config_updated", "payload": updated_configs}
            )

        elif action == "reset_config_to_defaults":
            config_manager.reset_to_defaults()
            # After resetting, reload the new default config into the live app state
            if config_manager.file_path:
                config_manager.load(config_manager.file_path)
            
            response["payload"] = {
                "status": "success",
                "message": "Configuration has been reset to defaults.",
            }
            # Broadcast the update to all admins
            updated_configs = config_manager.settings.model_dump()
            await connection_manager.broadcast_to_admins(
                {"type": "config_updated", "payload": updated_configs}
            )

        elif action == "reset_data_directories":
            reset_data_directories_to_defaults()
            
            # Re-initialize agents to pick up the new default data
            agent = await create_agent(force_recreate=True)
            chatbot = await create_chatbot(force_recreate=True)

            await agent.reset_memory()
            if chatbot:
                await chatbot.reset_memory()

            response["payload"] = {
                "status": "success",
                "message": "Data directories have been reset to defaults.",
            }
            # Broadcast updates for all memory types to refresh the UI
            await connection_manager.broadcast_to_admins(
                {
                    "type": "core_memory_updated",
                    "payload": await agent.get_memory_blocks(),
                }
            )
            await connection_manager.broadcast_to_admins(
                {
                    "type": "temp_memory_updated",
                    "payload": await agent.get_temp_memory(),
                }
            )
            await connection_manager.broadcast_to_admins(
                {
                    "type": "init_memory_updated",
                    "payload": await agent.get_init_memory(),
                }
            )
            await connection_manager.broadcast_to_admins(
                {
                    "type": "agent_context",
                    "action": "update",
                    "messages": await agent.get_message_history(),
                }
            )

        # Other Agent Actions
        elif action == "get_agent_context":
            context = await agent.get_message_history()
            response["payload"] = context

        elif action == "get_last_prompt":
            try:
                # 1. Get the recent history from the agent itself
                history = await agent.get_message_history(limit=10)

                # 2. Reconstruct the 'messages' list that _build_neuro_prompt expects
                messages_for_prompt = []
                for entry in history:
                    if entry.get("role") == "user":
                        # Content is in the format "username: text"
                        content = entry.get("content", "")
                        parts = content.split(":", 1)
                        if len(parts) == 2:
                            messages_for_prompt.append(
                                {"username": parts[0].strip(), "text": parts[1].strip()}
                            )
                        elif content:  # Handle cases where there's no colon
                            messages_for_prompt.append(
                                {"username": "user", "text": content}
                            )

                # 3. Build the prompt using the agent's own internal logic
                prompt = await agent.build_neuro_prompt(messages_for_prompt)
                response["payload"] = {"prompt": prompt}
            except Exception as e:
                logger.error(f"Error generating last prompt: {e}", exc_info=True)
                response["payload"] = {"prompt": f"Failed to generate prompt: {e}"}
        elif action == "reset_agent_memory":
            await agent.reset_memory()
            response["payload"] = {"status": "success"}
            # Broadcast updates for all memory types
            await connection_manager.broadcast_to_admins(
                {
                    "type": "core_memory_updated",
                    "payload": await agent.get_memory_blocks(),
                }
            )
            await connection_manager.broadcast_to_admins(
                {
                    "type": "temp_memory_updated",
                    "payload": await agent.get_temp_memory(),
                }
            )
            await connection_manager.broadcast_to_admins(
                {
                    "type": "init_memory_updated",
                    "payload": await agent.get_init_memory(),
                }
            )
            await connection_manager.broadcast_to_admins(
                {
                    "type": "agent_context",
                    "action": "update",
                    "messages": await agent.get_message_history(),
                }
            )

        else:
            response["payload"] = {
                "status": "error",
                "message": f"Unknown action: {action}",
            }

        # Send the direct response to the requesting client
        if request_id:
            await websocket.send_json(response)

    except Exception as e:
        logger.error(
            f"Error handling admin WS message (action: {action}): {e}", exc_info=True
        )
        if request_id:
            response["payload"] = {"status": "error", "message": str(e)}
            await websocket.send_json(response)
