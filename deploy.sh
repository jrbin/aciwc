NAME=aciwc
HOST=root@47.89.15.185
REMOTE_DIR=/usr/local/opt/$NAME

rsync -rv --exclude ".*" --exclude "__pycache__" --exclude "deploy.sh" --exclude "env" . $HOST:$REMOTE_DIR
ssh $HOST NAME=$NAME 'bash -s' <<'ENDSSH'
    supervisorctl restart $NAME
ENDSSH
