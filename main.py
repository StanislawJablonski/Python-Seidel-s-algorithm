from enum import Enum
import random


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "( %.4f" % self.x + "; " + "%.4f" % self.y + ")"


class Line():
    def __init__(self, array):
        self.x = array[0]
        self.y = array[1]


class Function(Line):
    def value(self, point):
        return point.x*self.x + point.y*self.y


class Crossing(Enum):
    none = 0
    point = 1
    overlay = 2

class Constraint(Line):

    def __init__(self, array):
        super().__init__(array)
        self.b = array[2]

    def __str__(self):
        return str(self.x) + "x + " + str(self.y) + "y <= " + str(self.b)

    #zwraca kierunek w ktorym rozciaga sie obszar dopuszczalny przez ograniczenie
    def side(self):
        xside = -1 if self.x < 0 else 0 if self.x == 0 else 1
        yside = -1 if self.y < 0 else 0 if self.y == 0 else 1
        return xside,yside


    def isIn(self, point):
        return point.x * self.x + point.y * self.y <= self.b


    def fun(self, x):
        return x * (-1 * self.x / self.y) + self.b / self.y


    def cross(self, new):
        l1 = self
        l2 = new

        # czy sa rownolegle
        if l1.x == l2.x and l1.y == l2.y:
            #czy sie pokrywaja
            if l1.b == l2.b:
                return Point(0, l1.fun(0)), Crossing.overlay
            else:
                return Point(0, l1.fun(0)), Crossing.none
        else:
            if l1.x == -1*l2.x and l1.y == -1*l2.y:
                #sa rownolegle, ale obszary rozciagaja sie w przeciwne strony
                if l1.b == -1*l2.b:
                    return Point(0, l1.fun(0)), Crossing.overlay
                else:
                    # maja wspolny pas, ale sie nie przecinaja
                    if l1.x < 0:
                        l1, l2 = l2, l1
                    if l1.b < -1*l2.b:
                        return Point(0, 0), Crossing.none
                    else:
                        return Point(0, 0), Crossing.none
        # czy jest pozioma/pionowa a druga prostopadla
        if l1.x == 0:
            y = l1.b / l1.y
            # czy druga linia jest prostopadla
            if l2.y == 0:
                x = l2.b / l2.x
            else:
                x = -1 * y * l2.y / l2.x + l2.b / l2.x
            return Point(x, y), Crossing.point

        if l1.y == 0:
            x = l1.b / l1.x
            # czy druga linia jest prostopadla
            if l2.x == 0:
                y = l2.b / l2.y
            else:
                y = l2.fun(x)
            return Point(x, y), Crossing.point

        # liczymy punkt przeciecia
        x = (l1.y * l2.b - l2.y * l1.b) / (l2.x * l1.y - l1.x * l2.y)
        y = l1.fun(x)
        return Point(x, y), Crossing.point

class Status(Enum):
    unsolved = 1
    solved = 2
    unbounded = 3
    infeasible = 4

class Seidels():
    def __init__(self,A,f):

        self.status = Status.unsolved
        self.function = Function(f)

        self.constraints = [Constraint(a) for a in A]
        random.shuffle(self.constraints)

        # x,y sa dodatnie
        self.used = []
        self.used.append(Constraint([-1,0,0]))
        self.used.append(Constraint([0,-1,0]))

        self.solution = None

        onlyConstr = None

        xConstr = None
        yConstr = None

        #szukamy ograniczen ograniczajacych obszar dopuszczalny, szukamy gdzie sie przecinaja
        # zamykamy obszar, 1 lub 2 ograniczeniami
        for constr in self.constraints:
            if constr.side() == (1, 1):
                onlyConstr = constr
                break
            elif constr.side()[0] == 1:
                if yConstr is None:
                    xConstr = constr
                else:
                    if yConstr.cross(constr)[1] != Crossing.none:
                        xConstr = constr
                        break
            elif constr.side()[1] == 1:
                if xConstr is None:
                    yConstr = constr
                else:
                    if xConstr.cross(constr)[1] != Crossing.none:
                        yConstr = constr
                        break
        possSolutions = []
        if onlyConstr is not None:
            self.used.append(onlyConstr)
            possSolutions.append(onlyConstr.cross(self.used[0])[0]) # przeciecie z pierwszym
            possSolutions.append(onlyConstr.cross(self.used[1])[0]) # i z drugim ograniczeniem
            self.constraints.remove(onlyConstr)
        else:
            #nie ma jednego ograniczenia zamykaajacego obszar, szukamy pary ograniczen zamykajacych obszar
            if xConstr is None or yConstr is None:
                #jesli jest tylko 1 ograniczenie z 2 to obszar jest nieograniczony
                self.status = Status.unbounded

                if xConstr is None:
                    for constr in self.constraints:
                        if constr.side()[0] == 1:
                            self.status = Status.infeasible
                            break
                elif yConstr is None:

                    for constr in self.constraints:
                        if constr.side()[1] == 1:
                            self.status = Status.infeasible
                            break
                elif xConstr is None and yConstr is None:
                    # zostaje nieograniczony
                    pass

            else:
                self.used.append(xConstr)
                self.used.append(yConstr)
                # sprawdzamy przecinanie z osiami
                possSolutions.append(xConstr.cross(self.used[0])[0])
                possSolutions.append(yConstr.cross(self.used[1])[0])

                crossing = yConstr.cross(xConstr)
                if crossing[1] == Crossing.point:possSolutions.append(crossing[0])
                elif crossing[1] == Crossing.overlay:
                    pass
                elif crossing[1] == Crossing.none:
                    pass
