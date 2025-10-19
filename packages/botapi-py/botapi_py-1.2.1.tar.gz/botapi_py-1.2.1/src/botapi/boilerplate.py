import enum

from typing import TypeVar, Callable

# Enums
E = TypeVar('E', bound=enum.Enum)

def extend_enum(*sources: type[E]) -> Callable[..., type[E]]:
	'''
	Decorator that extends an Enum class with members
	from one or more source Enum classes.
	'''
	def decorator(target: type[E]) -> type[E]:
		for source in sources:
			for member in source:
				if member.name not in target.__members__:
					target._member_map_[member.name] = member
		return target
	return decorator
	
