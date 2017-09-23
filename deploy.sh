NAME=aciwc
HOST=root@aciwc.com
REMOTE_DIR=/srv/$NAME

rsync -av --exclude-from='rsyncignore.txt' --delete . $HOST:$REMOTE_DIR
ssh $HOST NAME=$NAME HOME=$REMOTE_DIR 'bash -s' <<'ENDSSH'
    $HOME/venv/bin/pip install -U -r $HOME/requirements.txt
    supervisorctl restart $NAME
ENDSSH
