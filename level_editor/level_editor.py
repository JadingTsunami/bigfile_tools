# SoR4 Bigfile Level Editor
# Copyright (C) 2023 JadingTsunami
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; If not, see <http://www.gnu.org/licenses/>.

import zlib
import sys
import struct
import os
import string

import uuid
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

from enum import IntEnum

class WireType(IntEnum):
    STRING = -2
    MESSAGE = -1
    VARINT = 0
    I64 = 1
    LEN = 2
    SGROUP = 3
    EGROUP = 4
    I32 = 5

# FIXME
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
+ '/bigfile_editor/')

from bigfile_editor import BigFileEditor

enemy_list = [
    "characters/sor4_enemies/barbon/chrsor4barbon",
    "characters/sor4_enemies/barbon/chrsor4barbonsurvival",
    "characters/sor4_enemies/barbon/chrsor4barbonsurvival_ally",
    "characters/sor4_enemies/barbon/chrsor4vulture",
    "characters/sor4_enemies/barbon/chrsor4wayne",
    "characters/sor4_enemies/barbon/chrsor4wayne_elite",
    "characters/sor4_enemies/bigben/chrsor4bigben_l0_bigben",
    "characters/sor4_enemies/bigben/chrsor4bigben_l2_anry",
    "characters/sor4_enemies/bigben/chrsor4bigben_l3_bongo",
    "characters/sor4_enemies/bigben/chrsor4bigben_l4_heart",
    "characters/sor4_enemies/bigben/chrsor4bigbenboss",
    "characters/sor4_enemies/bigben/chrsor4bigbenboss_ally",
    "characters/sor4_enemies/bigben/chrsor4bigbenboss_elite",
    "characters/sor4_enemies/commisser/chrsor4commisser",
    "characters/sor4_enemies/commisser/chrsor4commisser_7",
    "characters/sor4_enemies/commisser/chrsor4commisser_survival",
    "characters/sor4_enemies/commisser/chrsor4commisser_survival_ally",
    "characters/sor4_enemies/commisser/chrsor4deputy",
    "characters/sor4_enemies/commisser/chrsor4deputy_elite",
    "characters/sor4_enemies/commisser/chrsor4lieutenant",
    "characters/sor4_enemies/cop/ai_cop",
    "characters/sor4_enemies/cop/ai_cop2",
    "characters/sor4_enemies/cop/ai_cop_chief",
    "characters/sor4_enemies/cop/ai_cop_rookie",
    "characters/sor4_enemies/cop/ai_elite",
    "characters/sor4_enemies/cop/chrsor4cop_l0_cop",
    "characters/sor4_enemies/cop/chrsor4cop_l3_chief",
    "characters/sor4_enemies/cop/chrsor4cop_l6_grab",
    "characters/sor4_enemies/cop/chrsor4cop_l6_grab_ally",
    "characters/sor4_enemies/cop/chrsor4cop_l7_bad",
    "characters/sor4_enemies/cop/chrsor4cop_l8_badgrab",
    "characters/sor4_enemies/cop/chrsor4cop_l8_rookie",
    "characters/sor4_enemies/cop/chrsor4cop_l8_rookie_elite",
    "characters/sor4_enemies/diamond/aisor4_l4_pyrop",
    "characters/sor4_enemies/diamond/chrsor4_l0_diamond",
    "characters/sor4_enemies/diamond/chrsor4_l1_ruby",
    "characters/sor4_enemies/diamond/chrsor4_l2_garnet",
    "characters/sor4_enemies/diamond/chrsor4_l2_garnet_ally",
    "characters/sor4_enemies/diamond/chrsor4_l2_garnet_elite",
    "characters/sor4_enemies/diamond/chrsor4_l4_pyrop",
    "characters/sor4_enemies/diamond/chrsor4_l5_saphyr",
    "characters/sor4_enemies/diva/aisor4kalaas",
    "characters/sor4_enemies/diva/aisor4kalaas_survival",
    "characters/sor4_enemies/diva/aisor4mariah",
    "characters/sor4_enemies/diva/aisor4mariah_survival",
    "characters/sor4_enemies/diva/chrsor4_l4_tania",
    "characters/sor4_enemies/diva/chrsor4_l4_tania_elite",
    "characters/sor4_enemies/diva/chrsor4diva",
    "characters/sor4_enemies/diva/chrsor4diva_reinforcement",
    "characters/sor4_enemies/diva/chrsor4diva_survival",
    "characters/sor4_enemies/diva/chrsor4kalaas",
    "characters/sor4_enemies/diva/chrsor4kalaas_survival",
    "characters/sor4_enemies/diva/chrsor4mariah",
    "characters/sor4_enemies/diva/chrsor4mariah_survival",
    "characters/sor4_enemies/donovan/aisor4donovan",
    "characters/sor4_enemies/donovan/aisor4gudden",
    "characters/sor4_enemies/donovan/aisor4z",
    "characters/sor4_enemies/donovan/chrsor4_l0_donovan",
    "characters/sor4_enemies/donovan/chrsor4_l0_donovan_ally",
    "characters/sor4_enemies/donovan/chrsor4_l1_altet",
    "characters/sor4_enemies/donovan/chrsor4_l2_gudden",
    "characters/sor4_enemies/donovan/chrsor4_l3_z",
    "characters/sor4_enemies/donovan/chrsor4_l3_z_elite",
    "characters/sor4_enemies/doppelgangers/chrsor4adam_boss",
    "characters/sor4_enemies/doppelgangers/chrsor4axel_boss",
    "characters/sor4_enemies/doppelgangers/chrsor4blaze_boss",
    "characters/sor4_enemies/doppelgangers/chrsor4cherry_boss",
    "characters/sor4_enemies/doppelgangers/chrsor4floyd_boss",
    "characters/sor4_enemies/dylan/aisor4francis",
    "characters/sor4_enemies/dylan/aisor4kevin",
    "characters/sor4_enemies/dylan/chrsor4_l0_dylan",
    "characters/sor4_enemies/dylan/chrsor4_l3_kevin",
    "characters/sor4_enemies/dylan/chrsor4_l4_francis",
    "characters/sor4_enemies/dylan/chrsor4_l5_brandon",
    "characters/sor4_enemies/dylan/chrsor4_l5_brandon_elite",
    "characters/sor4_enemies/elite/chrsor4_l0_elite",
    "characters/sor4_enemies/elite/chrsor4_l3_elitegold",
    "characters/sor4_enemies/elite/chrsor4_l3_elitegoldhalberd",
    "characters/sor4_enemies/elite/chrsor4_l3_elitegoldhalberd_elite",
    "characters/sor4_enemies/elite/chrsor4_l4_elitedark",
    "characters/sor4_enemies/elite/chrsor4_l4_elitedark2",
    "characters/sor4_enemies/elite/chrsor4_l5_eliteshadow",
    "characters/sor4_enemies/elite/chrsor4_l6_elitelight",
    "characters/sor4_enemies/estel/chrsor4estel",
    "characters/sor4_enemies/estel/chrsor4estel_lvl7",
    "characters/sor4_enemies/estel/chrsor4estel_survival",
    "characters/sor4_enemies/galsia/aisor4_l0_galsia",
    "characters/sor4_enemies/galsia/aisor4_l0_galsiasuperfrombrash",
    "characters/sor4_enemies/galsia/aisor4_l4_brash",
    "characters/sor4_enemies/galsia/chrsor4_l0_galsia",
    "characters/sor4_enemies/galsia/chrsor4_l0_galsia_ally",
    "characters/sor4_enemies/galsia/chrsor4_l0_galsia_bt_boss",
    "characters/sor4_enemies/galsia/chrsor4_l0_galsia_lowstruggle",
    "characters/sor4_enemies/galsia/chrsor4_l0_galsiamaso",
    "characters/sor4_enemies/galsia/chrsor4_l0_galsiasuper",
    "characters/sor4_enemies/galsia/chrsor4_l0_joseph",
    "characters/sor4_enemies/galsia/chrsor4_l3_bt",
    "characters/sor4_enemies/galsia/chrsor4_l4_brash",
    "characters/sor4_enemies/galsia/chrsor4_l6_garam",
    "characters/sor4_enemies/galsia/chrsor4_l7_jonathan",
    "characters/sor4_enemies/galsia/chrsor4_l7_jonathan_elite",
    "characters/sor4_enemies/galsia/chrsor4_l8_surger",
    "characters/sor4_enemies/gold/chrsor4_l0_gold",
    "characters/sor4_enemies/gold/chrsor4_l0_gold_ally",
    "characters/sor4_enemies/gold/chrsor4_l1_silver",
    "characters/sor4_enemies/gold/chrsor4_l2_tin",
    "characters/sor4_enemies/gold/chrsor4_l2_tin_elite",
    "characters/sor4_enemies/gold/chrsor4_l3_bronze",
    "characters/sor4_enemies/karate/ai_chrsor4karate_l3_goro",
    "characters/sor4_enemies/karate/chrsor4karate_l0_masa",
    "characters/sor4_enemies/karate/chrsor4karate_l3_goro",
    "characters/sor4_enemies/karate/chrsor4karate_l3_goro_ally",
    "characters/sor4_enemies/karate/chrsor4karate_l3_goro_elite",
    "characters/sor4_enemies/karate/chrsor4karate_l6_tetsu",
    "characters/sor4_enemies/karate/chrsor4karate_l7_tiger",
    "characters/sor4_enemies/koobo/chrsor4baabo",
    "characters/sor4_enemies/koobo/chrsor4baabolesslife",
    "characters/sor4_enemies/koobo/chrsor4baabolesslife_elite",
    "characters/sor4_enemies/koobo/chrsor4fuubo",
    "characters/sor4_enemies/koobo/chrsor4koobig",
    "characters/sor4_enemies/koobo/chrsor4koobo",
    "characters/sor4_enemies/koobo/chrsor4koobolesslife",
    "characters/sor4_enemies/koobo/chrsor4koobolesslife_ally",
    "characters/sor4_enemies/koobo/chrsor4zeebo",
    "characters/sor4_enemies/kwashi/chrsor4kwashi",
    "characters/sor4_enemies/kwashi/chrsor4kwashi_survival",
    "characters/sor4_enemies/kwashi/chrsor4kwashiv2",
    "characters/sor4_enemies/kwashi/chrsor4kwashiv3",
    "characters/sor4_enemies/max/ai_max_boss",
    "characters/sor4_enemies/max/ai_max_boss_survival",
    "characters/sor4_enemies/max/chrsor4max",
    "characters/sor4_enemies/max/chrsor4maxsurvival",
    "characters/sor4_enemies/mry/chrsor4mry",
    "characters/sor4_enemies/mry/chrsor4mry_12",
    "characters/sor4_enemies/mry/chrsor4mry_12_survival",
    "characters/sor4_enemies/mry/chrsor4mrysurvival",
    "characters/sor4_enemies/mry/chrsor4mrysurvival2",
    "characters/sor4_enemies/mry/chrsor4mrysurvival_ally",
    "characters/sor4_enemies/msy/aisor4msy",
    "characters/sor4_enemies/msy/aisor4msy_12_survival",
    "characters/sor4_enemies/msy/aisor4msysuvival",
    "characters/sor4_enemies/msy/aisor4msysuvival2",
    "characters/sor4_enemies/msy/chrsor4msy",
    "characters/sor4_enemies/msy/chrsor4msy_12",
    "characters/sor4_enemies/msy/chrsor4msy_12survival",
    "characters/sor4_enemies/msy/chrsor4msy_12survival_2",
    "characters/sor4_enemies/msy/chrsor4msy_12survival_2_elite",
    "characters/sor4_enemies/msy/chrsor4msysurvival",
    "characters/sor4_enemies/msy/chrsor4msysurvival_ally",
    "characters/sor4_enemies/nora/chrsor4electra",
    "characters/sor4_enemies/nora/chrsor4noraboss",
    "characters/sor4_enemies/nora/chrsor4norabosssurvival",
    "characters/sor4_enemies/nora/chrsor4queen",
    "characters/sor4_enemies/nora/chrsor4queen_elite",
    "characters/sor4_enemies/nora/chrsor4stiletto",
    "characters/sor4_enemies/nora/chrsor4stiletto_ally",
    "characters/sor4_enemies/raven/chrsor4raven_l0_raven",
    "characters/sor4_enemies/raven/chrsor4raven_l1_condor",
    "characters/sor4_enemies/raven/chrsor4raven_l1_condor_ally",
    "characters/sor4_enemies/raven/chrsor4raven_l2_sparrow",
    "characters/sor4_enemies/raven/chrsor4raven_l2_sparrow_elite",
    "characters/sor4_enemies/raven/chrsor4raven_l4_pheasant",
    "characters/sor4_enemies/shiva/chrsor4shiva",
    "characters/sor4_enemies/shiva/chrsor4shivadouble",
    "characters/sor4_enemies/shiva/chrsor4shivasurvival",
    "characters/sor4_enemies/signal/aisor4signal",
    "characters/sor4_enemies/signal/aisor4signal_d",
    "characters/sor4_enemies/signal/chrsor4_l0_signal_y",
    "characters/sor4_enemies/signal/chrsor4_l1_signal_g",
    "characters/sor4_enemies/signal/chrsor4_l3_signal_r",
    "characters/sor4_enemies/signal/chrsor4_l4_signal_d",
    "characters/sor4_enemies/signal/chrsor4_l4_signal_d_elite",
    "characters/sor4_enemies/sugar/aisor4sugar_l0_sugar",
    "characters/sor4_enemies/sugar/aisor4sugar_l3_georgia",
    "characters/sor4_enemies/sugar/chrsor4sugar_l0_sugar",
    "characters/sor4_enemies/sugar/chrsor4sugar_l1_honey",
    "characters/sor4_enemies/sugar/chrsor4sugar_l2_janet",
    "characters/sor4_enemies/sugar/chrsor4sugar_l2_janet_elite",
    "characters/sor4_enemies/sugar/chrsor4sugar_l3_georgia",
    "characters/sor4_enemies/sugar/chrsor4sugar_l3_georgia_ally",
    "characters/sor4_enemies/victoria/ai_thrower",
    "characters/sor4_enemies/victoria/ai_thrower_turret",
    "characters/sor4_enemies/victoria/chrsor4victoria_l1_victoria",
    "characters/sor4_enemies/victoria/chrsor4victoria_l1_victoria_elite",
    "characters/sor4_enemies/victoria/chrsor4victoria_l2_toxyne",
    "characters/sor4_enemies/victoria/chrsor4victoria_l3_steffie",
    "characters/sor4_enemies/victoria/chrsor4victoria_l3_steffie_ally",
    "characters/sor4_enemies/victoria/chrsor4victoria_l3_steffie_turret",
    "characters/sor4_enemies/victoria/chrsor4victoria_l3_steffiestun",
    "characters/sor4_enemies/victoria/chrsor4victoria_l4_anne",
    "characters/sor3_enemies/chrsor3bruce",
    "characters/sor3_enemies/chrsor3bruce_spawn",
    "characters/sor3_enemies/chrsor3galsia",
    "characters/sor3_enemies/chrsor3goldie",
    "characters/sor3_enemies/chrsor3lisamona",
    "characters/sor3_enemies/chrsor3lisamonalesslife",
    "characters/sor3_enemies/chrsor3monalisa",
    "characters/sor3_enemies/chrsor3monalisa_elite",
    "characters/sor3_enemies/chrsor3robotx",
    "characters/sor3_enemies/chrsor3tiger",
    "characters/sor3_enemies/chrsor3yamato",
    "characters/sor3_enemies/chrsor3yamato_cursed",
    "characters/sor3_enemies/chrsor3yamato_elite",
    "characters/sor3_enemies/chrsor3yamatoclone",
    "characters/sor3_enemies/chrsor3zack",
    "characters/sor2_enemies/ai_sor2_jack",
    "characters/sor2_enemies/aisor2signal",
    "characters/sor2_enemies/chrsor2abadede_challenge",
    "characters/sor2_enemies/chrsor2abadede_challenge_survival",
    "characters/sor2_enemies/chrsor2abadede_challenge_survival_elite",
    "characters/sor2_enemies/chrsor2barbon_challenge",
    "characters/sor2_enemies/chrsor2barbon_challenge_elite",
    "characters/sor2_enemies/chrsor2bigben",
    "characters/sor2_enemies/chrsor2donovan",
    "characters/sor2_enemies/chrsor2electra_challenge",
    "characters/sor2_enemies/chrsor2fog",
    "characters/sor2_enemies/chrsor2galsia",
    "characters/sor2_enemies/chrsor2hakuyo",
    "characters/sor2_enemies/chrsor2jack",
    "characters/sor2_enemies/chrsor2kusanagi",
    "characters/sor2_enemies/chrsor2mrx_challenge",
    "characters/sor2_enemies/chrsor2mrx_challenge_survival",
    "characters/sor2_enemies/chrsor2mrx_challenge_survival_elite",
    "characters/sor2_enemies/chrsor2raven",
    "characters/sor2_enemies/chrsor2rbear_challenge",
    "characters/sor2_enemies/chrsor2rbear_challenge_elite",
    "characters/sor2_enemies/chrsor2shiva_challenge",
    "characters/sor2_enemies/chrsor2shiva_challenge_survival",
    "characters/sor2_enemies/chrsor2shiva_challenge_survival_elite",
    "characters/sor2_enemies/chrsor2signal",
    "characters/sor2_enemies/chrsor2zamza",
    "characters/sor2_enemies/chrsor2zamza_challenge",
    "characters/sor2_enemies/chrsor2zamza_challenge_survival",
    "characters/sor2_enemies/chrsor2zamza_challenge_survival_elite",
    "characters/sor1_enemies/aisor1souther",
    "characters/sor1_enemies/chrsor1abadede",
    "characters/sor1_enemies/chrsor1abadede_elite",
    "characters/sor1_enemies/chrsor1antonio",
    "characters/sor1_enemies/chrsor1antonio_elite",
    "characters/sor1_enemies/chrsor1bongo",
    "characters/sor1_enemies/chrsor1bongo_elite",
    "characters/sor1_enemies/chrsor1mrx",
    "characters/sor1_enemies/chrsor1mrx_elite",
    "characters/sor1_enemies/chrsor1souther",
    "characters/sor1_enemies/chrsor1souther_elite"
]

