# OfficePlacementM7

Neural Network for classification of products in a workplace/shop by location with input from an RFID reader.

Each product has an rfid tag.

Each location has an Active RFID Tag.

The objective is to classify the products into different locatikons just by the rssi value read by the RFID reader along with the time stamp.


The above task is achieved by constructing a Neural Network and training it to identify the underlying patterns in the data and the classify it.


Operation steps of the Program:  

    1. Run the main program
    2. A pygame simulation will be generated
    3. Control the movement of the reader with the W,A,S,D keys
    4. Make sure to scan all the "green" dots. The green dots are the products and the rest are Active location tags.
    5. Wait for a few seconds for the model to predict and display the result.
    6. On display, a new pygame window will be created with the products classified represented by colour.

Note : Make sure to run the program in a GPU environment for faster performance


In Case there is a need to generate and train the model once again:

    1. Run and generate the data once again.
    2. Check for the Landmark.csv, Active_Landmark.csv, Products.csv files.
    3. Open the NN_training_testing ipy notebook.
    4. Change the path in the read_data() function to the location of the 3 files.
    5. Run the ipynb to train the model.
    6.Change the batcch size and epoch count according to the convenience.
    7.Save the trained model and re run the entire simulation with the new model.

Note: Run wih GPU for training since huge datasets will ne generated.
![Unsorted](https://github.com/JonathanCecil01/OfficePlacementM7/assets/82434403/ec4bde65-011f-421a-af83-27a4dcb81d74)
![Traversed_path](https://github.com/JonathanCecil01/OfficePlacementM7/assets/82434403/e4fda42d-5b3c-40a7-8ec3-ad2c92a8243e)
![Sorted_products](https://github.com/JonathanCecil01/OfficePlacementM7/assets/82434403/69648cf8-6e09-4855-b4a1-3a86194250ef)
