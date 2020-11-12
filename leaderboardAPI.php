<?php
	//NOTE : 	THIS CODE IS THE EXACT SAME ONE AS THE ONE WORKING ON THE SERVER MANAGING THE LEADERBOARD
	//			THE DATABASE INFORMATIONS WERE REPLACED IN THE CONNECTION STRINGS, FOR THE SECURITY OF MY DATABASE
	
	//If all specified GET elements are given...
	if(isset($_GET['username']) and isset($_GET['time']) and isset($_GET['god']) and isset($_GET['levels']) and isset($_GET['key']))
	{
		$username = ucfirst($_GET['username']);
		$time =  $_GET['time'];
		$god = $_GET['god'];
		$levels = $_GET['levels'];
		$key = $_GET['key'];
		if ($key === sha1($username.$time."it's salty h€re"))	//If the given key is the given one
		{
			try
			{
				$bdd = new PDO('mysql:host=HOSTNAME;dbname=DBNAME', 'USERNAME', 'PASSWORD');	//Connect to the database
			}
			catch(Exception $e)
			{
				die('Error');
			}
			$reponse = $bdd->prepare('SELECT * FROM leaderboard WHERE username = :username');	//Try to get data from the specified username, if it already exists
			$reponse->execute(array(
				'username' => htmlspecialchars($username)
			));
			$oldtime = -1;	//If the player wasn't in the database, his old time is "-1"
			if ($donnees = $reponse->fetch())
			{
				$oldtime = $donnees['time'];		//Get player old time
				$oldlevels = $donnees['levels'];	//Get player old level progression
			}
			$reponse->closeCursor();
			//If the player wasn't in the database yet OR the new level progression is higher than the old one OR the level progression is the same but in less time
			if (($oldtime === -1) or ($levels > $oldlevels) or (($levels === $oldlevels) and ($time < $oldtime)))
			{
				try
				{
					$bdd = new PDO('mysql:host=HOSTNAME;dbname=DBNAME', 'USERNAME', 'PASSWORD');
				}
				catch(Exception $e)
				{
					die('Error');
				}
				$reponse = $bdd->prepare('DELETE FROM leaderboard WHERE username = :username; INSERT INTO leaderboard (username, time, levels, god) VALUES (:username, :time, :levels, :god)');	//Delete the old user infos and insert the new one
				$reponse->execute(array(
					'username' => htmlspecialchars($username),
					'time' => htmlspecialchars($time),
					'levels' => htmlspecialchars($levels),
					'god' => htmlspecialchars($god)
				));
				$reponse->closeCursor();
				echo "Your score was saved.\n";
			}
			else
			{
				echo "This score was worse than your previous one.\n";
			}
		}
		else
		{
			echo "Your score could not be saved.\n";
		}
	}
	echo "Leaderboard :\n";
	try
	{
		$bdd = new PDO('mysql:host=HOSTNAME;dbname=DBNAME', 'USERNAME', 'PASSWORD');
	}
	catch(Exception $e)
	{
		die('Error');
	}
	//Get the 10 best players, first being : no cheat activated, higher level progression, les time
	$reponse = $bdd->prepare('SELECT * FROM leaderboard ORDER BY god ASC, levels DESC, time ASC LIMIT 10');
	$reponse->execute();
	$i = 1;
	while ($donnees = $reponse->fetch())
	{
		$godmode = "";
		if (intval($donnees['god']) === 1)
		{
			$godmode = " - with cheats";
		}
		echo $i." : ".$donnees['username']." - ".$donnees['levels']." levels in ".$donnees['time']." sec".$godmode."\n";
		$i += 1;
	}
	$reponse->closeCursor();
?>