import os

from bs4 import BeautifulSoup

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    doc_dir = os.path.join(current_dir, "..", "documentation")
    handle = open(os.path.join(doc_dir, "build", "html", "index.html"), "r+")

    soup = BeautifulSoup(handle)
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
