"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x17permanent_storage.proto\x12\x03rpc"d\n\x0eStorageRequest\x12\x0b\n\x03key\x18\x01 \x01(\x04\x12\x0c\n\x04data\x18\x02 \x01(\x0c\x12\x17\n\x0forganization_id\x18\x04 \x01(\t\x12\x0e\n\x06job_id\x18\x05 \x01(\t\x12\x0e\n\x06run_id\x18\x06 \x01(\t",\n\x0fStorageResponse\x12\x0b\n\x03key\x18\x01 \x01(\x04\x12\x0c\n\x04data\x18\x02 \x01(\x0c2L\n\x16PermanentStorageWorker\x122\n\x05Check\x12\x13.rpc.StorageRequest\x1a\x14.rpc.StorageResponseB\x0bZ\t./pkg/rpcb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "permanent_storage_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\t./pkg/rpc"
    _globals["_STORAGEREQUEST"]._serialized_start = 32
    _globals["_STORAGEREQUEST"]._serialized_end = 132
    _globals["_STORAGERESPONSE"]._serialized_start = 134
    _globals["_STORAGERESPONSE"]._serialized_end = 178
    _globals["_PERMANENTSTORAGEWORKER"]._serialized_start = 180
    _globals["_PERMANENTSTORAGEWORKER"]._serialized_end = 256
