import os
import cv2
from termcolor import \
    colored  # https://pypi.org/project/termcolor/ # print(colored("XXX", color='magenta', on_color='on_green'))

from utilities import read_json


class Processing:
    def __init__(self, path_RESULTS):
        self.path_RESULTS = path_RESULTS
        print(colored("Image processing object created:", color='white', attrs=['bold']))

    def count_cars(self):
        print(colored("Cars counting started", color='blue'))

        cars = []
        nof_maps = 0
        for dirName, subdirList, fileList in os.walk(self.path_RESULTS):
            if 'mapId_0' in subdirList:
                nof_maps = len(subdirList)
            if 'detections.geojson' in fileList:
                cars_in_tile = 0
                detection = read_json(dirName+'/'+'detections.geojson')
                for idx in range(len((detection['features']))):
                    props = dict(detection['features'][idx]["properties"])
                    if props.get('class') and 'cars' in props.values():
                        cars_in_tile += int(props['count'])

                cars.append(cars_in_tile)

        print(colored("Total # of cars counted in the desired period: {}".format(sum(cars)),
                      color='magenta', on_color='on_white', attrs=['bold']))
        print(colored("counted in {} maps, resulting in {} of cars in average.".format(nof_maps, sum(cars)/nof_maps),
                      color='magenta', on_color='on_white', attrs=['bold']))

    def stitch_images(self, whattostitch):
        print(colored("Image stitching started: {}".format(whattostitch), color='blue'))
        for dirName, subdirList, fileList in os.walk(self.path_RESULTS):
            if 'tile_list.json' in fileList:
                tile_list = read_json(dirName + '/tile_list.json')
                self.just_stitch_them(tile_list, dirName, whattostitch)
        print(colored("Image stitching completed", color='green'))

    def just_stitch_them(self, tile_list, dirName, whattostitch):
        try:
            tile_list.sort()
            p_imLT = dirName+'/'+str(tile_list[0][0])+'_'+str(tile_list[0][1])+'/raster/'+whattostitch
            p_imLB = dirName+'/'+str(tile_list[1][0])+'_'+str(tile_list[1][1])+'/raster/'+whattostitch
            p_imRT = dirName+'/'+str(tile_list[2][0])+'_'+str(tile_list[2][1])+'/raster/'+whattostitch
            p_imRB = dirName+'/'+str(tile_list[3][0])+'_'+str(tile_list[3][1])+'/raster/'+whattostitch

            if os.path.exists(p_imLT) and os.path.exists(p_imLB) and os.path.exists(p_imRT) and os.path.exists(p_imRB):
                imLT = cv2.imread(p_imLT, cv2.IMREAD_COLOR)
                imLB = cv2.imread(p_imLB, cv2.IMREAD_COLOR)
                imRT = cv2.imread(p_imRT, cv2.IMREAD_COLOR)
                imRB = cv2.imread(p_imRB, cv2.IMREAD_COLOR)
                imL = cv2.vconcat([imLT, imLB])
                imR = cv2.vconcat([imRT, imRB])
                im2x2= cv2.hconcat([imL, imR])
                cv2.imwrite(dirName+'/'+whattostitch, im2x2)
        except Exception as e:
                    print(e)

    def combine_imgs(self, path_img_truecolor, path_img_cars):
        print(colored("background and mask combining started", color='blue'))
        if os.path.exists(path_img_truecolor) and os.path.exists(path_img_cars):

            subfoldersTruecolor = [f.path for f in os.scandir(path_img_truecolor) if f.is_dir()]
            subfoldersCars = [f.path for f in os.scandir(path_img_cars) if f.is_dir()]

            for subTrue, subCar in zip(subfoldersTruecolor, subfoldersCars):
                try:
                    imTruecolor = cv2.imread(subTrue+'/truecolor.png', cv2.IMREAD_COLOR)
                    imCars = cv2.imread(subCar+'/cars.png', cv2.IMREAD_COLOR)
                    imCombine = cv2.addWeighted(imTruecolor, 1, imCars, 2, 0)
                    cv2.imwrite(subCar + '/combined.png', imCombine)
                    print(colored("Combined image saved to: {}".format(subCar + '/combined.png'), color='green'))
                except Exception as e:
                    print(e)



if __name__ == "__main__":

    from utilities import set_output_path
    print("Processing runned independently")

    # In order to run you must have valid Token and Kraken data in the files,
    # run authorization.py + ragnar.py + kraken.py separately or run main.py

    path_RESULTS = set_output_path()
    process = Processing(path_RESULTS)
    process.count_cars()
    process.stitch_images('cars.png')
    process.stitch_images('truecolor.png')
    process.combine_imgs(path_RESULTS+"imagery",path_RESULTS+"cars")


