#!/bin/bash

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$dir"

history -r script_history

dictionary=$(python2.7 helper.py --dict)

declare -A opt2dic

start=0

bold='\033[0;1m'
red='\033[0;31m'
nc='\033[0m'

trap ctrl_c INT

function ctrl_c()
{
	exit 1
}


function tab
{
	if [[ -z "$READLINE_LINE" ]]; then return; fi
	end=`date +%s%N`

	remake=true
	if [ -f tabterms.txt ]; then
		{
			read searchterms
			read commonprefix
		} < tabterms.txt

		case "$READLINE_LINE" in
			"$prev_searchterms"|"$searchterms"|"$commonprefix") remake=false; ;;
		esac
	fi

	if [[ $remake ]]; then
		python2.7 autocomplete.py $READLINE_LINE --lang "$language" --trans "$translate"
		commonprefix="$(sed -n '2{p;q;}' tabterms.txt)"
	fi	
	prev_searchterms="$READLINE_LINE"
	
	duration=$((end-start))

	if [[ $duration -lt 200000000 ]]; then
		printf '> %s\n' "$READLINE_LINE"
		tail -n +3 tabterms.txt | 
		sed -e 's/\(.*\)/\o033[36m\1\o033[39m/' |	
		column | less -r -X -F -E
	elif [[ ! -z "$commonprefix" ]]; then
		READLINE_LINE="$commonprefix"
		READLINE_POINT="${#READLINE_LINE}"
		(( READLINE_POINT++ ))
	fi

	start=`date +%s%N`
}


function print_logo
{
	printf "${nc}=${nc}%.0s" {1..30}
	printf '\n'
	printf ' %.0s' {1..3}
	printf "${nc}%s${nc}\n" "GYLDENDALS RØDE ORDBØGER"
	printf "${nc}-${nc}%.0s" {1..30}
	printf '\n'
}


function print_main_options
{
	echo -e "Vælg en ordbog:\n"
	idx=0
	s=' '
	for i in $dictionary;
	do
		(( idx++ ))
		if [[ $idx = 10 ]]; then s=''; fi
		printf ' (%-d)%-s   %-s\n' "$idx" "$s" "$(python2.7 helper.py --name $i)"
		opt2dic["$idx"]="$i"
	done
	printf ' (%s)uit\n' "q"
}


function print_sub_options
{
	printf 'Vælg en ordbog:\n'
	printf ' (1)   Dansk-%-s\n' "$langname"
	printf ' (2)   %-s-Dansk\n' "$langname"
	if [[ $doubflag = 3 ]]; then 
		printf ' (3)   Dansk-%-s-Dansk\n' "$langname"
	fi
	printf ' (%s)uit\n' "q"
}


function print_dictionary_name
{
	langname="$(python2.7 helper.py --name $language)"
	doubflag="$(python2.7 helper.py --doubflag $language)"
	printf "$bold"
	if [[ $doubflag = 0 ]]; then
		printf "$langname"
	else
		case $translate in
			0) printf "Dansk-$langname" ;;
			1) printf "$langname-Dansk" ;;
			2) printf "Dansk-$langname-Dansk" ;;
		esac
	fi
	printf "$nc\n"
}


function print_help
{
	printf "$bold%s$nc\n" "Gyldendals Røde Ordbøger, verion 1.0"
	print_dictionary_name
	echo ""
	echo "Programmet understøtter \"tab completion\" og \"tabtab\" for at se forslag."
	echo "Tast 'help()' for at vise hjælpebesked."
	echo "Tast 'which()' for at se hvilken ordbog der p.t. kører."
	echo "Tast 'demo()' for nogle demoer."
	echo "Tast 'q()' for at lukke ordbogen og returnere til menuen."
	echo ""
	
}


function run_dictionary
{
	clear
	print_help
	while true
	do
		bind -x '"\t":"tab"';
		read -p"> " -e				

		if [[ "${REPLY}" = "q()" ]]; then
			return
		elif [[ "${REPLY}" = "which()" ]]; then
			print_dictionary_name
		elif [[ "${REPLY}" = "help()" ]]; then
			print_help
		elif ! [[ -z ${REPLY} ]]; then
			history -s "${REPLY}"
			./main.py ${REPLY} --lang $language --trans $translate | less -r -X -F -E -c
		fi
	done
}


function sub_menu 
{
	suboption=0
	until [[ "$suboption" = "q" ]]; do
		# Print sub menu
		clear
		print_logo
		print_sub_options

		# Get user input
		read -p":" -n1
		suboption="${REPLY,,}"
		if [[ "$suboption" = 'q' ]]; then
			break;
		fi

		# Look up in the dictionary
		if [[ "$suboption" = 1 || "$suboption" = 2 || "$suboption" = 3 && "$doubflag" = 3 ]];
		then
			translate=$((suboption - 1))
			run_dictionary;
		else
			tput setf 4; echo "Error: invalid input"; tput setf 4;
			sleep 1
		fi
	done
}


function main_menu 
{
	option=0
	until [[ "$option" = "q" ]]; do
		# Print main menu
		clear
		print_logo
		print_main_options

		# Get user input
		if [[ "$idx" -gt 9 ]]; then read -p ":"; else read -s -n1; fi
		option="${REPLY,,}"

		
		if [[ "$option" = 'q' ]]; then
			break;
		elif [[ "$option" -lt 1 || "$option" -gt "$idx" ]]; then
			tput setf 4; echo "Error: invalid input"; tput setf 4;
			sleep 1
		else
			language=${opt2dic["$option"]}
			doubflag="$(python2.7 helper.py --doubflag $language)"
			langname="$(python2.7 helper.py --name $language)"
			if [[ $doubflag -gt 1 ]]; then
				sub_menu;
			else
				translate=0
				run_dictionary
			fi
		fi
	done
	exit
}


function error_exit()
{
	tput setf 4;echo "Error: unknown dictionary";tput setf 4
	sleep 1
	exit 1;
}


# Run the program
function main_program()
{
	if [[ $# -eq 2 ]]; then	
		language=$1
		translate=$2 && ((translate++))
		langname="$(python2.7 helper.py --name $language)"
		if [[ -z $langname ]]; then error_exit; fi
		doubflag="$(python2.7 helper.py --doubflag $language)"
		if [[ $2 -ne 1 && $2 -gt $doubflag || $2 -lt 1 ]]; then error_exit; fi
		run_dictionary
	fi
	main_menu
}

main_program $@
