_pymoney_transaction()
{
	case ${COMP_WORDS[2]} in
		add)
			;;
		delete)
			;;
		list)
			;;
		*)
			COMPREPLY=( $( compgen -W "add delete list" ${COMP_WORDS[$COMP_CWORD]}) )
			;;
	esac
}

_pymoney_category()
{
	case ${COMP_WORDS[2]} in
		add)
			;;
		delete)
			;;
		merge)
			;;
		move)
			;;
		rename)
			;;
		list)
			;;
		*)
			COMPREPLY=( $( compgen -W "add delete merge move rename list" ${COMP_WORDS[$COMP_CWORD}} ) )
			;;
	esac
}

_pymoney_summary()
{
	case ${COMP_WORDS[2]} in
		categories)
			;;
		monthly)
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
