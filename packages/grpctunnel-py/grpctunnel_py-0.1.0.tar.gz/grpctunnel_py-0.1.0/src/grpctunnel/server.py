# Copyright 2024 Daniel Valdivia
# Ported from the original Go implementation by Joshua Humphries
# Original: https://github.com/jhump/grpctunnel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tunnel server implementation.

This module provides the server-side implementation of the gRPC tunnel protocol,
allowing a server to accept tunnel connections and dispatch RPCs to registered
service handlers.

Based on the Go implementation by Joshua Humphries:
https://github.com/jhump/grpctunnel
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

import grpc
from grpc import aio
from google.protobuf.message import Message as ProtoMessage
from google.rpc import status_pb2

from grpctunnel.flow_control import (
    Receiver,
    Sender,
    new_receiver,
    new_receiver_without_flow_control,
    new_sender,
    new_sender_without_flow_control,
)
from grpctunnel.metadata import from_proto, to_proto
from grpctunnel.options import TunnelOptions
from grpctunnel.proto.v1 import (
    REVISION_ONE,
    REVISION_ZERO,
    ClientToServer,
    ServerToClient,
)

# Initial window size for flow control (64KB)
INITIAL_WINDOW_SIZE = 65536


@dataclass
class MethodHandler:
    """Handler for a registered RPC method."""

    handler: Callable[..., Any]
    """The async handler function that implements the method."""

    is_client_stream: bool = False
    """Whether this is a client streaming method."""

    is_server_stream: bool = False
    """Whether this is a server streaming method."""


