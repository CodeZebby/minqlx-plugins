import minqlx
import time

this_is_broken = {
   'warmup': {
      'g_infiniteAmmo': '1',
      'g_freezeThawTime': '2000',
      'g_freezeAutoThawTime': '120000',
      'g_freezeEnvironmentalRespawnDelay': '5000',
   },
   'game': {
      'g_infiniteAmmo': '0',
      'g_freezeThawTime': '120000',
      'g_freezeAutoThawTime': '120000',
      'g_freezeEnvironmentalRespawnDelay': '120000',
   }
}

class zebby_warmup(minqlx.Plugin):
   def __init__(self):
      # self.add_hook("game_end", self.handleGameEnd) # good.
      self.add_hook('game_countdown', self.handleGameCountdown)
      self.add_hook('new_game', self.handleNewGame)
      self.add_command('zebby_warmup', self.handleZebbyWarmupCommand, 5)

   def setCvars(self, key):
      for cvar, value in this_is_broken[key].items():
         # self.msg('Setting: {} is {}'.format(cvar, value))

         if cvar == 'teamsize' and key == 'team_based':
            ''' We need to do this to keep sensible team sizes:
                - when switching between ffa and team based modes
                - when a teamsize has already been set (e.g., via a vote)
            '''
            teamsize = self.get_cvar('teamsize')
            if teamsize == '0':
               self.set_cvar(cvar, value)
         else:
            self.set_cvar(cvar, value)

   def handleZebbyWarmupCommand(self, player, msg, channel):
      g_infiniteAmmo = self.get_cvar('g_infiniteAmmo')

      # channel.reply('g_infiniteAmmo is {}'.format(g_infiniteAmmo))

      if g_infiniteAmmo == '1':
         self.set_cvar('g_infiniteAmmo', '0')
      elif self.game.state != 'in_progress':
         self.set_cvar('g_infiniteAmmo', '1')


   def handleGameEnd(self):
      self.setCvars('warmup')

   @minqlx.thread
   def handleNewGameThreaded(self):
      time.sleep(0.4)
      # self.msg('zebby_warmup: handlingNewGame ')
      if (self.game.state == 'in_progress'):
         self.setCvars('game')
      else:
         self.handleGameEnd()

   def handleNewGame(self):
      self.handleNewGameThreaded()
      return None


   #FreezeTag gamemode doesn't call this.
   def handleGameCountdown(self):
      # self.msg('GameCountdown...: ')
      self.setCvars('game')

