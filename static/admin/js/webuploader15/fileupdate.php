<?php
$file_db = "./upload/db.txt";
$db = array();
$rows = array();
if( file_exists($file_db) ){
    $db = file($file_db);
    foreach($db as $row){
        $row = trim($row);
        if(!empty($row)){
            $row = explode("\t",$row);
            $key = str_replace(".","_",trim($row[0]));
            if( isset($_POST[$key] ) ){
                $row[1] = $_POST[$key];
            }
            $rows[] = $row[0]."\t".$row[1];
        }
    }
    $content = implode("\n", $rows);
    file_put_contents($file_db, $content);
}

echo json_encode( array('code'=>0, 'msg'=>'ok') );
