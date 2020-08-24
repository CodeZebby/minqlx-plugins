import minqlx
import time

# Each cvar takes effect when warmup starts.
# cvars in the 'game_start' object take effect
# when the game starts.

zebby_factories = {
   'ca': {
      'g_friendlyFire': '0',
      'g_ammopack': '1',
      'g_regenHealth': '0',
      'roundtimelimit': '90',
      'g_startingWeapons': '8447',
      'dmflags': '28',
      'g_infiniteAmmo': '1',
      'game_start': {
         'g_infiniteAmmo': '0'
      }
      # 'g_runes': '0',
   },
   'duel': {
      'dmflags': '0',
      'fraglimit': '0',
      'g_loadout': '0',
      'g_startingWeapons': '3',
      # 'g_ammoPack': '0',
      'g_ammoRespawn': '40',
      'g_startingHealth': '100',
      'g_startingHealthBonus': '25',
      'g_regenHealth': '0',
      'g_startingArmor': '0',
      'g_voteDelay': '1000',
      # 'g_runes': '0',
   },
   'ctf': {
      'capturelimit': '4'
   },
   'oneflag': {
      'capturelimit': '4'
   },
   'insta': {
      'g_startingWeapons': '65',
      'g_railJump': '500'
   },
   'not_insta': {
      'g_railJump': '0'
   },
   'ffa': {

   },
   'ift': {
      'g_freezeThawTime': '2000',
      'g_freezeRoundDelay': '4000',
      'g_freezeThawThroughSurface': '1',
      'timelimit': '0',
      'dmflags': '28',
      'roundtimelimit': '90'
   },
   'ft': {
      'g_freezeRoundDelay': '10000',
      'g_startingAmmo_mg': '100',
      'g_startingAmmo_sg': '50',
      'g_startingAmmo_gl': '25',
      'g_startingAmmo_rl': '50',
      'g_startingAmmo_lg': '150',
      'g_startingAmmo_rg': '25',
      'g_startingAmmo_pg': '100',
      'g_startingAmmo_hmg': '150',
      # 'g_regenHealth': '0',
      # 'g_freezeThawThroughSurface': '0',
      'timelimit': '0',
      'dmflags': '28',
      'roundtimelimit': '80',
      'g_freezeThawTime': '2000',
      'g_freezeAutoThawTime': '120000',
      'g_freezeEnvironmentalRespawnDelay': '5000',
      'game_start': {
         'g_freezeThawTime': '120000',
         'g_freezeAutoThawTime': '120000',
         'g_freezeEnvironmentalRespawnDelay': '120000',
      }
   },
   'ffa_based': {
      'teamsize': '0',
      'timelimit': '10',
      'fraglimit': '30'
   },
   'team_based': {
      'teamsize': '4'
   },
   'tdm': {
      'fraglimit': '30'
   },
   'vlg': {
      'g_startingWeapons': "32",
      "roundtimelimit": "80",
      "g_vampiricDamage": "1",
      'game_start': {
         'g_infiniteAmmo': '1'
      }
   },
   'shared': {
      'dmflags': '28', #28 for no dmg
      'timelimit': '10',
      'g_startingAmmo_mg': '100',
      'g_startingAmmo_sg': '50',
      'g_startingAmmo_gl': '25',
      'g_startingAmmo_rl': '50',
      'g_startingAmmo_lg': '150',
      'g_startingAmmo_rg': '25',
      'g_startingAmmo_pg': '100',
      'g_startingAmmo_hmg': '150',
      'g_loadout': '0',
      'g_ammoPack': '1',
      'g_ammoRespawn': '5',
      'g_friendlyFire': '0',
      'g_startingHealth': '100',
      'g_startingHealthBonus': '100',
      # 'g_regenHealth': '1',
      'g_regenHealthRate': '1000',
      'g_startingArmor': '100',
      'g_startingWeapons': '8447', # or 255
      'g_voteDelay': '1000',
      'g_quadDamageFactor': '2',
      'g_allowKill': '0',
      'g_battleSuitDampen': '0.40',
      'g_spawnItemPowerup': '0',
      'g_spawnDelay_powerup': '99999999999',
      'g_spawnDelayRandom_powerup': '99999999999',
      "g_vampiricDamage": "0",
      # 'g_runes': '1',
      'g_infiniteAmmo': '1',
      'game_start': {
         'g_infiniteAmmo': '0'
      }
   }
}

