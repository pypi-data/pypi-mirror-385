from wisort.config import Config, loaded


def use_runes():
    for name, rune in loaded.runes.items():
        if not isinstance(rune, str):
            continue
        if rune.startswith("@"):
            if rune[1:] not in loaded.runes:
                print(f"`rune {rune[1:]}` not found in your config")
                continue
            loaded.runes[name] = loaded.runes[rune[1:]]
            # TODO: add type checking
    for name, lib in loaded.libraries.items():
        for attr, value in vars(lib).items():
            if not isinstance(value, str):
                continue
            if value.startswith("@"):
                if value[1:] not in loaded.runes:
                    print(f"`rune {value[1:]}` not found in your config")
                    continue
                setattr(loaded.libraries[name], attr, loaded.runes[value[1:]])
                # TODO: add type checking
    for attr, value in vars(loaded.orders).items():
        if not isinstance(value, str):
            continue
        if value.startswith("@"):
            if value[1:] not in loaded.runes:
                print(f"`rune {value[1:]}` not found in your config")
                continue
            setattr(loaded.libraries[name], attr, loaded.runes[value[1:]])
            # TODO: add type checking
