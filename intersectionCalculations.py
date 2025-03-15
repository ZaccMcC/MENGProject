from line import Line
from plane import Plane
import numpy as np

def direction_vectors(array1, array2):
    check_direction = np.multiply(array1, array2)
    check_direction = np.sum(check_direction)

    return check_direction


def parametric_equation(np, na, nu):
    return (np - na)/nu


def calculate_intersection(line, t):
    x = line.direction[0] * t + line.position[0]
    y = line.direction[1] * t + line.position[1]
    z = line.direction[2] * t + line.position[2]

    #coordinates = (x,y,z)
    coordinates = np.array([x,y,z])
    return coordinates

def intersection_wrapper(sensorPlane, line1):
    nU = direction_vectors(sensorPlane.direction, line1.direction)


    if nU > 0:
        #print(nU)
        nA = direction_vectors(sensorPlane.direction, line1.position)
        nP = direction_vectors(sensorPlane.direction, sensorPlane.position)

        #print(nA)
        #print(nP)
        x = parametric_equation(nP, nA, nU)
        IntersectionCoordinates = calculate_intersection(line1, x)
        # print("Intersection occurs at " + str(IntersectionCoordinates))

        return IntersectionCoordinates
    else:
        # print(nU)
        print(f"🚨 intersection not possible for nU vector: {nU}")
        # exit(1)
        return None

