'''
    This plugin persists teams through game type changes.
    When changing game type in Quake Live, the default behavior
    is that every player gets put into the spectator team, and then
    they must manually rejoin a team.

    This plugin remembers what team they were on previously and
    automatically puts them back with the right team. You can also
    turn on a flag to turn on the "spec loser" behavior.
'''

# All minqlx plug ins must import minqlx
import minqlx
import time

SUPPORTED_GAMETYPES = ['ca', 'tdm', 'ctf', 'ffa', 'duel', 'oneflag', '1f', 'ft', 'rr', 'har', 'dom', 'ad']
ffa_based_factories = ['ffa', 'iffa', 'duel', 'race']
DEFAULT_TEAMSIZE = 4


# All minqlx plugins must inherit minqlx.Plugin
class spec_losers(minqlx.Plugin):
    def __init__(self):
        # Instantiate a list to remember players on each team before
        # a new game event.
        self.blue_team = []
        self.red_team = []

        # Keep track of winning and losing team (red or blue).
        self.losing_team = ''
        self.winning_team = ''
        self.duel_winner = False

        # Keep track if the new_game is due to a game starting
        self.game_starting = False

        # Keep track of factory...
        self.previous_factory = None

        # Flag to mark the critical time between one game's end and
        # a new game's beginning.
        self.criticalTime = False


        ''' This plugin will do its work at the end of games,
            when the losing team has been decided, so we add
            a listener to our plugin for that event
            (the end of a game). We also include a link to a function
            that is defined in this plugin, where we spell out what
            we want to happen when we reach the end of a game. Remember,
            we want to spec the losing team.
        '''
        self.add_hook("game_end", self.handle_game_end) # good.

        ''' At the end of games, this plugin will ONLY figure out which
            players to spec. This plugin will wait until a new game to
            actually move players to spec, so we need a new call to add_hook()
            in order to hook an event handler to the "new_game" event.
        '''
        self.add_hook("new_game", self.handleNewGame)
        self.add_hook('game_countdown', self.handleGameCountdown)

        ''' Perhaps a better time to move players to spec would be after
            they are finished loading in.
        '''
        self.add_hook("player_loaded", self.handlePlayerLoaded)

        ''' Between the time that I make a list of players to spec and
            actually spec them, some players on the list might disconnect.
            I am going to be proactive by removing from my list if I catch
            them leaving.
        '''
        self.add_hook("player_disconnect", self.handlePlayerDisconnect) #good

        ''' Used to reset blue_team, critical time, and other variables.
        '''
        self.add_hook('game_start', self.handleGameStart)

        ''' Preserve teams when changing map
        '''
        self.add_hook('vote_ended', self.handleVoteEnded)
        self.add_hook('command', self.handleCommand)

        ''' This is a test hook
        '''
        #self.add_hook("vote_started", self.handle_vote_started)
        ''' Now we are going to try adding a command. This command will just
            print "Hello World" to the whole channel.
        '''
        #self.add_command("helloworld", self.cmd_helloworld)

        # Commands for debugging
        self.add_command("printteams", self.cmd_printteams)

        # Turns spec loser functionality on or off.
        self.set_cvar_once("qlx_specLosersEnable", "0")

    ''' Helper function so that I can do self[key]
    '''
    def __getitem__(self,key):
        return getattr(self,key)

    def getFactory(self):
        return self.get_cvar('g_factory').lower()

    def isTeamBased(self):
        return self.getFactory() not in ffa_based_factories

    ''' In accordance with Python rules, self is a paramenter, and it's the
        first parameter, but where do the other parameters come from? The
        answer is a bit lengthy, but simple.

        They come from the hooks that we added. What a hook does is link an
        event to an event handler. In this case, the event is "game_end", and
        the event handler is this method.

        Events are defined in the file "_events.py", which you can see here:
        https://github.com/MinoMino/minqlx/blob/master/python/minqlx/_events.py

        If you scroll down a little bit, you will see a section called
        "EVENT DISPATCHERS". In that section, you will see many class
        definitions, and if you look at the body of those class definitions,
        you will always find a variable called "name" with a string assigned
        to it. These are the strings for the events that you end up putting in
        add_hook methods like those in this file.

        We hooked up this handler method (handle_game_end) to the "game_end"
        event, so go ahead and search for 'name = "game_end"' in _events.py.
        If you examine the class for "game_end", you will find a statement
        that says "super().dispatch(...)". In fact, you will find this
        statement in every class definition. This is where the parameters
        for the handler methods come from.

        In this case, the only argument in super().dispatch(...) is "data", so
        in addition to "self", we need to add a parameter for "data" in our
        function header.
    '''
    def handle_game_end(self, data):
        ''' The first thing we always want to do is check if the
            current game type is supported. Our plugin has no business
            executing if the game type isn't right!
        '''
        gameType = self.game.type_short
        if gameType not in SUPPORTED_GAMETYPES:
            # self.msg("This game mode is not supported by the spec_losers plugin.")
            return

        self.resetVariables()

        ''' We are now in the time between making a list of players to spec
            and actually speccing, so we set our criticalTime flag to true.
        '''
        self.criticalTime = True
        self.previous_factory = self.getFactory()

        ''' For now, just report that the game is over.

            The self.msg() function is the console.log() equivalent.
            The msg() function is inherited from the super class minqlx.Plugin.
            Remember, all plugins must inherit minqlx.Plugin! Just check the
            class header of this plugin. The definition of msg() is here:
            https://github.com/MinoMino/minqlx/blob/master/python/minqlx/_plugin.py
        '''
        # self.msg("spec_losers plugin says: The game is over.")

        ''' Print the data dictionary
        for k, v in data.items():
            self.msg(k)
            self.msg(v)
        '''

        if self.isTeamBased():
            ''' Determine which team won
                TSCORE0 is red team's score
                TSCORE1 is blue team's score
            '''
            if data['TSCORE0'] > data['TSCORE1']:
                self.winning_team = "red"
                self.losing_team = "blue"
            elif data['TSCORE0'] < data['TSCORE1']:
                self.winning_team = "blue"
                self.losing_team = "red"
        elif gameType == 'duel':
            self.duel_winner = True
            teams = self.teams()
            teams['free'].sort(reverse = True, key = self.getPlayerScore)

        self.rememberTeams()

        return

    def getPlayerScore(self, player):
        return player.stats.score

    def rememberTeams(self):
        ''' Now that we know which team is the losing team,
            we will populate our list of players to be spec'd.

            We won't spec them now. We will wait until a new map
            loads to spec players.
        '''
        # self.msg('spec_losers.py: Remembering teams. Wish me luck!')
        teams = self.teams()
        teams['free'].sort(reverse = True, key = self.getPlayerScore)

        # Handles ffa
        for i, player in enumerate(teams['free']):
            game_factory = self.getFactory()

            if game_factory == 'duel' and i > 0 and self.duel_winner:
                # self.msg("spec_losers.py: Gonna spec " + player.name)
                continue

            if i % 2 == 0 and len(self.blue_team) <= DEFAULT_TEAMSIZE:
                self.blue_team.append(player)
            elif i % 2 == 1 and len(self.red_team) <= DEFAULT_TEAMSIZE:
                self.red_team.append(player)
            else:
                # self.msg("spec_losers.py: Gonna spec " + player.name)
                pass

        for player in teams['blue']:
            if self.losing_team == 'blue':
                # self.msg("spec_losers.py: Gonna spec " + player.name)
                pass
            self.blue_team.append(player)

        for player in teams['red']:
            if self.losing_team == 'red':
                # self.msg("spec_losers.py: Gonna spec " + player.name)
                pass
            self.red_team.append(player)

    def handleGameCountdown(self):
        self.game_starting = True

    def handleNewGame(self):
        if self.game_starting:
            self.game_starting = False
            return

        ''' Before most new_games, Quake puts everyone in spectator team.
            If the new_game's factory is the same as the previous game's factory,
            then QL will automatically put players back into the teams. But if the
            new_game's factory is different, then QL will leave everyone in spectator team.
            So, my job is to put everyone back in the teams manually.
        '''

        game_factory = self.getFactory()
        # self.cmd_printteams('hello', 'this', 'test')
        if game_factory != self.previous_factory:
            # self.msg('spec_losers.py: Different factory - Manually restoring order')
            ffa_based_factory = game_factory in ffa_based_factories
            if ffa_based_factory:
                # self.msg('spec_losers.py: ffa based game.')
                self.putPlayersInTeams('free', 'free')
            else:
                # self.msg('spec_losers.py: team based game.')
                self.putPlayersInTeams('red', 'blue')
        else:
            # self.msg('spec_losers.py: Same factory - Server will automatically restore order')
            pass

        # Remove losers
        self.removeLosers()
        return None

    def putPlayersInTeams(self, red_destination, blue_destination):
        game_factory = self.getFactory()
        ffa_based_factory = game_factory in ffa_based_factories

        if ffa_based_factory:
            joined_list = self.red_team + self.blue_team
            joined_list.sort(reverse = True, key = self.getPlayerScore)
            for i, player in enumerate(joined_list):
                if game_factory == 'duel' and i > 1:
                    continue

                self.putPlayerInTeam(player, 'free')
        else:
            for player in self.red_team:
                self.putPlayerInTeam(player, red_destination)
            for player in self.blue_team:
                self.putPlayerInTeam(player, blue_destination)


    def putPlayerInTeam(self, player, destination):
        teams = self.teams()
        # self.msg('spec_losers.py: Putting {} in {}'.format(str(player.name), str(destination)))
        player.put(destination)
        teams[destination].append(player)


    def handleVoteEnded(self, votes, vote, args, passed):
        # self.msg(str(votes))
        # self.msg(str(vote)) # map
        # self.msg(str(args)) # ragnarok tdm
        # self.msg(str(passed)) # True or False

        if passed and vote == 'map':
            # self.msg('spec_losers.py: handleVoteEnded')
            self.resetVariables()
            self.rememberTeams()
            self.criticalTime = True
            self.previous_factory = self.getFactory()

    def handleCommand(self, caller, command, args):
        if '!map ' in args:
            # self.msg('speclosers.py: Handling !map command')
            self.resetVariables()
            self.rememberTeams()
            self.criticalTime = True
            self.previous_factory = self.getFactory()

    @minqlx.thread
    def removeLosers(self):
        # Return if removeLoser functionality is disabled.
        enable = self.get_cvar("qlx_specLosersEnable")
        if enable != '1':
            return

        # Return if we're not between the time of making a list and speccing.
        if self.criticalTime == False:
            return

        # self.msg('spec_losers.py: Removing losing team in 0.5 secs')
        time.sleep(1)
        # self.msg('spec_losers.py: losing team: {}'.format(str(self.losing_team)))

        if self.losing_team:
            teams = self.teams()
            loser_squad = ''
            if self.losing_team == 'red':
                loser_squad = 'red_team'
            elif self.losing_team == 'blue':
                loser_squad = 'blue_team'

            losing_players = []
            game_factory = self.getFactory()
            ffa_based_factory = game_factory in ffa_based_factories
            if ffa_based_factory:
                losing_players = teams['free']
            else:
                losing_players = teams[self.losing_team]

            # self.msg('spec_losers.py: loser_squad: {}'.format(str(loser_squad)))

            for player in losing_players:
                # self.msg('spec_losers.py: player up: {}'.format(player))
                if player in self[loser_squad]:
                    # self.msg('spec_losers.py: loser up: {}'.format(player))
                    player.put('spectator')
                    teams['spectator'].append(player)
                    # self.msg('spec_losers.py: I have removed {}'.format(str(player.name)))

        self.resetVariables()


    ''' When a player finishes loading, check if he's on the list.
        If so, remove him. If not, do nothing.
    '''
    def handlePlayerLoaded(self, player):
        # self.msg('spec_losers.py: Player {} has joined the chat!'.format(str(player.name)))
        return

    def handleGameStart(self, data):
        self.resetVariables(1)

    ''' When the game starts, I want to delay resetting of variables a
        little bit (to prevent the new_game handler from running).
    '''
    @minqlx.thread
    def resetVariables(self, delay = None):
        if delay:
            time.sleep(delay)

        self.blue_team = []
        self.red_team = []
        self.losing_team = ''
        self.winning_team = ''
        self.duel_winner = False
        self.criticalTime = False
        self.game_starting = False
        self.previous_factory = None

    ''' Between the time that I make my list of players to spec and the time
        that I actually move them to spec, some of those players might
        disconnect. In those cases, this function will remove those players
        from my list.
    '''
    def handlePlayerDisconnect(self, player, reason):
        # Return if we're not between the time of making a list and speccing.
        if self.criticalTime == False:
            return

        # Return if game type is not supported.
        gameType = self.game.type_short
        if gameType not in SUPPORTED_GAMETYPES:
            # self.msg("This game mode is not supported by the spec_losers plugin.")
            return


        # Return if the player is not on our list, or
        # remove the player from our list.
        if player in self.blue_team:
            self.blue_team.remove(player)
        elif player in self.red_team:
            self.red_team.remove(player)

        # Method is complete.
        return

    ''' Command methods always take the following four parameters
    def handle_vote_started(self, caller, vote, args):
        # Check if the game type is right
        gameType = self.game.type_short
        if gameType not in SUPPORTED_GAMETYPES:
            caller.tell("This game mode is not supported by the spec_losers plugin.")
            return

        # Report that a vote has been started
        caller.tell("spec_losers plugin says: A vote has been started.")
        return

    def cmd_helloworld(self, player, msg, channel):
        channel.reply("Hello, World!")
    '''
    # Prints what the teams are
    def cmd_printteams(self, player, msg, channel):
        teams = self.teams()
        teamRedString = "RED: "
        teamBlueString = "BLUE: "
        teamSpectatorString = "SPEC: "
        teamFreeString = "FREE: "

        # Build string for red team
        for player in teams["red"]:
            teamRedString += player.name + ", "
        # Build string for blue team
        for player in teams["blue"]:
            teamBlueString += player.name + ", "
        # Build string for spectator team
        for player in teams["spectator"]:
            teamSpectatorString += player.name + ", "
        # Build string for free team
        for player in teams["free"]:
            teamFreeString += player.name + ", "

        # Print results
        # channel.reply(teamRedString)
        # channel.reply(teamBlueString)
        # channel.reply(teamSpectatorString)
        # channel.reply(teamFreeString)

        self.msg(teamRedString)
        self.msg(teamBlueString)
        self.msg(teamSpectatorString)
        self.msg(teamFreeString)

        # End method
        return

