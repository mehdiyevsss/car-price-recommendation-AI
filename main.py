import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

import pandas as pd
import numpy as np

# import sklearn
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

matplotlib.use('Qt5Agg') # although PyQt6

# PyQt6!
from PyQt6 import QtGui
# from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QApplication,
    QWidget, QMessageBox, QCheckBox,
    QDial,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QComboBox)

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QCoreApplication, Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

apptitle = 'Munich rent index'
cardata = []
predictedPrice = 224722.57

minyear = 2010
maxyear = 2022 

# global functions

# function, that creates a string
# and returns the first 4 chars
def first4chars(x):
    x = str(x)
    return x[:4]

# from Geron example
# extra code – code to save the figures as high-res PNGs for the book
IMAGES_PATH = Path() / "images" 
IMAGES_PATH.mkdir(parents=True, exist_ok=True)
def save_fig(fig, fig_id, tight_layout=True, fig_extension="png", resolution=300):
    path = IMAGES_PATH / f"{fig_id}.{fig_extension}"
    # added by UG, see https://mldoodles.com/matplotlib-saves-blank-plot/
    # https://pythonguides.com/matplotlib-savefig-blank-image/
    # https://stackabuse.com/save-plot-as-image-with-matplotlib/
    # fig, ax = plt.subplots()
    if tight_layout:
        fig.tight_layout()
    fig.savefig(path, format=fig_extension, dpi=resolution) # ax=self.sc.axes, 


# Classes

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        super(MplCanvas, self).__init__(self.figure)

class SecondWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # use global data
        global cardata
        
        wid = QWidget()
        # Vertical Layout
        layout2 = QVBoxLayout()
        # Create a new Canvas
        self.sc2 = MplCanvas(self, width=5, height=4, dpi=100)
        # https://stackoverflow.com/questions/32371571/gridspec-of-multiple-subplots-the-figure-containing-the-passed-axes-is-being-cl
        cardata.hist(ax=self.sc2.axes)
        save_fig(self.sc2.figure,"histogram", tight_layout=True, fig_extension="png", resolution=300)  # extra code
        layout2.addWidget(self.sc2)
        self.setCentralWidget(wid)
        wid.setLayout(layout2)
   

