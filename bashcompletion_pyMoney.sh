_pymoney_transaction()
{
	case ${COMP_WORDS[2]} in
		add)
			case ${COMP_CWORD} in
				3)
					# date
					;;

				4)
					# category
					COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category listnames )" ${COMP_WORDS[$COMP_CWORD]} ) )
					;;

				5)
					# amount
					;;

				6)
					# comment
			esac
			;;

		delete)
			;;

		list)
			;;

		*)
			COMPREPLY=( $( compgen -W "add delete list" ${COMP_WORDS[$COMP_CWORD]} ) )
			;;
	esac
}

_pymoney_category()
{
	case ${COMP_WORDS[2]} in
		add)
			;;

		delete | rename)
			case $COMP_CWORD in
				3)
				# category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category listnames )" ${COMP_WORDS[$COMP_CWORD]} ) )
				;;
			esac
			;;

		merge | move)
			case $COMP_CWORD in
				3 | 4)
				# category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category listnames )" ${COMP_WORDS[$COMP_CWORD]} ) )
				;;
			esac
			;;

		list)
			;;

		*)
			COMPREPLY=( $( compgen -W "add delete merge move rename list" ${COMP_WORDS[$COMP_CWORD]} ) )
			;;
	esac
}

_pymoney_summary()
{
	case ${COMP_WORDS[2]} in
		categories)
			;;

		monthly)
			case $COMP_CWORD in
				3)
				# category
				COMPREPLY=( $( compgen -W "$( ${COMP_WORDS[0]} category listnames )" ${COMP_WORDS[$COMP_CWORD]} ) )
				;;
			esac
			;;

		*)
			COMPREPLY=( $( compgen -W "categories monthly" ${COMP_WORDS[$COMP_CWORD]} ) )
			;;
	esac
}

_pymoney()
{
	case ${COMP_WORDS[1]} in
		transaction)
			_pymoney_transaction
			;;

		category)
			_pymoney_category
			;;

		summary)
			_pymoney_summary
			;;

		*)
			COMPREPLY=( $( compgen -W "transaction category summary" ${COMP_WORDS[$COMP_CWORD]} ) )
			;;
	esac
}

complete -F _pymoney pymoney.py
