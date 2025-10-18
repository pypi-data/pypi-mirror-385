# wisort :magic_wand:
Your file-sorting wizard :mage: that manages your file magically :crystal_ball:

## Requirements
- python `>=3.14`
- uv (heavily recommended)
- a UNIX OS

## Installation
`wisort` is published on [PyPi](https://pypi.org/project/wisort/)
```bash
# using uv (recommended)
uv tool install wisort

# or with pip
pip install wisort
```
if you want to just try out and run the project you can use `uvx wisort`.
Make sure to copy the default `config.json` to `$XDG_CONFIG_HOME`(fallback to `$HOME/.config`).

## Concept and features
`wisort` is supposed to be a file sorting cli. Below can be seen my ideas for the project even if they might not be fully implemented yet. To see the progress go read the [ROADMAP](./ROADMAP.md)
It has different characters:
- apprentice
- magician (coming soon)
- witch
- dragon (coming soon)

These are different magical users so they clean your file system differently.
The apprentice is unsure about his work so he leave the most things to you to manually handle (confirmations when deleting etc.).
The magician works way more autonomously but is very calm and doesn't destroy anything. This means a lot of capabilties with a good amount of safety.
The witch is a brazen sorcerer not afraid of destruction. She cleans your filesystem very very thoroughly.

(As of now magician and witch are not implemented)

### The :sparkles: magic :sparkles:
* smart unzip:
archives can be automatically unpacked before being moved.
they get moved into a new folder or directly to the destination depending on the content 
* file duplicate removal strategies
    - replace the (older) duplicate by symlink
    - matching exact contents
    - diffing contents
    - intentional duplicate recognition -> diffing file names
* auto-remove empty files
* automatic move conflict resolution
when the programm wants to move a file somewhere where a file with the same name already exist it can handle that automatically

## Config
Configuration is done through `config.json` file in `$XDG_CONFIG_HOME/wisort/`

Example:
```json
{
	"runes": {
		"images": ["png", "jpeg", "jpg"]
	},
	"libraries": {
		"pics": {
			"destination": "~/Pictures/",
			"filetypes": "@images",
			"flatten": true
		}
	},
	"orders": {
		"recurse": true,
		"honor_gitignore": true,
		"ignore_dotfiles": true
	},
	"args": {
		"quiet": true,
		"force": false
	}
}
```

## Usage
For the exact CLI usage do `wisort --help`
