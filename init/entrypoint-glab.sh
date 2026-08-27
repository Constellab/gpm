#!/bin/bash
set -e

ENTRYPOINT_SCRIPT="$0"
ENTRYPOINT_ARGS=("$@")
source /init-lab/align-user.sh
align_labuser_and_switch "${LAB_FOLDER}" /init-lab/init-ssh.sh

# Running as labuser from here on.
# If the container was started directly as labuser (via `user:` in compose),
# the hook above was skipped — run the SSH init now via sudo.
if [ ! -f /run/init-ssh-done ]; then
    sudo -E bash /init-lab/init-ssh.sh
fi

bash /init-lab/init_lab.sh GLAB
echo "Glab environment is ready."

case "${RUN_MODE:-server}" in
    server)
        exec bash -c "gws server run --settings-path ${LAB_FOLDER}/.sys/app/settings.json"
        ;;
    test)
        test_args=()
        case "${TEST_PARALLEL:-true}" in
            true)  test_args+=(--parallel) ;;
            false) ;;
            *)
                echo "Unknown TEST_PARALLEL '${TEST_PARALLEL}'. Expected 'true' or 'false'." >&2
                exit 2
                ;;
        esac
        for brick in ${TEST_BRICK_NAME}; do
            test_args+=(--brick-name "${brick}")
        done
        if [[ -n "${TEST_OUTPUT_DIR:-}" ]]; then
            test_args+=(--output-dir "${TEST_OUTPUT_DIR}")
        fi
        exec gws server test-all "${test_args[@]}"
        ;;
    *)
        echo "Unknown RUN_MODE '${RUN_MODE}'. Expected 'server' or 'test'." >&2
        exit 2
        ;;
esac
