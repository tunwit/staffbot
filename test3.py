hours = int(input('Enter number of hours: '))
minutes = int(input('Enter number of minutes: '))
buyAmt = int(input('Enter shopping amount: '))
total_minute = hours *60 + minutes
if hours > 20 or hours < 0:
    print("Invalid time.")
elif minutes > 59 or minutes < 0:
    print("Invalid time.")
elif total_minute > 1200:
    print("Invalid time.")
else:
    free = 2
    if buyAmt >= 300 and buyAmt <=3000:
        free =4
    cost = 0
    counter = 1
    while total_minute >  0:
        if buyAmt > 3000:
            break
        if counter <= free:
            total_minute = total_minute - 60
            counter += 1
            continue
        elif counter >= 5:
            cost += 50
        else:
            cost += 20
        total_minute = total_minute - 60
        counter += 1

    if cost:
        print(f"Total amount due is {cost} Baht, thank you.")
    else:
        print("No charge, thank you.")





