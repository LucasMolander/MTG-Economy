# MTG Economy
This project aims to track the MTG economy.

# Setup
Run `./setup.sh` to set up the project (it creates some files and folders).

Then, populate `keys.json` (see the relevant section below).

# keys.json
If you're going to run this yourself, you need to have `keys.json` that looks like this:
```
{
    "tcgplayer": {
        "public": "<your public key here>",
        "private": "<your private key here>",
        "user_agent_header": "<your project name here>"
    }
}
```