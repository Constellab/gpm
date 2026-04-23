#!/bin/bash
set -e

ENTRYPOINT_SCRIPT="$0"
ENTRYPOINT_ARGS=("$@")
source /init-lab/align-user.sh
align_labuser_and_switch /lab

# Running as labuser from here on.

bash /init-lab/init_lab.sh GLAB
echo "Glab environment is ready."

case "${RUN_MODE:-server}" in
    server)
        exec bash -c "gws server run --settings-path /lab/.sys/app/settings.json"
        ;;
    test)
        case "${TEST_PARALLEL:-true}" in
            true)  test_cmd="test-parallel" ;;
            false) test_cmd="test" ;;
            *)
                echo "Unknown TEST_PARALLEL '${TEST_PARALLEL}'. Expected 'true' or 'false'." >&2
                exit 2
                ;;
        esac
        exec bash -c "gws server ${test_cmd} all --brick-name \"${TEST_BRICK_NAME}\""
        ;;
    *)
        echo "Unknown RUN_MODE '${RUN_MODE}'. Expected 'server' or 'test'." >&2
        exit 2
        ;;
esac