destroyable_list = [
    "objects/object_arcade",
    "objects/object_arcade_bar",
    "objects/object_arcade_cursed2",
    "objects/object_arcade_cursed3",
    "objects/object_arcade_gallery",
    "objects/object_arcade_prison",
    "objects/object_armor",
    "objects/object_armor_flail",
    "objects/object_armor_sword",
    "objects/object_bar_chair",
    "objects/object_bar_chair_right",
    "objects/object_bar_table",
    "objects/object_barrel_blue",
    "objects/object_barrel_electricity",
    "objects/object_barrel_explosion",
    "objects/object_barrel_red",
    "objects/object_barrel_toxic",
    "objects/object_big_crate",
    "objects/object_big_crate_bateau",
    "objects/object_bonus_tv",
    "objects/object_bucket",
    "objects/object_bureau",
    "objects/object_chair",
    "objects/object_chandelier",
    "objects/object_chandelier_ground",
    "objects/object_chicken_gold",
    "objects/object_command_chair",
    "objects/object_crashing_car",
    "objects/object_distributeur",
    "objects/object_door_diva",
    "objects/object_door_metro",
    "objects/object_door_police_station",
    "objects/object_door_prison_breakable",
    "objects/object_elevator_side",
    "objects/object_elevator_side2",
    "objects/object_garbage_can",
    "objects/object_garbage_standart",
    "objects/object_invisible",
    "objects/object_moto_1",
    "objects/object_moto_2",
    "objects/object_moto_3",
    "objects/object_moto_4",
    "objects/object_moto_5",
    "objects/object_moto_6",
    "objects/object_moto_7",
    "objects/object_moto_8",
    "objects/object_moto_9",
    "objects/object_moto_barbon",
    "objects/object_museum_chair",
    "objects/object_museum_chair_right",
    "objects/object_phone_booth",
    "objects/object_pool_table",
    "objects/object_poutre_temple",
    "objects/object_roadsing",
    "objects/object_siege_avion1",
    "objects/object_siege_avion2",
    "objects/object_siege_avion3",
    "objects/object_siege_avion4",
    "objects/object_sink",
    "objects/object_sor2_alien_egg",
    "objects/object_sor2_bags",
    "objects/object_sor2_barrel",
    "objects/object_sor2_barrier",
    "objects/object_sor2_chair",
    "objects/object_sor2_crate",
    "objects/object_sor2_menus",
    "objects/object_sor2_metal_crate_01",
    "objects/object_sor2_metal_crate_02",
    "objects/object_sor2_metal_urn",
    "objects/object_sor2_steel_trash",
    "objects/object_sor2_table",
    "objects/object_sor2_vase",
    "objects/object_table",
    "objects/object_tactical_box",
    "objects/object_torture",
    "objects/object_tuctuc",
    "objects/object_vase",
    "objects/object_water_distrib",
    "objects/object_wet_floor"
]

