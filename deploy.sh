NAME=aciwc
HOST=root@47.89.15.185
REMOTE_DIR=/usr/local/opt/$NAME

rsync -av --exclude-from='rsyncignore.txt' --delete . $HOST:$REMOTE_DIR
ssh $HOST NAME=$NAME 'bash -s' <<'ENDSSH'
    supervisorctl restart $NAME
ENDSSH
