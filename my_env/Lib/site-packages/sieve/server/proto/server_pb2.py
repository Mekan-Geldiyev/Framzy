"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0cserver.proto\x12\x03rpc"E\n\x11GetOutputsRequest\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x0e\n\x06run_id\x18\x02 \x01(\t\x12\x0e\n\x06job_id\x18\x03 \x01(\t"g\n\x06Output\x12\x0c\n\x04stop\x18\x01 \x01(\x08\x12\r\n\x05error\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\t\x12!\n\x06status\x18\x04 \x01(\x0e2\x11.rpc.ResponseType\x12\x0e\n\x06run_id\x18\x05 \x01(\t"\x17\n\x04File\x12\x0f\n\x07content\x18\x01 \x01(\x0c"1\n\tFileChunk\x12\x0f\n\x07content\x18\x01 \x01(\x0c\x12\x13\n\x0bend_of_file\x18\x02 \x01(\x08"#\n\x0eGetFileRequest\x12\x11\n\tfile_hash\x18\x03 \x01(\t")\n\x14GetFileStreamRequest\x12\x11\n\tfile_hash\x18\x01 \x01(\t*.\n\x0cResponseType\x12\t\n\x05ERROR\x10\x00\x12\x0b\n\x07TIMEOUT\x10\x01\x12\x06\n\x02OK\x10\x022F\n\rOutputService\x125\n\nGetOutputs\x12\x16.rpc.GetOutputsRequest\x1a\x0b.rpc.Output"\x000\x012z\n\x0bFileService\x12+\n\x07GetFile\x12\x13.rpc.GetFileRequest\x1a\t.rpc.File"\x00\x12>\n\rGetFileStream\x12\x19.rpc.GetFileStreamRequest\x1a\x0e.rpc.FileChunk"\x000\x01B\x0bZ\t./pkg/rpcb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "server_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\t./pkg/rpc"
    _globals["_RESPONSETYPE"]._serialized_start = 353
    _globals["_RESPONSETYPE"]._serialized_end = 399
    _globals["_GETOUTPUTSREQUEST"]._serialized_start = 21
    _globals["_GETOUTPUTSREQUEST"]._serialized_end = 90
    _globals["_OUTPUT"]._serialized_start = 92
    _globals["_OUTPUT"]._serialized_end = 195
    _globals["_FILE"]._serialized_start = 197
    _globals["_FILE"]._serialized_end = 220
    _globals["_FILECHUNK"]._serialized_start = 222
    _globals["_FILECHUNK"]._serialized_end = 271
    _globals["_GETFILEREQUEST"]._serialized_start = 273
    _globals["_GETFILEREQUEST"]._serialized_end = 308
    _globals["_GETFILESTREAMREQUEST"]._serialized_start = 310
    _globals["_GETFILESTREAMREQUEST"]._serialized_end = 351
    _globals["_OUTPUTSERVICE"]._serialized_start = 401
    _globals["_OUTPUTSERVICE"]._serialized_end = 471
    _globals["_FILESERVICE"]._serialized_start = 473
    _globals["_FILESERVICE"]._serialized_end = 595
