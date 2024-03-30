cvat-cli --server-host 192.168.1.26 --server-port 8080 --auth "monurcan:iammemo55" \
    dump --format 'YOLO 1.1' --with-images True $1 $1.zip
