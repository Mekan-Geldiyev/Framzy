"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\rbilling.proto\x12\x07billing\x1a\x1fgoogle/protobuf/timestamp.proto"\xd9\x02\n\x0eBillingRequest\x12\x17\n\x0forganization_id\x18\x01 \x01(\t\x12\x10\n\x08model_id\x18\x02 \x01(\t\x12\x0e\n\x06job_id\x18\x03 \x01(\t\x12\x0e\n\x06run_id\x18\x04 \x01(\t\x123\n\x0fstart_timestamp\x18\x05 \x01(\x0b2\x1a.google.protobuf.Timestamp\x121\n\rend_timestamp\x18\x06 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12-\n\ttimestamp\x18\x07 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x0c\n\x04type\x18\x08 \x01(\t\x12\x14\n\x0cmachine_type\x18\t \x01(\t\x12\r\n\x05split\x18\n \x01(\r\x12\x13\n\x0buse_credits\x18\x0b \x01(\x08\x12\x1d\n\x15override_cost_dollars\x18\x0c \x01(\x01""\n\x0fBillingResponse\x12\x0f\n\x07success\x18\x01 \x01(\x082W\n\x0eBillingManager\x12E\n\x0eRequestBilling\x12\x17.billing.BillingRequest\x1a\x18.billing.BillingResponse"\x00B\x12Z\x10./pkg/billing/pbb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "billing_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\x10./pkg/billing/pb"
    _globals["_BILLINGREQUEST"]._serialized_start = 60
    _globals["_BILLINGREQUEST"]._serialized_end = 405
    _globals["_BILLINGRESPONSE"]._serialized_start = 407
    _globals["_BILLINGRESPONSE"]._serialized_end = 441
    _globals["_BILLINGMANAGER"]._serialized_start = 443
    _globals["_BILLINGMANAGER"]._serialized_end = 530
