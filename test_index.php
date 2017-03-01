<html>
<body>
<head>
<meta charset="utf-8">
<title>testphp.com</title>
<style>
.error {color: #FF0000;}
</style>
</head>
<?php
$serverlist='';
if ($_SERVER["REQUEST_METHOD"] == "POST")
{
    if (empty($_POST["serverlist"]))
    {
        $serverlistErr = "该项不能为空";
    }
    else
    {
        $serverlist = test_input($_POST["serverlist"]);
        // 检测名字是否只包含字母跟空格
        if (!preg_match("/^[a-zA-Z0-9 ]*$/",$serverlist))
        {
            $serverlistErr = "只允许字母数字和空格"; 
        }
    }
}
function test_input($data)
{
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}
?>
<h1>请提交你的服务器列表.</h1>
<form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">
<textarea name="serverlist" rows="5" cols="40"><?php echo $serverlist;?></textarea>
</br><span class="error">* <?php echo $serverlistErr;?></span>
</br></br>
<input type="submit" value="提交">
</form>
<?php
echo "your input server is: ".$serverlist;
?>
</body>
</html> 