pickup_list = [
    "objects/pickup_apple",
    "objects/pickup_axe",
    "objects/pickup_ball",
    "objects/pickup_bat",
    "objects/pickup_big_chinese_sword",
    "objects/pickup_bigknife",
    "objects/pickup_black_sword",
    "objects/pickup_blue_vial",
    "objects/pickup_boomrang",
    "objects/pickup_boomrang_gold",
    "objects/pickup_bottle",
    "objects/pickup_bottle_broken",
    "objects/pickup_bowling_ball",
    "objects/pickup_brick",
    "objects/pickup_broom",
    "objects/pickup_butcherknife",
    "objects/pickup_chicken",
    "objects/pickup_chinese_sword",
    "objects/pickup_durian",
    "objects/pickup_eel",
    "objects/pickup_espadon",
    "objects/pickup_fire_sword",
    "objects/pickup_fleau",
    "objects/pickup_fugu",
    "objects/pickup_gladiator_stick",
    "objects/pickup_gold_pipe",
    "objects/pickup_golden_chicken",
    "objects/pickup_golf",
    "objects/pickup_green_vial",
    "objects/pickup_grenade",
    "objects/pickup_grenade_estel",
    "objects/pickup_grenade_stun",
    "objects/pickup_grenade_stun_long",
    "objects/pickup_halberd",
    "objects/pickup_halberd_gold",
    "objects/pickup_hammer",
    "objects/pickup_katana",
    "objects/pickup_knife",
    "objects/pickup_knife_gold",
    "objects/pickup_laser_sabre",
    "objects/pickup_lead_pipe",
    "objects/pickup_lead_pipe_invincible",
    "objects/pickup_mass",
    "objects/pickup_mine",
    "objects/pickup_money_big",
    "objects/pickup_money_small",
    "objects/pickup_nailed_bat",
    "objects/pickup_pepper",
    "objects/pickup_poison_sword",
    "objects/pickup_pool_queue",
    "objects/pickup_pool_queue_broken",
    "objects/pickup_red_vial",
    "objects/pickup_roadsign",
    "objects/pickup_sai",
    "objects/pickup_shuriken",
    "objects/pickup_sor1boomrang",
    "objects/pickup_sor2_katana",
    "objects/pickup_sor2_lead_pipe",
    "objects/pickup_sor2_shuriken",
    "objects/pickup_sor2knife",
    "objects/pickup_sor3_shuriken",
    "objects/pickup_star",
    "objects/pickup_sword",
    "objects/pickup_talkie_walkie",
    "objects/pickup_taser",
    "objects/pickup_thunder_sword",
    "objects/pickup_tonfa",
    "objects/pickup_torque",
    "objects/pickup_trainingspawner1",
    "objects/pickup_trainingspawner2",
    "objects/pickup_trainingspawner3",
    "objects/pickup_trainingspawner4",
    "objects/pickup_trainingspawner5",
    "objects/pickup_trainingspawner6",
    "objects/pickup_trainingstart1",
    "objects/pickup_trainingstart2",
    "objects/pickup_trainingstart3",
    "objects/pickup_trainingstart4",
    "objects/pickup_trident",
    "objects/pickup_tuna",
    "objects/pickup_umbrella",
    "objects/pickup_zan_ball"
]

