NAME=aciwc
HOST=root@47.89.15.185
REMOTE_DIR=/usr/local/opt/$NAME

rsync -av --exclude-from='rsyncignore.txt' --delete . $HOST:$REMOTE_DIR
ssh $HOST NAME=$NAME HOME=$REMOTE_DIR 'bash -s' <<'ENDSSH'
    $HOME/env/bin/pip install -U -r $HOME/requirements.txt
    supervisorctl restart $NAME
ENDSSH
