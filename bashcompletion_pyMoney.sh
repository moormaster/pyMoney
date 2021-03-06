mincacheageseconds=60

_pymoney_category_list()
{
	pymoneycmd="$*"
	now=$( date +%s )
	cachetimestamp=""
	cachefile=pymoney.completioncache.categories

	if [ -e "$cachefile" ]
	then
		cachetimestamp=$( head -n 1 "$cachefile" )
	fi

	if ! [ -e "$cachefile" ] || [ "$cachetimestamp" == "" ] || [ $(( $now - $cachetimestamp )) -ge $mincacheageseconds ] && [ "$cachefile" -ot "pymoney.categories" ]
	then
		( date +%s; "$pymoneycmd" category list) > "$cachefile"
	fi

	tail -n +2 "$cachefile"
}

_pymoney_paymentplan_list()
{
	pymoneycmd="$*"
	now=$( date +%s )
	cachetimestamp=""
	cachefile=pymoney.completioncache.paymentplans

	if [ -e "$cachefile" ]
	then
		cachetimestamp=$( head -n 1 "$cachefile" )
	fi

	if ! [ -e "$cachefile" ] || [ "$cachetimestamp" == "" ] || [ $(( $now - $cachetimestamp )) -ge $mincacheageseconds ] && [ "$cachefile" -ot "pymoney.paymentplans" ]
	then
		( date +%s; "$pymoneycmd" paymentplan listnames) > "$cachefile"
	fi

	tail -n +2 "$cachefile"
}

_pymoney_paymentplangroup_list()
{
	pymoneycmd="$*"
	now=$( date +%s )
	cachetimestamp=""
	cachefile=pymoney.completioncache.paymentplangroups

	if [ -e "$cachefile" ]
	then
		cachetimestamp=$( head -n 1 "$cachefile" )
	fi

	if ! [ -e "$cachefile" ] || [ "$cachetimestamp" == "" ] || [ $(( $now - $cachetimestamp )) -ge $mincacheageseconds ] && [ "$cachefile" -ot "pymoney.paymentplans" ]
	then
		( date +%s; "$pymoneycmd" paymentplan listgroupnames) > "$cachefile"
	fi

	tail -n +2 "$cachefile"
}

_pymoney_transactioncomments_list()
{
	pymoneycmd="$*"
	now=$( date +%s )
	cachetimestamp=""
	cachefile=pymoney.completioncache.transactioncomments

	if [ -e "$cachefile" ]
	then
		cachetimestamp=$( head -n 1 "$cachefile" )
	fi

	if ! [ -e "$cachefile" ] || [ "$cachetimestamp" == "" ] || [ $(( $now - $cachetimestamp )) -ge $mincacheageseconds ] && [ "$cachefile" -ot "pymoney.categories" ]
	then
		( date +%s; "$pymoneycmd" transaction list | sed -e "s/\([ ]*[^ ]\+\)\{5\}[ ]*\(.*\)/\2/" | sort | uniq ) > "$cachefile"
	fi

	tail -n +2 "$cachefile"
}