class DataSpooler:
    def __init__(self, data, end=None):
        self.load(data, end)

    def load(self, data, end):
        self.data = data
        self.ptr = 0
        if end:
            self.len = end
        else:
            self.len = len(data)

    def read(self, howmany, advance=True):
        if howmany <= 0:
            raise ValueError("Read less than or equal to 0")
        if self.ptr + howmany > self.len:
            raise EOFError("Tried to read past end of file")
        if advance:
            self.ptr += howmany
        return self.data[self.ptr-howmany:self.ptr]

    def splice(self, where, howmany, what):
        if where < 0:
            raise ValueError("Splice location less than 0")
        elif howmany <= 0:
            raise ValueError("Splice width less than or equal to 0")

        self.data = self.data[:where] + what + self.data[where+howmany:]

    def peek(self, howmany):
        return self.read(howmany, advance=False)

    def tell(self):
        return self.ptr

    def has_more(self):
        return self.ptr < self.len

    def _clip_bounds(self):
        self.ptr = max(0, min(self.ptr, self.len))

    def seek(self, where, whence):
        if whence == 0:
            self.ptr = where
        elif whence == 1:
            self.ptr = self.ptr + where
        elif whence == 2:
            self.ptr = self.len + where
        self._clip_bounds()

def read_varint(data, dataspool):
    return read_varint_raw(data, dataspool.tell(), dataspool)

