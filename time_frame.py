import time


class TimeFrame:
    def __init__(self, updateTime, timeFrame="h" | "m" | "s") -> None:
        self.timeFrame = timeFrame
        self.counter = []
        self.timeHandler = {
            "h": self.hTime,
            "m": self.mTime,
            "s": self.sTime
        }
        self.h
        self.m
        self.s

    async def countTime(self, updateTime):
        self.h, self.m, self.s = map(int, updateTime['values'].split(":"))
        await self.timePicker()

    async def timePicker(self):
        self.timeHandler[self.timeFrame]

    async def hTime(self):
        self.counter.append(self.h)
        return self.compareTime()

    async def mTime(self):
        self.counter.append(self.m)
        return self.compareTime()

    async def sTime(self):
        self.counter.append(self.s)
        print("m")
        return self.compareTime()

    def compareTime(self):
        return (self.counter[-1] != self.counter[-2])
