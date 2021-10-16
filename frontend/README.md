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





