# Base Class for all pages. All pages should inherit from this class. 
# This class contains all the generic methods and utilities for all pages.
# This class is abstract and should not be instantiated directly.

from abc import ABC, abstractmethod

class BasePage(ABC):
    
    @abstractmethod
    def show(self):
        print("Showing the page")