class TunnelServer:
    """
    Server-side implementation of the gRPC tunnel protocol.

    The TunnelServer accepts incoming tunnel connections and dispatches RPCs
    to registered service handlers. Each tunnel connection can multiplex many
    concurrent RPCs.

    Example usage:
        server = TunnelServer()
        server.register_method("myservice.MyService/MyMethod", my_handler)
        await server.serve_tunnel(stream)
    """

    def __init__(
        self,
        options: Optional[TunnelOptions] = None,
        interceptors: Optional[Sequence[aio.ServerInterceptor]] = None,
    ):
        """
        Initialize a new TunnelServer.

        Args:
            options: Optional tunnel configuration. If None, uses default options.
            interceptors: Optional sequence of server interceptors to apply.
        """
        self._options = options or TunnelOptions()
        self._interceptors = list(interceptors) if interceptors else []
        self._handlers: Dict[str, MethodHandler] = {}
        self._streams: Dict[int, "TunnelServerStream"] = {}
        self._last_seen = -1
        self._stream_lock = asyncio.Lock()
        self._is_closing = False

    def register_method(
        self,
        method_name: str,
        handler: Callable[..., Any],
        is_client_stream: bool = False,
        is_server_stream: bool = False,
    ) -> None:
        """
        Register a method handler.

        Args:
            method_name: Full method name like "myservice.MyService/MyMethod"
            handler: Async callable that implements the method.
                     For unary methods: async def handler(request, context) -> response
                     For streaming methods: async def handler(stream) -> None
            is_client_stream: Whether this is a client streaming method
            is_server_stream: Whether this is a server streaming method
        """
        # Apply interceptors if any
        if self._interceptors:
            handler = self._wrap_handler_with_interceptors(
                method_name, handler, is_client_stream, is_server_stream
            )

        self._handlers[method_name] = MethodHandler(
            handler=handler,
            is_client_stream=is_client_stream,
            is_server_stream=is_server_stream,
        )

    def _wrap_handler_with_interceptors(
        self,
        method_name: str,
        handler: Callable[..., Any],
        is_client_stream: bool,
        is_server_stream: bool,
    ) -> Callable[..., Any]:
        """
        Wrap a handler with interceptors.

        Args:
            method_name: Full method name
            handler: The original handler
            is_client_stream: Whether this is a client streaming method
            is_server_stream: Whether this is a server streaming method

        Returns:
            A wrapped handler that applies the interceptor chain
        """
        # Create handler call details
        class HandlerCallDetails:
            def __init__(self, method: str):
                self.method = method
                self.invocation_metadata = None

        call_details = HandlerCallDetails(method=method_name)

        # Build continuation chain from interceptors
        def build_continuation(index: int) -> Callable:
            """Build the continuation chain recursively."""
            if index >= len(self._interceptors):
                # Base case: return the original handler
                return lambda _: handler

            # Get next continuation
            next_continuation = build_continuation(index + 1)
            interceptor = self._interceptors[index]

            # Create continuation that invokes interceptor
            def continuation(details: Any) -> Callable:
                # Invoke the interceptor's intercept_service method
                try:
                    return interceptor.intercept_service(next_continuation, details)
                except AttributeError:
                    # If interceptor doesn't have intercept_service, skip it
                    return next_continuation(details)

            return continuation

        # Apply the interceptor chain
        continuation = build_continuation(0)
        wrapped_handler = continuation(call_details)

        # If we got back a valid handler, use it; otherwise use original
        return wrapped_handler if wrapped_handler is not None else handler

    def shutdown(self) -> None:
        """Mark the server as shutting down."""
        self._is_closing = True

    async def serve_tunnel(
        self,
        stream: grpc.aio.StreamStreamCall[ClientToServer, ServerToClient],
        client_accepts_settings: bool = True,
    ) -> None:
        """
        Serve a tunnel connection.

        This method handles an incoming OpenTunnel RPC stream, negotiates settings
        with the client, and dispatches incoming RPCs to registered handlers.

        Args:
            stream: The bidirectional gRPC stream for the tunnel
            client_accepts_settings: Whether the client accepts settings negotiation
        """
        # Send settings if client accepts them
        if client_accepts_settings:
            settings_msg = ServerToClient(
                stream_id=-1,
                settings={
                    "initial_window_size": INITIAL_WINDOW_SIZE,
                    "supported_protocol_revisions": self._options.supported_revisions(),
                },
            )
            # Send settings and wait for it to be written
            await stream.write(settings_msg)

        # Main receive loop - use read() instead of async for to handle stream closing
        try:
            while not self._is_closing:
                # Try to read next message
                msg = await stream.read() if hasattr(stream, 'read') else await stream.__anext__()

                if msg is None:
                    # Stream is closing or no more messages
                    # Wait a bit and check if we should exit
                    async with self._stream_lock:
                        num_streams = len(self._streams)
                    # If there are no active streams, we can exit
                    if num_streams == 0:
                        break
                    # Otherwise wait a bit and continue
                    await asyncio.sleep(0.05)
                    continue

                # Handle NewStream messages - create new stream
                if msg.HasField("new_stream"):
                    ok, err = await self._create_stream(stream, msg.stream_id, msg.new_stream)
                    if not ok:
                        # Protocol error - abort tunnel
                        raise Exception(f"Protocol error: {err}")
                    if err is not None:
                        # Stream error - send close but keep tunnel alive
                        close_msg = ServerToClient(
                            stream_id=msg.stream_id,
                            close_stream={
                                "status": _error_to_status(err),
                            },
                        )
                        asyncio.create_task(stream.write(close_msg))
                    continue

                # Route message to appropriate stream
                target_stream = await self._get_stream(msg.stream_id)
                if target_stream is not None:
                    await target_stream._accept_client_frame(msg)

        except asyncio.CancelledError:
            # Clean shutdown
            pass
        except Exception as e:
            # Log or handle error
            import traceback
            traceback.print_exc()
            raise

    async def _create_stream(
        self,
        tunnel_stream: grpc.aio.StreamStreamCall[ClientToServer, ServerToClient],
        stream_id: int,
        new_stream_msg: Any,
    ) -> tuple[bool, Optional[Exception]]:
        """
        Create a new stream with the given ID.

        Returns:
            (ok, err) tuple where:
            - ok=False means protocol error, tunnel should be aborted
            - ok=True, err=None means stream created successfully
            - ok=True, err=Exception means stream should be closed with error
        """
        if self._is_closing:
            return True, grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNAVAILABLE,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details="server is shutting down",
            )

        # Validate protocol revision
        revision = new_stream_msg.protocol_revision
        if revision not in (REVISION_ZERO, REVISION_ONE):
            return True, grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNAVAILABLE,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details=f"server does not support protocol revision {revision}",
            )

        no_flow_control = revision == REVISION_ZERO

        async with self._stream_lock:
            # Check for duplicate stream ID
            if stream_id in self._streams:
                return False, Exception(
                    f"cannot create stream ID {stream_id}: already exists"
                )

            # Check for monotonic stream IDs
            if stream_id <= self._last_seen:
                return False, Exception(
                    f"cannot create stream ID {stream_id}: that ID has already been used"
                )

            self._last_seen = stream_id

            # Parse method name
            method_name = new_stream_msg.method_name
            if method_name.startswith("/"):
                method_name = method_name[1:]

            # Look up handler
            handler_info = self._handlers.get(method_name)
            if handler_info is None:
                return True, grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNIMPLEMENTED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details=f"{method_name} not implemented",
                )

            # Parse request headers metadata
            headers = from_proto(new_stream_msg.request_headers)

            # Create sender for this stream
            async def send_func(data: bytes, total_size: int, first: bool) -> None:
                if first:
                    msg = ServerToClient(
                        stream_id=stream_id,
                        response_message={"size": total_size, "data": data},
                    )
                else:
                    msg = ServerToClient(
                        stream_id=stream_id,
                        more_response_data=data,
                    )
                await tunnel_stream.write(msg)

            # Create sender and receiver based on protocol revision
            if no_flow_control:
                sender = new_sender_without_flow_control(send_func)
                receiver: Receiver[Any] = new_receiver_without_flow_control()
            else:

                def send_window_update(window: int) -> None:
                    # Don't send window updates if stream is half-closed
                    # Note: server_stream doesn't exist yet, so we'll check in the async task
                    async def do_send() -> None:
                        msg = ServerToClient(
                            stream_id=stream_id,
                            window_update=window,
                        )
                        await tunnel_stream.write(msg)

                    asyncio.create_task(do_send())

                def measure_frame(frame: Any) -> int:
                    """Measure the size of a frame for flow control."""
                    if frame.HasField("request_message"):
                        return len(frame.request_message.data)
                    elif frame.HasField("more_request_data"):
                        return len(frame.more_request_data)
                    return 0

                sender = new_sender(send_func, new_stream_msg.initial_window_size)
                receiver = new_receiver(
                    measure_frame, send_window_update, INITIAL_WINDOW_SIZE
                )

            # Create the stream
            server_stream = TunnelServerStream(
                server=self,
                tunnel_stream=tunnel_stream,
                stream_id=stream_id,
                method_name=method_name,
                sender=sender,
                receiver=receiver,
                handler=handler_info.handler,
                is_client_stream=handler_info.is_client_stream,
                is_server_stream=handler_info.is_server_stream,
                headers=headers,
            )

            self._streams[stream_id] = server_stream

            # Start serving the stream in background
            asyncio.create_task(server_stream._serve_stream())

        return True, None

    async def _get_stream(self, stream_id: int) -> Optional["TunnelServerStream"]:
        """Get a stream by ID, or None if it doesn't exist."""
        async with self._stream_lock:
            # Check if stream is active
            target = self._streams.get(stream_id)
            if target is not None:
                return target

            # If stream ID was already seen, ignore (late message)
            if stream_id <= self._last_seen:
                return None

            # Stream never created - protocol error
            raise Exception(f"received frame for stream ID {stream_id}: stream never created")

    async def _remove_stream(self, stream_id: int) -> None:
        """Remove a stream from the active streams map."""
        async with self._stream_lock:
            self._streams.pop(stream_id, None)


