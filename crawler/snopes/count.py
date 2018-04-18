import json
import codecs


def s_c(num):
    num = num.replace("K", "000")
    num = num.replace("M", "000000")
    return num


if __name__ == "__main__":

    data1 = json.load(codecs.open('./share_count/201803092210.json', 'r', 'utf-8'))
    data2 = json.load(codecs.open('./share_count/201803112210.json', 'r', 'utf-8'))
    data3 = json.load(codecs.open('./share_count/201803121914.json', 'r', 'utf-8'))

    '''
    #insert value in dictionary
    d = {}
    r = {}
    for item in data1:
        d[item['post_id']] = int(s_c(item['share_count']))

    #compare with the day
    for item in data2:
        try :
           print(item['post_id'], item['url'], item['modified_date'])
           r[item['post_id']] = int(s_c(item['share_count'])) - d[item['post_id']]
        except KeyError:
            print("key error")

    #print 1 and 2 day gap
    print("gap")
    for key in r.keys():
       print(key, r[key])
#    data2 = json.load(codecs.open('201803112210.json', 'r', 'utf-8'))
   
    d = {}
    r = {}
    for item in data2:
        d[item['post_id']] = int(s_c(item['share_count']))

    
    for item in data3:
        try :
            print(item['post_id'], item['url'], item['modified_date'])
            r[item['post_id']] = int(s_c(item['share_count'])) - d[item['post_id']]
        except KeyError:
            print("key error")

    print("gap2")
    for key in r.keys():
        print(key, r[key])
    '''
    print("1")
    for item in data3:
        print(item['post_id'], item['published_date'])

