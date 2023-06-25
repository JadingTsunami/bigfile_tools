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
        }
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
    if "name" in type_lookup:
        kt = type_lookup["name"]
    return kt
