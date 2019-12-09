import numpy as np
import time

class MergeSort(object):
    def __init__(self, unsorted):
        self.L = unsorted
        self.sorted = []
    

    def sort(self):
        self.merge_sort(0,len(self.L)-1)
        self.sorted = self.L

    def merge_sort(self, start, end):
        if start < end:
            mid = int((start + end)/2)
            self.merge_sort(start, mid)
            self.merge_sort(mid+1, end)
            self.merge(start, mid, end)


    def merge(self, start, mid, end):

        tmp = np.zeros(int(end-start+1))

        i = start
        j = mid+1
        k = 0
        while i <= mid and j <= end:
            if self.L[i] < self.L[j]:
                tmp[k] = self.L[i]
                k +=1
                i +=1
            else:
                tmp[k] = self.L[j]
                k +=1
                j +=1
        
        while i <= mid:
            tmp[k] = self.L[i]
            k +=1
            i +=1
        while j <= end:
            tmp[k] = self.L[j]
            k +=1
            j +=1
        
        for i in range(start, end+1):
            self.L[i] = tmp[i-start]

    def get(self):
        return self.L


if __name__ == "__main__":
    random_list = np.random.rand(100000)*100
    copy_random = random_list.copy()
    Sorter = MergeSort(random_list)
    t_now = time.time()
    Sorter.sort()
    sorted_list = Sorter.get()
    print(copy_random)
    print(sorted_list)
    print(time.time() - t_now)
