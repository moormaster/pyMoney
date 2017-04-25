_pymoney_transaction()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[$_ARGINDEX]} in
		--fullnamecategories)
			_pymoney_transaction $(( $_ARGINDEX + 1 ))
			;;

		add)
			case ${COMP_CWORD} in
				$(( $_ARGINDEX + 1 )) )
					# date
					;;

				$(( $_ARGINDEX + 2 )) )
					# category
					COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category list )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				$(( $_ARGINDEX + 3 )) )
					# amount
					;;

				$(( $_ARGINDEX + 4 )) )
					# comment
			esac
			;;

		delete)
			;;

		list)
			case ${COMP_WORDS[$(( $COMP_CWORD - 1 ))]} in
				--category)
					COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category list )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;

				*)
					COMPREPLY=( $( compgen -W "--category" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
					;;
			esac
			;;

		*)
			COMPREPLY=( $( compgen -W "--fullnamecategories add delete list" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

_pymoney_category()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[$_ARGINDEX]} in
		--fullnamecategories)
			_pymoney_category $(( $_ARGINDEX + 1 ))
			;;

		add)
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) )
				# parent category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category list )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		delete | rename | setsign )
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) )
				# category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category list )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		merge | move)
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) | $(( $_ARGINDEX + 2 )) )
				# parent category / category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category list )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		list | tree)
	        ;;

		*)
			COMPREPLY=( $( compgen -W "--fullnamecategories add delete merge move rename setsign list tree" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

_pymoney_summary()
{
	_ARGINDEX=$1
	case ${COMP_WORDS[2]} in
		categories)
			;;

		monthly)
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) )
				# category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category list )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		yearly)
			case $COMP_CWORD in
				$(( $_ARGINDEX + 1 )) )
				# category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category list )" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
				;;
			esac
			;;

		*)
			COMPREPLY=( $( compgen -W "categories monthly yearly" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
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

		summary)
			_pymoney_summary 2
			;;

		*)
			COMPREPLY=( $( compgen -W "transaction category summary" "\\${COMP_WORDS[$COMP_CWORD]}" ) )
			;;
	esac
}

complete -F _pymoney pyMoney.py
