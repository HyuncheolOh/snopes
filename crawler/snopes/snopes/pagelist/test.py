import re

if __name__ == "__main__":
    data = "u\"\n\t\t\t\t\t\t\t\tCelebrities say the most outrageous things, especially when it comes to politics! Or do they?  Sometimes they do, and sometimes they don't.\t\t\t"
    print data
    
    print data.replace("u\"\n\t\t\t\t\t\t\t\t","").replace("\t\t\t'","")

    p = re.compile('\s*[a-zA-Z]')
    m = p.search(data)

    if m:
        print('Match found')
    else:
        print('Match not found')

    print(m.group())
