# Zebby's Minqlx Plugins

### About

pql_warmup.py, spec_losers.py, zebby_gamemodes.py, and zebby_warmup.py were written by me. The other files were written by others, but modified by me to fix bugs or add functionality.

###### pql_warmup.py
Allows me, as the server admin, to toggle air control and crouch sliding on my server during warmup.

###### spec_losers.py
Originally written to move losing teams to spectator mode to reduce waiting times in the queue. While it retains this functionality, it now also serves to persist teams during game type changes. The default Quake Live behavior when the game type changes is to put all players in spectator mode. To me this is unacceptable.

###### zebby_gamemodes.py
Applies custom settings to each game type to make them actually fun to play. For example, spawns players with all weapons and full health, like in the Clan Arena game type.

###### zebby_warmup.py
Applies custom settings based on the game state, warmup or in_progress. For example, enables infinite ammo during warmup.

### Installation
Just like any other plugin, put the desired plugin source file (e.g., spec_losers.py) in your minqlx-plugins folder, and then add the plugin's name (filename w/o the extension (e.g., spec_losers)) to the qlx_plugins variable! In your bash terminal, cd to the minqlx-plugins directory and use wget on the raw copy of the plugin you want. Be sure to include the -O flag to overwrite if the file already exists in the directory!!

```
cd minqlx-plugins
wget https://raw.githubusercontent.com/codezebby/minqlx-plugins/master/zebby_warmup.py -O zebby_warmup.py
```
