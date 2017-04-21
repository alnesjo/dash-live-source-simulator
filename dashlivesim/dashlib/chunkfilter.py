from mp4filter import MP4Filter


class ChunkFilter(MP4Filter):
    """Generate chunk from segment"""
    def __init__(self, data, begin, duration):
        """
        :param data: Binary representation of segment
        :param begin: Start time in milliseconds
        :param duration: Duration in milliseconds
        """
        super(ChunkFilter, self).__init__(data)
        self.top_level_boxes_to_parse = ["styp", "moof", "mdat"]
        self.composite_boxes_to_parse = ['moof', 'traf']

        def process_styp(self, data):
            """
            Remove `styp' box
            :param data: `styp' box
            :return: Empty string
            """
            return ""

        def process_moof(self, data):
            """ 
            :param data: 
            :return: 
            """
            return ""


        def process_trun(self, data):
            """ 
            :param data: Binary representation of `trun' box
            :return: Samples matching chunk time window
            """
            return ""

        def process_mdat(self, data):
            """Keep data described by remaining samples"""
            return ""