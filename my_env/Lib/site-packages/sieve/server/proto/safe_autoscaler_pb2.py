"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x15safe_autoscaler.proto\x12\x03rpc"(\n\x0fStopWorkRequest\x12\x15\n\rreply_address\x18\x01 \x01(\t"&\n\rStopWorkReply\x12\x15\n\rresponse_code\x18\x01 \x01(\r"!\n\rKillMeRequest\x12\x10\n\x08pod_name\x18\x01 \x01(\t"$\n\x0bKillMeReply\x12\x15\n\rresponse_code\x18\x01 \x01(\r2B\n\x0eSafeAutoscaler\x120\n\x06KillMe\x12\x12.rpc.KillMeRequest\x1a\x10.rpc.KillMeReply"\x002D\n\nJobManager\x126\n\x08StopWork\x12\x14.rpc.StopWorkRequest\x1a\x12.rpc.StopWorkReply"\x00B\x0bZ\t./pkg/rpcb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "safe_autoscaler_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\t./pkg/rpc"
    _globals["_STOPWORKREQUEST"]._serialized_start = 30
    _globals["_STOPWORKREQUEST"]._serialized_end = 70
    _globals["_STOPWORKREPLY"]._serialized_start = 72
    _globals["_STOPWORKREPLY"]._serialized_end = 110
    _globals["_KILLMEREQUEST"]._serialized_start = 112
    _globals["_KILLMEREQUEST"]._serialized_end = 145
    _globals["_KILLMEREPLY"]._serialized_start = 147
    _globals["_KILLMEREPLY"]._serialized_end = 183
    _globals["_SAFEAUTOSCALER"]._serialized_start = 185
    _globals["_SAFEAUTOSCALER"]._serialized_end = 251
    _globals["_JOBMANAGER"]._serialized_start = 253
    _globals["_JOBMANAGER"]._serialized_end = 321
