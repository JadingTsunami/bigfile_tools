"""
Look up known types inside the bigfile to provide a user-friendly meaning for
the field.


known_types:
    keys: tables in bigfile
    values: dictionary of next-level lookup for each table

table lookup dictionary:
    keys: either a number or '*' (wildcard)
        if the exact match is in the dictionary, it's used
        else the '*' will match if present
    values: nested dictionary OR
            'name' used for the top-level name OR
            string with a value

The "name" key exists so you can give a name to a section while still giving names to entries beneath it in the hierarchy.
"""
known_types = {
    "MetaGameConfigData" : {
        "1" : {
            "name" : "Character definitions",
            "0" : "Axel4 Character",
            "1" : "Blaze4 Character",
            "2" : "Cherry Character",
            "3": "Floyd Character",
            "4": "Adam4 Character",
            "5": "Blaze1 Character",
            "6": "Adam1 Character",
            "7": "Axel1 Character",
            "8": "Skate2 Character",
            "9": "Blaze2 Character",
            "10": "Axel2 Character",
            "11": "Max2 Character",
            "12": "Axel3 Character",
            "13": "Blaze3 Character",
            "14": "Roo Character",
            "15": "Skate3 Character",
            "16": "Zan Character",
            "17": "Shiva3 Character",
            "18": "Estel Character",
            "19": "Max4 Character",
            "20": "Shiva4 Character"
        },
        "14" : {
            "name": "Single Player Levels",
            "0" : {
                "name": "Story Mode Levels",
                "1": {
                    "*" : {
                        "1": "Level Screens",
                        "5": "Par Time (60 fps tics)",
                        "6": "Base Par Score"
                    }
                }
            },
            "1": "Boss Rush"
        },
        "29": {
            "name": "Difficulty definitions",
            "0": "Easy",
            "1": "Normal",
            "2": "Hard",
            "3": "Hardest",
            "4": "Mania",
            "5": "Mania Plus",
            "*": {
                "1": "Difficulty name",
                "4": {
                    "7" : "Aggro slots", # Credit and thanks to MoonLightFox
                    "8" : "Enemy activity (higher=more active)", # Credit and thanks to MoonLightFox
                    "13": "Starting lives",
                    "14": "Required score multiplier for ranks",
                    "19": "Extra life points (story/level select)",
                    "20": "Extra life points (arcade)"
                }
            }
        },
        "100": {
            "name": "Single-player unlocks",
            "*": {
                "1": "Unlockable",
                "2": "Required score",
                "3": "Unlocked character"
            }
        },
        "106": "PvP Arenas",
        "114": "Training levels",
        "115": "Free Training",
        "116": "Survival config",
        "117": "(Maybe) Training enemy spawner"
    },

    "CharacterData" : {
        "9" : {
            "1" : "HP (16.16)"
        },
        "10" : {
            "1" : {
                "1" : "Enemy AI type"
            }
        },
        "12" : {
            "1" : "Death sound effect"
        },
        "13" : "Localizable string name",
        "14" : {
            "1" : "Enemy portrait icon"
        },
        "34" : {
            "name" : "Usable Weapons",
            "*" : "Weapon identifier"
        },
        "99": {
            "name": "Moves",
            "*" : {
                "2" : "Input trigger button",           # Credit and thanks to Honganqi and FuzzYetPatchy!
                "3" : "Input trigger direction",        # Credit and thanks to Honganqi and FuzzYetPatchy!
                "6" : {
                    "name": "Hit",
                    "*" : {
                        "1" : {
                            "1": "Damage (16.16)"
                        },
                        "2" : {
                            "1" : "Horizontal Force"    # Credit and thanks to Bragdras!
                        },
                        "3" : {
                            "1" : "Vertical Force"      # Credit and thanks to Bragdras!
                        },
                        "4" : "Hitstop",
                        "5" : "Hitstun",
                        "9" : "Turnaround on hit",      # Credit and thanks to MoonLightFox
                        "10" : "Multihit",              # Credit and thanks to MoonLightFox
                        "11" : "Collision enabled",     # Credit and thanks to MoonLightFox
                        "12" : "Collision damage (11 must be set)", # Credit and thanks to MoonLightFox
                        "13" : "Pushback direction",    # Credit and thanks to MoonLightFox
                        "15" : {
                            "1" : "Air juggle launch height" # Credit and thanks to MoonLightFox
                        },
                        "17" : "Ground bounce count",   # Credit and thanks to MoonLightFox
                        "20" : {
                            "1" : "Strength of pushback of airborne enemy (+ toward / - away)" # Credit and thanks to MoonLightFox
                        },
                        "21" : {
                            "1" : "Sound effect"
                        },
                        "24" : {
                            "1" : "Hit depth"           # Credit and thanks to Bragdras!
                        },
                        "27" : "Move forward after move", # Credit and thanks to MoonLightFox
                        "28" : "Recovery/freeze", # Credit and thanks to MoonLightFox

                        "29" : { # Credit and thanks to MoonLightFox
                            "name" : "Wallbounce properties", # Credit and thanks to MoonLightFox
                            "2" : "Damage" # Credit and thanks to MoonLightFox

                        },

                        "32" : {
                            "1" : "Gravity" # Credit and thanks to MoonLightFox
                        },
                        "35" : "Ignore weight", # Credit and thanks to MoonLightFox
                        "37": "Ignore OTG limitations", # Credit and thanks to FuzzYetPatchy and MoonLightFox!
                        "41": "Change state of enemy on hit", # Credit and thanks to FuzzYetPatchy and MoonLightFox!
                        "44": "Increased pushback", # Credit and thanks to FuzzYetPatchy and MoonLightFox!
                        "51": "Allow OTG",               # Credit and thanks to FuzzYetPatchy and MoonLightFox!
                        "59": "Enable y-axis hitbox"    # Credit and thanks to MoonLightFox
                    }
                },
                "7" : { # Credit and thanks to MoonLightFox for this entire section!
                    "name" : "Move cancels",
                    "*" : {
                        "1" : "Name of the move that will be canceled",
                        "2" : "Input button",
                        "3" : "Condition (direction)",
                        "4" : "Starting frame for cancel",
                        "5" : "Ending frame for cancel",
                        "6" : "Disable cancel on whiff",
                        "9" : "Direction of canceled move (0 - straight)"
                    }
                },
                "14" : "Can move cancel normal hit animation", # Credit and thanks to MoonLightFox
                "19" : "Move vulnerability: 0-7 (0 – fully vulnerable, 1 – armor before first hit, 2 – armor whole move, 3 – i-frames before first hit, 4 – full i-frames)", # Credit and thanks to MoonLightFox
                "21" : {
                    "1" : "HP Cost for Move"
                },
                "27" : "Can move cancel special animation",
                "35" : "Incoming damage multiplier during move",
                "66" : {
                    "name" : "Alt moves"
                }
                # 99.7.2: Maybe: buffer inputs for MoveCondition (FuzzYetPatchy)
                # 99.7.3: Maybe: buffer inputs for MoveCommand (FuzzYetPatchy)
            }
        }
    },

    # Credit and thanks to MoonLightFox for this entire table decoding!
    "DamageAreaData" : {
        "1" : "Sprite name",
        "2" : "Hit properties",
        "3" : "Duration (frames)"
    },

    "SurvivalConfigData" : {
        "1" : {
            "name" : "Enemy spawn groups",
            "*" : {
                "1" : "Enemy grouping name",
                "2" : {
                    "name" : "Group definiton",
                    "*" : {
                        "1" : {
                            "1" : "Enemy grouping definition pointer",
                            "2" : "Enemy spawn count",
                            "4" : "Max simultaneous spawns"
                        },
                    }
                }
            }
        },
        "2" : "Enemy group definitions",
        "3" : "Survival map configs",
        "5" : {
            "name" : "Survival perk definitions",
            "*" : {
                "4" : {
                    "1" : "(Initial) Strength/% of perk"
                },
                "7" : "Perk name",
                "8" : "Localizable title string",
                "9" : "Localizable description string - line 1",
                "10" : "Localizable description string - line 2",
                "13" : {
                    "name" : "Subsequent pickup strengths",
                    "*" : {
                        "1" : "(nth pickup) perk strength/%"
                    }
                },
                "17" : "How many times perk can appear",
                "18" : "Sound effect on pickup",
                "23" : "Localizable title string",
            },
        },
        "27" : "Random crate weapons",
        "48" : {
            "name" : "Random crate pickups",
            "*" : {
                "1" : {
                    "1" : "Pickup type"
                },
                "2" : "Probability of appearing (out of 100)"
            }
        },
        "53" : {
            "name" : "Buddy/Ally definitions",
            "*" : {
                "1" : "Level 0/1/2/3 random allies"
            }
        }
    }
}

def lookup_type(crumb):
    kt = ''
    type_lookup = known_types
    in_array = False
    skip_next = False
    for i,chunk in enumerate(crumb):
        if chunk.endswith('[]'):
            in_array = True
            chunk = chunk.rstrip('[]')

        if isinstance(type_lookup, str):
            kt = ''
            type_lookup = {}
            break
        elif skip_next and "*" in type_lookup:
            type_lookup = type_lookup["*"]
            skip_next = False
        elif chunk in type_lookup:
            # note: this relies on the LAST iteration of the loop
            # hitting the desired endpoint
            type_lookup = type_lookup[chunk]
            if in_array:
                skip_next = True
            else:
                skip_next = False
        elif "*" in type_lookup:
            type_lookup = type_lookup["*"]
            if chunk in type_lookup:
                type_lookup = type_lookup[chunk]
        else:
            kt = ''
            type_lookup = {}
            break
        in_array = False
    if isinstance(type_lookup, dict) and "name" in type_lookup:
        kt = type_lookup["name"]
    elif isinstance(type_lookup, str):
        kt = type_lookup
    return kt
