import requests
from bs4 import BeautifulSoup
import folium
import pandas
import io
import json

r = requests.get("http://pythonhow.com/real-estate/rock-springs-wy/LCWYROCKSPRINGS/")
c = r.content

soup = BeautifulSoup(c,"html.parser")

all = soup.find_all("div",{"class":"propertyRow"})

all[0].find("h4",{"class":"propPrice"}).text.encode('utf-8').replace("\n","").replace(" ","")

page_nr=soup.find_all("a",{"class":"Page"})[-1].text


l = []
base_url = "http://pythonhow.com/real-estate/rock-springs-wy/LCWYROCKSPRINGS/t=0&s="
for page in range(0,int(page_nr)*10,10):
    print(base_url+str(page)+".html")
    r = requests.get(base_url+str(page)+".html")
    c = r.content
    soup = BeautifulSoup(c,"html.parser")
    all = soup.find_all("div",{"class":"propertyRow"})
    
    for item in all:
        d = {}
        d["location"]=item.find_all("span",{"class","propAddressCollapse"})[0].text.encode('utf-8')+item.find_all("span",{"class","propAddressCollapse"})[1].text.encode('utf-8')
        d["Price"]=item.find("h4",{"class":"propPrice"}).text.encode('utf-8').replace("\n","").replace(" ","")
             
        l.append(d)

df = pandas.DataFrame(l)
df.to_csv("Output.txt")

data = pandas.read_csv("Output.txt")

address = list(data["location"])
price = list(data["Price"])

latlist = []
lnglist = []
base_url1 = "https://maps.googleapis.com/maps/api/geocode/json?address="
for index in range(len(address)):
    r1 = requests.get(base_url1+address[index].replace(" ","+")+"&key=AIzaSyDhp9OZnv0n8U8Aw8gd_KjbSMclKwijj-A")
    c1 = r1.content
    array = json.loads(c1)
    try:
        lat = array["results"][0]['geometry']['location']['lat']
        lng = array["results"][0]['geometry']['location']['lng']
    except:
        pass
    latlist.append(lat)
    lnglist.append(lng)


map = folium.Map(location = [38.58,-99.09],zoom_start = 10, tiles='Mapbox Bright')

fgv = folium.FeatureGroup(name = "House")

for lt,ln,pr,adr in zip(latlist,lnglist,price,address):
    fgv.add_child(folium.Marker(location=[lt,ln], popup=str(pr) , icon = folium.Icon(color="red")))

fgp = folium.FeatureGroup(name = "Population")

fgp.add_child(folium.GeoJson(data =(io.open('world.json', 'r', encoding = 'utf-8-sig').read()), 
style_function=lambda x:{'fillColor':'green' if x['properties']['POP2005'] < 1000000 
else 'orange' if x['properties']['POP2005'] < 2000000 else 'red'}))


map.add_child(fgv)
map.add_child(fgp)
map.add_child(folium.LayerControl()) 

map.save("Map1.html")