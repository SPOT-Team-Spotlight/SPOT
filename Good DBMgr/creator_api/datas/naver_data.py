class NaverData():
    content : str
    vectorized_content : str
    link : str

    def __init__(self, content, link):
        self.content = content
        self.link = link

    def print_data(self):
        return "NaverData { link:" + {self.link} + "content:" + {self.content} + " }"