#
        if len(possSolutions) > 0:
            valid_solutions = []
            for s in possSolutions:
                if s.x >= 0 and s.y >= 0:
                    valid_solutions.append(s)

            if len(valid_solutions) == 0:
                self.status = Status.infeasible

            else:
                # szukamy maksymalnej wartosci funkcji
                self.solution = valid_solutions[0]
                for solution in valid_solutions:
                    if self.function.value(solution) > self.function.value(self.solution):
                        self.solution = solution


    def solve(self):
        while len(self.constraints) > 0 and self.status == Status.unsolved:
            constraint = self.constraints.pop()
            self.use_constraint(constraint)

        if len(self.constraints) == 0 and self.status == Status.unsolved:
            self.status = Status.solved


    def use_constraint(self, constraint):
        # ograniczenie nie zmienia rozwiazania
        if constraint.isIn(self.solution):
            self.used.append(constraint)
            return

        # gdy ograniczenie zmienia rozwiazanie
        crossing = []
        for con in self.used:
            point, status = constraint.cross(con)

            if status == Crossing.overlay:
                # gdy sie pokrywaja
                continue
            elif status == Crossing.none:
                # nie ma obszaru wspolnego
                self.status = Status.infeasible
                crossing = []
                break

            for constr in self.used:
                if constr.isIn(point):
                    continue
                else:
                    break

            else:
                crossing.append(point)

        if len(crossing) == 0:
            print("Nie ma rozwiązań")
            self.status = Status.infeasible
        else:
            self.solution = crossing[0]
            for solution in crossing:
                if self.function.value(solution) > self.function.value(self.solution):
                    self.solution = solution
            self.used.append(constraint)

    def result(self):
        if self.status == Status.solved:
            print("Znaleziono optymalne rozwiązanie.\nDla punktu: " + str(self.solution)
                  + "\nWartość funkcji: " + "%.4f" % self.function.value(self.solution))
        elif self.status == Status.unbounded:
            print("Nie znaleziono rozwiązania, nieograniczone.")
        elif self.status == Status.infeasible:
            print("Nie znaleziono rozwiązania, niewykonalne.")
        elif self.status == Status.unsolved:
            print("Nie rozwiązano.")

        print("\n_____________________________________________\n")



if __name__ == '__main__':
    print()

    A = [[0,1,2],
         [1,0,2]]
    f = [1,1]
    seidel = Seidels(A,f)
    seidel.solve()
    seidel.result()

    A = [[-4,3,-2],
         [1,2,3],
         [2,-1,3]]
    f = [3,1]
    seidel = Seidels(A,f)
    seidel.solve()
    seidel.result()


    A = [[-2,1,3],
         [-2,1,3]]
    f = [3,1]
    seidel = Seidels(A,f)
    seidel.solve()
    seidel.result()

    A = [[2,-1,4]
         ,[-1,2,-3]]
    f = [3,1]
    seidel = Seidels(A,f)
    seidel.solve()
    seidel.result()


    A = [[3,4,5],
         [1,5,5],
         [3,3,3],
         [3,5,2],
         [2,3,5]]
    f = [5,4]
    seidel = Seidels(A,f)
    seidel.solve()
    seidel.result()