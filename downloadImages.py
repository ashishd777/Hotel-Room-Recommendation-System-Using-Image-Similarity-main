from pandas import *
import urllib.request

# retrieving image links
data = read_csv("listings.csv")
images = data['picture_url'].tolist()

# for all image links, fetch image using urllib and save in images folder
for i in range(1000, 1500):
    loc = "static/images" + images[i][images[i].rfind('/'):]
    urllib.request.urlretrieve(images[i], loc)
    print(i + 1, "/ 2625: " + loc)
