#this is the example to predict the salary based on the expere+ience 
#  this is a linear regression model here weren't using matplotlib 
'''import numpy as np
from sklearn.linear_model import LinearRegression 

experience = [1, 2, 3, 4, 5, 6]
salary = [15000, 18000, 25000, 30000, 38000, 45000]

x=np.array(experience).reshape(-1,1)
y=np.array(salary)

model=LinearRegression()
model.fit(x,y)
new_exp=4.5
print(model.predict([[new_exp]]))'''

#or if we need in the form of graph we can use matplotlib 
# for house rent predictions example 
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

house_size=[800,900,1000,1200,1300]
house_rent=[10000,12000,15000,18000,22000]

x=np.array(house_size).reshape(-1,1)
y=np.array(house_rent)

model=LinearRegression()
model.fit(x,y)

new_house_size=1000
new_house_rent=model.predict([[new_house_size]])

print("House size:", new_house_size)
print("Predicted rent:", new_house_rent[0])

plt.figure(figsize=(10,6))   
plt.scatter(house_size,house_rent,label="actual values",s=100,color="red")
plt.plot(house_size,model.predict(x),label="predicted data",linewidth=2)
plt.scatter(new_house_size,new_house_rent,label="our prediction",color="green",marker="o")
plt.xlabel("house size in sqft",fontsize=12)
plt.ylabel("house rent",fontsize=12)
plt.title("house rents in cities",fontsize=14)
plt.legend()
plt.grid(True,alpha=0.2)
plt.savefig("house_predictions.png",dpi=150,bbox_inches="tight")
plt.show()

print("Image saved as house_predictions.png")


