# SpaceKnow-homework

SpaceKnow interview homework: first encounter with nippy Python. Oh, how I started to like that slimy lizard...
Please provide any comments, suggstions, improvements...

Howto:

1)  fill your SpaceKnow credentials in "input/credentials.json"
2)  use / define * the data (provider (atm works only gbdx), dataset(atm works only idaho-pansharpened), time period) and Area of Interest in "input/ "dataset.json", "area_of_interest.json"
*)  if desired, path to inputs (credentials,dataset,area of interest) can be changed in "declarations.py" 

Status:
- Downloads available data for map_type cars and imagery at a default zoom (resolution)
- Counts the cars in the specified time period and AoI, sum and average per image(mapId)
- stitches the tiles from 2x2 images
- combines imagery (truecolor.png) with analysis .png (cars.png) into masked result.

Issues:
- Downloads only images with default resolution as specified in response tile from "POST /kraken/release/{map_type}/geojson/retrieve", no zoom available.
- Image stitching and combining works only if 2x2 tiles are available and of the same resolution

TODOs:
- rework Tile download to asynchronous, currently slow synchronous.
- simplyfy json + dictionary handling. 
- let user input the parameters at runtime? if deemed necessary


