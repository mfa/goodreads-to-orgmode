import re
from pathlib import Path

from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parse
from jinja2 import Environment, FileSystemLoader


def parse_html_files():
    all_books = []
    for fn in Path("data").glob("*.html"):
        with open(fn, "r") as f:
            contents = f.read()
            soup = BeautifulSoup(contents, "lxml")

            for book in soup.find("table", id="books").find_all("tr"):
                items = book.find_all("td")
                if len(items) == 0:
                    continue
                d = {}
                for item in items:
                    _cls = list(set(item.attrs.get("class")) - {"field"})[0]

                    if _cls == "author":
                        d["author"] = (
                            item.text.replace("author", "")
                            .replace("\n", "")
                            .replace("*", "")
                            .strip()
                        )
                    if _cls == "date_added":
                        d["date_added"] = str(
                            date_parse(
                                item.text.replace("date added", "")
                                .replace("\n", "")
                                .strip()
                            ).date()
                        )
                    if _cls == "date_read":
                        if "not set" not in item.text:
                            d["date_read"] = str(
                                date_parse(
                                    item.text.replace("date read", "")
                                    .replace("[edit]", "")
                                    .replace("\n", "")
                                    .strip()
                                ).date()
                            )
                    if _cls == "isbn13":
                        d["isbn13"] = (
                            item.text.replace("isbn13", "").replace("\n", "").strip()
                        )
                    if _cls == "rating":
                        _x = re.search("\[(.*) stars \]", item.text)
                        if _x:
                            d["rating"] = _x[1].strip()
                    if _cls == "title":
                        d["title"] = re.sub(
                            "\s+",
                            " ",
                            item.text.replace("title", "").replace("\n", "").strip(),
                        )
                    if _cls == "cover":
                        d["url"] = (
                            "https://www.goodreads.com" + item.find("a").attrs["href"]
                        )
                all_books.append(d)
    return all_books


def write_as_orgmode(books):
    env = Environment(
        loader=FileSystemLoader("templates"),
    )
    template = env.get_template("books.org")
    with open("goodreads-books.org", "w") as fp:
        fp.write(template.render(books=books))


if __name__ == "__main__":
    write_as_orgmode(parse_html_files())
