from plot import Covid19Dataset

if __name__ == '__main__':
    dataset = Covid19Dataset()
    for r in dataset.regions:
        print(r)
    dataset.plot(0, dataset.whole_russia_id, show_new=True)
