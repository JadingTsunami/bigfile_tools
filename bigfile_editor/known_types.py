known_types = {
    "MetaGameConfigData" : {
        "1" : {
            "name" : "Character definitions",
            "0" : {
                "name": "Axel4 Character"
            }
        },
        "14" : {
            "1" : {
                "name": "Hud Icon"
            }
        },
        "29": {
            "name": "Difficulty definitions",
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
            "name": "Survival unlocks",
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
                "6" : {
                    "name": "Hit",
                    "1" : {
                        "1" : {
                            "name": "Damage (16.16)"
                        }
                    }
                }
            }
        }
    }
}

def lookup_type(crumb):
    kt = ''
    type_lookup = known_types
    for chunk in crumb:
        if chunk in type_lookup:
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
