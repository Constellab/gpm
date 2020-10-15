
user_dir=$1
find ${user_dir}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${user_dir}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${user_dir}/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