def read_varint_raw(data, index, dataspool=None):
    assert index < len(data) and index >= 0
    varint = data[index] & 0x7F
    more = data[index] & 0x80
    index += 1
    while more:
        assert index < len(data)
        varint = ((data[index] & 0x7F) << 7) | (varint)
        more = data[index] & 0x80
        index += 1
    if dataspool:
        dataspool.seek(index,0)
    return varint

def read_tag(data, index, dataspool=None):
    assert index < len(data) and index >= 0
    v = read_varint_raw(data, index, dataspool)
    field = v >> 3
    msgtype = v & 0x7
    return (field, msgtype)

def encode_varint(v):
    if not v:
        return bytearray([0])

    b = bytearray()
    while v:
        cur_byte = (v & 0x7F)
        v >>= 7
        if v:
            cur_byte |= 0x80
        b.append(cur_byte)
    return b

def encode_tag(field_num, wire_type):
    assert wire_type >= WireType.VARINT and wire_type <= WireType.I32
    assert field_num > 0
    tag = (wire_type & 0x7) | (field_num << 3)
    return encode_varint(tag)

def likely_string(value, threshold=0.6):
    if not value:
        return False
    if not value.isascii():
        return False

    value = str(value, 'utf-8')
    length = len(value)
    alpha = 0
    num = 0
    for c in value:
        if c.isalpha():
            alpha += 1
        elif c.isnumeric():
            num += 1
        elif c not in string.punctuation:
            return False

    if float(alpha + num)/float(length) >= threshold and alpha > 0:
        return True

    return False

