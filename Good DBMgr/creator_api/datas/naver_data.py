class NaverData():
    name: str
    address: str
    content : str
    vectorized_content : str
    img_src : str
    link : str

    def __init__(self, name, address, content, src, link):
        self.name = name
        self.address = address
        self.content = content
        self.img_src = src
        vectorized_content : None
        self.link = link
