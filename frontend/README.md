## 1.  Frontend - Gameplay  Record

Here we are going to create a program that will record the the keyboard and mouse and screen during your gameplay.

First we will need create a new environment to perform our program.

First you need to install anaconda at this [link](https://www.anaconda.com/products/individual)

<img src="../assets/images/posts/README/1-16336103937251.jpg" alt="img" style="zoom:50%;" />

then in the command prompt terminal we type

```
conda create -n game   python==3.7 findspark tensorflow pytorch jupyterlab
```

I will use **Tensorflow** + **Pytorch** + **Spark** as the  main frameworks for future work, and this time I will use JupyterLab 

```
conda game activate
```

then in your terminal type the following commands:

```
conda install ipykernel
python -m ipykernel install --user --name game --display-name "Python (game)"
```



Installing libraries needed for the frontend

```
pip install pynput numpy pyautogui opencv-python
```

then open the jupyterlab with the command

```
jupyter lab
```



## Requirements of the images gameplay (v.01)

The pictures of the gameplay should be  with the following requirements;



Dimensions: **320x160**, 

Width: **320 pixels**

Height **160 pixels**

Horizontal resolution:**96dpi**

Vertical resolution: **96 dpi**

Bith depth: **24**

Format: **JPG**



The screenshots should be saved in the directory **IMG**:

C:\IMG\gameplay_2021_10_17_12_15_37_666.jpg

C:\IMG\gameplay_2021_10_17_12_15_37_771.jpg

 C:\IMG\gameplay_2021_10_17_12_15_37_876.jpg

.

.

.

C:\IMG\right_2021_10_17_12_15_45_810.jpg

### Requirements of the gaming_log.csv (v.01)

The log file  should be saved in the directory **LOG**:

The csv file  should include









C:\IMG\right_2021_10_17_12_15_37_666.jpg, 0, 0, 0, 7.874666E-05

 C:\IMG\right_2021_10_17_12_15_37_771.jpg, 0, 0, 0, 7.789639E-05

 C:\IMG\right_2021_10_17_12_15_37_876.jpg, 0, 0, 0, 7.820319E-05

.

.

.

C:\IMG\right_2021_10_17_12_15_45_810.jpg, 0, 0, 0, 7.792677E-05
