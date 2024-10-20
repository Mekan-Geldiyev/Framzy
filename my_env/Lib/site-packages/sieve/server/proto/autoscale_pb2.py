"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0fautoscale.proto\x12\tautoscale\x1a\x1fgoogle/protobuf/timestamp.proto"2\n\x0eScalingRequest\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x0e\n\x06source\x18\x02 \x01(\t"]\n\x0bScalingInfo\x12\x12\n\nqueue_size\x18\x01 \x01(\x05\x12\x1c\n\x14currently_processing\x18\x02 \x01(\x05\x12\x1c\n\x14average_predict_time\x18\x03 \x01(\x01"\x9d\x01\n\x0cScalingEvent\x12\x19\n\x11previous_replicas\x18\x01 \x01(\x05\x12\x14\n\x0cnew_replicas\x18\x02 \x01(\x05\x12.\n\nevent_time\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12,\n\x0cscaling_info\x18\x04 \x01(\x0b2\x16.autoscale.ScalingInfo"8\n\rScalingEvents\x12\'\n\x06events\x18\x01 \x03(\x0b2\x17.autoscale.ScalingEvent"\\\n\x0fScalingResponse\x12\x11\n\tdid_scale\x18\x01 \x01(\x08\x12\x0e\n\x06cached\x18\x02 \x01(\x08\x12&\n\x05event\x18\x03 \x01(\x0b2\x17.autoscale.ScalingEvent2Y\n\nAutoscaler\x12K\n\x10RequestAutoscale\x12\x19.autoscale.ScalingRequest\x1a\x1a.autoscale.ScalingResponse"\x00B\x17Z\x15./pkg/modelscaling/pbb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "autoscale_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\x15./pkg/modelscaling/pb"
    _globals["_SCALINGREQUEST"]._serialized_start = 63
    _globals["_SCALINGREQUEST"]._serialized_end = 113
    _globals["_SCALINGINFO"]._serialized_start = 115
    _globals["_SCALINGINFO"]._serialized_end = 208
    _globals["_SCALINGEVENT"]._serialized_start = 211
    _globals["_SCALINGEVENT"]._serialized_end = 368
    _globals["_SCALINGEVENTS"]._serialized_start = 370
    _globals["_SCALINGEVENTS"]._serialized_end = 426
    _globals["_SCALINGRESPONSE"]._serialized_start = 428
    _globals["_SCALINGRESPONSE"]._serialized_end = 520
    _globals["_AUTOSCALER"]._serialized_start = 522
    _globals["_AUTOSCALER"]._serialized_end = 611
