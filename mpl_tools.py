import matplotlib.pyplot as plt

def visualize(canvas):

    for i in range(3):
        plt.subplot(131+i).matshow(canvas.sum(axis=i))

    plt.show()