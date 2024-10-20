"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0cevents.proto\x12\x05event\x1a\x1fgoogle/protobuf/timestamp.proto"\x8b\x02\n\x05Event\x12\x0b\n\x03key\x18\x01 \x01(\t\x12&\n\x02ts\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12-\n\x10dummy_event_data\x18\x02 \x01(\x0b2\x11.event.DummyEventH\x00\x12-\n\x10scale_event_data\x18\x04 \x01(\x0b2\x11.event.ScaleEventH\x00\x126\n\x15pod_status_event_data\x18\x05 \x01(\x0b2\x15.event.PodStatusEventH\x00\x12)\n\x0ejob_event_data\x18\x06 \x01(\x0b2\x0f.event.JobEventH\x00B\x0c\n\nevent_data"\x1f\n\nDummyEvent\x12\x11\n\ttest_data\x18\x01 \x01(\t"\r\n\x0bEventStatus"4\n\nScaleEvent\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x14\n\x0cnum_replicas\x18\x02 \x01(\x05"\xea\x01\n\x0ePodStatusEvent\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x0e\n\x06pod_id\x18\x02 \x01(\t\x12$\n\npod_status\x18\x03 \x01(\x0e2\x10.event.PodStatus\x12\n\n\x02id\x18\x04 \x01(\t\x12\x17\n\x0fcontainer_index\x18\x05 \x01(\r\x12\r\n\x05split\x18\x06 \x01(\r\x12\x0f\n\x07node_id\x18\x07 \x01(\t\x12\x14\n\x0cmachine_type\x18\x08 \x01(\t\x125\n\x0eevent_metadata\x18\t \x01(\x0b2\x1d.event.PodStatusEventMetadata"-\n\x16PodStatusEventMetadata\x12\x13\n\x0bdescription\x18\x01 \x01(\t"\xb0\x01\n\x08JobEvent\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12C\n\x1cjob_status_change_event_data\x18\x02 \x01(\x0b2\x1b.event.JobStatusChangeEventH\x00\x12=\n\x19job_new_output_event_data\x18\x03 \x01(\x0b2\x18.event.JobNewOutputEventH\x00B\x10\n\x0ejob_event_data"*\n\x14JobStatusChangeEvent\x12\x12\n\njob_status\x18\x01 \x01(\t"\'\n\x11JobNewOutputEvent\x12\x12\n\noutput_key\x18\x01 \x01(\x04*t\n\tPodStatus\x12\x16\n\x12CONTAINER_CREATING\x10\x00\x12\t\n\x05SETUP\x10\x01\x12\x08\n\x04IDLE\x10\x02\x12\x0e\n\nPREDICTING\x10\x03\x12\x0f\n\x0bTERMINATING\x10\x04\x12\t\n\x05ERROR\x10\x05\x12\x0e\n\nHEART_BEAT\x10\x062D\n\x0eEventProcessor\x122\n\x0cProcessEvent\x12\x0c.event.Event\x1a\x12.event.EventStatus"\x00B\x10Z\x0e./pkg/event/pbb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "events_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\x0e./pkg/event/pb"
    _globals["_PODSTATUS"]._serialized_start = 976
    _globals["_PODSTATUS"]._serialized_end = 1092
    _globals["_EVENT"]._serialized_start = 57
    _globals["_EVENT"]._serialized_end = 324
    _globals["_DUMMYEVENT"]._serialized_start = 326
    _globals["_DUMMYEVENT"]._serialized_end = 357
    _globals["_EVENTSTATUS"]._serialized_start = 359
    _globals["_EVENTSTATUS"]._serialized_end = 372
    _globals["_SCALEEVENT"]._serialized_start = 374
    _globals["_SCALEEVENT"]._serialized_end = 426
    _globals["_PODSTATUSEVENT"]._serialized_start = 429
    _globals["_PODSTATUSEVENT"]._serialized_end = 663
    _globals["_PODSTATUSEVENTMETADATA"]._serialized_start = 665
    _globals["_PODSTATUSEVENTMETADATA"]._serialized_end = 710
    _globals["_JOBEVENT"]._serialized_start = 713
    _globals["_JOBEVENT"]._serialized_end = 889
    _globals["_JOBSTATUSCHANGEEVENT"]._serialized_start = 891
    _globals["_JOBSTATUSCHANGEEVENT"]._serialized_end = 933
    _globals["_JOBNEWOUTPUTEVENT"]._serialized_start = 935
    _globals["_JOBNEWOUTPUTEVENT"]._serialized_end = 974
    _globals["_EVENTPROCESSOR"]._serialized_start = 1094
    _globals["_EVENTPROCESSOR"]._serialized_end = 1162
