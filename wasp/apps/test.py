import math

hand_shape = [(0, 10, 2, 5)]  # initial, final, xresolution, width

hand = []
for i in hand_shape:
    for y in range(i[3]):
        y = y-i[3]//2-i[3] % 2 + 1
        hand +=[[x, y] for x in range(i[0], i[1], i[2])]

print(hand)


def _draw_hand(time, dial_number, x_center, y_center, hand, color=0xffff):
    new_hand = []
    angle = 360 / dial_number * time - 90
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))
    for pix in hand:
        u = int(pix[0] * cos + pix[1] * sin)
        v = int(pix[1] * cos - pix[0] * sin)
        new_hand.append([u,v])
    print(new_hand)




_draw_hand(6, 60, 120, 120, hand, 0x27E0)