class TunnelServerStream:
    """
    Server-side implementation of a single tunneled stream.

    This class implements the server side of a single RPC call within the tunnel,
    handling message send/receive with flow control, headers/trailers, and
    dispatching to the actual service handler.
    """

    def __init__(
        self,
        server: TunnelServer,
        tunnel_stream: grpc.aio.StreamStreamCall[ClientToServer, ServerToClient],
        stream_id: int,
        method_name: str,
        sender: Sender,
        receiver: Receiver[Any],
        handler: Callable[..., Any],
        is_client_stream: bool,
        is_server_stream: bool,
        headers: grpc.aio.Metadata,
    ):
        self._server = server
        self._tunnel_stream = tunnel_stream
        self._stream_id = stream_id
        self._method_name = method_name
        self._sender = sender
        self._receiver = receiver
        self._handler = handler
        self._is_client_stream = is_client_stream
        self._is_server_stream = is_server_stream

        # Metadata
        self._request_headers = headers
        self._response_headers: Optional[grpc.aio.Metadata] = None
        self._response_trailers: Optional[grpc.aio.Metadata] = None

        # State
        self._sent_headers = False
        self._closed = False
        self._half_closed_err: Optional[Exception] = None
        self._num_sent = 0
        self._read_err: Optional[Exception] = None

        # Locks
        self._write_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()

        # Context for handler
        self._context = _ServerContext(self)

    async def _accept_client_frame(self, msg: ClientToServer) -> None:
        """Accept and process a frame from the client."""
        # Handle half-close
        if msg.HasField("half_close"):
            await self._half_close(None)
            return

        # Handle cancel
        if msg.HasField("cancel"):
            err = Exception("cancelled")
            await self._finish_stream(err)
            return

        # Handle window update
        if msg.HasField("window_update"):
            self._sender.update_window(msg.window_update)
            return

        # Handle message data
        if msg.HasField("request_message") or msg.HasField("more_request_data"):
            try:
                await self._receiver.accept(msg)
            except Exception as e:
                await self._finish_stream(e)
            return

    async def _serve_stream(self) -> None:
        """Serve this stream by invoking the handler."""
        err: Optional[Exception] = None

        try:
            # For unary methods, receive request, invoke handler, send response
            if not self._is_client_stream and not self._is_server_stream:
                # Unary-unary
                request = await self.recv_message()
                response = await self._handler(request, self._context)
                await self.send_message(response)
            elif self._is_client_stream and not self._is_server_stream:
                # Stream-unary
                response = await self._handler(self, self._context)
                await self.send_message(response)
            elif not self._is_client_stream and self._is_server_stream:
                # Unary-stream
                request = await self.recv_message()
                await self._handler(request, self, self._context)
            else:
                # Stream-stream
                await self._handler(self, self._context)

        except Exception as e:
            import traceback
            traceback.print_exc()
            err = e

        finally:
            await self._finish_stream(err)

    async def send_message(
        self,
        message: Any,
        serializer: Optional[Callable[[Any], bytes]] = None,
    ) -> None:
        """
        Send a message to the client.

        Args:
            message: The message to send (protobuf or other serializable object)
            serializer: Optional serializer function. If not provided, assumes
                        message is a protobuf Message.
        """
        async with self._write_lock:
            # Send headers if not already sent
            if not self._sent_headers:
                await self._send_headers_locked()

            # Check if we're allowed to send another message
            if not self._is_server_stream and self._num_sent >= 1:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.INTERNAL,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details=f"Already sent response for non-server-stream method {self._method_name}",
                )

            self._num_sent += 1

            # Serialize message
            if serializer:
                data = serializer(message)
            elif isinstance(message, ProtoMessage):
                data = message.SerializeToString()
            else:
                data = message

            # Send with flow control
            await self._sender.send(data)

    async def recv_message(
        self,
        deserializer: Optional[Callable[[bytes], Any]] = None,
    ) -> Any:
        """
        Receive a message from the client.

        Args:
            deserializer: Optional deserializer function. If not provided,
                          returns raw bytes.

        Returns:
            The deserialized message
        """
        async with self._read_lock:
            data = await self._recv_message_locked()

            # Check if we should fail if there's another message (for unary methods)
            if not self._is_client_stream:
                # Try to read another message - should get EOF
                try:
                    await self._recv_message_locked()
                    # If we got here, there's an extra message
                    err = grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INVALID_ARGUMENT,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details=f"Already received request for non-client-stream method {self._method_name}",
                    )
                    self._read_err = err
                    raise err
                except StopAsyncIteration:
                    # Expected EOF
                    pass

            # Deserialize
            if deserializer:
                result: Any = deserializer(data)
                return result
            return data

    async def _recv_message_locked(self) -> bytes:
        """Receive a single message (must hold read lock)."""
        if self._read_err is not None:
            raise self._read_err

        msg_size = -1
        data = b""

        while True:
            # Dequeue next frame
            frame, ok = await self._receiver.dequeue()

            if not ok or frame is None:
                # Stream closed
                if self._half_closed_err is not None:
                    self._read_err = self._half_closed_err
                    raise self._half_closed_err
                raise StopAsyncIteration()

            # Handle message frames
            if frame.HasField("request_message"):
                if msg_size != -1:
                    err = grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INVALID_ARGUMENT,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details="received request message envelope before previous message finished",
                    )
                    self._read_err = err
                    raise err

                msg_size = frame.request_message.size
                data = bytes(frame.request_message.data)

                if len(data) >= msg_size:
                    return data

            elif frame.HasField("more_request_data"):
                if msg_size == -1:
                    err = grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INVALID_ARGUMENT,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details="never received envelope for request message",
                    )
                    self._read_err = err
                    raise err

                data += bytes(frame.more_request_data)

                if len(data) >= msg_size:
                    return data

    async def set_response_headers(self, headers: grpc.aio.Metadata) -> None:
        """Set response headers (must be called before sending any messages)."""
        async with self._write_lock:
            if self._sent_headers:
                raise Exception("already sent headers")
            if self._response_headers is None:
                self._response_headers = headers
            else:
                # Merge with existing headers
                self._response_headers = grpc.aio.Metadata(
                    *self._response_headers, *headers
                )

    async def send_response_headers(self, headers: grpc.aio.Metadata) -> None:
        """Send response headers immediately."""
        async with self._write_lock:
            if self._sent_headers:
                raise Exception("already sent headers")
            if self._response_headers is None:
                self._response_headers = headers
            else:
                self._response_headers = grpc.aio.Metadata(
                    *self._response_headers, *headers
                )
            await self._send_headers_locked()

    async def _send_headers_locked(self) -> None:
        """Send response headers (must hold write lock)."""
        if self._sent_headers:
            return

        headers_proto = to_proto(self._response_headers)
        msg = ServerToClient(
            stream_id=self._stream_id,
            response_headers=headers_proto,
        )
        await self._tunnel_stream.write(msg)
        self._sent_headers = True
        self._response_headers = None

    async def set_response_trailers(self, trailers: grpc.aio.Metadata) -> None:
        """Set response trailers (sent when stream closes)."""
        async with self._write_lock:
            if self._closed:
                raise Exception("already finished")
            if self._response_trailers is None:
                self._response_trailers = trailers
            else:
                self._response_trailers = grpc.aio.Metadata(
                    *self._response_trailers, *trailers
                )

    async def _half_close(self, err: Optional[Exception]) -> None:
        """Mark the stream as half-closed (no more data from client)."""
        if self._half_closed_err is not None:
            # Already half-closed
            return

        if err is None:
            err = StopAsyncIteration()

        self._half_closed_err = err
        self._receiver.close()

    async def _finish_stream(self, err: Optional[Exception]) -> None:
        """Finish the stream and send close message to client."""
        # Mark as half-closed
        await self._half_close(err)

        # Remove from server's stream map
        await self._server._remove_stream(self._stream_id)

        async with self._write_lock:
            if self._closed:
                return

            self._closed = True

            # Convert error to status
            status = _error_to_status(err)

            # Prepare headers and trailers
            send_headers = not self._sent_headers
            headers = self._response_headers if send_headers else None
            trailers = self._response_trailers

            # Send close message (don't block)
            async def send_close() -> None:
                if send_headers and headers is not None:
                    headers_msg = ServerToClient(
                        stream_id=self._stream_id,
                        response_headers=to_proto(headers),
                    )
                    await self._tunnel_stream.write(headers_msg)

                close_msg = ServerToClient(
                    stream_id=self._stream_id,
                    close_stream={
                        "status": status,
                        "response_trailers": to_proto(trailers),
                    },
                )
                await self._tunnel_stream.write(close_msg)

            asyncio.create_task(send_close())

            # Clear state
            self._sent_headers = True
            self._response_headers = None
            self._response_trailers = None


class _ServerContext:
    """Context object passed to server handlers."""

    def __init__(self, stream: TunnelServerStream):
        self._stream = stream

    def invocation_metadata(self) -> grpc.aio.Metadata:
        """Get the request headers metadata."""
        return self._stream._request_headers

    async def set_trailing_metadata(self, metadata: grpc.aio.Metadata) -> None:
        """Set trailing metadata (trailers)."""
        await self._stream.set_response_trailers(metadata)


def _error_to_status(err: Optional[Exception]) -> status_pb2.Status:
    """Convert an exception to a gRPC status."""
    if err is None:
        return status_pb2.Status(code=0)  # OK

    # Check for AioRpcError which has code() and details() methods
    if isinstance(err, grpc.aio.AioRpcError):
        return status_pb2.Status(
            code=err.code().value[0],
            message=err.details() or "",
        )

    if isinstance(err, asyncio.CancelledError):
        return status_pb2.Status(
            code=grpc.StatusCode.CANCELLED.value[0],
            message="cancelled",
        )

    # Unknown error
    return status_pb2.Status(
        code=grpc.StatusCode.UNKNOWN.value[0],
        message=str(err),
    )
