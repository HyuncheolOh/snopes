def make_page_list():
    f = open('../../pagecount.txt', 'r')
    pagecount = f.readline()
    page_url = "https://www.snopes.com/category/facts/page/"
    url_list = []
    url_file = open('url_list.txt', 'w')
    for i in range(2, int(pagecount)+1):
        url_list.append(page_url + str(i)+'/')
        url_file.write(page_url+str(i)+'/\n')
        


if  __name__ == "__main__":
    make_page_list()
