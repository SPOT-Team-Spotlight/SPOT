class NaverData():
    name: str
    address: str
    content : str
    vectorized_content : str
    link : str

    def __init__(self, name, address, content, link):
        self.name = name
        self.address = address
        self.content = content
        vectorized_content : None
        self.link = link