def guess_if_message(data, dataspool, length):
    rewind = dataspool.tell()
    try:
        (f, m) = read_tag(data, dataspool.tell(), dataspool)
    except:
        return False
    # arbitrary limit on field numbers based on experience, but should revise this
    # based on what's actually present in the decoded file (todo)
    if f > 1024:
        return False

    if m == WireType.LEN:
        size = read_varint(data, dataspool)
        bytes_read = dataspool.tell() - rewind
        if size <= length - bytes_read:
            # will guess this is a message
            dataspool.seek(rewind, 0)
            return True
    dataspool.seek(rewind, 0)
    if m >= WireType.VARINT and m <= WireType.I32 and m != WireType.LEN:
        return True
    return False

def read_field(data, dataspool):
    (field, msgtype) = read_tag(data, dataspool.tell(), dataspool)
    if msgtype == WireType.VARINT:
        return field, msgtype, read_varint(data, dataspool)
    elif msgtype == WireType.I64:
        df = dataspool.read(8)
        if df:
            df = struct.unpack('<d', df)[0]
        return field, msgtype, df
    elif msgtype == WireType.I32:
        df = dataspool.read(4)
        if df:
            df = struct.unpack('<f', df)[0]
        return field, msgtype, df
    elif msgtype == WireType.SGROUP or msgtype == WireType.EGROUP:
        # fail on this for now
        raise ValueError("Did not expect SGROUP/EGROUP encoding but found at " + str(dataspool.tell()))
    elif msgtype == WireType.LEN:
        length = read_varint(data, dataspool)
        guess_message = guess_if_message(data, dataspool, length)
        content = dataspool.read(length)
        if likely_string(content):
            content = content.decode('utf-8')
            msgtype = WireType.STRING
        elif guess_message:
            msgtype = WireType.MESSAGE
        return field, msgtype, content
    else:
        raise ValueError("Unknown message type encoding " + str(msgtype) + " found at " + str(dataspool.tell()))

class Node:
    def __init__(self, parent, tag_start, data_start, data_len, field_num, content=None):
        self.parent = parent
        self.tag_start = tag_start
        self.data_start = data_start
        self.data_len = data_len
        self.field_num = field_num
        self.content = content

def find_string_hierarchy(data, spool, parent=None, string_list=None, known_parents=None):
    # for each string, find:
    #  parent
    #  tag start
    #  string start
    #  string length (end)
    if string_list is None:
        string_list = []

    if known_parents is None:
        known_parents = {}

    while spool.has_more():
        # is the next field a string?
        try:
            tag_start = spool.tell()
            (field, msgtype) = read_tag(data, spool.tell(), spool)
            if msgtype == WireType.LEN:
                data_len = read_varint(data, spool)
            else:
                data_len = 0
            data_start = spool.tell()
            spool.seek(tag_start, 0)
            (f, m, c) = read_field(data, spool)
            data_end = spool.tell()
        except Exception as e:
            break
        if m == WireType.STRING:
            new_node = Node(parent, tag_start, data_start, data_len, f, c)
            string_list.append(new_node)
        elif m == WireType.MESSAGE and c:
            spool_new = DataSpooler(data, end=data_end)
            spool_new.seek(data_start, 0)
            if tag_start in known_parents:
                new_node = known_parents[tag_start]
            else:
                new_node = Node(parent, tag_start, data_start, data_len, f, None)
                known_parents[tag_start] = new_node
            find_string_hierarchy(data, spool_new, new_node, string_list, known_parents)

    return string_list