class Window(QMainWindow):

    def __init__(self):
      super().__init__()
      self.loadData()
      self.initUI()

    def loadData(self):
        global cardata
        
        self.cardata = pd.read_csv('car_prices_dataset.csv', delimiter=',')
        # take cols 1-7 (without index)
        X2 = self.cardata.loc[:,["year","num_doors","num_seats"]]
        # X2 must be converted to array
        # https://stackoverflow.com/questions/69326639/sklearn-warning-valid-feature-names-in-version-1-0
        X2 = X2.values
        Y2 = self.cardata[["price"]]
        Y2 = Y2.values
        print("self.rentdata.head(8):")
        print(self.cardata.head(8))
        print("self.rentdata.info():")
        self.cardata.info()
        print("self.rentdata.describe():")
        print(self.cardata.describe())
        print("rentdata.corr():")
        corr_matrix = self.cardata.corr()
        print(corr_matrix)
        
        # assign to global variable
        cardata = self.cardata
        
        # Split the targets into training/testing sets
        # diabetes_y_train = diabetes_y[:-20]
        # diabetes_y_test = diabetes_y[-20:]
        X_train = X2[:-20]
        X_test = X2[-20:]
        Y_train = Y2[:-20]
        Y_test = Y2[-20:]
        
        # Create linear regression object
        self.regr = linear_model.LinearRegression()

        # Train the model using the training sets
        self.regr.fit(X_train, Y_train)

        # Make predictions using the testing set
        Y_pred = self.regr.predict(X_test)
        self.test_y = Y_test

        # The coefficients
        print("Coefficients: \n", self.regr.coef_) 
        # The mean squared error
        # print("Mean squared error: %.2f" % mean_squared_error(diabetes_y_test, diabetes_y_pred))
        print("Mean squared error: %.2f" % mean_squared_error(self.test_y, Y_pred))
        # The coefficient of determination: 1 is perfect prediction
        # print("Coefficient of determination: %.2f" % r2_score(diabetes_y_test, diabetes_y_pred))
        print("Coefficient of determination: %.2f" % r2_score(self.test_y, Y_pred))

    def show_second_window(self):
        if self.w2.isHidden(): 
            self.w2.show()
    
    def initUI(self):
      global minyear
      global maxyear
      global predictedPrice
      
      print("initUI")
      try:
        self.w2 = SecondWindow()
        # set Appilcation default styles
        font = QtGui.QFont("Sanserif", 12)
        # font.setStyleHint(QtGui.QFont.)
        QApplication.setFont(QtGui.QFont(font))
        QApplication.setWindowIcon(QtGui.QIcon('application-document.png'))
        
        # grid layout
        layout = QGridLayout()

        
        # Slider
        self.tsl = QSlider(Qt.Orientation.Horizontal)
        self.tsl.setMinimum(minyear) # min bjahr
        self.tsl.setMaximum(maxyear) # max bjahr
        self.tsl.valueChanged.connect(self.updateSelectedYear)
        layout.addWidget(self.tsl, 0,1)
        
     
        # in 2nd cell of 2nd row we use a Horizontal Layout for the 2 labels
        layout2 = QHBoxLayout()
        widget2 = QWidget()
        self.minYear = QLabel(self)
        self.maxYear = QLabel(self)
        self.selectedYear = QLabel(self)
        self.selectedYear.setStyleSheet("QLabel {color: red}")
        self.minYear.setText("Building Year from: " + str(minyear) + " (select with Slider)")
        self.maxYear.setText("           to: " + str(maxyear))
        self.selectedYear.setText(str(minyear))
        layout2.addWidget(self.minYear)
        layout2.addWidget(self.selectedYear)
        layout2.addWidget(self.maxYear)
        widget2.setLayout(layout2)
        layout.addWidget(widget2, 1, 1)
        
        # 3rd row of GridLayout
        # self.lab2.setFont(QtGui.QFont("Sanserif", 15))
        # Stack layout for labels in Grid cell 1,0
        layout3 = QVBoxLayout()
        widget3 = QWidget()

        # Replace the checkbox creation code with combobox creation
        # num_doors combobox
        labelNumDoors = QLabel()
        labelNumDoors.setText("Number of Doors: ")
        layout3.addWidget(labelNumDoors)

        self.cbNumDoors = QComboBox(self)
        self.cbNumDoors.addItem("2")  # Example values, replace with your data
        self.cbNumDoors.addItem("4")
        
        self.cbNumDoors.setPlaceholderText("Number of Doors")
        layout3.addWidget(self.cbNumDoors)


        labelNumSeats = QLabel()
        labelNumSeats.setText("Number of Seats: ")
        layout3.addWidget(labelNumSeats)
        # num_seats combobox
        self.cbNumSeats = QComboBox(self)
        self.cbNumSeats.addItem("2")  # Example values, replace with your data
        self.cbNumSeats.addItem("5")
        self.cbNumSeats.setPlaceholderText("Number of Seats")
        layout3.addWidget(self.cbNumSeats)

        btn = QPushButton("Predict", self)
        btn.setToolTip("Show Prediction")
        btn.clicked.connect(self.showPrediction)
        layout3.addWidget(btn)

        self.labPrediction = QLabel(self)
        self.labPrediction.setText("Predicted rent: " + str(predictedPrice))
        layout3.addWidget(self.labPrediction)

        widget3.setLayout(layout3)
        layout.addWidget(widget3, 2, 0)
        
        
        # Canvas for plot
        # https://stackoverflow.com/questions/67590023/embedding-dataframe-plot-on-figure-canvas
        # https://matplotlib.org/3.2.2/gallery/misc/plotfile_demo_sgskip.html
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.plot_price(1970,predictedPrice)
        
        self.sc.setMinimumWidth(100)
        layout.addWidget(self.sc, 2,1)
        
        widget = QWidget()
        widget.setLayout(layout)
        
        # Menu
        # First action - Show Historgrams Window
        button_action1 = QAction(QIcon("application-block.png"), "&Histogram", self)
        button_action1.setStatusTip("Show histograms of data")
        button_action1.triggered.connect(self.show_second_window)
        # Second action
        button_action2 = QAction(QIcon("store.png"), "&Save Prediction Image", self)
        button_action2.setStatusTip("Save Image")
        button_action2.triggered.connect(self.sClick)
        button_action2.setCheckable(True)
         # Third action
        button_action3 = QAction(QIcon("external.png"), "&Close", self)
        button_action3.setStatusTip("Close Application")
        button_action3.triggered.connect(self.closeEvent)
        button_action3.setCheckable(True)
        # Menubar
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action1)
        file_menu.addAction(button_action2)
        file_menu.addAction(button_action3)
        
        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)
        self.setWindowTitle(apptitle) # apptitle global var 
        self.setGeometry(30, 30, 700, 550)
        self.show()
        return True
      except Exception as e:
        print(f"Error while initializing the User Interface: {e}")
        sys.exit()


    # function to print rent against year
    # when year and rent are set, a marker is set in the plot
    def plot_price(self, year=None, price=None):
        global cardata
        # clear canvas
        self.sc.axes.cla()
        # attributes = ["mieteqm", "bjahr"] # , "flaeche", "bjahr"
        # self.df = rentdata[attributes]
        # See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy     
        self.df = cardata.loc[:, ('price', 'year')]
        # plot the pandas DataFrame, passing in the
        # matplotlib Canvas axes.
        # https://stackoverflow.com/questions/37787698/how-to-sort-pandas-dataframe-from-one-column
        # SettingWithCopyWarning:
        # A value is trying to be set on a copy of a slice from a DataFrame
        #      c:\Users\ugarmann\Documents\python-projekte\sas-ws-22-23-1\main.py:261: SettingWithCopyWarning: 
        # A value is trying to be set on a copy of a slice from a DataFrame
        
        self.df.sort_values(by=['year'], inplace=True)
        self.df.reset_index(drop = True, inplace = True)
        # self.df.sort_index(inplace=True)
        print("Min year: %s" % self.df['year'].min())
        print("Max year: %s" % self.df['year'].max())
        print(self.df.head(8))
        # https://pandas.pydata.org/docs/getting_started/intro_tutorials/04_plotting.html
        # https://www.tutorialspoint.com/python_pandas/python_pandas_visualization.htm
        self.df.set_index('year').plot(ax=self.sc.axes) # , columns=self.rentdata["bjahr"]
        
        self.sc.axes.plot(year, price, marker="*", markersize=5, c='red')
        save_fig(self.sc.figure, "prediction_plot", tight_layout=True, fig_extension="png", resolution=300)  # extra code
        
        self.sc.draw()

    def updateSelectedYear(self):
        val = self.tsl.value()
        self.selectedYear.setText(str(val))
        print(val)
        
   
        
        # self.sc.axes.cla() # not clear()
        # self.sc.axes.plot([0,1,2,3,4], [val,1,20,3,val]) # r? is color
        # self.sc.draw()
    
        
    def sClick(self, event):
        save_fig(self.sc.figure, "prediction_plot")
        
    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.

        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(
            self, "Message",
            "Are you sure you want to quit? Any unsaved work will be lost.",
            # QMessageBox.StandardButton since PyQt6
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Cancel)

        if (reply == QMessageBox.StandardButton.Close)  : 
            print("Close Event reply close")
            sys.exit()        
        else:
            if (reply == QMessageBox.StandardButton.Save): 
                save_fig(self.sc.figure, "prediction_plot")
                sys.exit()
            else:
                print("Cancel Closing")
                if not type(event) == bool:
                    event.ignore()
        
    def showPrediction(self):
        global predictedPrice
        y = self.tsl.value()
        k = int(self.cbNumDoors.currentText())  # Convert selected text to int
        
        h = int(self.cbNumSeats.currentText())  # Convert selected text to int
        X_test = [[y, k, h]]
        predictedPrice = round(self.regr.predict(X_test)[0][0], 2)
        print(type(predictedPrice))
        print("Predicted rent: %.2f" % predictedPrice)
        self.labPrediction.setText("Predicted rent: " + str(predictedPrice))
        self.plot_price(year=y, price=predictedPrice)

# main
if __name__ == '__main__':
  app = QApplication(sys.argv)
  w = Window() # show is called in initUI()
  sys.exit(app.exec()) # exec_ only with PyQt5
