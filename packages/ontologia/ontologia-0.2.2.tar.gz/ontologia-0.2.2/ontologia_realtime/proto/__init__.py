"""Generated gRPC bindings for the real-time entity service."""

import sys

from . import realtime_pb2, realtime_pb2_grpc

__all__ = list(getattr(realtime_pb2, "__all__", [])) + list(
    getattr(realtime_pb2_grpc, "__all__", [])
)

globals().update(
    {name: getattr(realtime_pb2, name) for name in getattr(realtime_pb2, "__all__", [])}
)
globals().update(
    {name: getattr(realtime_pb2_grpc, name) for name in getattr(realtime_pb2_grpc, "__all__", [])}
)

sys.modules.setdefault("realtime_pb2", realtime_pb2)
sys.modules.setdefault("realtime_pb2_grpc", realtime_pb2_grpc)
