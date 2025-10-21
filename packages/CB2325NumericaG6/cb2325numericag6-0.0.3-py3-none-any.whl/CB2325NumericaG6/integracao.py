from typing import Callable


def integral(f:Callable, start: float, end: float, divisions: int) -> float:
    """
        This method will calculate by trapezoidal aproximation the integral of a function.
        
        Args:
            f (Callable): Function.
            start (float): start point
            end (float): end point
            divisions (int): number of divisions, higher divisions implies a more precise approximation but also requires more CPU.
    """
    
    sumVal: float = 0
    Xincrement: float = abs(start-end)/divisions
    
    i: float = start
    while i < end:
        area: float = ( f(i) + f(min(end, i+Xincrement)) )
        area *= Xincrement/2.0 if i+Xincrement < end else (end-i)/2.0
        
        sumVal += area
        i += Xincrement
    
    return sumVal
