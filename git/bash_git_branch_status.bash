# add to ~/.bashrc next string:
# . ~/.local/bash_git_branch_status.bash

BLACK="\[\033[0;30m\]"
RED="\[\033[0;31m\]"
GREEN="\[\033[0;32m\]"
YELLOW="\[\033[0;33m\]"
BLUE="\[\033[01;34m\]"
MAGENTA="\[\033[0;35m\]"
CYAN="\[\033[0;36m\]"
WHITE="\[\033[0;37m\]"
NONE="\[\033[0m\]"    # unsets color to terms fg color

function __is_gitdir {
  git status &> /dev/null
  return $?
}

function __git_branch {
  __is_gitdir
  if [ $? == 0 ]
  then
      local branch_name=`git branch | grep '* ' | awk '{print $2}'`
      if [ $? == 0 ]
      then
        echo "(${branch_name})"
      else
        echo ""
      fi
  fi
}

function __get_color {
  __is_gitdir
  if [ $? == 0 ]
  then  
    git status | grep 'git add\|git reset HEAD' &> /dev/null;
    if [ $? != 0 ]
    then
        echo "32"
    else
        echo "33"
    fi
  fi
}

function bash_prompt {
  local USER_COLOR=$GREEN
  [ $UID -eq "0" ] && USER_COLOR=$RED

  PS1="\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}${USER_COLOR}\u@\h${WHITE}:${BLUE}\w\[\033[0;\$(__get_color)m\]\$(__git_branch)${NONE}$ "
}

bash_prompt
unset bash_prompt