def replace_node(table, node, replacement_string):
    # node MUST be a leaf
    assert table
    assert node
    assert node.content

    spool = DataSpooler(table['data'])
    repl_bytes = bytearray(replacement_string,"utf-8")
    size_diff = len(repl_bytes) - len(node.content)
    new_tag = encode_tag(node.field_num, WireType.LEN)
    new_tag += encode_varint(len(repl_bytes))
    spool.splice(node.tag_start, (node.data_start-node.tag_start) + node.data_len, new_tag + repl_bytes)
    size_diff += len(new_tag) - (node.data_start-node.tag_start)
    # now write size delta all the way up
    p = node.parent
    while p:
        p_tag = encode_tag(p.field_num, WireType.LEN)
        p_tag += encode_varint(p.data_len + size_diff)
        spool.splice(p.tag_start, p.data_start-p.tag_start, p_tag)
        size_diff += len(p_tag) - (p.data_start-p.tag_start)
        p = p.parent

    table['data'] = spool.data
    table['size'] = len(spool.data)
    spool.seek(0,0)

    # certainly we could be more efficient than rebuilding
    # the entire node network. BUT, if a node has duplicates
    # in the tree, we really don't have a good way of finding
    # them unless we searched the structure for the same tag
    # start point and replaced on that basis.
    return find_string_hierarchy(table['data'], spool)


class SelectReplacementDialog:
    def __init__(self, root, prompt, choices):
        self.top = tk.Toplevel(root)
        self.label = tk.Label(self.top, text=prompt)
        self.ok_button = tk.Button(self.top, text="OK", command=self.on_ok)

        self.listframe = ttk.Frame(self.top)

        self.list = tk.Listbox(self.listframe)
        self.list.bind('<<ListboxSelect>>', self.select_replacement)

        self.bary = ttk.Scrollbar(self.listframe)
        self.barx = ttk.Scrollbar(self.listframe, orient=tk.HORIZONTAL)

        self.list.config(yscrollcommand = self.bary.set)
        self.list.config(xscrollcommand = self.barx.set)

        self.bary.config(command=self.list.yview)
        self.barx.config(command=self.list.xview)

        self.bary.pack(side=tk.RIGHT, fill=tk.Y)
        self.barx.pack(side=tk.BOTTOM, fill=tk.X)
        self.list.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(1, weight=1)
        
        self.label.grid(row=0, column=0, sticky=tk.N)
        self.listframe.grid(row=1, column=0, sticky=tk.NSEW)
        self.ok_button.grid(row=2, column=0, stick=tk.S)

        for choice in choices:
            self.list.insert(tk.END, choice)

        self.list.bind("<Return>", self.on_ok)
        self.list.bind('<Double-1>', self.on_ok)
        self.list.bind("<Escape>", self.abandon)

        self.top.geometry('700x350')
        self.replacement = None

    def abandon(self, event=None):
        self.replacement = None
        self.top.destroy()
        
    def on_ok(self, event=None):
        self.top.destroy()

    def select_replacement(self, e):
        sel = e.widget.curselection()
        if sel:
            self.replacement = self.list.get(sel[0])

    def show(self):
        self.top.wm_deiconify()
        self.list.focus_force()
        self.top.wait_window()
        return self.replacement

