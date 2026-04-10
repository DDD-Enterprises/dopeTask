    # Schema-Authority Cleanup Scan

    ## Surfaces reviewed
    - docs/13_TASK_PACKET_FORMAT.md
    - docs/23_INTEGRATION_GUIDE.md
    - docs/schemas/task_packet.schema.json
    - dopetask_schemas/task_packet.schema.json
    - src/dopetask/utils/schema_registry.py
    - src/dopetask/schemas/validator.py

    ## 1. Documented schema authority
    - `docs/23_INTEGRATION_GUIDE.md` is the clearest doc-level authority claim in this set. It says supervisors should emit JSON packets matching `docs/schemas/task_packet.schema.json`, which presents the docs mirror as the contract reference.
    - `docs/13_TASK_PACKET_FORMAT.md` defines the JSON TaskPacket contract in prose and says packets are schema-validated, but it does not name which schema file is authoritative.
    - `docs/schemas/task_packet.schema.json` exists as a doc-visible schema surface and therefore reads as a likely authority target even though that status is not explicitly qualified inside the file itself.

    ## 2. Runtime-authoritative schema surface
    - Runtime authority is `dopetask_schemas/task_packet.schema.json`.
    - `src/dopetask/utils/schema_registry.py` states that schemas are loaded exclusively from installed `dopetask_schemas` package data, with no working-directory or repository fallback.
    - `src/dopetask/schemas/validator.py` loads schemas through that registry and validates against the package-data schema, not the docs mirror.

    ## 3. Mismatch between docs and runtime
    - Yes. The integration guide points supervisors at `docs/schemas/task_packet.schema.json`, while runtime validation resolves schema authority from packaged `dopetask_schemas`.
    - In this snapshot the two schema files are textually aligned, so the immediate problem is authority drift risk rather than active shape drift.
    - The risk is contractual: docs can imply the mirror is source-of-truth even though installed runtime behavior depends on the packaged schema registry path.

    ## 4. Docs to repair first
    - First: `docs/23_INTEGRATION_GUIDE.md`, because it makes the strongest explicit authority claim and currently names the docs mirror as the packet contract target.
    - Second: `docs/13_TASK_PACKET_FORMAT.md`, because it defines the TaskPacket contract and should state the authority boundary clearly even though it is less explicitly wrong today.
    - Third: any future or adjacent doc that points users to `docs/schemas/task_packet.schema.json` without labeling it as a documentation mirror.

    ## 5. Recommended wording rule for future docs
    - Treat `dopetask_schemas/*.schema.json` as runtime authority.
    - Treat `docs/schemas/*.schema.json` as documentation mirrors unless a doc explicitly says otherwise.
    - When describing validation behavior, say runtime validation loads packaged schemas through the schema registry and validator path, not from the docs tree.
