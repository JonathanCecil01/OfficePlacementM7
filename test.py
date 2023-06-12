product_time_dict = {}
max_time = 2500
i = 0
j = 500
while True:
    product_time_dict[i] = {}
    #print(max_time/j)
    if int(max_time/j)>0:
        j+=500
        i+=1
    else:
        break
    
print(product_time_dict.keys()) 