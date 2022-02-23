#Import modules
import snscrape.modules.twitter as sntwitter
import pandas as pd
import datetime as dt
from sklearn import feature_extraction, linear_model
import string 

#=================================================================================================

#Tweet Scraping
#Create variables for yesterday and today in date format
current_date = dt.datetime.now()
print("current date: ", current_date)
date_string = str(current_date)
date_today = date_string[:10]
day = date_today[-2:]
adjusted_date = str(date_today[:-2]) + "0" + str(int(day)+1) 
live_time = str(adjusted_date)
one_day_ago = str(date_today[:-2]) + "0" + str(int(day))

tweets = []

#Scrape tweets with the Bushfire keyword
for i,tweet in enumerate(sntwitter.TwitterSearchScraper('bushfire since:' + one_day_ago + ' until:' + live_time).get_items()):
    if i>999:
        break
    tweets.append([tweet.date, tweet.id, tweet.content])
    
# Creating a dataframe from the tweets list above
df = pd.DataFrame(tweets, columns=['Datetime', 'Tweet Id', 'Text'])
#Save tweets to a .csv file
df.to_csv(r"C:\Users\bbste\Documents\Coding\Python\Solution Challenge 2022\Tweets.csv")


#================================================================================================

#Natural Language Processing
#Note: 'predicted' means the target prediction is 1

#Transform training data to vectors
training_data = pd.read_csv(r"C:\Users\bbste\Documents\Coding\Python\Solution Challenge 2022\Inputted Target Dataset.csv")
count_vectorizer = feature_extraction.text.CountVectorizer()
train_vectors = count_vectorizer.fit_transform(training_data["Text"])

#Select model
clf = linear_model.RidgeClassifier()

#Fit training data
clf.fit(train_vectors, training_data["Target"])

scraped = pd.read_csv(r"C:\Users\bbste\Documents\Coding\Python\Solution Challenge 2022\Tweets.csv")
sample_tweets = scraped['Text']
tweet_vectors = count_vectorizer.transform(sample_tweets)

#Predict tweets and export to .csv file
df = pd.DataFrame()
df['Prediction'] = clf.predict(tweet_vectors)
df['Text'] = sample_tweets

#===============================================================================================

#Data handling and sorting

#Export dataframe to .csv file
nlp = df.to_csv(r"C:\Users\bbste\Documents\Coding\Python\Solution Challenge 2022\NLP.csv")

#Print number of tweets in last day
number_of_tweets = len(df['Prediction'])
print("Number of tweets: ", number_of_tweets)

#Calculate number of predicted tweets
Total = 0
for x in df['Prediction']:
    if x == 1:
        Total += 1
print("Number of predicted tweets: ", Total)
print("Percentage predicted: ", round((Total/number_of_tweets)*100, 1), "%")
      
#Get all Australian towns into a list  
towns = []
towns_df = pd.read_csv(r"C:\Users\bbste\Documents\Coding\Python\Solution Challenge 2022\Australian Towns.csv")

def AllTowns():
    for town in towns_df['Town'][:len(towns_df['Town'])]:
        towns.append(town.lower())

print(AllTowns())
#print(towns[-5:])  

#Create a list of all predicted tweets   
predicted = []

def PredictedTweets():
    for i in range(len(df['Prediction'])):
        if df['Prediction'][i] == 1:
            predicted.append(df['Text'][i])

print(PredictedTweets())
#print(PredictedTweets())
        
#Create a list of all towns mentioned in a predicted tweet
current_bushfires = []

def CurrentBushfire():   
    for i in range(len(predicted)):
        sentence = predicted[i]
        removed_punctuation = sentence.translate(str.maketrans('','',string.punctuation))
        words = str.split(removed_punctuation.lower())
        for x in words:
            if x in towns:
                current_bushfires.append(x)

print(CurrentBushfire())
#print(current_bushfires)

#Create a list of all regions of Australia
Regions = []
for region in towns_df['Region']:
    if region not in Regions:
        Regions.append(region)
        
print(Regions)

#Sort all towns into the region they are in
NSW = []
SA = []
NT = []
QLD = []
VIC = []
WA = []
TAS = []
ACT = []


def TownsToRegion():
    for i in range(len(towns_df['Region'])):
        x = towns_df['Region'][i]
        y = towns_df['Town'][i]
        if x == 'NSW':
            NSW.append(y.lower())
        elif x == 'SA':
            SA.append(y.lower())
        elif x == 'NT':
            NT.append(y.lower())
        elif x == 'QLD':
            QLD.append(y.lower())
        elif x == 'VIC':
            VIC.append(y.lower())
        elif x == 'WA':
            WA.append(y.lower())
        elif x == 'TAS':
            TAS.append(y.lower())
        else:
            ACT.append(y.lower())
                              
print(TownsToRegion())   

#Remove duplicates from current_bushfire
unique_bushfires = []
for x in current_bushfires:
    if x not in unique_bushfires:
        unique_bushfires.append(x)
        
print(unique_bushfires)
    
#Find the number of current bushfires in each region 
NSW_count = 0
SA_count = 0
NT_count = 0
QLD_count = 0
VIC_count = 0
WA_count = 0
TAS_count = 0
ACT_count = 0  

for x in unique_bushfires:
    if x in NSW:
        NSW_count += 1
    elif x in SA:
        SA_count += 1
    elif x in NT:
        NT_count += 1
    elif x in QLD:
        QLD_count += 1
    elif x in VIC:
        VIC_count += 1
    elif x in WA:
        WA_count += 1
    elif x in TAS:
        TAS_count += 1
    elif x in ACT:
        ACT_count += 1
    else:
        None
        
print(NSW_count, SA_count, NT_count, QLD_count, VIC_count, WA_count, TAS_count, ACT_count)
print(len(unique_bushfires))

#================================================================================================

#Data visualisation with a map


from geopy.geocoders import Nominatim
import folium


towns_df = pd.read_csv(r"C:\Users\bbste\Documents\Coding\Python\Solution Challenge 2022\Australian Towns.csv")
towns = towns_df['Town']

geolocator = Nominatim(user_agent="MyApp")

latitude = []
longitude = []
name = []

#print(towns[582])
#location = geolocator.geocode(towns[582])
#print(location.latitude, location.longitude)

for x in unique_bushfires:
    location = geolocator.geocode(x)
    latitude.append(location.latitude)
    longitude.append(location.longitude)
    name.append(x)
    
#Create a map of Australia
m = folium.Map(location=[-33, 133], zoom_start=4.4, width=1000, height=1000, control_scale=True)

#Add markers for each bushfire 
for i in range(len(unique_bushfires)):
    folium.Marker(
        location=[latitude[i], longitude[i]],
        icon=folium.Icon(icon = 'fire', color="red")    
).add_to(m)

m.save("Map.html")
