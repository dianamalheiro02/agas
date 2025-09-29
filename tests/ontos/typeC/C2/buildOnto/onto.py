from bs4 import BeautifulSoup
import requests
import json

def extrair_books(html):
    book_dict = {}

    soup = BeautifulSoup(html, 'html.parser')

    # Each book listing is inside a div with class "searchresult title book-details"
    common_parent = soup.find_all("div", class_="col-sm-24")
    #print(common_parent)
    print(f"Found {len(common_parent)} book entries")  # DEBUGGING LINE

    for div in common_parent:
        # Extract title
        div_title = div.find("h4", class_="tlc")
        title = div_title.a.text.strip() if div_title and div_title.a else "Unknown Title"
        
        # Extract author
        author_element = div.find("p")
        print(author_element)
        author = author_element.text.strip() if author_element else "Unknown Author"

        # Extract description
        div_sub = div.find("p", class_="book-description")
        sub = div_sub.text.strip() if div_sub else "No Description"

        #print(title)
        #print(author)
        #print(sub)
        print("------------------")

        book_dict[title] = f"{author}; {sub}"

    return book_dict
    


final_dict = {}
url_main = "https://www.free-ebooks.net/book-list/self-improvement-and-motivation"


response = requests.get(url_main)

html = response.text
book_dict = extrair_books(html)
final_dict.update(book_dict)

# Save to JSON
with open("bookAll2.json", "w", encoding="utf-8") as f_out:
    json.dump(final_dict, f_out, indent=4, ensure_ascii=False)

print("Scraping complete! Data saved to bookAll1.json")
