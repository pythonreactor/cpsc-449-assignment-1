# Path to your oh-my-zsh installation.
export ZSH="/root/.oh-my-zsh"

# Aliases
alias flask-run='cd /code/src/flask_app; poetry run python app.py'

# Set name of the theme to load
ZSH_THEME="robbyrussell"

# Uncomment the following line to display red dots whilst waiting for completion.
# Caution: this setting can cause issues with multiline prompts (zsh 5.7.1 and newer seem to work)
# See https://github.com/ohmyzsh/ohmyzsh/issues/5765
COMPLETION_WAITING_DOTS="true"

# Fix multi-user environment bug
ZSH_DISABLE_COMPFIX=true

source $ZSH/oh-my-zsh.sh

# User configuration

PATH=$PATH:~/.local/bin/
