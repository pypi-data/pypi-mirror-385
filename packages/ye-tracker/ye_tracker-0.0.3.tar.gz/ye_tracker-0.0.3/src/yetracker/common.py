import typing
import pprint

type Row = list[str]
type Range = list[Row]

def add_repr[T](cls: type[T]):
    def __repr__(self: T):
        print_dict = {attr: self.__dict__[attr] 
                      for attr in self.__dict__
                      if attr[0] != '_'}

        return pprint.pformat(print_dict)

    cls.__repr__ = __repr__
    return cls