class LevelEditorGUI:
    def __init__(self, bfe):
        self.root = tk.Tk()
        self.bfe = bfe
        self.root.title("bigfile level editor")

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.levelframe = ttk.Frame(self.root)

        self.levellist = tk.Listbox(self.levelframe)
        self.levelbary = ttk.Scrollbar(self.levelframe)
        self.levelbarx = ttk.Scrollbar(self.levelframe, orient=tk.HORIZONTAL)

        self.levellist.config(yscrollcommand = self.levelbary.set)
        self.levellist.config(xscrollcommand = self.levelbarx.set)

        self.levelbary.config(command=self.levellist.yview)
        self.levelbarx.config(command=self.levellist.xview)

        self.levellist.bind('<<ListboxSelect>>', self.select_level)

        self.levelbary.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.levelbarx.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.levellist.pack(side=tk.LEFT, fill=tk.BOTH)
        self.levelframe.grid(row=0, column=0, sticky=tk.NS)

        self.QuitButton = ttk.Button(self.root, text="Quit", command=self.root.destroy)

        self.FileButtonFrame = ttk.Frame(self.root)
        self.ImportCompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Import COMPRESSED Bigfile", command=self.import_compressed_bigfile)
        self.ImportUncompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Import UNCOMPRESSED Bigfile", command=self.import_uncompressed_bigfile)
        self.ExportCompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Export COMPRESSED Bigfile", command=self.export_compressed_bigfile)
        self.ExportUncompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Export UNCOMPRESSED Bigfile", command=self.export_uncompressed_bigfile)

        self.ImportCompressedBigfileButton.grid(row=0, column=0)
        self.ImportUncompressedBigfileButton.grid(row=0, column=1) 
        self.ExportUncompressedBigfileButton.grid(row=0, column=2)
        self.ExportCompressedBigfileButton.grid(row=0, column=3) 
        
        self.FileButtonFrame.grid(row=1, column=0, columnspan=2)
        self.QuitButton.grid(row=2, column=1, sticky=tk.E)

        self.TreeFrame = ttk.Frame(self.root, padding="3")
        self.TreeFrame.grid(row=0, column=1, sticky=tk.NSEW)

        self.tree = ttk.Treeview(self.TreeFrame)
        self.tree.bind('<Double-1>', self.edit_item)
        self.tree.bind('<Return>', self.edit_item)

        self.tvsb = ttk.Scrollbar(self.TreeFrame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tvsb.set)
        self.thsb = ttk.Scrollbar(self.TreeFrame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.thsb.set)

        self.tvsb.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.thsb.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.tree.pack(fill=tk.BOTH, expand=1)

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())

        self.uuid_lookup = {}
        self.level_lookup = []
        self.selected_level = None
        self.replacements = {}
        self.children = {}

        self.root.geometry('1200x600')
        self.root.mainloop()

    def import_compressed_bigfile(self):
        self._import_bigfile(True)

    def import_uncompressed_bigfile(self):
        self._import_bigfile(False)

    def _import_bigfile(self, compressed):
        inf = fd.askopenfilename(parent=self.root, title="Import Compressed Bigfile")
        if inf:
            try:
                if compressed:
                    self.bfe.read_compressed_bigfile(inf)
                else:
                    self.bfe.read_uncompressed_bigfile(inf)
                self.build_gui(self.bfe.tables)
            except Exception as e:
                mb.showerror("Error importing file", "Error importing big file.\nDid you choose the right file?\nException details:\n" + str(e))
                self.clear_gui()

    def export_compressed_bigfile(self):
        self._export_bigfile(True)

    def export_uncompressed_bigfile(self):
        self._export_bigfile(False)

    def _export_bigfile(self, compressed):
        ouf = fd.asksaveasfilename(parent=self.root, title="Export Uncompressed Bigfile")
        if ouf:
            try:
                self.apply_replacements()
                if compressed:
                    self.bfe.write_compressed_bigfile(ouf)
                else:
                    self.bfe.write_uncompressed_bigfile(ouf)
            except Exception as e:
                mb.showerror("Error exporting file", "Error exporting bigfile.\nDo you have write permissions and enough drive space?\nException details:\n" + str(e))

    def apply_replacements(self):
        # 1. walk each replacement and apply it
        # WARNING: This relies on the fact that we never replace or
        # delete nodes, we only modify them.
        # Therefore they end up in the same relative location every
        # time we make changes, no matter what those changes are.
        # *IF* nodes can be added or removed, then a new method to link
        # old and new nodes would be required.
        new_children = {}
        for r in self.replacements:
            (t, n, r) = self.replacements[r]
            s2 = t['s2']
            index = self.children[s2].index(n)
            if not index:
                mb.showerror("Uh oh", "Internal error: Index of child node not found!")
            elif s2 in new_children:
                new_children[s2] = replace_node(t, new_children[s2][index], r)
            else:
                new_children[s2] = replace_node(t, n, r)

        # 2. clear replacements (they're applied)
        self.replacements = {}

        # 3. rebuild GUI
        self.build_gui(self.bfe.tables)

    def build_gui(self, tables):
        self.clear_gui()
        for table in tables:
            max_name = 0
            if table['s1'].decode('utf-16') == "LevelData":
                s2 = table['s2'].decode('utf-16')
                self.levellist.insert(tk.END, s2)
                self.level_lookup.append(table)
                max_name = max(max_name, len(s2))
        self.levellist.configure(width=max_name)

    def clear_gui(self):
        self.clear_tree()
        self.selected_level = None
        self.children = {}
        self.level_lookup = []
        self.levellist.delete(0, tk.END)

    def edit_item(self, e):
        uid = str(self.tree.focus())
        if uid not in self.uuid_lookup:
            mb.showwarning("Can't edit top-level", "Can't replace top-level items; choose an enemy, destroyable or pickup instead.")
        else:
            n = self.uuid_lookup[uid]
            choices = []
            if n.content in enemy_list:
                choices = enemy_list
            elif n.content in destroyable_list:
                choices = destroyable_list
            elif n.content in pickup_list:
                choices = pickup_list
            chosen = SelectReplacementDialog(self.root, "Replace " + str(n.content) + " with:", choices).show()
            if chosen:
                self.replacements[uid] = (self.selected_level, n, chosen)
                w = e.widget
                w.item(w.focus(), text=chosen)

    def clear_tree(self):
        self.uuid_lookup = {}
        for item in self.tree.get_children():
            self.tree.delete(item)

    def build_gui_tree(self, tree, parent, data):
        children = find_string_hierarchy(data, DataSpooler(data))
        self.children[self.selected_level['s2']] = children
        current_parent = ''
        for c in children:
            path = ""
            p = c.parent
            while p:
                path = str(p.field_num) + "." + path
                p = p.parent
            path += str(c.field_num)
            if path == "101.13.1":
                current_parent = self.tree.insert('', 'end', text=c.content)
            elif c.content in enemy_list or c.content in destroyable_list or c.content in pickup_list:
                uid = uuid.uuid4()
                self.tree.insert(current_parent, 'end', uid, text=c.content)
                self.uuid_lookup[str(uid)] = c

    def select_level(self, e):
        sel = e.widget.curselection()
        if sel:
            self.selected_level = self.level_lookup[sel[0]]
            self.clear_tree()
            self.build_gui_tree(self.tree, '', self.selected_level['data'])

if __name__ == "__main__":
    bfe = BigFileEditor()
    leg = LevelEditorGUI(bfe)
