import os
from slugify import slugify

class Article:
    def __init__(self):
        self.title = ""
        self.names = ""
        self.content = ""

    def load_names(self):
        self.names = os.listdir("articles")

    def load_title(self):
        folders = os.listdir("articles")
        slug_titles = {}
        for folder in folders:
            slug = slugify(folder)
            slug_titles[folder] = slug
            self.title = folder.rstrip('.')

    def load_content(self):
        with open(f"articles/{self.title}", 'r', encoding='utf-8') as file:
            self.content = file.read()


