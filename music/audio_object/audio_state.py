import enum


class AudioState(enum.Enum):

    """ This class serves as an Enum to track the state of audio player"""
    NONE = 0
    YOUTUBE = 1
    RADIO = 2

    def __eq__(self, other):                   # Specifying comparisons between two AudioState Objects
        if self.__class__ is other.__class__:  # If two class are the same
            return self.value == other.value
        return NotImplemented
