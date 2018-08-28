<?php
if(empty($_FILES))
    die(json_encode(array('code'=>-1,'msg'=>'error')));

$file = $_FILES['file'];
if($file['error']!=0 || $file['size']< 1 ){
    die(json_encode(array('code'=>-1,'msg'=>'error','id'=>$_POST['id'])));
}

move_uploaded_file( $file['tmp_name'], "./upload/".$file['name']);

$file_db = "./upload/db.txt";
$db = array();
$rows = array();
if( file_exists($file_db) ){
    $db = file($file_db);
    foreach($db as $row){
        $row = trim($row);
        if(!empty($row)){
            $row = explode("\t",$row);
            $rows[$row[0]] = $row[1];
        }
    }
}
$rows[$file['name']] = $_POST['sort'];

$write_db = array();
foreach($rows as $key=>$val){
    $write_db[] = trim($key."\t".$val);
}

$content = implode("\n",$write_db);
file_put_contents($file_db, $content);

echo json_encode( array( 'code'=>0, 'msg'=>'ok', 'id'=>$_POST['id'] ) );
