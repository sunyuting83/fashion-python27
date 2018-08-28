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
            $rows[] = array(
                'name'=>$row[0],
                'sort'=>$row[1],
                'path'=>"http://localhost/webuploader/upload/".$row[0],
                'key'=>$row[0],
                'size'=>0,
            );
        }
    }
}

function cmp($a, $b){
    return $a['sort']>$b['sort'] ? 1: -1;
}
usort($rows, 'cmp');

echo json_encode( $rows );
