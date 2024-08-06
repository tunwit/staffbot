fram = 0
score = 0
while fram < 10:
    fram += 1
    times = 0
    while times < 2:
        times += 1
        print(f"Frame # {fram}")
        if times == 1:
            down = int(input("  Number of pins down: "))
        else:
            down = int(input(f"  Number of pins down (0-{10-down}): "))
        if (times == 1 and down == 10):
            score += 10
            break
        else:
            score += down
        print(score)
print(f"Total score is {score}")