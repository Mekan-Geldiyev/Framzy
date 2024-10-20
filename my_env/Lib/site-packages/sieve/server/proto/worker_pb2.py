"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0cworker.proto\x12\x03rpc"D\n\x12HealthCheckRequest\x12\x14\n\x07service\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x0c\n\x04kill\x18\x02 \x01(\x08B\n\n\x08_service"h\n\x13HealthCheckResponse\x12\x1e\n\nsetup_info\x18\x01 \x01(\x0b2\n.rpc.Setup\x12!\n\x06status\x18\x02 \x01(\x0e2\x11.rpc.HealthStatus\x12\x0e\n\x06killed\x18\x03 \x01(\x08"f\n\x05Setup\x12 \n\x06status\x18\x01 \x01(\x0e2\x10.rpc.SetupStatus\x12\x0f\n\x07retries\x18\x02 \x01(\x05\x12\x0c\n\x04time\x18\x03 \x01(\x02\x12\x12\n\x05error\x18\x04 \x01(\tH\x00\x88\x01\x01B\x08\n\x06_error"]\n\x0fPredictionInput\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0c\n\x04data\x18\x02 \x01(\x0c\x12\x13\n\x0bfile_server\x18\x03 \x01(\t\x12\x0c\n\x04stop\x18\x04 \x01(\x08\x12\x0c\n\x04kill\x18\x05 \x01(\x08"3\n\x12PredictionMetadata\x12\x1d\n\x15override_cost_dollars\x18\x01 \x01(\x01"\xcf\x01\n\x12PredictionResponse\x12\x0c\n\x04data\x18\x01 \x01(\x0c\x12\x1b\n\x06status\x18\x02 \x01(\x0e2\x0b.rpc.Status\x12\x0c\n\x04stop\x18\x03 \x01(\x08\x12\x12\n\x05error\x18\x04 \x01(\tH\x00\x88\x01\x01\x12\x10\n\x03key\x18\x05 \x01(\tH\x01\x88\x01\x01\x12\x0e\n\x06killed\x18\x06 \x01(\x08\x12)\n\x08metadata\x18\x07 \x01(\x0b2\x17.rpc.PredictionMetadata\x12\r\n\x05fatal\x18\x08 \x01(\x08B\x08\n\x06_errorB\x06\n\x04_key*Z\n\x0cHealthStatus\x12\x12\n\x0eHEALTH_UNKNOWN\x10\x00\x12\x12\n\x0eHEALTH_SERVING\x10\x01\x12\x10\n\x0cHEALTH_SETUP\x10\x02\x12\x10\n\x0cHEALTH_ERROR\x10\x03*\x83\x01\n\x0bSetupStatus\x12\x11\n\rSETUP_UNKNOWN\x10\x00\x12\x11\n\rSETUP_STARTED\x10\x01\x12\x0f\n\x0bSETUP_ERROR\x10\x02\x12\x11\n\rSETUP_SUCCESS\x10\x03\x12\x14\n\x10SETUP_NODE_ERROR\x10\x04\x12\x14\n\x10SETUP_LOAD_ERROR\x10\x05*H\n\x06Status\x12\x14\n\x10STATUS_SUCCEEDED\x10\x00\x12\x11\n\rSTATUS_FAILED\x10\x01\x12\x15\n\x11STATUS_PROCESSING\x10\x022O\n\tJobWorker\x12B\n\x0bWorkRequest\x12\x14.rpc.PredictionInput\x1a\x17.rpc.PredictionResponse"\x00(\x010\x012\x88\x01\n\x0cWorkerHealth\x12:\n\x05Check\x12\x17.rpc.HealthCheckRequest\x1a\x18.rpc.HealthCheckResponse\x12<\n\x05Watch\x12\x17.rpc.HealthCheckRequest\x1a\x18.rpc.HealthCheckResponse0\x01B\x0bZ\t./pkg/rpcb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "worker_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\t./pkg/rpc"
    _globals["_HEALTHSTATUS"]._serialized_start = 659
    _globals["_HEALTHSTATUS"]._serialized_end = 749
    _globals["_SETUPSTATUS"]._serialized_start = 752
    _globals["_SETUPSTATUS"]._serialized_end = 883
    _globals["_STATUS"]._serialized_start = 885
    _globals["_STATUS"]._serialized_end = 957
    _globals["_HEALTHCHECKREQUEST"]._serialized_start = 21
    _globals["_HEALTHCHECKREQUEST"]._serialized_end = 89
    _globals["_HEALTHCHECKRESPONSE"]._serialized_start = 91
    _globals["_HEALTHCHECKRESPONSE"]._serialized_end = 195
    _globals["_SETUP"]._serialized_start = 197
    _globals["_SETUP"]._serialized_end = 299
    _globals["_PREDICTIONINPUT"]._serialized_start = 301
    _globals["_PREDICTIONINPUT"]._serialized_end = 394
    _globals["_PREDICTIONMETADATA"]._serialized_start = 396
    _globals["_PREDICTIONMETADATA"]._serialized_end = 447
    _globals["_PREDICTIONRESPONSE"]._serialized_start = 450
    _globals["_PREDICTIONRESPONSE"]._serialized_end = 657
    _globals["_JOBWORKER"]._serialized_start = 959
    _globals["_JOBWORKER"]._serialized_end = 1038
    _globals["_WORKERHEALTH"]._serialized_start = 1041
    _globals["_WORKERHEALTH"]._serialized_end = 1177