ffa_based_factories = ['ffa', 'iffa', 'duel', 'race']
shared_factories = ['ctf', 'tdm', 'ffa', 'ft', 'oneflag', 'har', 'vlg']

class zebby_gamemodes(minqlx.Plugin):
   def __init__(self):
      # TODO keep track of teamsize voted on by players to
      # restore it when switching between ffa/team modes
      self.voted_team_based_teamsize = None
      self.voted_ffa_teamsize = None
      self.add_hook('new_game', self.handleNewGame)
      self.add_hook('game_countdown', self.handleGameCountdown)
      self.previous_factory = None

   def setCvars(self, key, phase = "warmup"):
      for cvar, value in zebby_factories[key].items():
         if cvar == 'teamsize' and key == 'team_based':
            ''' We need to do this to keep sensible team sizes:
                - when switching between ffa and team based modes
                - when a teamsize has already been set (e.g., via a vote)
            '''
            teamsize = self.get_cvar('teamsize')
            if teamsize == '0':
               self.set_cvar(cvar, value)
         elif cvar == 'game_start':
            # game_start cvar must always be applied last
            # to overwrite warmup cvars, so skip for now
            # and do it in the next loop.
            pass
         else:
            self.set_cvar(cvar, value)

      for cvar, value in zebby_factories[key].items():
         if cvar == 'game_start' and phase == 'game':
            for cvar2, value2 in zebby_factories[key]['game_start'].items():
               self.set_cvar(cvar2, value2)

   @minqlx.thread
   def mapRestart(self):
      @minqlx.next_frame # Game logic should never be done in a thread directly
      def game_logic(func): func()

      time.sleep(5)
      for x in range(5, -1, -1):
         if x == 0:
            minqlx.send_server_command(None, "cp \"map restarting...\"")
            continue

         minqlx.send_server_command(None, "cp \"map restarting in {}...\"".format(x))
         time.sleep(1)

      game_logic(lambda: minqlx.console_command('map_restart'))

   def handleNewGame(self):
      game_factory = self.get_cvar('g_factory').lower()
      # self.msg('ZEBBY: game factory is {}'.format(str(game_factory)))

      # Only load cvars if the game type has changed.
      if game_factory != self.previous_factory:
         # Keep track of current game type, so we can check
         # if it has changed later.
         self.previous_factory = game_factory

         # Set cvars
         self.setGameSettings()

         # self.mapRestart()
      else:
         # If the game type did not change,
         # maybe this method was called because
         # the game started.
         self.handleGamePossiblyStarted()

      return None

   def setGameSettings(self, phase = "warmup"):
      game_factory = self.get_cvar('g_factory').lower()
      # self.msg('ZEBBY: game factory is {}'.format(str(game_factory)))

      # Load common cvar settings.
      if game_factory in shared_factories:
         self.setCvars('shared', phase)

      # Load insta related cvars (or unload them)
      if game_factory == 'ictf' or game_factory == 'iffa' or game_factory == 'ift':
         self.setCvars('insta', phase)
      else:
         self.setCvars('not_insta', phase)

      # Load ffa or team based cvars.
      if game_factory in ffa_based_factories:
         self.setCvars('ffa_based', phase)
      else:
         self.setCvars('team_based', phase)

      # Lastly, load any cvars specific to the game type.
      if game_factory in zebby_factories:
         self.setCvars(game_factory, phase)

   @minqlx.thread
   def handleGamePossiblyStarted(self):
      time.sleep(0.4)
      if (self.game.state == 'in_progress'):
         self.setGameSettings("game")
      else: # For example, when someone callvotes map_restart.
         self.setGameSettings()

   #FreezeTag gamemode doesn't call this.
   def handleGameCountdown(self):
      self.setGameSettings('game')