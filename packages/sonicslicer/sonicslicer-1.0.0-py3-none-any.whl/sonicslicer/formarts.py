SUPPORTED_AUDIO_FORMATS = ["wav", "mp3", "ogg", "flac", "aiff"]

SUPPORTED_AUDIO_FORMATS_FUTURE = ["aac"]


class AudioFormarts:
    """
    House supported audio formats and future formart partialy or not yet supported.
    Args:
        None
    Returns:
        list
    """

    def __init__(self):
        self.surpoted = SUPPORTED_AUDIO_FORMATS
        self.future = ["aac"]

    def _surpoted(self):
        """
        Args:
            self -> instance
        Returns:
            list"""
        return self.surpoted

    def _future(self):
        """
        Args:
            self -> instance
        Returns:
            list"""
        return self.future
