from __future__ import annotations

class Vector_Class:
    # --- INITIALIZATION OF VECTOR OBJECTS ------------------------------
    def __init__(self, dimension: int = None, coordinates: list = None):
        if (coordinates == None and type(dimension) == int):
            self.dimension = dimension
            self.coordinates = [0] * dimension
        elif (coordinates == None and type(dimension) == list):
            self.dimension = len(dimension)
            self.coordinates = dimension
        elif (dimension != len(coordinates)):
            raise Exception('Dimension does not coincide with given coordinates')
        else:
            self.dimension = dimension
            self.coordinates = coordinates
    # -------------------------------------------------------------------

    # --- MULTIPLICATION OPERATION --------------------------------------
    def __mul__(self, obj: Vector_Class | list | float | int) -> Vector_Class | float:
        if (type(obj) == Vector_Class):
            if (self.dimension != obj.dimension):
                raise Exception('Dimensions of objects do not coincide')
            else:
                return sum([self.coordinates[i] * obj.coordinates[i] for i in range(self.dimension)])
        
        # METHOD FOR SCALAR PROGUCT OF Vector_Class AND list
        elif (type(obj) == list):
            if (self.dimension != len(obj)):
                raise Exception('Dimensions of objects do not coincide')
            else:
                try:
                    return sum([self.coordinates[i] * obj[i] for i in range(self.dimension)])
                except Exception:
                    raise Exception(f'Failed to multiply objects of type {type(self)} and {type(obj)}')
        
        # METHOD FOR MULTIPLYING Vector_Class BY FLOAT
        elif (type(obj) == float or type(obj) == int):
            temp = Vector_Class(self.dimension)
            for i in range(self.dimension):
                temp.coordinates[i] = self.coordinates[i] * obj
            return temp
        # EXCEPTION
        else:
            raise Exception(f'Operation * between {type(self)} and {type(obj)} is not supported')
    # -------------------------------------------------------------------

    # --- ADDITION OPERATION --------------------------------------------
    def __add__(self, obj: Vector_Class | list) -> Vector_Class:
        # METHOD FOR ADDING TWO Vector_Class OBJECTS
        if (type(obj) == Vector_Class):
            if (self.dimension != obj.dimension):
                raise Exception('Dimensions of objects do not coincide')
            else:
                temp = Vector_Class(self.dimension)
                for i in range(self.dimension):
                    temp.coordinates[i] = self.coordinates[i] + obj.coordinates[i]
                return temp
        
        # METHOD FOR ADDING Vector_Class AND list
        elif (type(obj) == list):
            if (self.dimension != len(obj)):
                raise Exception('Dimensions of objects do not coincide')
            else:
                try:
                    temp = Vector_Class(self.dimension)
                    for i in range(self.dimension):
                        temp.coordinates[i] = self.coordinates[i] + obj[i]
                    return temp
                except Exception:
                    raise Exception(f'Failed to add objects of type {type(self)} and {type(obj)}')
        else:
            raise Exception(f'Operation + between {type(self)} and {type(obj)} is not supported')
    # -------------------------------------------------------------------

    # --- SUBTRACTION OPERATION --------------------------------------------
    def __sub__(self, obj: Vector_Class | list) -> Vector_Class:
        # METHOD FOR SUBTRACTIONG TWO Vector_Class OBJECTS
        if (type(obj) == Vector_Class):
            if (self.dimension != obj.dimension):
                raise Exception('Dimensions of objects do not coincide')
            else:
                temp = Vector_Class(self.dimension)
                for i in range(self.dimension):
                    temp.coordinates[i] = self.coordinates[i] - obj.coordinates[i]
                return temp
        
        # METHOD FOR SUBRACTING list FROM Vector_Class
        elif (type(obj) == list):
            if (self.dimension != len(obj)):
                raise Exception('Dimensions of objects do not coincide')
            else:
                try:
                    temp = Vector_Class(self.dimension)
                    for i in range(self.dimension):
                        temp.coordinates[i] = self.coordinates[i] - obj[i]
                    return temp
                except Exception:
                    raise Exception(f'Failed to subtract objects of type {type(self)} and {type(obj)}')
        else:
            raise Exception(f'Operation - between {type(self)} and {type(obj)} is not supported')
    # -------------------------------------------------------------------

    # --- SCALAR PRODUCT OPERATION --------------------------------------
    def scal_product(self, obj: Vector_Class | list) -> float:
        if (type(obj) == Vector_Class):
            if (self.dimension != obj.dimension):
                raise Exception('Dimensions of objects do not coincide')
            else:
                return sum([self.coordinates[i] * obj.coordinates[i] for i in range(self.dimension)])
        
        # METHOD FOR ADDING Vector_Class AND list
        if (type(obj) == list):
            if (self.dimension != len(obj)):
                raise Exception('Dimensions of objects do not coincide')
            else:
                return sum([self.coordinates[i] * obj[i] for i in range(self.dimension)])
    # -------------------------------------------------------------------

    # --- VECTOR ADDITION OPERATION -------------------------------------
    def vect_sum(self, obj: Vector_Class | list) -> Vector_Class:
        # METHOD FOR ADDING TWO Vector_Class OBJECTS
        if (type(obj) == Vector_Class):
            if (self.dimension != obj.dimension):
                raise Exception('Dimensions of objects do not coincide')
            else:
                temp = Vector_Class(self.dimension)
                for i in range(self.dimension):
                    temp.coordinates[i] = self.coordinates[i] + obj.coordinates[i]
                return temp
        
        # METHOD FOR ADDING Vector_Class AND list
        if (type(obj) == list):
            if (self.dimension != len(obj)):
                raise Exception('Dimensions of objects do not coincide')
            else:
                temp = Vector_Class(self.dimension)
                for i in range(self.dimension):
                    temp.coordinates[i] = self.coordinates[i] + obj[i]
                return temp
    # -------------------------------------------------------------------

    # --- VECTOR PRODUCT OPERATION --------------------------------------
    def vect_product(self, obj: Vector_Class | list) -> Vector_Class:
        # METHOD FOR MULTIPLYING TWO Vector_Class OBJECTS
        if (type(obj) == Vector_Class):
            if (self.dimension != 3 or obj.dimension != 3):
                raise Exception(f"Vector product is not supported for dimensions {self.dimension} and {obj.dimension}")
            else:
                temp = Vector_Class(self.dimension)
                temp.coordinates[0] = self.coordinates[1] * obj.coordinates[2] - self.coordinates[2] * obj.coordinates[1]
                temp.coordinates[1] = self.coordinates[2] * obj.coordinates[0] - self.coordinates[0] * obj.coordinates[2]
                temp.coordinates[2] = self.coordinates[0] * obj.coordinates[1] - self.coordinates[1] * obj.coordinates[0]
                return temp
            
        # METHOD FOR MULTIPLYING Vector_Class AND list
        if (type(obj) == list[float]):
            if (self.dimension != 3 or len(obj) != 3):
                raise Exception(f"Vector product is not supported for dimensions {self.dimension} and {len(obj)}")
            else:
                temp = Vector_Class(self.dimension)
                temp.coordinates[0] = self.coordinates[1] * obj[2] - self.coordinates[2] * obj[1]
                temp.coordinates[1] = self.coordinates[2] * obj[0] - self.coordinates[0] * obj[2]
                temp.coordinates[2] = self.coordinates[0] * obj[1] - self.coordinates[1] * obj[0]
                return temp
    # -------------------------------------------------------------------

    # --- FOR GETTING DISTANCE BETWEEN TWO POINTS -----------------------
    def get_distance(self, obj: Vector_Class | list) -> float:
        # METHOD FOR GETTING DISTANCE BETWEEN TWO Vector_Class OBJECTS
        if (type(obj) == Vector_Class):
            if (self.dimension != 3 or obj.dimension != 3):
                raise Exception(f"Distance is not supported for dimensions {self.dimension} and {obj.dimension}")
            else:
                return sum([(self.coordinates[i] - obj.coordinates[i])**2 for i in range(self.dimension)])**0.5
            
        # METHOD FOR GETTING DISTANCE BETWEEN Vector_Class AND list
        if (type(obj) == list[float]):
            if (self.dimension != 3 or len(obj) != 3):
                raise Exception(f"Vector product is not supported for dimensions {self.dimension} and {len(obj)}")
            else:
                return sum([(self.coordinates[i] - obj[i])**2 for i in range(self.dimension)])**0.5
    # -------------------------------------------------------------------

    # --- FOR PRINTING THE COORDINATES OF THE VECTOR --------------------
    def __str__(self) -> str:
        return str(self.coordinates)
    # -------------------------------------------------------------------

    # --- FOR PRINTING GETTING COORDINATES ------------------------------
    def get_coordinates(self) -> list:
        return self.coordinates
    # -------------------------------------------------------------------