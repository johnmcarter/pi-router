## Seam Carving Project - Spring 2020  
#### CS 583 Computer Vision  
#### Jocelyn Rego & John Carter  


To run this implementation, download or clone this repository. To install the required dependencies, run 
```
pip3 install -r requirements.txt
```
in the same directory on the command line. To then run the code and launch the web GUI, run 
```
python3 app.py
```
in the local directory on the command line. Then go to http://127.0.0.1:5000/ on a web browser with app.py still running, and use the application. On the GUI, choose an image you have locally, specify the number of horizontal and vertical seams to either add or subtract as integers, and click "Seam it." When the calculation is finished, another page will open displaying the original image, the result after seam carving, and a visualization of where the seams were either added or subtracted. The result image and visualization will also be saved locally in the static directory, which is in the main directory. Some examples of images we tested and used in our write-up are stored in that directory as well and can be used as examples.

Notes:
- It is sometimes necessary to clear your browser cache if the same image is seam carved multiple times with a different number of seams. The correct image will be saved to the static directory, but a previous iteration of the image can be displayed on the result page if it is cached.
