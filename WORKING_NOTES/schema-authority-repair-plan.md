# Schema Authority Repair Plan

## Runtime authority
- Runtime schema authority is `dopetask_schemas/task_packet.schema.json`
- Runtime validation loads packaged schemas through `src/dopetask/utils/schema_registry.py` and `src/dopetask/schemas/validator.py`

## Documentation mirror
- `docs/schemas/task_packet.schema.json` is a documentation mirror, not the runtime authority surface

## Repair targets

### 1. docs/23_INTEGRATION_GUIDE.md
Problem:
- currently points readers to `docs/schemas/task_packet.schema.json` as if it were the packet contract authority

Required correction:
- point runtime/schema authority at `dopetask_schemas/task_packet.schema.json`
- if `docs/schemas/task_packet.schema.json` is mentioned, label it explicitly as a documentation mirror

### 2. docs/13_TASK_PACKET_FORMAT.md
Problem:
- defines packet contract in prose without clearly stating runtime schema authority

Required correction:
- add an explicit schema-authority note
- state that runtime validation uses packaged schemas via schema registry / validator path
- if docs mirror is mentioned, label it as documentation-only mirror

## Wording rule
- Treat `dopetask_schemas/*.schema.json` as runtime authority
- Treat `docs/schemas/*.schema.json` as documentation mirrors unless explicitly stated otherwise
- Never describe the docs tree as the runtime validation source

## Scope rule
- do not broaden into general schema cleanup
- do not edit schema files themselves
- repair authority wording only
