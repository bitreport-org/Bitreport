import Bitfinex_API as ba
import numpy as np
import talib
import matplotlib.pyplot as plt

# To view the EliottWave phenomenon right angle is needed
# When directional movement price makes
# And data travels from bottom left to top right (or vice versa)
# Then it should oscillate around diagonal of a perfect square
#
# Define sqrx as length of this square'side
# Define x as distance between two data points -> x = sqrx / [number of points in suare]
#
# Input: [a,b,c,d], x
# Output: Boolean
# Remarks: https://docs.google.com/document/d/1PkmYe0vZet1nEmpcFGOMe5YFgDD0w9EdbP65lcdegAI/edit?usp=sharing
def RuleOfNeutrality(L, x=1):
    a = L[0]
    b = L[1]
    c = L[2]
    d = L[3]

    value = False
    y = a-b
    tgv = y/x

    if (0 <=  tgv <= 1 and c > b) or (-1 <=  tgv <= 0 and c < b) :
        value = True

    if value == True:
        if a >= b > c and d > a:
            return False
        elif a <= b < c and d < a:
            return False

    return value


#print(RuleOfNeutrality([5,9/2, 2, 7]))


class MonoWave:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.sub = [[a,b]]



# m1 = [a, b] is a starting monovawe
# wave is i a list of point followin b : [c,d,...]
def CreateMonoWave(m1, wave):
    start = m1.b
    end = wave[0]
    sub = []

    i=0
    last_end = start
    last_start = m1.a

    while True:
        if i < len(wave):
            if m1.a < wave[i] < m1.b:
                sub.append([last_end, wave[i]])
                last_start = last_end
                last_end=wave[i]
                end = wave[i]
            elif len(sub) > 1 and wave[i] > max(m1.a, m1.b) and wave[i] > last_start:
                sub.append([last_end, wave[i]])
                end = wave[i]
                break
            elif len(sub) > 1 and wave[i] < min(m1.a, m1.b) and wave[i] < last_start:
                sub.append([last_end, wave[i]])
                end = wave[i]
                break
            i += 1

    if sub == []:
        sub.append([start, end])

    if len(sub) % 2 == 0:
        end= sub[-1][0]
        sub.pop()


    mono = MonoWave(start, end)
    mono.sub = sub
    return mono


# class Wave:
#     # m1 = [a, b] is a starting monovawe
#     # wave is i a list of point followin b : [c,d,...]
#     def __init__(self, m1, wave):
#         start = m1.b
#         end = wave[0]
#         sub = []
#
#
#         i=0
#         last_end = start
#
#         while True:
#             if m1.a < wave[i] < m1.b:
#                 sub.append([last_end, wave[i]])
#                 last_end=wave[i]
#                 end = wave[i]
#             elif wave[i] > max(m1.a, m1.b) or wave[i] < min(m1.a, m1.b):
#                 break
#             i+=1
#
#         if sub == []:
#             sub.append([start, end])
#
#         if len(sub) % 2 == 0:
#             end= sub[-1][0]
#             sub.pop()
#
#
#         self.mono = [start, end]
#         self.sub = sub


# Example

m1 = MonoWave(12,15)
print(m1.sub)
x = CreateMonoWave(m1, [15,13,14,13.5, 14, 16])

print(x.a, x.b, x.sub)




