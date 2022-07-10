from typing import List
import matplotlib.pyplot as plt

class PlotUtil:
  @staticmethod
  def makeHist(data: List[float], nBins=None) -> None:
    if nBins is None:
      nBins = min(int(len(data) / 5) + 1, 100)

    plt.hist(
      data,
      color = 'blue',
      bins = nBins,
      cumulative=False,
    )
    plt.title('Simulated Pack Values')
    plt.xlabel('Value ($)')
    plt.ylabel('N Packs')
    plt.show()

    plt.hist(
      data,
      color = 'blue',
      bins = nBins,
      cumulative=True,
    )
    plt.title('Simulated Pack Values (Cumulative)')
    plt.xlabel('Value ($)')
    plt.ylabel('N Packs')
    plt.show()
