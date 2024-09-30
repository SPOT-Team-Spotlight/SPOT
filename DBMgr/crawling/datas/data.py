class Data():
    title : str
    desc : list
    summary : str = "생성되지 않음"
    link : str

    def __init__(self, title, chunked_desc, summary, link) -> None:
        self.title = title
        self.desc = chunked_desc
        self.summary = summary
        self.link = link

    def print_data(self):
        return "Data { title:" + self.title + "desc:" + str(self.desc[0]) + \
            "summary:" + str(self.summary[0]) + "link:" + str(self.link) + " }"
