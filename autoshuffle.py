import minqlx

ffa_based_factories = ['ffa', 'iffa', 'duel']

class autoshuffle(minqlx.Plugin):
   def __init__(self):
      self.add_hook('vote_called', self.handleVoteCalled)
      self.add_hook('game_countdown', self.handleGameCountdown)

   def handleVoteCalled(self, caller, vote, args):
      # If it is not shuffle, whatever
      if vote.lower() != 'shuffle':
         return

      # Shuffle won't be called in ffa or duel
      if self.game.type_short in ffa_based_factories:
         return

      self.msg("^7Callvote shuffle ^1DENIED ^7since the server will ^3autoshuffle ^7on match start.")
      return minqlx.RET_STOP_ALL

   @minqlx.delay(5)
   def handleGameCountdown(self):
      if self.game.type_short in ffa_based_factories:
         return

      # Do the autoshuffle
      self.center_print("*autoshuffle*")
      self.msg("^7Autoshuffle...")
      self.shuffle()

      if 'balance' in minqlx.Plugin._loaded_plugins:
         self.msg("^7Balancing on skill ratings...")
         b = minqlx.Plugin._loaded_plugins['balance']
         teams = self.teams()
         players = dict([(p.steam_id, self.game.type_short) for p in teams["red"] + teams["blue"]])
         b.add_request(players, b.callback_balance, minqlx.CHAT_CHANNEL)
      else:
         self.msg("^7Couldn't balance on skill, make sure ^6balance^7 is loaded.")