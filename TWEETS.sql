----------------------------------
-- TWEETS.sql                   --
--                              --
-- Creates the TWEETS table     --
--                              --
-- Compatibility: MySQL         --
--
-- For use with twitter_stream_word.php
--                              
--                              --
----------------------------------

--
-- Table structure for table `TWEETS`
--

CREATE TABLE `TWEETS` (
  `id` int(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Table key',
  `tweet_id` bigint(20) UNSIGNED NOT NULL COMMENT 'Twitter tweet ID for lookup',
  `text` varchar(150) NOT NULL,
  `emotion` varchar(150) NOT NULL,
  `screen_name` varchar(255) NOT NULL,
  `retweet_count` int(11) NOT NULL,
  `created_at` datetime NOT NULL COMMENT 'Timestamp of database insert',
  `timezone` varchar(255) NOT NULL COMMENT 'Twitter-defined, see seperate SQL file for datetime conversion',
  `flag` tinyint(4) NOT NULL COMMENT 'Generic Flag',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;