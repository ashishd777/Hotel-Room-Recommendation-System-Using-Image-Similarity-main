# DEMO BUILD OF APPLICATION FOR REVIEW 2
import numpy as np
import pandas as pd
import PIL as Image
import cv2
from DeepImageSearch import LoadData, SearchImage

# load the dataset and image names
image_list = LoadData().from_folder(folder_list=['images'])
data = pd.read_csv("listings.csv")
name_list = data['name'].tolist()
desc_list = data['description'].tolist()
cap_list = data['accommodates'].tolist()
book_list = data['listing_url'].tolist()
price_list = data['price'].tolist()
tag_list = data['amenities'].tolist()
rating_list = data['review_scores_rating'].tolist()

# take image input
print("CSE3013 Artificial Intelligence Project Review 2")
print("Title: Hotel Room Recommendation System Using Image Similarity")
print("Team Members:\n19BCI0001: Dayeem Parkar\n19BCI0036: Akashdeep\n19BCE0891: Anmol")
ipImg = input("\nEnter filename: ")
matches = int(input("Enter number of desired recommendations: "))

# find best matches
result = SearchImage().get_similar_images("images/" + ipImg, number_of_images=matches)

print("\nBest room matches are: ")
counter, images = 1, []
for key in result.keys():
    print("\n" + str(counter) + ". " + '\033[1m' + "Name: " + name_list[key] + '\033[0m')
    print("Book Room: " + book_list[key])
    print("Room for:", cap_list[key])
    print("Price: " + price_list[key])
    print(desc_list[key])
    print("Rating:", rating_list[key])
    print("Tags: " + tag_list[key])
    print("Debug: Img Name =", result[key])
    counter += 1
