<?php
if( empty($_GET['id']) ){
    echo json_encode( array('code'=>-1, 'msg'=>'error'));
    exit;
}

$file_db = "./upload/db.txt";
$db = array();
$rows = array();
if( file_exists($file_db) ){
    $db = file($file_db);
    foreach($db as $key=>$row){
        $row = trim($row);
        if(!empty($row)){
            $row = explode("\t",$row);
            if( $row[0] == $_GET['id'] ){
                unset($db[$key]);
                break;;
            }
        }
    }
    $content = implode("\n",$db);
    file_put_contents($file_db, $content);
}

echo json_encode( array('code'=>0, 'msg'=>'ok') );
