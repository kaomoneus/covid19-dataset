from plot import Covid19Dataset

if __name__ == '__main__':
    dataset = Covid19Dataset()
    for r in dataset.regions:
        print(r)
    dataset.plot_world(7, dataset.world_id, show_new=True)
