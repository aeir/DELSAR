<?php
/*  twitter_stream_word.php
 *
 *  Creates a twitter stream for a single keyword
 *  Filters out tweets that contain specific phrases
 *  Saves matching tweets into a database
 *  
 *  Changes emotion every 5 minutes
 *  @requires: JSON.php; timer.php 
 *  @author: Eugene Yuta Bann
 *  @version: 29.12.12    
 *
 */ 
  set_time_limit(0);
  include("JSON.php");
  include("timer.php");
  $currentEmotionCode = 0;
  $filter = array();
  $filter[0] = array(0 => 'RT ','not accepting', 'not really accepting', 'not that accepting', 'wasn\'t that accepting', 'wasn\'t very accepting', 'unaccepting', 'disaccepting', 'http://', ' RT', '@');
  $filter[1] = array(0 => 'RT ','not angry', 'not really angry', 'not that angry', 'wasn\'t that angry', 'wasn\'t very angry', 'unangry', 'angry birds', 'http://', ' RT', '@');
  $filter[2] = array(0 => 'RT ','not anticipating', 'not really anticipating', 'not that anticipating', 'wasn\'t that anticipating', 'wasn\'t very anticipating', 'unanticipating', 'disanticipating', 'http://', ' RT', '@');
  $filter[3] = array(0 => 'RT ','not anxious', 'not really anxious', 'not that anxious', 'wasn\'t that anxious', 'wasn\'t very anxious', 'unanxious', 'disanxious', 'http://', ' RT', '@');
  $filter[4] = array(0 => 'RT ','not ashamed', 'not really ashamed', 'not that ashamed', 'wasn\'t that ashamed', 'wasn\'t very ashamed', 'unashamed', 'disashamed', 'http://', ' RT', '@');
  $filter[5] = array(0 => 'RT ','not contempt', 'not really contempt', 'not that contempt', 'wasn\'t that contempt', 'wasn\'t very contempt', 'uncontempt', 'discontempt', 'in contempt', 'contempt of', 'http://', ' RT', '@');
  $filter[6] = array(0 => 'RT ','not depressed', 'not really depressed', 'not that depressed', 'wasn\'t that depressed', 'wasn\'t very depressed', 'undepressed', 'disdepressed', 'http://', ' RT', '@');
  $filter[7] = array(0 => 'RT ','not disgusted', 'not really disgusted', 'not that disgusted', 'wasn\'t that disgusted', 'wasn\'t very disgusted', 'undisgusted', 'disdisgusted', 'http://', ' RT', '@');
  $filter[8] = array(0 => 'RT ','not excited', 'not really excited', 'not that excited', 'wasn\'t that excited', 'wasn\'t very excited', 'unexcited', 'disexcited', 'http://', ' RT', '@');
  $filter[9] = array(0 => 'RT ','not guilty', 'not really guilty', 'not that guilty', 'wasn\'t that guilty', 'wasn\'t very guilty', 'unguilty', 'found guilty', 'http://', ' RT', '@');
  $filter[10] = array(0 => 'RT ','not happy', 'not really happy', 'not that happy', 'wasn\'t that happy', 'wasn\'t very happy', 'unhappy', 'happy birthday', 'http://', ' RT', '@');
  $filter[11] = array(0 => 'RT ','not interested', 'not really interested', 'not that interested', 'wasn\'t that interested', 'wasn\'t very interested', 'uninterested', 'disinterested', 'http://', ' RT', '@');
  $filter[12] = array(0 => 'RT ','not joyful', 'not really joyful', 'not that joyful', 'wasn\'t that joyful', 'wasn\'t very joyful', 'unjoyful', 'disjoyful', 'http://', ' RT', '@');
  $filter[13] = array(0 => 'RT ','not miserable', 'not really miserable', 'not that miserable', 'wasn\'t that miserable', 'wasn\'t very miserable', 'unmiserable', 'dismiserable', 'http://', ' RT', '@');
  $filter[14] = array(0 => 'RT ','not pleased', 'not really pleased', 'not that pleased', 'wasn\'t that pleased', 'wasn\'t very pleased', 'unpleased', 'displeased', 'http://', ' RT', '@');
  $filter[15] = array(0 => 'RT ','not relaxed', 'not really relaxed', 'not that relaxed', 'wasn\'t that relaxed', 'wasn\'t very relaxed', 'unrelaxed', 'disrelaxed', 'http://', ' RT', '@');
  $filter[16] = array(0 => 'RT ','not sad', 'not really sad', 'not that sad', 'wasn\'t that sad', 'wasn\'t very sad', 'unsad', 'dissad', 'http://', ' RT', '@');
  $filter[17] = array(0 => 'RT ','not scared', 'not really scared', 'not that scared', 'wasn\'t that scared', 'wasn\'t very scared', 'unscared', 'disscared', 'http://', ' RT', '@');
  $filter[18] = array(0 => 'RT ','not sleepy', 'not really sleepy', 'not that sleepy', 'wasn\'t that sleepy', 'wasn\'t very sleepy', 'unsleepy', 'dissleepy', 'http://', ' RT', '@');
  $filter[19] = array(0 => 'RT ','not stressed', 'not really stressed', 'not that stressed', 'wasn\'t that stressed', 'wasn\'t very stressed', 'unstressed', 'disstressed', 'http://', ' RT', '@');
  $filter[20] = array(0 => 'RT ','not surprised', 'not really surprised', 'not that surprised', 'wasn\'t that surprised', 'wasn\'t very surprised', 'unsurprised', 'dissurprised', 'http://', ' RT', '@'); 
  $searchword = array();
  $searchword[0] = "accepting"; 
  $searchword[1] = "angry"; 
  $searchword[2] = "anticipating"; 
  $searchword[3] = "anxious"; 
  $searchword[4] = "ashamed"; 
  $searchword[5] = "contempt"; 
  $searchword[6] = "depressed"; 
  $searchword[7] = "disgusted"; 
  $searchword[8] = "excited"; 
  $searchword[9] = "guilty"; 
  $searchword[10] = "happy"; 
  $searchword[11] = "interested"; 
  $searchword[12] = "joyful"; 
  $searchword[13] = "miserable"; 
  $searchword[14] = "pleased"; 
  $searchword[15] = "relaxed"; 
  $searchword[16] = "sad"; 
  $searchword[17] = "scared"; 
  $searchword[18] = "sleepy"; 
  $searchword[19] = "stressed"; 
  $searchword[20] = "surprised";
  
  function harvest() {
    global $currentEmotionCode;
    global $filter;
    global $searchword;    
    $query_data = array('track' => $searchword[$currentEmotionCode]);
    $user = 'USERNAME';	
    $pass = 'PASSWORD'; 
    $fp = fsockopen("ssl://stream.twitter.com", 443, $errno, $errstr, 720);
    if(!$fp){
      echo "$errstr ($errno)\n";
    } 
    else {
      $mysqli = new mysqli('HOSTNAME', 'USERNAME', 'PASSWORD', 'DATABASE');
      if (mysqli_connect_errno()) { 
         printf("Can't connect to MySQL Server. Errorcode: %s\n", mysqli_connect_error());  
      }
    	$request = "GET /1/statuses/filter.json?".http_build_query($query_data)." HTTP/1.1\r\n";
    	$request .= "Host: stream.twitter.com\r\n";
    	$request .= "Authorization: Basic ".base64_encode($user.":".$pass)."\r\n\r\n";
    	fwrite($fp, $request);
    	// Start a timer, end streaming the current emotion after 5 minutes
      $timer = new timer(1); // constructor starts the timer
      while(!feof($fp) && $timer->get() < 300) {
    		$json = fgets($fp);
    		$tweet = json_decode($json, true);
    		if($tweet) {
          $in = true;		
          foreach($filter[$currentEmotionCode] as $word) {
            if(stripos($tweet["text"],$word) !== false) {$in = false; echo "SKIPPED ".$word."\n\n";} 
          }
          if(str_word_count($tweet["text"]) < 10) {$in = false; echo "Less than 10 words SKIPPED\n\n";} 
          //if(!preg_match('~[^A-Za-z0-9 ]~', $tweet["text"])) {$in = false; echo "Non alphanumeric SKIPPED\n\n";} 
          if($in) {     
      		  $text = $mysqli->real_escape_string($tweet["text"]);
      		  $tweet_id = $mysqli->real_escape_string($tweet["id_str"]);
      		  $screen_name = $mysqli->real_escape_string($tweet["user"]["screen_name"]);
      		  $retweet_count = $mysqli->real_escape_string($tweet["retweet_count"]);
            $time_zone = $mysqli->real_escape_string($tweet["user"]["time_zone"]);
            if($result = $mysqli->query("INSERT INTO `PROJtwitterEDB`.`ETWEETS`(`tweet_id`,`text`,`emotion`,`screen_name`,`retweet_count`,
              `created_at`,`timezone`) VALUES($tweet_id,'$text','$searchword[$currentEmotionCode]','$screen_name',$retweet_count,NOW(),
              '$time_zone')")) {
              echo $tweet["text"]." FROM ".$tweet["user"]["time_zone"]." SAVED TO DATABASE AT ".date("Y-m-d H:i:s")."\n";
            }
            else {
              echo $mysqli->error;
            }		
    		  }
        }
      }
    	$mysqli->close();
    	fclose($fp);                   
    }
    // Increment up to 21 the loop round to 1
    if($currentEmotionCode + 1 == 21) {
      $currentEmotionCode = 0;
    }
    else {
      $currentEmotionCode += 1;
    }
    harvest();
  }
  
  harvest();    
?>