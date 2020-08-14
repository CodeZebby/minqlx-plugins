import minqlx

game_settings = {
   'pmove_AirControl': { 'pql': '1', 'vql': '0' },
   'pmove_CrouchSlide': { 'pql': '1', 'vql': '0' }
}

class pql_warmup(minqlx.Plugin):
   def __init__(self):
      self.active_ruleset = 'vql'
      # self.add_hook('map', self.handleMapChange)
      # self.add_hook('game_start', self.handleGameStart)
      self.add_command('pql_warmup', self.handlePqlWarmupCommand, 5)

   def handlePqlWarmupCommand(self, player, msg, channel):
      new_ruleset = 'vql'
      if self.active_ruleset == 'vql' and self.game.state != 'in_progress':
         new_ruleset = 'pql'
      self.applyRuleSet(new_ruleset)

   # def handleMapChange(self, mapname, factory):
   #    self.applyRuleSet('pql')

   # def handleGameStart(self, data):
   #    self.applyRuleSet('vql')

   def applyRuleSet(self, ruleset):
      self.active_ruleset = ruleset
      self.msg('pql_warmup.py: applying {} settings'.format(str(ruleset)))
      for cvar in game_settings:
         self.set_cvar(cvar, game_settings[cvar][ruleset])
      minqlx.console_command('map_restart')
