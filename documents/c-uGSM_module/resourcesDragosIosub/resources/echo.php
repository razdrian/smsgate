<?php
    echo 'via POST'.chr(0x0A).chr(0x0D);
    foreach($_POST as $key=>$data)
        echo $key.':'.$data.chr(0x0A).chr(0x0D);
    echo 'via GET'.chr(0x0A).chr(0x0D);
    foreach($_GET as $key=>$data)
        echo $key.':'.$data.chr(0x0A).chr(0x0D);
?>