_pymoney_transaction()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[$_ARGINDEX]} in
		add)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# date
					;;

				$(( $_ARGINDEX + 2 )) )
					# fromcategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 3 )) )
					# tocategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 4 )) )
					# amount
					;;

				$(( $_ARGINDEX + 5 )) )
					# comment
					tmpfile=$( mktemp )
					_pymoney_transactioncomments_list ${COMP_WORDS[0]} > $tmpfile
					readarray -t comments < $tmpfile
					rm $tmpfile

					withcolon=0
					searchstring=${COMP_WORDS[$COMP_CWORD]}
					if [ "${searchstring:0:1}" == "\"" ]
					then
						withcolon=1
						searchstring="${searchstring:1}"
					fi
					if [ "${searchstring:$(( ${#searchstring}-1 )):1}" == "\"" ]
					then
						searchstring="${searchstring:0:$(( ${#searchstring}-1 ))}"
					fi

					for l in "${comments[@]}"
					do
						if [ "${l:0:${#searchstring}}" == "${searchstring}" ]
						then
							if [[ "$l" == *" "* ]] || [ $withcolon -eq 1 ]
							then
								COMPREPLY=( "${COMPREPLY[@]}" "\"$l\"" )
							else
								COMPREPLY=( "${COMPREPLY[@]}" "$l" )
							fi
						fi
					done
					;;
			esac
			;;

		edit)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# index
					;;

				$(( $_ARGINDEX + 2 )) )
					# date
					;;

				$(( $_ARGINDEX + 3 )) )
					# fromcategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 4 )) )
					# tocategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 5 )) )
					# amount
					;;

				$(( $_ARGINDEX + 6 )) )
					# comment
					tmpfile=$( mktemp )
					_pymoney_transactioncomments_list ${COMP_WORDS[0]} > $tmpfile
					readarray -t comments < $tmpfile
					rm $tmpfile

					withcolon=0
					searchstring=${COMP_WORDS[$COMP_CWORD]}
					if [ "${searchstring:0:1}" == "\"" ]
					then
						withcolon=1
						searchstring="${searchstring:1}"
					fi
					if [ "${searchstring:$(( ${#searchstring}-1 )):1}" == "\"" ]
					then
						searchstring="${searchstring:0:$(( ${#searchstring}-1 ))}"
					fi

					for l in "${comments[@]}"
					do
						if [ "${l:0:${#searchstring}}" == "${searchstring}" ]
						then
							if [[ "$l" == *" "* ]] || [ $withcolon -eq 1 ]
							then
								COMPREPLY=( "${COMPREPLY[@]}" "\"$l\"" )
							else
								COMPREPLY=( "${COMPREPLY[@]}" "$l" )
							fi
						fi
					done
					;;
			esac
			;;

		delete)
			;;

		list)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--category | --fromcategory | --tocategory)
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--paymentplan)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--paymentplangroup)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					COMPREPLY=( $( compgen -W "--after --after-or-from --before --before-or-from --from --category --fromcategory --tocategory --fullnamecategories --nopaymentplans --paymentplansonly --paymentplan --paymentplangroup" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
			esac
			;;

		*)
			COMPREPLY=( $( compgen -W "add edit delete list" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

_pymoney_category()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[$_ARGINDEX]} in
		add)
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) )
				# parent category
				COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		delete | rename )
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) )
				# category
				COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		merge | move)
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) | $(( $_ARGINDEX + 2 )) )
				# parent category / category
				COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		list | tree)
			COMPREPLY=( $( compgen -W "--fullnamecategories" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
	        ;;

		*)
			COMPREPLY=( $( compgen -W "add delete merge move rename list tree" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

_pymoney_paymentplan()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[$_ARGINDEX]} in
		add)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# name
					;;

				$(( $_ARGINDEX + 2 )) )
					# group
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 3 )) )
					# fromcategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 4 )) )
					# tocategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 5 )) )
					# amount
					;;

				$(( $_ARGINDEX + 6 )) )
					# comment
			esac
			;;

		edit)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# name
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 2 )) )
					# group
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 3 )) )
					# fromcategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 4 )) )
					# tocategory
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 5 )) )
					# amount
					;;

				$(( $_ARGINDEX + 6 )) )
					# comment
			esac
			;;

		move)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# name
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 2 )) )
					# new group
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
			esac
			;;

		rename)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# name
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
				$(( $_ARGINDEX + 2 )) )
					# newname
					;;
			esac
			;;

		execute)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# name
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 2 )) )
					# date
					;;
			esac
			;;

		delete)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# name
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
			esac
			;;

		list)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--category | --fromcategory | --tocategory)
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--group)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					COMPREPLY=( $( compgen -W "--category --fromcategory --tocategory --fullnamecategories --group" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

			esac
			;;

		listnames)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--group)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					COMPREPLY=( $( compgen -W "--group" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
			esac
			;;

		*)
			COMPREPLY=( $( compgen -W "add edit rename move execute delete list listnames listgroupnames" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

_pymoney_summary()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[2]} in
		categories)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--category | --cashflowcategory)
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--paymentplan)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--paymentplangroup)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					COMPREPLY=( $( compgen -W "--after --after-or-from --before --before-or-from --from --category --cashflowcategory --nopaymentplans --paymentplansonly --paymentplan --paymentplangroup --showempty --maxlevel" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
			esac
			;;

		paymentplansprediction)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--category | --cashflowcategory)
					COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--group)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					COMPREPLY=( $( compgen -W "--category --cashflowcategory --factor --divisor --group --showempty --maxlevel" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
			esac
			;;

		monthly)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--paymentplan)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--paymentplangroup)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					case $COMP_CWORD in
						$(( $_ARGINDEX + 1 )) )
							# category
							COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
							;;

						*)
							COMPREPLY=( $( compgen -W "--after --after-or-from --before --before-or-from --from --balance --nopaymentplans --paymentplansonly --paymentplan --paymentplangroup" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
							;;
					esac
					;;
			esac
			;;

		yearly)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--paymentplan)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplan_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				--paymentplangroup)
					COMPREPLY=( $( compgen -W "$( _pymoney_paymentplangroup_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					case $COMP_CWORD in
						$(( $_ARGINDEX + 1 )) )
							# category
							COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
							;;

						*)
							COMPREPLY=( $( compgen -W "--after --after-or-from --before --before-or-from --from --balance --nopaymentplans --paymentplansonly --paymentplan --paymentplangroup" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
							;;
					esac
					;;
			esac
			;;

		*)
			COMPREPLY=( $( compgen -W "categories paymentplansprediction monthly yearly" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

_pymoney_export()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
		--category | --fromcategory | --tocategory)
			COMPREPLY=( $( compgen -W "$( _pymoney_category_list ${COMP_WORDS[0]} )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;

		*)
			COMPREPLY=( $( compgen -W "--after --after-or-from --before --before-or-from --from --category --fromcategory --tocategory" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

_pymoney()
{
	case ${COMP_WORDS[1]} in
		transaction)
			_pymoney_transaction 2
			;;

		category)
			_pymoney_category 2
			;;

		paymentplan)
			_pymoney_paymentplan 2
			;;

		summary)
			_pymoney_summary 2
			;;

		export)
			_pymoney_export 2
			;;

		--script)
			;;

		--cli)
			;;

		*)
			COMPREPLY=( $( compgen -W "transaction category paymentplan summary export --script --cli" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

complete -F _pymoney pyMoney.py
