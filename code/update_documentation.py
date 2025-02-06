import os

from bs4 import BeautifulSoup


def update_index(file: str) -> None:
    handle = open(file, "r+")

    soup = BeautifulSoup(handle, "lxml")
    handle.seek(0)

    # Add link to transformation documentation
    nav_list = soup.find("div", class_="sphinxsidebar", attrs={"role": "navigation"})
    nav_list = nav_list.find("ul")
    li_tag = soup.new_tag("li", attrs={"class": "toctree-l1"})
    a_tag = soup.new_tag(
        "a",
        attrs={
            "href": "/TransformationDocumentation.html",
            "class": "reference internal",
        },
    )
    a_tag.string = "Transformation Documentation"
    li_tag.append(a_tag)
    nav_list.append(li_tag)

    # Save changes
    handle.write(str(soup))
    handle.close()


def update_transformation_documentation(file: str):
    handle = open(file, "r+", encoding="utf-8")

    soup = BeautifulSoup(handle, "lxml")
    new_soup = BeautifulSoup(features="lxml")
    handle.close()

    # Prepare header
    header = soup.new_tag("head")
    header.append(soup.new_tag("meta", attrs={"charset": "utf-8"}))
    header.append(
        soup.new_tag(
            "meta",
            attrs={
                "name": "viewport",
                "content": "width=device-width, initial-scale=1.0",
            },
        )
    )
    header_title = soup.new_tag("title")
    header_title.string = (
        "OFA TANF Longitudinal Dataset Documentation - Transformation Documentation"
    )
    header.append(header_title)
    header.append(
        soup.new_tag(
            "link",
            attrs={
                "rel": "stylesheet",
                "type": "text/css",
                "href": "_static/pygments.css?v=d1102ebc",
            },
        )
    )
    header.append(
        soup.new_tag(
            "link",
            attrs={
                "rel": "stylesheet",
                "type": "text/css",
                "href": "_static/basic.css?v=686e5160",
            },
        )
    )
    header.append(
        soup.new_tag(
            "link",
            attrs={
                "rel": "stylesheet",
                "type": "text/css",
                "href": "_static/alabaster.css?v=27fed22d",
            },
        )
    )
    header.append(
        soup.new_tag(
            "script", attrs={"src": "_static/documentation_options.js?v=d45e8c67"}
        )
    )
    header.append(
        soup.new_tag("script", attrs={"src": "_static/doctools.js?v=9bcbadda"})
    )
    header.append(
        soup.new_tag("script", attrs={"src": "_static/sphinx_highlight.js?v=dc90522c"})
    )
    header.append(
        soup.new_tag(
            "link",
            attrs={
                "rel": "index",
                "title": "Index",
                "href": "genindex.html",
            },
        )
    )
    header.append(
        soup.new_tag(
            "link",
            attrs={
                "rel": "search",
                "title": "Search",
                "href": "search.html",
            },
        )
    )
    header.append(
        soup.new_tag(
            "link",
            attrs={
                "rel": "next",
                "title": "otld",
                "href": "_autosummary/otld.html",
            },
        )
    )
    header.append(
        soup.new_tag(
            "link",
            attrs={
                "rel": "stylesheet",
                "type": "text/css",
                "href": "_static/custom.css",
            },
        )
    )

    # Add body and divs
    main_tag = soup.new_tag("div", attrs={"class": "body", "role": "main"})
    body_wrapper = soup.new_tag("div", attrs={"class": "bodywrapper"})
    document_wrapper = soup.new_tag("div", attrs={"class": "documentwrapper"})
    document = soup.new_tag("div", attrs={"class": "document"})

    # Insert header
    new_soup.append(new_soup.new_tag("html"))
    html_tag = new_soup.find("html")
    html_tag.insert(0, new_soup.new_tag("body"))
    html_tag.insert(0, header)

    body_tag = new_soup.find("body")
    body_tag.insert(0, document)
    document.insert(0, document_wrapper)
    document_wrapper.insert(0, body_wrapper)
    body_wrapper.insert(0, main_tag)

    contents = soup.find("body").contents
    for content in contents:
        main_tag.append(content)

    # Update attributes of all tables
    tables = new_soup.find_all("table")
    for table in tables:
        table.attrs.update({"class": "longtable docutils align-default"})

    return new_soup


def add_nav_bar(file: str, soup: BeautifulSoup):
    # Load nav_bar
    handle = open(file, "r")
    nav_bar = BeautifulSoup(handle, "html.parser")
    handle.close()

    # Add to transformation documentation
    document = soup.find("div", class_="document")
    document.append(nav_bar)

    return soup


def write_soup(file: str, soup: BeautifulSoup):
    handle = open(file, "w", encoding="utf-8")
    handle.write(soup.prettify())
    handle.close()


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    doc_dir = os.path.join(current_dir, "..", "documentation")
    transformation_documentation = os.path.join(
        doc_dir, "build", "html", "TransformationDocumentation.html"
    )
    index = os.path.join(doc_dir, "build", "html", "index.html")
    nav_bar = os.path.join(doc_dir, "html", "nav_bar.html")
    soup = update_transformation_documentation(transformation_documentation)
    soup = add_nav_bar(nav_bar, soup)
    write_soup(transformation_documentation, soup)
    update_index(index)
