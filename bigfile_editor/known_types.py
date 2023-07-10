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
            "2" : "Cherry Character"
        },
        "14" : {
            "name": "Single Player Levels",
            "0" : {
                "name": "Story Mode Levels",
                "*": {
                    "1": "Level Screens",
                    "5": "Par Time (60 fps tics)",
                    "6": "Base Par Score"
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
                    "13": "Starting lives",
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
                        "21" : {
                            "1" : "Sound effect"
                        },
                        "24" : {
                            "1" : "Hit depth"           # Credit and thanks to Bragdras!
                        },
                        "37": "Ignore OTG limitations", # Credit and thanks to FuzzYetPatchy and MoonLightFox!
                        "51": "Allow OTG"               # Credit and thanks to FuzzYetPatchy and MoonLightFox!
                    }
                },
                "21" : {
                    "1" : "HP Cost for Move"
                }
                # 99.7.2: Maybe: buffer inputs for MoveCondition (FuzzYetPatchy)
                # 99.7.3: Maybe: buffer inputs for MoveCommand (FuzzYetPatchy)
            }
        }
    }
}

def lookup_type(crumb):
    kt = ''
    type_lookup = known_types
    for i,chunk in enumerate(crumb):
        if isinstance(type_lookup, str):
            kt = ''
            type_lookup = {}
            break
        elif chunk in type_lookup:
            # note: this relies on the LAST iteration of the loop
            # hitting the desired endpoint
            type_lookup = type_lookup[chunk]
        elif "*" in type_lookup:
            type_lookup = type_lookup["*"]
        else:
            kt = ''
            type_lookup = {}
            break
    if isinstance(type_lookup, dict) and "name" in type_lookup:
        kt = type_lookup["name"]
    elif isinstance(type_lookup, str):
        kt = type_lookup
    return kt
